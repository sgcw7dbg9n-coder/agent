import pandas as pd

KEY = "transaction_id"
COMPARE_COLS = ["quantity", "unit_price", "total"]


def load(path):
    return pd.read_csv(path)


def _native(value):
    return value.item() if hasattr(value, "item") else value


def find_duplicates(df, source):
    dup_ids = df[KEY][df[KEY].duplicated(keep=False)].unique().tolist()
    return [{"transaction_id": tid, "source": source} for tid in dup_ids]


def reconcile(sales, warehouse):
    sales_ids = set(sales[KEY])
    warehouse_ids = set(warehouse[KEY])

    missing_in_warehouse = sorted(sales_ids - warehouse_ids)
    missing_in_sales = sorted(warehouse_ids - sales_ids)
    duplicates = find_duplicates(sales, "sales") + find_duplicates(warehouse, "warehouse")

    s = sales.drop_duplicates(subset=KEY).set_index(KEY)
    w = warehouse.drop_duplicates(subset=KEY).set_index(KEY)
    shared = sorted(sales_ids & warehouse_ids)

    mismatches = []
    for tid in shared:
        for col in COMPARE_COLS:
            sv, wv = s.at[tid, col], w.at[tid, col]
            if sv != wv:
                mismatches.append({
                    "transaction_id": tid,
                    "field": col,
                    "sales_value": _native(sv),
                    "warehouse_value": _native(wv),
                })

    return {
        "missing_in_warehouse": missing_in_warehouse,
        "missing_in_sales": missing_in_sales,
        "duplicates": duplicates,
        "field_mismatches": mismatches,
    }


if __name__ == "__main__":
    sales = load("data/sales_system.csv")
    warehouse = load("data/warehouse.csv")
    result = reconcile(sales, warehouse)

    print("Missing in warehouse:", result["missing_in_warehouse"])
    print("Missing in sales:", result["missing_in_sales"])
    print("Duplicates:", result["duplicates"])
    print("Field mismatches:")
    for m in result["field_mismatches"]:
        print(f"  {m['transaction_id']} {m['field']}: sales={m['sales_value']} warehouse={m['warehouse_value']}")