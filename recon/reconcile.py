import numbers

import pandas as pd

DEFAULT_KEY = "transaction_id"
DEFAULT_COMPARE = ["quantity", "unit_price", "total"]
DEFAULT_TOLERANCE = 0.01


def load(path):
    return pd.read_csv(path)


def _native(value):
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def _cells_differ(a, b, tol):
    a_missing, b_missing = pd.isna(a), pd.isna(b)
    if a_missing and b_missing:
        return False
    if a_missing or b_missing:
        return True
    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        return abs(a - b) > tol
    return a != b


def find_duplicates(df, key, source):
    dup_ids = df[key][df[key].duplicated(keep=False)].unique().tolist()
    return [{key: _native(tid), "source": source} for tid in dup_ids]


def reconcile(left, right, key=DEFAULT_KEY, compare_cols=None, tol=DEFAULT_TOLERANCE):
    if compare_cols is None:
        compare_cols = DEFAULT_COMPARE

    left_ids = set(left[key])
    right_ids = set(right[key])

    missing_in_right = [_native(x) for x in sorted(left_ids - right_ids)]
    missing_in_left = [_native(x) for x in sorted(right_ids - left_ids)]
    duplicates = find_duplicates(left, key, "left") + find_duplicates(right, key, "right")

    l = left.drop_duplicates(subset=key).set_index(key)
    r = right.drop_duplicates(subset=key).set_index(key)
    shared = sorted(left_ids & right_ids)

    mismatches = []
    for tid in shared:
        for col in compare_cols:
            lv, rv = l.at[tid, col], r.at[tid, col]
            if _cells_differ(lv, rv, tol):
                mismatches.append({
                    key: _native(tid),
                    "field": col,
                    "left_value": _native(lv),
                    "right_value": _native(rv),
                })

    return {
        "missing_in_right": missing_in_right,
        "missing_in_left": missing_in_left,
        "duplicates": duplicates,
        "field_mismatches": mismatches,
    }