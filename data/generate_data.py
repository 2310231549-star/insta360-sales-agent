"""Generate realistic multi-channel sales data for an Insta360-like brand."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# ── Product catalog ──
PRODUCTS = {
    "X4":       {"cat": "Action Camera", "cost": 320, "price": 499},
    "X3":       {"cat": "Action Camera", "cost": 220, "price": 399},
    "GO 3S":    {"cat": "Action Camera", "cost": 140, "price": 239},
    "Ace Pro":  {"cat": "Action Camera", "cost": 200, "price": 349},
    "Selfie Stick": {"cat": "Accessory", "cost": 8,  "price": 25},
    "Lens Cap":     {"cat": "Accessory", "cost": 2,  "price": 9},
    "Battery":      {"cat": "Accessory", "cost": 15, "price": 39},
    "Charging Hub": {"cat": "Accessory", "cost": 20, "price": 59},
    "Bike Mount":   {"cat": "Mount", "cost": 6,  "price": 19},
    "Helmet Mount": {"cat": "Mount", "cost": 7,  "price": 22},
    "Tripod Stand": {"cat": "Mount", "cost": 10, "price": 35},
    "Invisible Stick": {"cat": "Accessory", "cost": 12, "price": 45},
}

REGIONS_AMAZON = ["US", "UK", "DE", "JP"]
REGIONS_SHOPIFY = ["US", "UK", "EU"]
REGION_WEIGHTS = {"US": 0.45, "UK": 0.20, "DE": 0.15, "JP": 0.10, "EU": 0.10}


def gen_orders(channel: str, start_date: str, n_orders: int) -> pd.DataFrame:
    regions = REGIONS_AMAZON if channel == "Amazon" else REGIONS_SHOPIFY
    weights = [REGION_WEIGHTS[r] for r in regions]
    wsum = sum(weights)
    weights = [w / wsum for w in weights]

    dates = pd.date_range(start=start_date, periods=n_orders, freq="h")
    orders = []
    for i, dt in enumerate(dates):
        if np.random.random() < 0.15:  # 15% skip
            continue
        sku = np.random.choice(list(PRODUCTS.keys()), p=[
            0.22, 0.15, 0.12, 0.10, 0.08, 0.05, 0.08, 0.05, 0.05, 0.04, 0.03, 0.03
        ])
        prod = PRODUCTS[sku]
        region = np.random.choice(regions, p=weights)
        qty = np.random.choice([1, 1, 1, 1, 2, 2, 3], p=[0.5, 0.2, 0.1, 0.05, 0.07, 0.05, 0.03])
        # price with small random fluctuation and regional markup
        price_mul = {"US": 1.0, "UK": 1.15, "DE": 1.12, "JP": 1.08, "EU": 1.15}
        price = round(prod["price"] * price_mul.get(region, 1.0) * np.random.uniform(0.88, 1.05), 2)
        revenue = round(price * qty, 2)
        cost = round(prod["cost"] * qty, 2)
        shipping = round(np.random.uniform(3.99, 9.99) * (1 + 0.5 * (qty - 1)), 2)
        platform_fee = round(revenue * (0.15 if channel == "Amazon" else 0.05), 2)
        ad_spend = round(revenue * np.random.uniform(0.05, 0.12) if channel == "Amazon" else 0, 2)

        orders.append({
            "date": dt.strftime("%Y-%m-%d"),
            "order_id": f"{channel[:3].upper()}-{i+100000:06d}",
            "sku": sku,
            "product_name": sku,
            "category": prod["cat"],
            "channel": channel,
            "region": region,
            "units_sold": qty,
            "unit_price": price,
            "revenue": revenue,
            "cost": cost,
            "shipping_cost": round(shipping, 2),
            "platform_fee": platform_fee,
            "ad_spend": ad_spend,
        })
    return pd.DataFrame(orders)


if __name__ == "__main__":
    amazon = gen_orders("Amazon", "2025-05-01", 3000)
    shopify = gen_orders("Shopify", "2025-05-01", 1200)

    amazon.to_csv("data/amazon_sales.csv", index=False)
    shopify.to_csv("data/shopify_sales.csv", index=False)
    print(f"Generated {len(amazon)} Amazon orders + {len(shopify)} Shopify orders")
    print(f"Amazon:  {amazon['revenue'].sum():,.0f} revenue | Shopify: {shopify['revenue'].sum():,.0f} revenue")
