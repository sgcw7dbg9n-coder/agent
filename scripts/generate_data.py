"""Generate two retail datasets with known discrepancies for reconciliation testing.

Planted differences (sales_system vs warehouse):
  T003  in sales, missing from warehouse   (unrecorded sale)
  T011  in warehouse, missing from sales    (phantom record)
  T005  quantity differs, 20 vs 18          (quantity mismatch)
  T007  total differs via unit_price change (amount mismatch)
  T009  duplicated in warehouse             (duplicate)
Everything else matches exactly.
"""
import os
import pandas as pd

sales = [
    {"transaction_id": "T001", "date": "2026-11-01", "product": "Widget A", "quantity": 10, "unit_price": 25.00},
    {"transaction_id": "T002", "date": "2026-11-01", "product": "Widget B", "quantity": 5,  "unit_price": 40.00},
    {"transaction_id": "T003", "date": "2026-11-02", "product": "Widget C", "quantity": 8,  "unit_price": 15.00},
    {"transaction_id": "T004", "date": "2026-11-02", "product": "Widget D", "quantity": 2,  "unit_price": 120.00},
    {"transaction_id": "T005", "date": "2026-11-03", "product": "Widget E", "quantity": 20, "unit_price": 5.00},
    {"transaction_id": "T006", "date": "2026-11-03", "product": "Widget F", "quantity": 1,  "unit_price": 300.00},
    {"transaction_id": "T007", "date": "2026-11-04", "product": "Widget G", "quantity": 12, "unit_price": 18.00},
    {"transaction_id": "T008", "date": "2026-11-04", "product": "Widget H", "quantity": 7,  "unit_price": 22.00},
    {"transaction_id": "T009", "date": "2026-11-05", "product": "Widget I", "quantity": 3,  "unit_price": 55.00},
    {"transaction_id": "T010", "date": "2026-11-05", "product": "Widget J", "quantity": 15, "unit_price": 9.00},
]

warehouse = [dict(row) for row in sales if row["transaction_id"] != "T003"]

for row in warehouse:
    if row["transaction_id"] == "T005":
        row["quantity"] = 18
    if row["transaction_id"] == "T007":
        row["unit_price"] = 20.00

warehouse.append({"transaction_id": "T011", "date": "2026-11-06", "product": "Widget K", "quantity": 4, "unit_price": 30.00})
warehouse.append(dict(next(r for r in warehouse if r["transaction_id"] == "T009")))


def finalize(rows):
    df = pd.DataFrame(rows)
    df["total"] = (df["quantity"] * df["unit_price"]).round(2)
    return df


os.makedirs("data", exist_ok=True)
finalize(sales).to_csv("data/sales_system.csv", index=False)
finalize(warehouse).to_csv("data/warehouse.csv", index=False)

print("Wrote data/sales_system.csv and data/warehouse.csv")
print(f"sales rows: {len(sales)}  warehouse rows: {len(warehouse)}")