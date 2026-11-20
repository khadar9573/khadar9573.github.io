"""Builds the small data files used by dashboard.html from the project outputs.
Run:  python prepare_dashboard_data.py online_retail_cleaned.csv rfm_customers.csv cars_cleaned.csv
(the first two files are created by online_retail_analysis.ipynb, the third by used_car_price_analysis.ipynb)"""
import sys, shutil, pandas as pd
cleaned, rfm_file, cars_file = sys.argv[1:4]
d = pd.read_csv(cleaned, parse_dates=["InvoiceDate"])
seg = pd.read_csv(rfm_file).set_index("CustomerID")["Segment"]
d["ym"] = d["InvoiceDate"].dt.strftime("%Y-%m")
d["cust"] = d["CustomerID"].map(lambda x: "" if pd.isna(x) else str(int(x)))
d["segment"] = d["CustomerID"].map(seg).fillna("No customer ID")
cube = (d.groupby(["ym", "Country", "cust", "segment"])
          .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique")).reset_index().round(2))
cube.rename(columns={"Country": "country"}).to_csv("retail_customer_month.csv", index=False)
prod = d.groupby(["ym", "StockCode"])["Revenue"].sum().round(2).reset_index()
prod.columns = ["ym", "stockcode", "revenue"]; prod.to_csv("retail_product_month.csv", index=False)
names = d.groupby("StockCode")["Description"].agg(lambda s: s.mode()[0]).reset_index()
names.columns = ["stockcode", "description"]; names.to_csv("retail_products.csv", index=False)
import os
if os.path.abspath(cars_file) != os.path.abspath("cars_cleaned.csv"): shutil.copy(cars_file, "cars_cleaned.csv")
# checks: every file must add up to the same totals as the cleaned data
total = round(d["Revenue"].sum(), 2)
assert abs(cube["revenue"].sum() - total) < 1 and abs(prod["revenue"].sum() - total) < 1
assert cube["orders"].sum() == d["InvoiceNo"].nunique()
print("OK. Total revenue", total, "| orders", cube["orders"].sum(), "| rows in cube", len(cube))
