
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Fashion Sales Dashboard",
    page_icon="👗",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}
h1 {
    color: #172554;
}
h2, h3 {
    color: #1e293b;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DASHBOARD TITLE
# ==========================================

st.title("👗 FASHION SALES ANALYTICS")
st.markdown(
    "### Business Intelligence Dashboard | Sales Performance"
)

st.markdown("---")

# ==========================================
# GENERATE SAMPLE DATA
# ==========================================

@st.cache_data
def create_data():

    np.random.seed(42)

    years = [2022, 2023, 2024, 2025, 2026]
    months = list(range(1, 13))

    products = ["Jeans", "T-Shirt", "Shorts", "Skirts"]
    genders = ["Male", "Female"]

    price_dict = {
        "Jeans": 1500,
        "T-Shirt": 700,
        "Shorts": 900,
        "Skirts": 1100
    }

    data = []

    for year in years:
        for month in months:
            for gender in genders:
                for product in products:

                    quantity = np.random.randint(30, 150)

                    price = price_dict[product]

                    revenue = quantity * price

                    cost = revenue * np.random.uniform(0.5, 0.75)

                    profit = revenue - cost

                    inventory = np.random.randint(20, 300)

                    data.append({
                        "Year": year,
                        "Month": month,
                        "Gender": gender,
                        "Product": product,
                        "Quantity": quantity,
                        "Price": price,
                        "Revenue": revenue,
                        "Cost": cost,
                        "Profit": profit,
                        "Inventory": inventory
                    })

    df = pd.DataFrame(data)

    df["Month Name"] = pd.to_datetime(
        df["Month"], format="%m"
    ).dt.month_name()

    return df


df = create_data()

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.title("⚙️ Dashboard Filters")

st.sidebar.markdown("Customize your analysis")

year_filter = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df["Year"].unique()),
    default=[2026]
)

gender_filter = st.sidebar.multiselect(
    "Select Gender",
    options=["Male", "Female"],
    default=["Male", "Female"]
)

product_filter = st.sidebar.multiselect(
    "Select Product",
    options=["Jeans", "T-Shirt", "Shorts", "Skirts"],
    default=["Jeans", "T-Shirt", "Shorts", "Skirts"]
)

month_filter = st.sidebar.multiselect(
    "Select Month",
    options=df["Month Name"].unique(),
    default=df["Month Name"].unique().tolist()
)

# ==========================================
# FILTER DATA
# ==========================================

