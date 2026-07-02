# konvy-beauty-deals-skill

> **GenPark AI Agent Skill** -- Discover authentic beauty deals on [Konvy.com](https://www.konvy.com), Thailand's leading cosmetics e-commerce platform.

## Overview

Konvy.com offers 20-70% discounts on **100% authentic** skincare, makeup, fragrance, vitamins, and beauty tools across 500+ global and Thai brands. This skill distills Konvy's core capabilities into a structured AI agent SDK.

### Supported Actions

| Method | Description |
|---|---|
| `search_products(query)` | Search by keyword (product, ingredient, brand) |
| `browse_category(category)` | Browse by category (skincare, makeup, fragrance, etc.) |
| `browse_brand(brand)` | List products from a specific brand |
| `get_promotions(promo_sign)` | Access promotional pages (LUXE, New Arrivals, etc.) |
| `find_best_deals(category)` | Surface highest-discount products in a category |

### Categories

`skincare` | `makeup` | `fragrance` | `health` | `baby` | `tools` | `fashion` | `body` | `home`

## Quick Start

```python
from client import KonvyBeautyClient

client = KonvyBeautyClient()

# Search for CeraVe products
results = client.search_products("CeraVe", max_price_thb=500, limit=10)
print(results["best_deal"])

# Find makeup deals >= 30% off
deals = client.find_best_deals("makeup", min_discount_pct=30.0)
for product in deals["products"]:
    price = product['sale_price_thb']
    disc = product['discount_pct']
    print(f"{product['name']} -- THB {price:,.0f} ({disc}% off)")
```

## Installation

```bash
# No external dependencies -- uses Python stdlib only
python --version  # Python 3.9+
python example_usage.py
```

## Response Format

```json
{
  "query": "CeraVe",
  "products": [
    {
      "name": "CeraVe Moisturizing Cream 340g",
      "brand": "CeraVe",
      "sale_price_thb": 399.0,
      "original_price_thb": 599.0,
      "discount_pct": 33.4,
      "url": "https://www.konvy.com/item/...",
      "image_url": "https://..."
    }
  ],
  "total_found": 8,
  "best_deal": { "..." : "..." }
}
```

## Popular Brands on Konvy

CeraVe | Neutrogena | L'Oreal Paris | Maybelline | Garnier | Biore | Vaseline | Mediheal | BANOBAGI | Srichand | Kiehls | Eucerin | Plantnery | ROM&ND | SKINTIFIC

## Skill Metadata

```json
{
  "name": "konvy-beauty-deals-skill",
  "category": "e-commerce",
  "tags": ["beauty", "cosmetics", "skincare", "deals", "thailand", "konvy"],
  "platform": "Konvy.com"
}
```

## About Konvy.com

- Thailand's #1 authentic beauty marketplace
- 500+ brands from Korea, Japan, Europe, USA, and Thailand
- Free shipping on orders over THB 499
- Flash deals up to 70% off
- Mobile apps on iOS, Android & Huawei AppGallery
- Supports Thai, English, and Chinese

---

Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
