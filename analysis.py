"""
Amazon Home Improvement Product Analysis
=========================================
Analysing ~5,000 Amazon home improvement products (Q1 2020) to uncover
pricing strategies, brand positioning, and market dynamics relevant to
building materials and home furnishings retail.

Author: Tommy Nguyen
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ── Configuration ────────────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("muted")
VISUALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visuals")
os.makedirs(VISUALS_DIR, exist_ok=True)
DPI = 150

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "marketing_sample_for_amazon_com-amazon_home_improvement_data"
    "__20200101_20200331__5k_data.ldjson",
)


# ── 1. Load & Clean Data ────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_json(DATA_FILE, lines=True)
print(f"Raw dataset: {df.shape[0]:,} products, {df.shape[1]} columns\n")

# --- Price cleaning ---
# sales_price is already numeric in most rows; force any stragglers
df["sales_price"] = pd.to_numeric(df["sales_price"], errors="coerce")

# --- Discount cleaning (strip %, convert to float) ---
df["discount_pct"] = (
    df["discount_percentage"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .pipe(pd.to_numeric, errors="coerce")
)

# --- Rating & reviews ---
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["reviews"] = pd.to_numeric(df["no__of_reviews"], errors="coerce")

# --- Prime flag ---
df["is_prime"] = df["amazon_prime__y_or_n"].str.upper() == "Y"

# --- Best seller flag ---
df["is_bestseller"] = df["best_seller_tag__y_or_n"].str.upper() == "Y"

# --- Extract sub-category from the nested dict ---
def extract_subcategory(val):
    """Pull the most specific (child) category from the nested dict."""
    if not isinstance(val, dict):
        return "Uncategorised"
    keys = [k for k in val.keys() if k != "HomeImprovement"]
    return keys[0] if keys else "General Home Improvement"

df["category"] = df["parent___child_category__all"].apply(extract_subcategory)

# Quick summary after cleaning
print("After cleaning:")
print(f"  Valid prices:    {df['sales_price'].notna().sum():,}")
print(f"  Valid ratings:   {df['rating'].notna().sum():,}")
print(f"  Valid discounts: {df['discount_pct'].notna().sum():,}")
print(f"  Prime products:  {df['is_prime'].sum():,}")
print(f"  Categories:      {df['category'].nunique()}\n")


# ── 2. Price Distribution Across Categories ─────────────────────────────────
print("Generating price distribution chart...")

# Focus on top 12 categories by product count for readability
top_cats = df["category"].value_counts().head(12).index.tolist()
df_top = df[df["category"].isin(top_cats) & df["sales_price"].notna()].copy()

# Cap extreme outliers for the visual (99th percentile)
price_cap = df_top["sales_price"].quantile(0.99)
df_top["price_capped"] = df_top["sales_price"].clip(upper=price_cap)

fig, ax = plt.subplots(figsize=(12, 6))
order = (
    df_top.groupby("category")["price_capped"]
    .median()
    .sort_values(ascending=False)
    .index
)
sns.boxplot(data=df_top, y="category", x="price_capped", order=order, ax=ax)
ax.set_xlabel("Price (INR, capped at 99th pctl)")
ax.set_ylabel("")
ax.set_title("Price Distribution by Category (Top 12 Categories)")
plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, "01_price_by_category.png"), dpi=DPI)
plt.close()


# ── 3. Top Brands — Product Count & Average Rating ──────────────────────────
print("Generating brand analysis chart...")

brand_stats = (
    df.groupby("brand")
    .agg(product_count=("brand", "size"), avg_rating=("rating", "mean"))
    .sort_values("product_count", ascending=False)
    .head(15)
)

fig, ax1 = plt.subplots(figsize=(12, 6))
x = range(len(brand_stats))
bars = ax1.bar(x, brand_stats["product_count"], color=sns.color_palette("muted")[0],
               alpha=0.8, label="Product Count")
ax1.set_ylabel("Number of Products")
ax1.set_xlabel("")
ax1.set_xticks(x)
ax1.set_xticklabels(brand_stats.index, rotation=45, ha="right")

ax2 = ax1.twinx()
ax2.plot(x, brand_stats["avg_rating"], color=sns.color_palette("muted")[3],
         marker="o", linewidth=2, label="Avg Rating")
ax2.set_ylabel("Average Rating")
ax2.set_ylim(2.5, 5.2)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

ax1.set_title("Top 15 Brands: Product Count vs Average Rating")
plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, "02_top_brands.png"), dpi=DPI)
plt.close()


# ── 4. Discount vs Reviews — Do Bigger Discounts Drive Engagement? ──────────
print("Generating discount vs reviews chart...")

df_disc = df.dropna(subset=["discount_pct", "reviews"]).copy()
# Bin discounts for clearer visual
df_disc["discount_bin"] = pd.cut(
    df_disc["discount_pct"],
    bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 100],
    labels=["1-10%", "11-20%", "21-30%", "31-40%", "41-50%",
            "51-60%", "61-70%", "71-80%", "81-100%"],
)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: median reviews by discount band
median_reviews = df_disc.groupby("discount_bin", observed=True)["reviews"].median()
median_reviews.plot(kind="bar", ax=ax1, color=sns.color_palette("muted")[1])
ax1.set_ylabel("Median Number of Reviews")
ax1.set_xlabel("Discount Band")
ax1.set_title("Customer Engagement by Discount Level")
ax1.tick_params(axis="x", rotation=45)

# Right: scatter (sampled for clarity)
sample = df_disc.sample(min(1000, len(df_disc)), random_state=42)
ax2.scatter(sample["discount_pct"], sample["reviews"],
            alpha=0.3, s=20, color=sns.color_palette("muted")[2])
ax2.set_xlabel("Discount (%)")
ax2.set_ylabel("Number of Reviews")
ax2.set_title("Discount % vs Review Count (sampled)")
ax2.set_yscale("log")

plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, "03_discount_vs_reviews.png"), dpi=DPI)
plt.close()


# ── 5. Rating Distribution + Avg Rating by Category ─────────────────────────
print("Generating rating analysis chart...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: overall rating distribution
df["rating"].dropna().hist(bins=20, ax=ax1, color=sns.color_palette("muted")[4],
                           edgecolor="white")
ax1.axvline(df["rating"].mean(), color="red", linestyle="--", label=f'Mean: {df["rating"].mean():.2f}')
ax1.set_xlabel("Rating")
ax1.set_ylabel("Number of Products")
ax1.set_title("Overall Rating Distribution")
ax1.legend()

# Right: avg rating by top categories
cat_rating = (
    df[df["category"].isin(top_cats)]
    .groupby("category")["rating"]
    .mean()
    .sort_values(ascending=True)
)
cat_rating.plot(kind="barh", ax=ax2, color=sns.color_palette("muted")[0])
ax2.set_xlabel("Average Rating")
ax2.set_title("Avg Rating by Category (Top 12)")
ax2.set_ylabel("")

plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, "04_rating_analysis.png"), dpi=DPI)
plt.close()


# ── 6. Prime vs Non-Prime Comparison ────────────────────────────────────────
print("Generating Prime comparison chart...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Price comparison
prime_prices = df[df["is_prime"] & df["sales_price"].notna()]["sales_price"]
non_prime_prices = df[~df["is_prime"] & df["sales_price"].notna()]["sales_price"]

price_data = pd.DataFrame({
    "Prime": [prime_prices.median(), prime_prices.mean()],
    "Non-Prime": [non_prime_prices.median(), non_prime_prices.mean()],
}, index=["Median Price", "Mean Price"])

price_data.plot(kind="bar", ax=ax1, color=[sns.color_palette("muted")[0],
                                           sns.color_palette("muted")[2]])
ax1.set_ylabel("Price (INR)")
ax1.set_title("Price: Prime vs Non-Prime")
ax1.tick_params(axis="x", rotation=0)

# Rating comparison
prime_stats = df.groupby("is_prime").agg(
    avg_rating=("rating", "mean"),
    avg_reviews=("reviews", "mean"),
    avg_discount=("discount_pct", "mean"),
).rename(index={True: "Prime", False: "Non-Prime"})

prime_stats[["avg_rating"]].plot(kind="bar", ax=ax2,
                                 color=[sns.color_palette("muted")[0],
                                        sns.color_palette("muted")[2]],
                                 legend=False)
ax2.set_ylabel("Average Rating")
ax2.set_title("Avg Rating: Prime vs Non-Prime")
ax2.tick_params(axis="x", rotation=0)
ax2.set_ylim(3.0, 5.0)

plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, "05_prime_comparison.png"), dpi=DPI)
plt.close()


# ── 7. Seller Concentration — Who Controls the Market? ──────────────────────
print("Generating seller concentration chart...")

seller_counts = df["seller_name"].value_counts()
top_10_sellers = seller_counts.head(10)
others = seller_counts.iloc[10:].sum()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: top 10 sellers bar chart
top_10_sellers.plot(kind="barh", ax=ax1, color=sns.color_palette("muted")[5])
ax1.set_xlabel("Number of Products Listed")
ax1.set_title("Top 10 Sellers by Product Count")
ax1.set_ylabel("")
ax1.invert_yaxis()

# Right: market concentration (top 10 vs rest)
total = len(df)
top10_pct = top_10_sellers.sum() / total * 100
rest_pct = 100 - top10_pct
ax2.pie([top10_pct, rest_pct],
        labels=[f"Top 10 Sellers\n({top10_pct:.1f}%)",
                f"All Others\n({rest_pct:.1f}%)"],
        colors=[sns.color_palette("muted")[0], sns.color_palette("muted")[7]],
        startangle=90, textprops={"fontsize": 11})
ax2.set_title(f"Market Concentration ({df['seller_name'].nunique()} total sellers)")

plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, "06_seller_concentration.png"), dpi=DPI)
plt.close()


# ── 8. Print Key Findings Summary ───────────────────────────────────────────
print("\n" + "=" * 60)
print("KEY FINDINGS SUMMARY")
print("=" * 60)

print(f"\nDataset: {len(df):,} products across {df['category'].nunique()} categories")
print(f"Price range: INR {df['sales_price'].min():,.0f} – {df['sales_price'].max():,.0f}")
print(f"Median price: INR {df['sales_price'].median():,.0f}")
print(f"Average rating: {df['rating'].mean():.2f} / 5.0")
print(f"Average discount: {df['discount_pct'].mean():.1f}%")

print(f"\nPrime products: {df['is_prime'].sum():,} ({df['is_prime'].mean()*100:.1f}%)")
print(f"  Prime avg price:     INR {prime_prices.mean():,.0f}")
print(f"  Non-Prime avg price: INR {non_prime_prices.mean():,.0f}")
print(f"  Prime avg rating:    {prime_stats.loc['Prime', 'avg_rating']:.2f}")
print(f"  Non-Prime avg rating:{prime_stats.loc['Non-Prime', 'avg_rating']:.2f}")

print(f"\nTop 5 brands by product count:")
for brand, count in df["brand"].value_counts().head(5).items():
    avg_r = df[df["brand"] == brand]["rating"].mean()
    print(f"  {brand}: {count} products (avg rating: {avg_r:.2f})")

print(f"\nTop 5 categories:")
for cat, count in df["category"].value_counts().head(5).items():
    print(f"  {cat}: {count} products")

print(f"\nDiscount insight:")
high_disc = df[df["discount_pct"] >= 50]
low_disc = df[df["discount_pct"] < 50]
print(f"  Products with 50%+ discount: {len(high_disc):,}")
print(f"  Their median reviews: {high_disc['reviews'].median():.0f}")
print(f"  Products with <50% discount: {len(low_disc):,}")
print(f"  Their median reviews: {low_disc['reviews'].median():.0f}")

print(f"\nSeller concentration:")
print(f"  Total unique sellers: {df['seller_name'].nunique()}")
print(f"  Top 10 sellers control: {top10_pct:.1f}% of listings")

print(f"\nAll charts saved to: {VISUALS_DIR}/")
print("=" * 60)
