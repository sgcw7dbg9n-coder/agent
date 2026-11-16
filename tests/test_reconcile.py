import numpy as np
import pandas as pd

from recon.reconcile import reconcile

KEY = "id"
COMPARE = ["qty", "price"]


def _df(rows):
    return pd.DataFrame(rows)


def test_identical_sources_reconcile_cleanly():
    left = _df([{"id": "A", "qty": 1, "price": 10.0},
                {"id": "B", "qty": 2, "price": 20.0}])
    result = reconcile(left, left.copy(), key=KEY, compare_cols=COMPARE)
    assert result["missing_in_left"] == []
    assert result["missing_in_right"] == []
    assert result["duplicates"] == []
    assert result["field_mismatches"] == []


def test_missing_records_detected_both_directions():
    left = _df([{"id": "A", "qty": 1, "price": 10.0},
                {"id": "B", "qty": 2, "price": 20.0}])
    right = _df([{"id": "A", "qty": 1, "price": 10.0},
                 {"id": "C", "qty": 3, "price": 30.0}])
    result = reconcile(left, right, key=KEY, compare_cols=COMPARE)
    assert result["missing_in_right"] == ["B"]
    assert result["missing_in_left"] == ["C"]


def test_duplicate_detected():
    left = _df([{"id": "A", "qty": 1, "price": 10.0}])
    right = _df([{"id": "A", "qty": 1, "price": 10.0},
                 {"id": "A", "qty": 1, "price": 10.0}])
    result = reconcile(left, right, key=KEY, compare_cols=COMPARE)
    assert result["duplicates"] == [{"id": "A", "source": "right"}]


def test_field_mismatch_detected():
    left = _df([{"id": "A", "qty": 5, "price": 10.0}])
    right = _df([{"id": "A", "qty": 4, "price": 10.0}])
    result = reconcile(left, right, key=KEY, compare_cols=COMPARE)
    assert result["field_mismatches"] == [
        {"id": "A", "field": "qty", "left_value": 5, "right_value": 4}
    ]


def test_float_tolerance_ignores_tiny_difference():
    left = _df([{"id": "A", "qty": 1, "price": 10.00}])
    right = _df([{"id": "A", "qty": 1, "price": 10.001}])
    result = reconcile(left, right, key=KEY, compare_cols=COMPARE)
    assert result["field_mismatches"] == []


def test_both_missing_values_not_flagged():
    left = _df([{"id": "A", "qty": 1, "price": np.nan}])
    right = _df([{"id": "A", "qty": 1, "price": np.nan}])
    result = reconcile(left, right, key=KEY, compare_cols=COMPARE)
    assert result["field_mismatches"] == []


def test_one_missing_value_flagged():
    left = _df([{"id": "A", "qty": 1, "price": 10.0}])
    right = _df([{"id": "A", "qty": 1, "price": np.nan}])
    result = reconcile(left, right, key=KEY, compare_cols=COMPARE)
    assert len(result["field_mismatches"]) == 1
    assert result["field_mismatches"][0]["right_value"] is None