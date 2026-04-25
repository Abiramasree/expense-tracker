import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")

FILE = "expenses.csv"

# ---------- Create file ----------
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
    df.to_csv(FILE, index=False)

# ---------- Load data ----------
df = pd.read_csv(FILE)
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

# ---------- Title ----------
st.markdown("<h1 style='text-align:center;color:#4CAF50;'>💸 Expense Tracker Dashboard</h1>", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.header("🔍 Filters")

if not df.empty:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
else:
    min_date = max_date = pd.to_datetime("today")

date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

categories = ["All"] + list(df["Category"].unique()) if not df.empty else ["All"]
selected_category = st.sidebar.selectbox("Category", categories)

search = st.sidebar.text_input("Search Description")

# ---------- Filter Data ----------
filtered_df = df.copy()

if not df.empty:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]

    if search:
        filtered_df = filtered_df[filtered_df["Description"].str.contains(search, case=False)]

# ---------- Layout ----------
col1, col2 = st.columns([2, 1])

# ---------- Add Expense ----------
with col1:
    st.subheader("➕ Add Expense")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        date = st.date_input("Date")
    with c2:
        amount = st.number_input("Amount", min_value=0.0)
    with c3:
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
    with c4:
        description = st.text_input("Description")

    if st.button("Add"):
        new_data = pd.DataFrame([[date, amount, category, description]],
                                columns=["Date", "Amount", "Category", "Description"])
        new_data.to_csv(FILE, mode='a', header=False, index=False)
        st.success("Added! Refreshing...")
        st.rerun()

# ---------- Metrics ----------
with col2:
    st.subheader("📊 Summary")

    if not filtered_df.empty:
        total = filtered_df["Amount"].sum()
        avg = filtered_df["Amount"].mean()
        max_val = filtered_df["Amount"].max()

        st.metric("Total", f"₹{total:.2f}")
        st.metric("Average", f"₹{avg:.2f}")
        st.metric("Max", f"₹{max_val:.2f}")
    else:
        st.info("No data")

# ---------- Data Table ----------
st.subheader("📋 Expenses")

if not filtered_df.empty:
    st.dataframe(filtered_df, use_container_width=True)

    # Delete option
    delete_index = st.number_input("Enter row index to delete", min_value=0, step=1)
    if st.button("Delete Row"):
        df = df.drop(delete_index)
        df.to_csv(FILE, index=False)
        st.warning("Deleted! Refreshing...")
        st.rerun()
else:
    st.warning("No data available")

# ---------- Charts ----------
if not filtered_df.empty:
    st.subheader("📊 Visual Insights")

    col1, col2 = st.columns(2)

    # Pie chart
    with col1:
        cat_data = filtered_df.groupby("Category")["Amount"].sum()
        fig1, ax1 = plt.subplots()
        ax1.pie(cat_data, labels=cat_data.index, autopct='%1.1f%%')
        ax1.set_title("Category Distribution")
        st.pyplot(fig1)

    # Bar chart
    with col2:
        fig2, ax2 = plt.subplots()
        cat_data.plot(kind="bar", ax=ax2)
        ax2.set_title("Category Comparison")
        st.pyplot(fig2)

    # Monthly trend
    st.subheader("📅 Monthly Trend")
    filtered_df["Month"] = filtered_df["Date"].dt.to_period("M")
    monthly = filtered_df.groupby("Month")["Amount"].sum()

    fig3, ax3 = plt.subplots()
    monthly.plot(ax=ax3)
    ax3.set_title("Monthly Spending")
    st.pyplot(fig3)

# ---------- Download ----------
st.subheader("📥 Download Data")
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "expenses.csv", "text/csv")