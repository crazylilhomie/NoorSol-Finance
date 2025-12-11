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
BAGS_PER_BIKE_PER_YEAR = 1.0        # Conservative (1 bag per rider per year)
ANNUAL_BAG_DEMAND = int(TOTAL_BIKES_DUBAI * BAGS_PER_BIKE_PER_YEAR)  # 40,000 bags

# B2C: estimated Dubai cooler-style market (TAM in units/year)
B2C_MARKET_SIZE_DUBAI = 200_000     # Cooler-style TAM per year in Dubai

# ---- Fixed product economics ----
# B2B: NOORSOL retrofit (upcycling existing boxes)
B2B_PRICE_LAUNCH = 450
B2B_COGS = 200

# B2C: NOORSOL MOVE (Beach-Lite)
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def compute_scenario(name: str,
                     adoption_rate_b2b: float,
                     adoption_rate_b2c: float) -> dict:
    """
    Compute Year 1 financials for a given scenario.
    - adoption_rate_b2b: fraction of annual bag demand captured as NOORSOL retrofits (0–1).
    - adoption_rate_b2c: fraction of B2C cooler-style TAM captured as NOORSOL MOVE (0–1).
    Uses launch pricing.
    """
    # Units from adoption rates
    b2b_units = ANNUAL_BAG_DEMAND * adoption_rate_b2b
    b2c_units = B2C_MARKET_SIZE_DUBAI * adoption_rate_b2c

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
        "Adoption B2B (bags %)": adoption_rate_b2b,
        "Adoption B2C (coolers %)": adoption_rate_b2c,
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
    .sidebar-note {
        font-size: 12px;
        color: #3c4a60;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">📦 NOORSOL – Dubai Financial Dashboard</div>', unsafe_allow_html=True)
st.caption("Solar-powered smart delivery & outdoor boxes • Focus: Dubai • All values in AED")

# ============================================================
# SIDEBAR – MARKET CAPTURE SLIDERS (ENHANCED & IN %)
# ============================================================
st.sidebar.header("🎯 Market Capture Assumptions")

st.sidebar.write(
    "All prices, COGS, riders, and TAMs are fixed based on Dubai-focused "
    "research and smart guesstimates. Use the sliders to choose how "
    "**aggressive or conservative** NOORSOL is in **Year 1**."
)

# ----------------- B2B SLIDERS -----------------
st.sidebar.subheader("🚚 B2B: Delivery Box Market")

st.sidebar.markdown(
    '<p class="sidebar-note">'
    "Pessimistic = slow platform uptake • Base = realistic launch • Optimistic = strong platform push"
    "</p>",
    unsafe_allow_html=True,
)

adoption_pess_b2b_pct = st.sidebar.slider(
    "Pessimistic B2B adoption (% of bag market)",
    min_value=1,
    max_value=20,
    value=5,
    step=1,
    format="%d %%"
)
adoption_base_b2b_pct = st.sidebar.slider(
    "Base B2B adoption (% of bag market)",
    min_value=5,
    max_value=40,
    value=10,
    step=1,
    format="%d %%"
)
adoption_opt_b2b_pct = st.sidebar.slider(
    "Optimistic B2B adoption (% of bag market)",
    min_value=10,
    max_value=80,
    value=20,
    step=1,
    format="%d %%"
)

# Convert to decimals for backend calculations
adoption_pess_b2b = adoption_pess_b2b_pct / 100
adoption_base_b2b = adoption_base_b2b_pct / 100
adoption_opt_b2b = adoption_opt_b2b_pct / 100

# ----------------- B2C SLIDERS -----------------
st.sidebar.subheader("🏖️ B2C: Cooler / Outdoor Market")

st.sidebar.markdown(
    '<p class="sidebar-note">'
    "These % values are of the ~200k cooler-style units per year in Dubai (all brands). "
    "We stay well below 1% in Base case."
    "</p>",
    unsafe_allow_html=True,
)

b2c_pess_pct = st.sidebar.slider(
    "Pessimistic B2C adoption (% of cooler market)",
    min_value=0.1,
    max_value=2.0,
    value=0.3,
    step=0.1,
    format="%.1f %%"
)
b2c_base_pct = st.sidebar.slider(
    "Base B2C adoption (% of cooler market)",
    min_value=0.2,
    max_value=3.0,
    value=0.45,
    step=0.05,
    format="%.2f %%"
)
b2c_opt_pct = st.sidebar.slider(
    "Optimistic B2C adoption (% of cooler market)",
    min_value=0.3,
    max_value=5.0,
    value=0.60,
    step=0.1,
    format="%.1f %%"
)

# Convert to decimals
b2c_pess = b2c_pess_pct / 100
b2c_base = b2c_base_pct / 100
b2c_opt = b2c_opt_pct / 100

# ============================================================
# PRE-COMPUTE YEAR 1 SCENARIOS (USED IN MULTIPLE TABS)
# ============================================================
scenarios = [
    compute_scenario("Pessimistic", adoption_pess_b2b, b2c_pess),
    compute_scenario("Base",        adoption_base_b2b, b2c_base),
    compute_scenario("Optimistic",  adoption_opt_b2b,  b2c_opt),
]
df_scen = pd.DataFrame(scenarios)

# ============================================================
# TABS (OVERVIEW, P&L, BREAKEVEN)
# ============================================================
tab_overview, tab_pnl, tab_breakeven = st.tabs(
    ["🏁 Overview", "📊 P&L & Brands", "⚖️ Breakeven"]
)

# ============================================================
# OVERVIEW TAB
# ============================================================
with tab_overview:
    st.markdown('<div class="section-title">Dubai Ecosystem & NOORSOL Snapshot</div>', unsafe_allow_html=True)

    # Top metrics row: core TAMs
    top_col1, top_col2, top_col3, top_col4 = st.columns(4)
    with top_col1:
        st.metric("Active delivery bikes (Dubai)", f"{TOTAL_BIKES_DUBAI:,.0f}")
    with top_col2:
        st.metric("Bags per bike per year", f"{BAGS_PER_BIKE_PER_YEAR:.1f}")
    with top_col3:
        st.metric("B2B bag TAM (year)", f"{ANNUAL_BAG_DEMAND:,.0f}")
    with top_col4:
        st.metric("B2C cooler TAM (year)", f"{B2C_MARKET_SIZE_DUBAI:,.0f}")

    st.markdown("")
    col1, col2 = st.columns(2)

    # B2B assumptions card
    with col1:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### 🚚 B2B – Delivery Ecosystem (Fixed Assumptions)")
        st.markdown(
            f"""
            - **{TOTAL_BIKES_DUBAI:,}** active delivery riders in Dubai  
            - Each rider replaces **~{BAGS_PER_BIKE_PER_YEAR:.0f}** delivery bag per year  
            - Implied B2B annual replacement: **{ANNUAL_BAG_DEMAND:,} bags**

            These numbers reflect:
            - RTA-registered delivery motorcycles  
            - Conservative replacement (1 bag per rider per year)  
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # B2C smart guesstimate card
    with col2:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### 🏖️ B2C – Outdoor Lifestyle & Cooler Market")
        st.markdown(
            f"""
            - Dubai households: **~771,000**  
            - Outdoor-active families (≈35%): **~270,000**  
            - Beach & outdoor tourist groups (annual): **50,000–90,000**  
            - UAE cooler market: **~530,000 units/year**, of which Dubai ≈ **40%**  

            👉 Therefore, we assume a **B2C cooler-style TAM of {B2C_MARKET_SIZE_DUBAI:,} units/year**  
            (all brands).  
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">💰 Product Unit Economics – Per Unit (Year 1 Pricing)</div>', unsafe_allow_html=True)

    # Unit economics for both products
    b2b_profit_per_unit = B2B_PRICE_LAUNCH - B2B_COGS
    b2b_margin_pct = (b2b_profit_per_unit / B2B_PRICE_LAUNCH) * 100 if B2B_PRICE_LAUNCH > 0 else 0

    b2c_profit_per_unit = B2C_PRICE_LAUNCH - B2C_COGS
    b2c_margin_pct = (b2c_profit_per_unit / B2C_PRICE_LAUNCH) * 100 if B2C_PRICE_LAUNCH > 0 else 0

    econ_col1, econ_col2 = st.columns(2)
    with econ_col1:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### B2B – NOORSOL Retrofit (Delivery Platforms)")
        st.markdown(
            f"""
            - **Retail price**: {B2B_PRICE_LAUNCH} AED / unit  
            - **COGS (retrofit & components)**: {B2B_COGS} AED / unit  
            - **Profit per unit**: **{b2b_profit_per_unit} AED**  
            - **Gross margin**: **{b2b_margin_pct:.1f}%**
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with econ_col2:
        st.markdown('<div class="subtle-card">', unsafe_allow_html=True)
        st.markdown("#### B2C – NOORSOL MOVE (Outdoor & Beach Users)")
        st.markdown(
            f"""
            - **Retail price**: {B2C_PRICE_LAUNCH} AED / unit  
            - **COGS (box, wheels, solar, insulation)**: {B2C_COGS} AED / unit  
            - **Profit per unit**: **{b2c_profit_per_unit} AED**  
            - **Gross margin**: **{b2c_margin_pct:.1f}%**
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
    st.markdown('<div class="section-title">How Much of Each Market Does NOORSOL Capture in Year 1?</div>', unsafe_allow_html=True)

    # B2B/B2C capture for each scenario
    demand_data = pd.DataFrame({
        "Scenario": ["Pessimistic", "Base", "Optimistic"],
        "B2B adoption %": [adoption_pess_b2b, adoption_base_b2b, adoption_opt_b2b],
        "B2C adoption %": [b2c_pess, b2c_base, b2c_opt],
    })
    demand_data["B2B captured bags"] = demand_data["B2B adoption %"] * ANNUAL_BAG_DEMAND
    demand_data["B2C captured units"] = demand_data["B2C adoption %"] * B2C_MARKET_SIZE_DUBAI

    col_b2b, col_b2c = st.columns(2)

    with col_b2b:
        fig_b2b = px.bar(
            demand_data,
            x="Scenario",
            y="B2B captured bags",
            color="Scenario",
            color_discrete_sequence=["#5dade2", "#2874a6", "#154360"],
            text_auto=".0f",
            title="B2B Market Capture – Bags Replaced by NOORSOL (Year 1)"
        )
        fig_b2b.update_layout(
            yaxis_title="Bags captured (units)",
            xaxis_title="Scenario",
            legend_title="Scenario",
        )
        st.plotly_chart(fig_b2b, use_container_width=True)

    with col_b2c:
        fig_b2c = px.bar(
            demand_data,
            x="Scenario",
            y="B2C captured units",
            color="Scenario",
            color_discrete_sequence=["#7fb3d5", "#2e86c1", "#1b4f72"],
            text_auto=".0f",
            title="B2C Market Capture – NOORSOL MOVE Units (Year 1)"
        )
        fig_b2c.update_layout(
            yaxis_title="Units captured",
            xaxis_title="Scenario",
            legend_title="Scenario",
        )
        st.plotly_chart(fig_b2c, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 TAM vs NOORSOL Target – Base Scenario (Stacked View)")

    # Stacked bar: Remaining Market vs NOORSOL Target for B2B & B2C (Base scenario)
    base_captured_b2b = ANNUAL_BAG_DEMAND * adoption_base_b2b
    base_captured_b2c = B2C_MARKET_SIZE_DUBAI * b2c_base

    remaining_b2b = max(ANNUAL_BAG_DEMAND - base_captured_b2b, 0)
    remaining_b2c = max(B2C_MARKET_SIZE_DUBAI - base_captured_b2c, 0)

    df_stack = pd.DataFrame({
        "Market": ["B2B bags", "B2B bags", "B2C coolers", "B2C coolers"],
        "Segment": ["NOORSOL Target", "Remaining Market", "NOORSOL Target", "Remaining Market"],
        "Units": [base_captured_b2b, remaining_b2b, base_captured_b2c, remaining_b2c],
    })

    fig_stack = px.bar(
        df_stack,
        x="Market",
        y="Units",
        color="Segment",
        barmode="stack",
        color_discrete_sequence=["#1f77b4", "#d6e4ff"],
        title="TAM vs NOORSOL Target – Base Scenario (Year 1)",
        text_auto=".0f"
    )
    fig_stack.update_layout(
        yaxis_title="Units",
        xaxis_title="Market",
        legend_title="Segment",
    )
    st.plotly_chart(fig_stack, use_container_width=True)


# ============================================================
# P&L & BRANDS TAB – YEAR 1 ONLY
# ============================================================
with tab_pnl:
    st.markdown('<div class="section-title">P&L, Brand Contribution & Scenarios – Year 1</div>', unsafe_allow_html=True)

    # --- Dropdown: Scenario (Year 1 only) ---
    scenario_choice = st.selectbox(
        "Select Year 1 scenario to analyse",
        ["Pessimistic", "Base", "Optimistic"],
        index=1
    )

    selected_row = df_scen[df_scen["Scenario"] == scenario_choice].iloc[0]
    selected_fin = selected_row.to_dict()
    selected_label = f"Year 1 – {scenario_choice} Scenario"

    # --- Key metrics for selected case ---
    st.markdown(f"#### Income Statement – {selected_label}")

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Revenue", f"{selected_fin['Total revenue (AED)']:,.0f}")
    col_m2.metric("Gross Profit", f"{selected_fin['Gross profit (AED)']:,.0f}")
    col_m3.metric("EBIT", f"{selected_fin['EBIT (AED)']:,.0f}")

    # --- Income Statement Table (Industry-style) ---
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
    st.markdown("### Brand Contribution – Revenue & Profit (Selected Year 1 Scenario)")

    # --- Donut charts: brand contribution to revenue & gross profit ---
    gp_b2b = selected_fin["B2B revenue (AED)"] - selected_fin["B2B COGS total (AED)"]
    gp_b2c = selected_fin["B2C revenue (AED)"] - selected_fin["B2C COGS total (AED)"]

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        rev_split_df = pd.DataFrame({
            "Segment": ["B2B NOORSOL (retrofit)", "B2C NOORSOL MOVE"],
            "Value": [selected_fin["B2B revenue (AED)"], selected_fin["B2C revenue (AED)"]],
        })
        fig_donut_rev = px.pie(
            rev_split_df,
            names="Segment",
            values="Value",
            hole=0.55,
            title=f"Revenue Mix – {selected_label}",
            color_discrete_sequence=["#1f77b4", "#aec7e8"]
        )
        fig_donut_rev.update_traces(
            textposition="inside",
            textinfo="percent+label",
            insidetextorientation="radial"
        )
        st.plotly_chart(fig_donut_rev, use_container_width=True)

    with col_d2:
        profit_split_df = pd.DataFrame({
            "Segment": ["B2B NOORSOL (retrofit)", "B2C NOORSOL MOVE"],
            "Value": [gp_b2b, gp_b2c],
        })
        fig_donut_gp = px.pie(
            profit_split_df,
            names="Segment",
            values="Value",
            hole=0.55,
            title=f"Gross Profit Mix – {selected_label}",
            color_discrete_sequence=["#5dade2", "#21618c"]
        )
        fig_donut_gp.update_traces(
            textposition="inside",
            textinfo="percent+label",
            insidetextorientation="radial"
        )
        st.plotly_chart(fig_donut_gp, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Key Financial Ratios – Selected Year 1 Scenario")

    total_rev = selected_fin["Total revenue (AED)"]
    if total_rev > 0:
        gross_margin_pct = selected_fin.get("Gross margin (%)", 0)
        ebit_margin_pct = selected_fin.get("EBIT margin (%)", 0)
        b2b_share = selected_fin["B2B revenue (AED)"] / total_rev * 100
        b2c_share = selected_fin["B2C revenue (AED)"] / total_rev * 100
    else:
        gross_margin_pct = ebit_margin_pct = b2b_share = b2c_share = 0

    metrics_df = pd.DataFrame({
        "Metric": [
            "Gross Margin (%)",
            "EBIT Margin (%)",
            "B2B Share of Revenue (%)",
            "B2C Share of Revenue (%)",
        ],
        "Value": [
            gross_margin_pct,
            ebit_margin_pct,
            b2b_share,
            b2c_share,
        ],
    })

    fig_metrics = px.bar(
        metrics_df,
        x="Value",
        y="Metric",
        orientation="h",
        text_auto=".1f",
        title="Key Financial Ratios – Year 1",
        color_discrete_sequence=["#2874a6"],
    )
    fig_metrics.update_layout(
        xaxis_title="Percentage (%)",
        yaxis_title="",
    )
    st.plotly_chart(fig_metrics, use_container_width=True)

    st.markdown("---")
    st.markdown("### Scenario Comparison – Year 1 (All Cases)")

    compare_df = df_scen[["Scenario", "Total revenue (AED)", "EBIT (AED)"]].copy()

    fig_compare = px.bar(
        compare_df.melt(id_vars="Scenario", var_name="Metric", value_name="AED"),
        x="Scenario",
        y="AED",
        color="Metric",
        barmode="group",
        color_discrete_sequence=["#5dade2", "#1f618d"],
        title="Year 1 – Revenue & EBIT Across Scenarios",
    )
    fig_compare.update_layout(
        yaxis_title="AED",
        xaxis_title="Scenario",
        legend_title="Metric"
    )
    st.plotly_chart(fig_compare, use_container_width=True)


# ============================================================
# BREAKEVEN TAB – BASE SCENARIO, YEAR 1
# ============================================================
with tab_breakeven:
    st.markdown('<div class="section-title">Breakeven Analysis – Base Scenario (Year 1)</div>', unsafe_allow_html=True)

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
        st.markdown("### 📈 Cumulative Profit vs Units Sold (Base Scenario – Year 1)")

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
            title="Cumulative Profit Curve – Base Scenario (Year 1)",
            color_discrete_sequence=["#1f77b4"],
        )
        fig_be.add_hline(y=0, line_dash="dash", line_color="#7f8c8d")
        fig_be.update_layout(
            xaxis_title="Total units sold (B2B + B2C blended)",
            yaxis_title="Cumulative profit (AED)",
        )
        st.plotly_chart(fig_be, use_container_width=True)

        st.info(
            f"In the **Base Scenario (Year 1)**, NOORSOL needs to sell approximately "
            f"**{be_units_total:,.0f} units** in total to breakeven on fixed costs."
        )
    else:
        st.warning(
            "Contribution per unit is non-positive in the Base Scenario, so breakeven cannot be achieved "
            "with the current assumptions."
        )