filtered_df = df[
    (df["Year"].isin(year_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["Product"].isin(product_filter)) &
    (df["Month Name"].isin(month_filter))
]

if filtered_df.empty:
    st.warning("No data found. Please change the filters.")
    st.stop()

# ==========================================
# KPI CALCULATIONS
# ==========================================

total_revenue = filtered_df["Revenue"].sum()
total_sales = filtered_df["Quantity"].sum()
total_profit = filtered_df["Profit"].sum()

# Inventory represents a stock snapshot in this demo.
# Use the latest month for each year rather than summing
# repeated stock observations.
stock = (
    filtered_df.sort_values(["Year", "Month"])
    .groupby(["Year", "Gender", "Product"])
    .tail(1)
)

total_inventory = stock["Inventory"].sum()

profit_margin = (
    total_profit / total_revenue * 100
    if total_revenue > 0 else 0
)

# ==========================================
# KPI CARDS
# ==========================================

st.subheader("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "Total Sales",
    f"{total_sales:,} Units"
)

col3.metric(
    "Total Profit",
    f"₹{total_profit:,.0f}"
)

col4.metric(
    "Total Inventory",
    f"{total_inventory:,} Units"
)

st.caption(f"Overall Profit Margin: {profit_margin:.2f}%")

st.markdown("---")

# ==========================================
# YEARLY REVENUE
# ==========================================

st.subheader("📈 Yearly Revenue Analysis")

yearly_data = (
    filtered_df.groupby("Year", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    )
)

fig1 = px.bar(
    yearly_data,
    x="Year",
    y="Revenue",
    color="Revenue",
    text_auto=".2s",
    title="Yearly Revenue",
    color_continuous_scale="Blues",
    template="plotly_white"
)

fig1.update_layout(
    xaxis_title="Year",
    yaxis_title="Revenue (₹)"
)

st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# MONTHLY SALES TREND
# ==========================================

st.subheader("📅 Monthly Sales Performance")

month_order = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

monthly_data = (
    filtered_df.groupby("Month Name", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Sales=("Quantity", "sum")
    )
)

monthly_data["Month Name"] = pd.Categorical(
    monthly_data["Month Name"],
    categories=month_order,
    ordered=True
)

monthly_data = monthly_data.sort_values("Month Name")

fig2 = px.line(
    monthly_data,
    x="Month Name",
    y=["Revenue", "Profit"],
    markers=True,
    title="Monthly Revenue vs Profit",
    template="plotly_white"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="Month",
    yaxis_title="Amount (₹)"
)

st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# GENDER ANALYSIS
# ==========================================

st.markdown("---")
st.subheader("👨‍👩‍👧 Gender-wise Analysis")

col1, col2 = st.columns(2)

with col1:

    gender_data = (
        filtered_df.groupby("Gender", as_index=False)
        .agg(Revenue=("Revenue", "sum"))
    )

    fig3 = px.pie(
        gender_data,
        names="Gender",
        values="Revenue",
        hole=0.5,
        title="Revenue by Gender",
        color="Gender",
        color_discrete_map={
            "Male": "#3498db",
            "Female": "#e84393"
        }
    )

    st.plotly_chart(fig3, use_container_width=True)

with col2:

    gender_sales = (
        filtered_df.groupby("Gender", as_index=False)
        .agg(Sales=("Quantity", "sum"))
    )

    fig4 = px.bar(
        gender_sales,
        x="Gender",
        y="Sales",
        color="Gender",
        title="Units Sold by Gender",
        text_auto=True,
        color_discrete_map={
            "Male": "#3498db",
            "Female": "#e84393"
        }
    )

    st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# PRODUCT ANALYSIS
# ==========================================

st.markdown("---")
st.subheader("👕 Product Category Analysis")

col1, col2 = st.columns(2)

with col1:

    product_revenue = (
        filtered_df.groupby("Product", as_index=False)
        .agg(Revenue=("Revenue", "sum"))
    )

    fig5 = px.bar(
        product_revenue,
        x="Product",
        y="Revenue",
        color="Product",
        text_auto=".2s",
        title="Revenue by Product",
        template="plotly_white"
    )

    st.plotly_chart(fig5, use_container_width=True)

with col2:

    product_sales = (
        filtered_df.groupby("Product", as_index=False)
        .agg(Sales=("Quantity", "sum"))
    )

    fig6 = px.pie(
        product_sales,
        names="Product",
        values="Sales",
        hole=0.4,
        title="Product Sales Distribution"
    )

    st.plotly_chart(fig6, use_container_width=True)

# ==========================================
# PROFIT ANALYSIS
# ==========================================

st.markdown("---")
st.subheader("💰 Profit Analysis")

profit_data = (
    filtered_df.groupby(
        ["Product", "Gender"], as_index=False
    ).agg(Profit=("Profit", "sum"))
)

fig7 = px.bar(
    profit_data,
    x="Product",
    y="Profit",
    color="Gender",
    barmode="group",
    title="Product-wise Profit Comparison",
    color_discrete_map={
        "Male": "#3498db",
        "Female": "#e84393"
    },
    template="plotly_white"
)

st.plotly_chart(fig7, use_container_width=True)

# ==========================================
# INVENTORY ANALYSIS
# ==========================================

st.markdown("---")
st.subheader("📦 Inventory Management")

inventory_data = (
    stock.groupby("Product", as_index=False)
    .agg(Inventory=("Inventory", "sum"))
)

fig8 = px.bar(
    inventory_data,
    x="Product",
    y="Inventory",
    color="Inventory",
    text_auto=True,
    title="Available Inventory by Product",
    color_continuous_scale="Teal",
    template="plotly_white"
)

st.plotly_chart(fig8, use_container_width=True)

# LOW STOCK ALERT

st.subheader("⚠️ Low Stock Products")

low_stock = inventory_data[
    inventory_data["Inventory"] < 300
]

if not low_stock.empty:
    st.warning("Some product categories have low inventory.")

    st.dataframe(
        low_stock,
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("No low-stock product categories detected.")

# ==========================================
# DETAILED DATA TABLE
# ==========================================

st.markdown("---")
st.subheader("📋 Detailed Sales Report")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# DOWNLOAD REPORT
# ==========================================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Sales Report",
    data=csv,
    file_name="fashion_sales_report.csv",
    mime="text/csv"
)

st.markdown("---")

st.markdown(
    "<center>Fashion Sales Dashboard | Built with Python, "
    "Streamlit and Plotly</center>",
    unsafe_allow_html=True
)
