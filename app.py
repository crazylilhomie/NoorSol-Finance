import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# CONFIG & CONSTANTS
# ============================================================
st.set_page_config(
    page_title="NOORSOL Dubai Financial Dashboard",
    layout="wide"
)

# ---- Fixed market assumptions (DO NOT EDIT IN UI) ----
TOTAL_BIKES_DUBAI = 40_000          # Based on RTA / survey style guesstimate
BAGS_PER_BIKE_PER_YEAR = 1.5        # Wear & tear in Dubai heat
ANNUAL_BAG_DEMAND = TOTAL_BIKES_DUBAI * BAGS_PER_BIKE_PER_YEAR  # 60,000 bags

# ---- Fixed product economics ----
# B2B: NOORSOL retrofit (upcycling existing boxes)
B2B_PRICE_PILOT = 399
B2B_PRICE_LAUNCH = 450
B2B_COGS = 200

# B2C: NOORSOL MOVE (Beach-Lite)
B2C_PRICE_PILOT = 499
B2C_PRICE_LAUNCH = 599
B2C_COGS = 305

# ---- Fixed cost structure (annual) ----
FIXED_SALARIES = 360_000
FIXED_MARKETING = 90_000
FIXED_RND = 40_000
FIXED_OPS = 120_000
FIXED_OTHER = 30_000
TOTAL_FIXED_COSTS = (
    FIXED_SALARIES
    + FIXED_MARKETING
    + FIXED_RND
    + FIXED_OPS
    + FIXED_OTHER
)

# ---- Default volumes (these are model assumptions, not sliders) ----
PILOT_B2B_UNITS = 400
PILOT_B2C_UNITS = 200

Y1_B2C_PESS = 600
Y1_B2C_BASE = 900
Y1_B2C_OPT = 1200


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def compute_scenario(name: str,
                     adoption_rate_b2b: float,
                     b2c_units: int) -> dict:
    """
    Compute Year 1 financials for a given scenario.
    Adoption_rate_b2b is % of annual bag demand captured as NOORSOL retrofits.
    Uses LAUNCH pricing.
    """
    b2b_units = ANNUAL_BAG_DEMAND * adoption_rate_b2b

    b2b_price = B2B_PRICE_LAUNCH
    b2c_price = B2C_PRICE_LAUNCH

    # Revenue
    b2b_revenue = b2b_units * b2b_price
    b2c_revenue = b2c_units * b2c_price
    total_revenue = b2b_revenue + b2c_revenue

    # COGS
    b2b_cogs_total = b2b_units * B2B_COGS
    b2c_cogs_total = b2c_units * B2C_COGS
    total_cogs = b2b_cogs_total + b2c_cogs_total

    # Gross profit
    gross_profit = total_revenue - total_cogs
    gross_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

    # EBIT
    ebit = gross_profit - TOTAL_FIXED_COSTS
    ebit_margin_pct = (ebit / total_revenue * 100) if total_revenue > 0 else 0

    # Contribution per unit (blended)
    total_units = b2b_units + b2c_units
    contribution_per_unit = (gross_profit / total_units) if total_units > 0 else 0

    return {
        "Scenario": name,
        "Adoption (B2B % of bags)": adoption_rate_b2b,
        "B2B units": b2b_units,
        "B2C units": b2c_units,
        "Total units": total_units,
        "B2B revenue (AED)": b2b_revenue,
        "B2C revenue (AED)": b2c_revenue,
        "Total revenue (AED)": total_revenue,
        "Total COGS (AED)": total_cogs,
        "Gross profit (AED)": gross_profit,
        "Gross margin (%)": gross_margin_pct,
        "Fixed costs (AED)": TOTAL_FIXED_COSTS,
        "EBIT (AED)": ebit,
        "EBIT margin (%)": ebit_margin_pct,
        "Contribution / unit (AED)": contribution_per_unit,
        "B2B COGS total (AED)": b2b_cogs_total,
        "B2C COGS total (AED)": b2c_cogs_total,
    }


def breakeven_units(contribution_per_unit: float) -> float:
    if contribution_per_unit <= 0:
        return float("inf")
    return TOTAL_FIXED_COSTS / contribution_per_unit


