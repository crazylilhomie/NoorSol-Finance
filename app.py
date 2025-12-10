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
TOTAL_BIKES_DUBAI = 40_000          # From Dubai RTA / market guesstimates
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

# ---- Default volumes (model assumptions) ----
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


def compute_pilot() -> dict:
    """
    Compute a 'pilot year' style income statement using pilot pricing and fixed Year 1 costs
    (for comparability). Treated as Year 0.
    """
    b2b_units = PILOT_B2B_UNITS
    b2c_units = PILOT_B2C_UNITS

    b2b_price = B2B_PRICE_PILOT
    b2c_price = B2C_PRICE_PILOT

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

    # EBIT (use same fixed cost structure for comparison)
    ebit = gross_profit - TOTAL_FIXED_COSTS
    ebit_margin_pct = (ebit / total_revenue * 100) if total_revenue > 0 else 0

    total_units = b2b_units + b2c_units
    contribution_per_unit = (gross_profit / total_units) if total_units > 0 else 0

    return {
        "Scenario": "Pilot (Year 0)",
        "Adoption (B2B % of bags)": np.nan,
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
# PAGE STYLING (BLUE/WHITE FEEL)
# ============================================================
st.markdown(
    """
    <style>
    .big-title {
        font-size: 32px;
        font-weight: 800;
        color: #0b3c5d;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f4e79;
    }
    .subtle-card {
        background-color: #f5f9ff;
        padding: 1rem 1.2rem;
        border-radius: 0.8rem;
        border: 1px solid #d6e4ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">📦 NOORSOL – Dubai Financial Dashboard</div>', unsafe_allow_html=True)
st.caption("Solar-powered smart delivery & outdoor boxes • Focus: Dubai • All values in AED")

# ============================================================
# SIDEBAR – ONLY MARKET CAPTURE ADJUSTABLE
# ============================================================
st.sidebar.header("🎯 Market Capture Assumptions")

st.sidebar.write(
    "All prices, COGS, riders, and bag demand are **fixed**, based on Dubai-focused "
    "research and smart guesstimates. The **only adjustable input** is how much of the "
    "delivery-bag market NOORSOL captures in Year 1."
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
# PRE-COMPUTE YEAR 1 SCENARIOS (USED IN MULTIPLE TABS)
# ============================================================
scenarios = [
    compute_scenario("Pessimistic", adoption_pess, Y1_B2C_PESS),
    compute_scenario("Base",        adoption_base, Y1_B2C_BASE),
    compute_scenario("Optimistic",  adoption_opt, Y1_B2C_OPT),
]
df_scen = pd.DataFrame(scenarios)

# ============================================================
# TABS (OVERVIEW, P&L, BREAKEVEN)
# ============================================================
tab_overview, tab_pnl, tab_breakeven = st.tabs(
    ["🏁 Overview", "📊 P&L & Visuals", "⚖️ Breakeven"]
)

# ============================================================
# OVERVIEW TAB
# ============================================================
with tab_overview:
    st.markdown('<div class="section-title">Dubai Delivery Ecosystem & NOORSOL Snapshot</div>', unsafe_allow_html=True)

    top_col1, top_col2, top_col3 = st.columns(3)
    with top_col1:
        st.metric("Active delivery bikes (Dubai)", f"{TOTAL_BIKES_DUBAI:,.0f}")
    with top_col2:
        st.metric("Bags per bike per year", f"{BAGS_PER_BIKE_PER_YEAR:.1f}")
    with top_col3:
        st.metric("Annual bag demand (est.)", f"{ANNUAL_BAG_DEMAND:,.0f}")

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### 🚚 Delivery Ecosystem (Fixed Assumptions)")
        st.markdown(
            f"""
            - **{TOTAL_BIKES_DUBAI:,}** active delivery bikes in Dubai  
            - Each bike uses **~{BAGS_PER_BIKE_PER_YEAR:.1f}** thermal bags per year  
            - Implied annual bag replacement: **{int(ANNUAL_BAG_DEMAND):,} bags**  

            These numbers reflect:
            - Registered delivery motorcycles in Dubai  
            - Wear-and-tear due to heat and heavy daily usage  
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### 💰 Product Economics (Fixed)")
        st.markdown(
            f"""
            **B2B – NOORSOL Retrofit (Delivery Platforms)**  
            - Launch price: **{B2B_PRICE_LAUNCH} AED / unit**  
            - COGS (retrofit upcycling): **{B2B_COGS} AED / unit**  
            - Gross margin per B2B unit: **{B2B_PRICE_LAUNCH - B2B_COGS} AED**

            **B2C – NOORSOL MOVE (Beach-Lite)**  
            - Launch price: **{B2C_PRICE_LAUNCH} AED / unit**  
            - COGS: **{B2C_COGS} AED / unit**  
            - Gross margin per B2C unit: **{B2C_PRICE_LAUNCH - B2C_COGS} AED**
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Fixed Cost Structure – Year 1</div>', unsafe_allow_html=True)

    col_fc1, col_fc2, col_fc3, col_fc4, col_fc5 = st.columns(5)
    col_fc1.metric("Salaries", f"{FIXED_SALARIES:,.0f}")
    col_fc2.metric("Marketing", f"{FIXED_MARKETING:,.0f}")
    col_fc3.metric("R&D", f"{FIXED_RND:,.0f}")
    col_fc4.metric("Ops/Logistics", f"{FIXED_OPS:,.0f}")
    col_fc5.metric("Other", f"{FIXED_OTHER:,.0f}")

    st.metric("Total Fixed Costs (Annual)", f"{TOTAL_FIXED_COSTS:,.0f} AED")

    st.markdown("---")
    st.markdown('<div class="section-title">How Much of Dubai’s Bag Market Does NOORSOL Capture?</div>', unsafe_allow_html=True)

    # Simple visual: adoption vs total bag demand
    demand_data = pd.DataFrame({
        "Scenario": ["Pessimistic", "Base", "Optimistic"],
        "Adoption %": [adoption_pess, adoption_base, adoption_opt],
    })
    demand_data["Captured bags (units)"] = demand_data["Adoption %"] * ANNUAL_BAG_DEMAND

    fig_demand = px.bar(
        demand_data,
        x="Scenario",
        y="Captured bags (units)",
        color="Scenario",
        color_discrete_sequence=["#5dade2", "#2874a6", "#154360"],
        text_auto=".0f",
        title="B2B Market Capture – Bags Replaced by NOORSOL (Year 1)"
    )
    fig_demand.update_layout(
        yaxis_title="Bags captured (units)",
        xaxis_title="Scenario",
        legend_title="Scenario",
    )
    st.plotly_chart(fig_demand, use_container_width=True)


# ============================================================
# P&L & VISUALS TAB
# ============================================================
with tab_pnl:
    st.markdown('<div class="section-title">Year 0 & Year 1 P&L – with Detailed Income Statement</div>', unsafe_allow_html=True)

    # ---- Phase & Scenario selectors ----
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        phase_choice = st.selectbox(
            "Select phase",
            ["Pilot (Year 0)", "Year 1"],
            index=1
        )
    with col_sel2:
        scenario_choice = st.selectbox(
            "Select scenario",
            ["Pessimistic", "Base", "Optimistic"],
            index=1
        )

    # ---- Determine selected financials ----
    if phase_choice == "Pilot (Year 0)":
        selected_fin = compute_pilot()
        selected_label = "Pilot (Year 0)"
    else:
        selected_row = df_scen[df_scen["Scenario"] == scenario_choice].iloc[0]
        selected_fin = selected_row.to_dict()
        selected_label = f"Year 1 – {scenario_choice} Scenario"

    # ---- Top metrics for selected case ----
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Revenue", f"{selected_fin['Total revenue (AED)']:,.0f}")
    col_m2.metric("Gross Profit", f"{selected_fin['Gross profit (AED)']:,.0f}")
    col_m3.metric("EBIT", f"{selected_fin['EBIT (AED)']:,.0f}")

    st.markdown(f"#### Income Statement – {selected_label}")

    # ---- Build income statement ----
    income_rows = [
        ("Revenue - B2B", selected_fin["B2B revenue (AED)"]),
        ("Revenue - B2C", selected_fin["B2C revenue (AED)"]),
        ("Total Revenue", selected_fin["Total revenue (AED)"]),
        ("COGS - B2B", -selected_fin["B2B COGS total (AED)"]),
        ("COGS - B2C", -selected_fin["B2C COGS total (AED)"]),
        ("Total COGS", -selected_fin["Total COGS (AED)"]),
        ("Gross Profit", selected_fin["Gross profit (AED)"]),
        ("Operating Expenses - Salaries", -FIXED_SALARIES),
        ("Operating Expenses - Marketing", -FIXED_MARKETING),
        ("Operating Expenses - R&D", -FIXED_RND),
        ("Operating Expenses - Ops/Logistics", -FIXED_OPS),
        ("Operating Expenses - Other", -FIXED_OTHER),
        ("Total Operating Expenses", -TOTAL_FIXED_COSTS),
        ("EBIT", selected_fin["EBIT (AED)"]),
    ]

    df_income = pd.DataFrame(income_rows, columns=["Line Item", "Amount (AED)"])

    st.dataframe(
        df_income.style.format({"Amount (AED)": "{:,.0f}"}),
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("### Scenario Comparison – Year 1 (All Scenarios)")

    # High-level metrics for Year 1 scenarios
    col_top1, col_top2, col_top3 = st.columns(3)
    col_top1.metric("Pessimistic Revenue", f"{df_scen.loc[0, 'Total revenue (AED)']:,.0f}")
    col_top2.metric("Base Revenue",        f"{df_scen.loc[1, 'Total revenue (AED)']:,.0f}")
    col_top3.metric("Optimistic Revenue",  f"{df_scen.loc[2, 'Total revenue (AED)']:,.0f}")

    st.markdown("#### Year 1 Scenario Table")

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
    st.markdown("### Revenue & EBIT by Scenario (Year 1)")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_rev = px.bar(
            df_scen,
            x="Scenario",
            y="Total revenue (AED)",
            color="Scenario",
            color_discrete_sequence=["#5dade2", "#2874a6", "#154360"],
            text_auto=".0f",
            title="Total Revenue by Scenario (Year 1)",
        )
        fig_rev.update_layout(
            yaxis_title="Revenue (AED)",
            xaxis_title="Scenario",
            legend_title="Scenario"
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_chart2:
        fig_ebit = px.bar(
            df_scen,
            x="Scenario",
            y="EBIT (AED)",
            color="Scenario",
            color_discrete_sequence=["#7fb3d5", "#2e86c1", "#1b4f72"],
            text_auto=".0f",
            title="EBIT by Scenario (Year 1)",
        )
        fig_ebit.update_layout(
            yaxis_title="EBIT (AED)",
            xaxis_title="Scenario",
            legend_title="Scenario"
        )
        st.plotly_chart(fig_ebit, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🥧 Donut Charts – Revenue Mix & Value Capture (Base Scenario, Year 1)")

    base_row = df_scen[df_scen["Scenario"] == "Base"].iloc[0]

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        # Revenue split donut (B2B vs B2C)
        rev_split_df = pd.DataFrame({
            "Segment": ["B2B NOORSOL (retrofit)", "B2C NOORSOL MOVE"],
            "Revenue": [base_row["B2B revenue (AED)"], base_row["B2C revenue (AED)"]],
        })
        fig_donut_rev = px.pie(
            rev_split_df,
            names="Segment",
            values="Revenue",
            hole=0.55,
            title="Revenue Mix – Base Scenario (Year 1)",
            color_discrete_sequence=["#1f77b4", "#aec7e8"]
        )
        fig_donut_rev.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_donut_rev, use_container_width=True)

    with col_d2:
        # Value creation donut (COGS vs Gross Profit)
        value_df = pd.DataFrame({
            "Component": ["COGS", "Gross Profit"],
            "Value": [base_row["Total COGS (AED)"], base_row["Gross profit (AED)"]],
        })
        fig_donut_val = px.pie(
            value_df,
            names="Component",
            values="Value",
            hole=0.55,
            title="Value Capture – Base Scenario (Year 1)",
            color_discrete_sequence=["#5dade2", "#21618c"]
        )
        fig_donut_val.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_donut_val, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 Pilot vs Year 1 Base – Revenue & Gross Profit")

    # Pilot P&L (simple, non-annualised idea using pilot prices)
    pilot_stats = compute_pilot()
    compare_df = pd.DataFrame({
        "Phase": ["Pilot (Year 0)", "Year 1 Base"],
        "Revenue": [pilot_stats["Total revenue (AED)"], base_row["Total revenue (AED)"]],
        "Gross Profit": [pilot_stats["Gross profit (AED)"], base_row["Gross profit (AED)"]],
    })

    fig_compare = px.bar(
        compare_df.melt(id_vars="Phase", var_name="Metric", value_name="AED"),
        x="Phase",
        y="AED",
        color="Metric",
        barmode="group",
        color_discrete_sequence=["#5dade2", "#1f618d"],
        title="Pilot vs Year 1 Base – Revenue & Gross Profit",
    )
    fig_compare.update_layout(
        yaxis_title="AED",
        xaxis_title="Phase",
        legend_title="Metric"
    )
    st.plotly_chart(fig_compare, use_container_width=True)


# ============================================================
# BREAKEVEN TAB – ONLY BASE SCENARIO
# ============================================================
with tab_breakeven:
    st.markdown('<div class="section-title">Breakeven Analysis – Base Scenario Only (Year 1)</div>', unsafe_allow_html=True)

    # Use Base Scenario for breakeven
    base_row = df_scen[df_scen["Scenario"] == "Base"].iloc[0]
    contribution_per_unit = base_row["Contribution / unit (AED)"]
    be_units_total = breakeven_units(contribution_per_unit)

    col_be1, col_be2, col_be3 = st.columns(3)
    col_be1.metric("Contribution / unit (Base)", f"{contribution_per_unit:,.0f} AED")
    col_be2.metric("Fixed costs (Year 1)", f"{TOTAL_FIXED_COSTS:,.0f} AED")
    col_be3.metric(
        "Breakeven units (total)",
        "∞" if np.isinf(be_units_total) else f"{be_units_total:,.0f}"
    )

    st.markdown("---")

    if not np.isinf(be_units_total) and be_units_total > 0:
        st.markdown("### 📈 Cumulative Profit vs Units Sold (Base Scenario)")

        max_units = int(be_units_total * 1.5)
        units = np.linspace(0, max_units, 60)
        cum_profit = (units * contribution_per_unit) - TOTAL_FIXED_COSTS
        df_be = pd.DataFrame({
            "Total units sold": units,
            "Cumulative profit (AED)": cum_profit,
        })

        fig_be = px.line(
            df_be,
            x="Total units sold",
            y="Cumulative profit (AED)",
            title="Cumulative Profit Curve – Base Scenario",
            color_discrete_sequence=["#1f77b4"],
        )
        fig_be.add_hline(y=0, line_dash="dash", line_color="#7f8c8d")
        fig_be.update_layout(
            xaxis_title="Total units sold",
            yaxis_title="Cumulative profit (AED)",
        )
        st.plotly_chart(fig_be, use_container_width=True)

        st.info(
            f"In the **Base Scenario**, NOORSOL needs to sell approximately "
            f"**{be_units_total:,.0f} units** in Year 1 to breakeven on fixed costs."
        )
    else:
        st.warning(
            "Contribution per unit is non-positive in the Base Scenario, so breakeven cannot be achieved "
            "with the current assumptions."
        )
