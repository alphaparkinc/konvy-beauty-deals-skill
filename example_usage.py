"""
example_usage.py -- Demonstrates the KonvyBeautyClient SDK.

Konvy.com is Thailand's leading authentic beauty e-commerce platform,
offering 20-70% discounts on skincare, makeup, fragrance, and more.
"""

from client import KonvyBeautyClient


def display_products(results: dict, heading: str = "Results") -> None:
    print("\n" + "=" * 60)
    print(f"  {heading}")
    print("=" * 60)
    key = next(
        (k for k in results if k not in ("products", "total_found", "best_deal")),
        None
    )
    if key:
        print(f"  {key.capitalize()}: {results[key]}")
    print(f"  Total Found: {results['total_found']}")
    print()

    for i, p in enumerate(results["products"], 1):
        name = p["name"][:55] + "..." if len(p["name"]) > 55 else p["name"]
        price = f"THB {p['sale_price_thb']:,.0f}" if p["sale_price_thb"] else "N/A"
        orig  = f"THB {p['original_price_thb']:,.0f}" if p["original_price_thb"] else ""
        disc  = f"  (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
        brand = f" [{p['brand']}]" if p.get("brand") else ""
        print(f"  {i:>2}. {name}{brand}")
        print(f"      Price: {price}{(' / orig: ' + orig) if orig else ''}{disc}")
        print(f"      URL:   {p['url']}")
        print()

    if results.get("best_deal"):
        bd = results["best_deal"]
        print(f"  [BEST DEAL] {bd['name'][:50]}")
        if bd.get("sale_price_thb"):
            print(f"    Price: THB {bd['sale_price_thb']:,.0f}  Discount: {bd.get('discount_pct', 0)}%")
        print(f"    URL:   {bd['url']}")


def main():
    client = KonvyBeautyClient(timeout=15, delay_between_requests=0.5)

    # 1. Search by keyword
    print("\n[1] Searching for 'CeraVe' products on Konvy...")
    try:
        results = client.search_products("CeraVe", limit=5)
        display_products(results, "CeraVe Search Results")
    except Exception as e:
        print(f"  Search failed: {e}")

    # 2. Browse a category
    print("\n[2] Browsing Skincare category (under THB 500)...")
    try:
        results = client.browse_category("skincare", max_price_thb=500, limit=5)
        display_products(results, "Skincare Under THB 500")
    except Exception as e:
        print(f"  Category browse failed: {e}")

    # 3. Browse a brand
    print("\n[3] Browsing Neutrogena brand page...")
    try:
        results = client.browse_brand("neutrogena-2", limit=5)
        display_products(results, "Neutrogena Products on Konvy")
    except Exception as e:
        print(f"  Brand browse failed: {e}")

    # 4. Get promotions
    print("\n[4] Getting New Arrivals promotion...")
    try:
        results = client.get_promotions(promo_sign="NewArrival_20241001", limit=5)
        display_products(results, "New Arrivals on Konvy")
    except Exception as e:
        print(f"  Promotions failed: {e}")

    # 5. Find best deals
    print("\n[5] Finding best makeup deals (min 30% off)...")
    try:
        results = client.find_best_deals("makeup", min_discount_pct=30.0, limit=5)
        display_products(results, "Makeup Deals >= 30% Off")
    except Exception as e:
        print(f"  Deal finder failed: {e}")


if __name__ == "__main__":
    main()