# ============================================================
# PAGE HEADER & SIDEBAR
# ============================================================
st.markdown(
    """
    <style>
    .big-title {
        font-size: 32px;
        font-weight: 700;
        color: #1A5276;
    }
    .subtle-card {
        background-color: #f8fbff;
        padding: 1rem 1.2rem;
        border-radius: 0.8rem;
        border: 1px solid #e1e8f5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">📦 NOORSOL – Dubai Financial Dashboard</div>', unsafe_allow_html=True)
st.caption("Solar-powered smart delivery & outdoor boxes • Focus: Dubai only • All values in AED")

# Sidebar: ONLY adoption settings
st.sidebar.header("🎯 Market Capture Assumptions")

st.sidebar.write(
    "All prices, COGS, riders, and bag demand are **fixed** based on our "
    "research & guesstimates for Dubai. The **only thing you can play with** "
    "is how much of the delivery-bag market NOORSOL captures."
)

adoption_pess = st.sidebar.slider(
    "Pessimistic B2B adoption (% of annual bag demand)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01
)

adoption_base = st.sidebar.slider(
    "Base B2B adoption (% of annual bag demand)",
    min_value=0.05,
    max_value=0.40,
    value=0.10,
    step=0.01
)

adoption_opt = st.sidebar.slider(
    "Optimistic B2B adoption (% of annual bag demand)",
    min_value=0.10,
    max_value=0.80,
    value=0.20,
    step=0.01
)

# ============================================================
# TABS
# ============================================================
tab_overview, tab_pnl, tab_breakeven, tab_sensitivity = st.tabs(
    ["🏁 Overview", "📊 P&L & Visuals", "⚖️ Breakeven", "📈 Sensitivity"]
)

# ============================================================
# OVERVIEW TAB
# ============================================================
with tab_overview:
    st.subheader("Dubai Delivery Ecosystem & NOORSOL Assumptions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### 🚚 Delivery Ecosystem (Dubai – Fixed Assumptions)")
        st.markdown(
            f"""
            - Estimated active delivery bikes: **{TOTAL_BIKES_DUBAI:,}**
            - Average bags used per bike per year: **{BAGS_PER_BIKE_PER_YEAR:.1f}**
            - Implied annual bag demand: **{int(ANNUAL_BAG_DEMAND):,} bags**
            
            These numbers come from:
            - Registered delivery motorcycles & RTA info
            - Guesstimated bag wear rate in Dubai heat  
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### 💰 Fixed Product Economics (Non-Adjustable)")
        st.markdown(
            f"""
            **B2B – NOORSOL Retrofit (Delivery Platforms)**  
            - Launch price: **{B2B_PRICE_LAUNCH} AED / unit**  
            - COGS (retrofit upcycling): **{B2B_COGS} AED / unit**

            **B2C – NOORSOL MOVE (Beach-Lite)**  
            - Launch price: **{B2C_PRICE_LAUNCH} AED / unit**  
            - COGS: **{B2C_COGS} AED / unit**
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🧾 Fixed Cost Structure (Year 1)")

    col_fc1, col_fc2, col_fc3, col_fc4, col_fc5 = st.columns(5)
    col_fc1.metric("Salaries", f"{FIXED_SALARIES:,.0f}")
    col_fc2.metric("Marketing", f"{FIXED_MARKETING:,.0f}")
    col_fc3.metric("R&D", f"{FIXED_RND:,.0f}")
    col_fc4.metric("Ops/Logistics", f"{FIXED_OPS:,.0f}")
    col_fc5.metric("Other", f"{FIXED_OTHER:,.0f}")

    st.metric("Total Fixed Costs (Annual)", f"{TOTAL_FIXED_COSTS:,.0f} AED")


# ============================================================
# P&L & VISUALS TAB
# ============================================================
with tab_pnl:
    st.subheader("Year 1 P&L – Pessimistic / Base / Optimistic")

    # Compute scenarios for Year 1
    scenarios = [
        compute_scenario("Pessimistic", adoption_pess, Y1_B2C_PESS),
        compute_scenario("Base",        adoption_base, Y1_B2C_BASE),
        compute_scenario("Optimistic",  adoption_opt, Y1_B2C_OPT),
    ]
    df_scen = pd.DataFrame(scenarios)

    # High-level metrics
    col_top1, col_top2, col_top3 = st.columns(3)
    col_top1.metric("Pessimistic Revenue", f"{df_scen.loc[0, 'Total revenue (AED)']:,.0f}")
    col_top2.metric("Base Revenue",        f"{df_scen.loc[1, 'Total revenue (AED)']:,.0f}")
    col_top3.metric("Optimistic Revenue",  f"{df_scen.loc[2, 'Total revenue (AED)']:,.0f}")

    st.markdown("#### 📋 Scenario Table")

    st.dataframe(
        df_scen[[
            "Scenario",
            "Adoption (B2B % of bags)",
            "B2B units",
            "B2C units",
            "Total revenue (AED)",
            "Gross profit (AED)",
            "EBIT (AED)",
            "EBIT margin (%)"
        ]].style.format({
            "Adoption (B2B % of bags)": "{:.0%}",
            "B2B units": "{:,.0f}",
            "B2C units": "{:,.0f}",
            "Total revenue (AED)": "{:,.0f}",
            "Gross profit (AED)": "{:,.0f}",
            "EBIT (AED)": "{:,.0f}",
            "EBIT margin (%)": "{:,.1f}",
        }),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### 📊 Visuals – Revenue & EBIT by Scenario")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_rev = px.bar(
            df_scen,
            x="Scenario",
            y="Total revenue (AED)",
            color="Scenario",
            color_discrete_sequence=["#ffb703", "#219ebc", "#8ecae6"],
            title="Total Revenue by Scenario",
            text_auto=".0f",
        )
        fig_rev.update_layout(yaxis_title="Revenue (AED)")
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_chart2:
        fig_ebit = px.bar(
            df_scen,
            x="Scenario",
            y="EBIT (AED)",
            color="Scenario",
            color_discrete_sequence=["#fb8500", "#2a9d8f", "#264653"],
            title="EBIT by Scenario",
            text_auto=".0f",
        )
        fig_ebit.update_layout(yaxis_title="EBIT (AED)")
        st.plotly_chart(fig_ebit, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🥧 Donut Charts – Revenue Split & Value Creation")

    # Select scenario for donuts
    donut_scenario = st.selectbox(
        "Choose scenario to inspect in detail",
        options=df_scen["Scenario"].tolist(),
        index=1
    )
    row = df_scen[df_scen["Scenario"] == donut_scenario].iloc[0]

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        # Revenue split donut (B2B vs B2C)
        rev_split_df = pd.DataFrame({
            "Segment": ["B2B NOORSOL (retrofit)", "B2C NOORSOL MOVE"],
            "Revenue": [row["B2B revenue (AED)"], row["B2C revenue (AED)"]],
        })
        fig_donut_rev = px.pie(
            rev_split_df,
            names="Segment",
            values="Revenue",
            hole=0.5,
            title=f"Revenue Mix – {donut_scenario} Scenario",
            color_discrete_sequence=["#023047", "#ffb703"]
        )
        st.plotly_chart(fig_donut_rev, use_container_width=True)

    with col_d2:
        # Value creation donut (COGS vs Gross Profit)
        value_df = pd.DataFrame({
            "Component": ["COGS", "Gross Profit"],
            "Value": [row["Total COGS (AED)"], row["Gross profit (AED)"]],
        })
        fig_donut_val = px.pie(
            value_df,
            names="Component",
            values="Value",
            hole=0.5,
            title=f"Value Capture – {donut_scenario} Scenario",
            color_discrete_sequence=["#e76f51", "#2a9d8f"]
        )
        st.plotly_chart(fig_donut_val, use_container_width=True)


# ============================================================
# BREAKEVEN TAB
# ============================================================
with tab_breakeven:
    st.subheader("⚖️ Breakeven Analysis (Year 1 – Launch Economics)")

    # Choose scenario for breakeven
    be_scenario = st.selectbox(
        "Scenario for breakeven calculation",
        options=df_scen["Scenario"].tolist(),
        index=1
    )
    be_row = df_scen[df_scen["Scenario"] == be_scenario].iloc[0]
    contrib_unit = be_row["Contribution / unit (AED)"]
    be_units_total = breakeven_units(contrib_unit)

    col_be1, col_be2, col_be3 = st.columns(3)
    col_be1.metric("Contribution / unit", f"{contrib_unit:,.0f} AED")
    col_be2.metric("Total fixed costs", f"{TOTAL_FIXED_COSTS:,.0f} AED")
    col_be3.metric(
        "Breakeven units (total)",
        "∞" if np.isinf(be_units_total) else f"{be_units_total:,.0f}"
    )

    st.markdown("---")

    if not np.isinf(be_units_total) and be_units_total > 0:
        st.markdown("### 📈 Cumulative Profit vs Units Sold")

        max_units = int(be_units_total * 1.5)
        units = np.linspace(0, max_units, 60)
        cum_profit = (units * contrib_unit) - TOTAL_FIXED_COSTS
        df_be = pd.DataFrame({
            "Total units sold": units,
            "Cumulative profit (AED)": cum_profit,
        })

        fig_be = px.line(
            df_be,
            x="Total units sold",
            y="Cumulative profit (AED)",
            title=f"Cumulative Profit Curve – {be_scenario} Scenario",
            color_discrete_sequence=["#219ebc"]
        )
        fig_be.add_hline(y=0, line_dash="dash", line_color="#888")
        st.plotly_chart(fig_be, use_container_width=True)

        st.info(
            f"Breakeven occurs where the curve crosses zero. In the **{be_scenario}** scenario, "
            f"NOORSOL needs to sell approximately **{be_units_total:,.0f} units** in Year 1 "
            "to cover fixed costs."
        )
    else:
        st.warning(
            "Contribution per unit is non-positive for this scenario, so breakeven cannot be reached with "
            "the current assumptions."
        )


# ============================================================
# SENSITIVITY TAB
# ============================================================
with tab_sensitivity:
    st.subheader("📈 Sensitivity – How Sensitive is NOORSOL to Adoption?")

    st.markdown(
        """
        Here we hold B2C units fixed and see how changing **B2B adoption** (as % of annual bag demand)
        impacts revenue, gross profit, and EBIT.
        """
    )

    b2c_units_for_sens = Y1_B2C_BASE  # keep base as reference

    adoption_grid = [0.15, 0.25, 0.40]
    sens_rows = [
        compute_scenario(f"{int(rate * 100)}%", rate, b2c_units_for_sens)
        for rate in adoption_grid
    ]
    df_sens = pd.DataFrame(sens_rows)

    st.markdown("### Sensitivity Table (B2B Adoption Levels)")
    st.dataframe(
        df_sens[[
            "Scenario",
            "Adoption (B2B % of bags)",
            "B2B units",
            "Total revenue (AED)",
            "Gross profit (AED)",
            "EBIT (AED)",
            "EBIT margin (%)"
        ]].style.format({
            "Adoption (B2B % of bags)": "{:.0%}",
            "B2B units": "{:,.0f}",
            "Total revenue (AED)": "{:,.0f}",
            "Gross profit (AED)": "{:,.0f}",
            "EBIT (AED)": "{:,.0f}",
            "EBIT margin (%)": "{:,.1f}",
        }),
        use_container_width=True
    )

    st.markdown("### 📉 Line Chart – Revenue, Gross Profit & EBIT vs Adoption")

    fig_sens = px.line(
        df_sens,
        x="Scenario",
        y=["Total revenue (AED)", "Gross profit (AED)", "EBIT (AED)"],
        markers=True,
        title="Impact of B2B Adoption (%) on Financial Outcomes",
        color_discrete_sequence=["#219ebc", "#2a9d8f", "#e76f51"]
    )
    fig_sens.update_layout(
        xaxis_title="B2B Adoption Scenario",
        yaxis_title="AED",
        legend_title="Metric"
    )
    st.plotly_chart(fig_sens, use_container_width=True)

    st.info(
        "Use this chart in your pitch to show that **even modest B2B adoption in Dubai** "
        "can generate significant revenue and EBIT once fixed costs are covered."
    )
