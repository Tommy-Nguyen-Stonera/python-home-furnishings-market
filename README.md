# Home Furnishings Market Analysis (Python)

[View Interactive Report](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Tommy-Nguyen-Stonera/python-home-furnishings-market/main/report.html)

Analysis of 5,000 Amazon home improvement product listings covering pricing, brands, ratings, discounts, and market concentration.

## Key Findings

- Pricing varies widely by category. The median price is INR 899. Most products sit under INR 2,000 but outliers stretch above INR 50,000. Power and hand tools show the widest spread.
- The market is fragmented across 2,000+ brands. The top brand (uxcell) holds just 3.4% of listings with 168 products. No single brand dominates.
- Products with 50%+ discounts average 35% more reviews (median 23 vs 17). Engagement plateaus past 60% off.
- Prime products rate slightly lower on average (4.06 vs 4.18 for non-Prime) and sell at much lower prices (INR 869 vs INR 2,488 average).
- The top 10 sellers control just 15.8% of listings across 2,000+ unique sellers. Concentration is low compared to physical retail.

## Tools

Python 3.12, Pandas, Matplotlib, Seaborn

## Files

- `analysis.py` - Full analysis script
- `report.html` - Interactive report with 6 embedded charts
- `marketing_sample_for_amazon_com-...ldjson` - Source dataset
- `visuals/` - 6 chart PNGs
