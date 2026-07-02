"""
konvy-beauty-deals-skill: Client SDK
Discover authentic beauty deals on Konvy.com — Thailand's top cosmetics marketplace.
"""

from __future__ import annotations
import urllib.request
import urllib.parse
import urllib.error
import json
import re
import time
from typing import Optional


# Konvy category IDs mapped to internal category param IDs
CATEGORY_MAP = {
    "skincare":  "113",
    "makeup":    "114",
    "baby":      "2993",
    "tools":     "8009",
    "fashion":   "5996",
    "fragrance": "115",
    "health":    "119",
    "home":      "6894",
    "body":      "116",
}

BASE_URL = "https://www.konvy.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.konvy.com/",
}


class KonvyBeautyClient:
    """
    SDK for discovering beauty deals and products on Konvy.com.

    Features:
      - Product search by keyword
      - Category browsing (skincare, makeup, fragrance, etc.)
      - Brand page scraping
      - Deal scoring by discount percentage
      - Price filtering in Thai Baht (THB)
      - Best deal extraction
    """

    def __init__(self, timeout: int = 15, delay_between_requests: float = 0.5):
        self.timeout = timeout
        self.delay = delay_between_requests

    # ── Public API ────────────────────────────────────────────────────────────

    def search_products(
        self,
        query: str,
        max_price_thb: Optional[float] = None,
        limit: int = 10,
    ) -> dict:
        """
        Search for beauty products by keyword on Konvy.com.

        Args:
            query:          Search keyword (product name, ingredient, etc.).
            max_price_thb:  Optional max price filter in Thai Baht.
            limit:          Max number of results to return.

        Returns:
            dict with keys: query, products, total_found, best_deal
        """
        url = f"{BASE_URL}/list/?title={urllib.parse.quote(query)}"
        html = self._fetch(url)
        products = self._parse_product_list(html, max_price_thb, limit)
        return self._build_result(query, products)

    def browse_category(
        self,
        category: str,
        max_price_thb: Optional[float] = None,
        limit: int = 10,
    ) -> dict:
        """
        Browse products by category.

        Args:
            category:       One of: skincare, makeup, fragrance, health, baby,
                            tools, fashion, body, home.
            max_price_thb:  Optional max price filter in Thai Baht.
            limit:          Max number of results.

        Returns:
            dict with keys: category, products, total_found, best_deal
        """
        cat_id = CATEGORY_MAP.get(category.lower())
        if not cat_id:
            raise ValueError(
                f"Unknown category: '{category}'. "
                f"Valid options: {list(CATEGORY_MAP.keys())}"
            )
        url = f"{BASE_URL}/mall/list.php?param={cat_id}-0-0-0&from=category"
        html = self._fetch(url)
        products = self._parse_product_list(html, max_price_thb, limit)
        return self._build_result(category, products, key="category")

    def browse_brand(
        self,
        brand: str,
        max_price_thb: Optional[float] = None,
        limit: int = 10,
    ) -> dict:
        """
        Browse products from a specific brand on Konvy.

        Args:
            brand:          Brand slug (e.g. 'cerave', 'maybelline', 'neutrogena-2').
            max_price_thb:  Optional max price filter.
            limit:          Max results.

        Returns:
            dict with keys: brand, products, total_found, best_deal
        """
        url = f"{BASE_URL}/brand/{brand.lower()}/"
        html = self._fetch(url)
        products = self._parse_product_list(html, max_price_thb, limit)
        return self._build_result(brand, products, key="brand")

    def get_promotions(
        self,
        promo_sign: str = "NewArrival_20241001",
        limit: int = 10,
    ) -> dict:
        """
        Get products from a Konvy promotional page.

        Common promo_signs:
          - "Luxe"                  -> Luxury brands
          - "NewArrival_20241001"   -> New arrivals
          - "CounterBrand_2022"     -> Counter brands
          - "Fragrance_20260525"    -> Fragrances

        Returns:
            dict with keys: promo_sign, products, total_found, best_deal
        """
        url = f"{BASE_URL}/promo/?sign={urllib.parse.quote(promo_sign)}"
        html = self._fetch(url)
        products = self._parse_product_list(html, None, limit)
        return self._build_result(promo_sign, products, key="promo_sign")

    def find_best_deals(
        self,
        category: str = "skincare",
        min_discount_pct: float = 20.0,
        limit: int = 10,
    ) -> dict:
        """
        Find products with the highest discount in a given category.

        Args:
            category:          Category to scan.
            min_discount_pct:  Minimum discount percentage threshold.
            limit:             Max results to return.

        Returns:
            Products sorted by discount percentage descending.
        """
        result = self.browse_category(category, limit=50)
        deals = [
            p for p in result["products"]
            if p.get("discount_pct", 0) >= min_discount_pct
        ]
        deals.sort(key=lambda x: x.get("discount_pct", 0), reverse=True)
        deals = deals[:limit]
        return self._build_result(category, deals, key="category")

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _fetch(self, url: str) -> str:
        """Fetch HTML from a Konvy URL with retry logic."""
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                time.sleep(self.delay)
                return html
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise ValueError(f"Page not found: {url}")
                if attempt == 2:
                    raise
                time.sleep(1.5 * (attempt + 1))
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1.5 * (attempt + 1))
        return ""

    def _parse_product_list(
        self,
        html: str,
        max_price_thb: Optional[float],
        limit: int,
    ) -> list[dict]:
        """
        Parse product cards from Konvy listing HTML.
        Tries JSON-LD structured data first, then regex fallback.
        """
        products = []

        # Try JSON-LD structured data
        json_ld_matches = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        for jld in json_ld_matches:
            try:
                data = json.loads(jld.strip())
                if isinstance(data, list):
                    for item in data:
                        p = self._extract_from_jsonld(item)
                        if p:
                            products.append(p)
                elif isinstance(data, dict):
                    p = self._extract_from_jsonld(data)
                    if p:
                        products.append(p)
            except Exception:
                continue

        # Fallback regex scraping
        if not products:
            products = self._regex_scrape_products(html)

        # Filter by price
        if max_price_thb is not None:
            products = [
                p for p in products
                if p.get("sale_price_thb") is None
                or p["sale_price_thb"] <= max_price_thb
            ]

        return products[:limit]

    def _extract_from_jsonld(self, data: dict) -> Optional[dict]:
        """Extract product info from JSON-LD structured data block."""
        if data.get("@type") not in ("Product", "Offer"):
            return None
        name = data.get("name", "")
        url = data.get("url", "")
        image = data.get("image", "")
        brand = ""
        if isinstance(data.get("brand"), dict):
            brand = data["brand"].get("name", "")
        offers = data.get("offers", {})
        if isinstance(offers, list) and offers:
            offers = offers[0]
        sale_price = None
        orig_price = None
        if isinstance(offers, dict):
            sale_price = self._parse_price(str(offers.get("price", "")))
        discount_pct = 0.0
        if orig_price and sale_price and orig_price > 0:
            discount_pct = round((1 - sale_price / orig_price) * 100, 1)
        if not name:
            return None
        return {
            "name": name,
            "brand": brand,
            "sale_price_thb": sale_price,
            "original_price_thb": orig_price,
            "discount_pct": discount_pct,
            "url": url if url.startswith("http") else BASE_URL + url,
            "image_url": image if isinstance(image, str) else "",
        }

    def _regex_scrape_products(self, html: str) -> list[dict]:
        """Fallback: extract products via regex from Konvy HTML."""
        products = []

        # Konvy product link pattern
        link_pattern = re.compile(
            r'href="(/(?:item|product|goods)/[^"]+)"[^>]*>\s*<[^>]+>\s*([^<]{5,80})\s*</',
            re.IGNORECASE
        )

        # Price pattern: Thai Baht symbol or THB prefix
        price_pattern = re.compile(r'(?:[\u0e3f]|THB|\bB\.?)\s*([\d,]+(?:\.\d{1,2})?)')

        seen = set()
        for m in link_pattern.finditer(html):
            path, name = m.group(1), m.group(2).strip()
            if not name or name in seen or len(name) < 5:
                continue
            seen.add(name)
            url = BASE_URL + path

            context = html[max(0, m.start() - 200): m.end() + 500]
            prices = []
            for p in price_pattern.findall(context):
                try:
                    prices.append(float(p.replace(",", "")))
                except ValueError:
                    pass

            sale_price = min(prices) if prices else None
            orig_price = max(prices) if len(prices) > 1 else None
            discount_pct = 0.0
            if orig_price and sale_price and orig_price > sale_price:
                discount_pct = round((1 - sale_price / orig_price) * 100, 1)

            products.append({
                "name": name,
                "brand": "",
                "sale_price_thb": sale_price,
                "original_price_thb": orig_price,
                "discount_pct": discount_pct,
                "url": url,
                "image_url": "",
            })

            if len(products) >= 50:
                break

        return products

    @staticmethod
    def _parse_price(raw: str) -> Optional[float]:
        """Parse a price string into a float."""
        raw = raw.replace(",", "").replace("\u0e3f", "").replace("THB", "").strip()
        try:
            return float(raw)
        except ValueError:
            return None

    @staticmethod
    def _build_result(
        key_value: str,
        products: list[dict],
        key: str = "query",
    ) -> dict:
        """Assemble the standard result dict."""
        best_deal = None
        if products:
            scored = sorted(
                [p for p in products if p.get("discount_pct", 0) > 0],
                key=lambda x: x["discount_pct"],
                reverse=True,
            )
            best_deal = scored[0] if scored else products[0]
        return {
            key: key_value,
            "products": products,
            "total_found": len(products),
            "best_deal": best_deal,
        }
