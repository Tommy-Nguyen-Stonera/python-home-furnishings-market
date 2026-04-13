# Home Furnishings Market Analysis (Python)

[View Interactive Report](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Tommy-Nguyen-Stonera/python-home-furnishings-market/main/report.html)

## Overview

This project analyses 5,000 Amazon India home improvement product listings to understand pricing, brand concentration, discount behaviour, and what drives customer engagement. The data comes from Q1 2020 and covers 145 sub-categories, giving a snapshot of how the market was structured at the start of the COVID period.

## Dataset

- Source: Amazon India Home Improvement listings (LDJSON format), Q1 2020
- Record count: 5,000 products
- Coverage: 145 sub-categories, 2,000+ unique brands and sellers
- Key columns: product title, category (extracted from nested dict), price, discount_pct (computed), is_prime (computed), is_bestseller (computed), rating, review count
- Single flat table after parsing and feature engineering, no joins required

## Research Questions

1. Which categories carry the highest prices, and how wide is the price spread within them?
2. Which brands dominate by listing count and by customer ratings?
3. Do bigger discounts drive more customer reviews, and is there a point where the effect plateaus?
4. What does the overall rating distribution look like across all 5,000 products?
5. Do Prime products outperform non-Prime products on ratings and price?
6. How concentrated is the seller base, and does it resemble physical retail or marketplace fragmentation?

## Data Model

Single flat table after LDJSON parsing. Discount percentage, Prime status, and bestseller flags are computed from raw fields during ingestion. Category is extracted from a nested dictionary field. All analysis runs from this one table.

## What Was Analysed

- Median and spread of prices by category, ranked from highest to lowest
- Top brands by listing count and by average customer rating
- Correlation between discount percentage and review count, with a threshold test at 60%+
- Distribution of product ratings across all 5,000 listings
- Prime vs non-Prime comparison on average rating and average price
- Seller concentration: top 10 sellers' share of total listings vs long tail

## Key Insights

1. Pricing varies widely by category. The median price is INR 899, most products sit under INR 2,000, but outliers stretch above INR 50,000. Power and hand tools show the widest price spread.
2. The market is fragmented across 2,000+ brands. The top brand (uxcell) holds just 3.4% of listings with 168 products. No single brand dominates.
3. Products with 50%+ discounts average 35% more reviews (median 23 vs 17 for lower-discount products). The engagement lift plateaus past 60% off, suggesting diminishing returns to deeper discounting.
4. Prime products rate slightly lower on average (4.06 vs 4.18 for non-Prime) and sell at much lower prices (INR 869 vs INR 2,488 average). Prime status is not a reliable signal of product quality.
5. The top 10 sellers control just 15.8% of listings. With 2,000+ unique sellers, the seller base is far more fragmented than physical retail, which means no single seller has meaningful pricing power.
6. The rating distribution is heavily skewed above 4.0. Products below 3.5 stars are rare, suggesting either genuine quality standards or review optimisation behaviour at scale.

## Recommendations

1. Use discount levels in the 50 to 60% range to maximise review engagement without sacrificing margin unnecessarily. The data shows engagement lifts plateau past 60%, making deeper discounts a cost with no proportional return.
2. Do not treat Prime status as a quality filter when sourcing or listing products. Prime products actually rate lower on average and sell at significantly lower price points in this dataset.
3. For new sellers entering this marketplace, differentiation is achievable. Seller concentration is low and no brand controls more than 3.4% of listings, which means the field is genuinely open.
4. Focus premium pricing strategy on power tools and high-end hardware categories, where the price spread is widest and customers are demonstrably willing to pay above the median.

## Tools

Python 3.12, Pandas, Matplotlib, Seaborn

## Files

- `analysis.py` - Full analysis script
- `report.html` - Interactive report with 6 embedded charts
- `marketing_sample_for_amazon_com-...ldjson` - Source dataset
- `visuals/` - 6 chart PNGs
