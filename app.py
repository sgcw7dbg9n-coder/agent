import pandas as pd
import streamlit as st

from recon.reconcile import reconcile
from recon.report import narrate

st.set_page_config(page_title="Reconciliation Agent", layout="wide")
st.title("Reconciliation Agent")
st.caption("Compare two datasets, find the discrepancies, and get an explained report.")

col1, col2 = st.columns(2)
with col1:
    sales_upload = st.file_uploader("Sales export (CSV)", type="csv")
with col2:
    warehouse_upload = st.file_uploader("Warehouse export (CSV)", type="csv")

if st.button("Reconcile", type="primary"):
    if sales_upload and warehouse_upload:
        sales = pd.read_csv(sales_upload)
        warehouse = pd.read_csv(warehouse_upload)
    else:
        st.info("No files uploaded, using the built-in sample data.")
        sales = pd.read_csv("data/sales_system.csv")
        warehouse = pd.read_csv("data/warehouse.csv")

    findings = reconcile(sales, warehouse)

    c1, c2, c3 = st.columns(3)
    c1.metric("Missing records", len(findings["missing_in_warehouse"]) + len(findings["missing_in_sales"]))
    c2.metric("Duplicates", len(findings["duplicates"]))
    c3.metric("Field mismatches", len(findings["field_mismatches"]))

    with st.expander("Raw findings"):
        st.json(findings)

    with st.spinner("Generating report..."):
        report = narrate(findings)

    st.markdown(report)