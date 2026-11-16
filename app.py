import os

import pandas as pd
import streamlit as st

from recon.reconcile import reconcile
from recon.report import narrate

try:
    for key, value in st.secrets.items():
        os.environ.setdefault(key, str(value))
except Exception:
    pass

st.set_page_config(page_title="Reconciliation Agent", layout="wide")
st.title("Reconciliation Agent")
st.caption("Compare two datasets, find the discrepancies, and get an explained report.")

col1, col2 = st.columns(2)
with col1:
    left_upload = st.file_uploader("First export (CSV)", type="csv")
with col2:
    right_upload = st.file_uploader("Second export (CSV)", type="csv")

if left_upload and right_upload:
    left = pd.read_csv(left_upload)
    right = pd.read_csv(right_upload)
else:
    st.info("No files uploaded, using the built-in sample data.")
    left = pd.read_csv("data/sales_system.csv")
    right = pd.read_csv("data/warehouse.csv")

common_cols = [c for c in left.columns if c in right.columns]

if not common_cols:
    st.error("The two files share no columns, so they can't be reconciled. Check that both have the same headers.")
    st.stop()

key_default = next((i for i, c in enumerate(common_cols) if "id" in c.lower()), 0)
key = st.selectbox("Key column (identifies the same record in both files)", common_cols, index=key_default)

compare_options = [c for c in common_cols if c != key]
compare_cols = st.multiselect("Columns to compare", compare_options, default=compare_options)

if st.button("Reconcile", type="primary"):
    if not compare_cols:
        st.warning("Pick at least one column to compare.")
        st.stop()

    findings = reconcile(left, right, key, compare_cols)

    c1, c2, c3 = st.columns(3)
    c1.metric("Missing records", len(findings["missing_in_left"]) + len(findings["missing_in_right"]))
    c2.metric("Duplicates", len(findings["duplicates"]))
    c3.metric("Field mismatches", len(findings["field_mismatches"]))

    with st.expander("Raw findings"):
        st.json(findings)

    with st.spinner("Generating report..."):
        report = narrate(findings)

    st.markdown(report)