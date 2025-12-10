import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="NOORSOL Dubai Financial Dashboard",
    layout="wide"
)

st.title("📦 NOORSOL Dubai Financial Dashboard")
st.caption("Solar-powered smart delivery & outdoor boxes – financial model for Dubai market")

# ----------------------------
# Sidebar – Core Assumptions
# ----------------------------
st.sidebar.header("🔧 Core Assumptions (Editable)")

# Raw market data assumptions (Dubai)
st.sidebar.subheader("📊 Delivery Ecosystem – Dubai")

total_bikes = st.sidebar.slider(
    "Estimated active delivery bikes in Dubai",
    min_value=10000,
    max_value=100000,
    value=40000,
    step=1000,
    help="Based on reports of 40k–90k registered delivery motorcycles in Dubai."
)

bags_per_bike_per_year = st.sidebar.slider(
    "Avg. delivery bags used per bike per year",
    min_value=0.5,
    max_value=3.0,
    value=1.5,
    step=0.1,
    help="Accounts for wear and replacement in Dubai heat (1–2 bags/year is typical)."
)

annual_bag_demand = total_bikes * bags_per_bike_per_year

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Product Economics – B2B (NOORSOL – Retrofit)")

b2b_price_pilot = st.sidebar.number_input(
    "B2B price per unit – Pilot (AED)",
    min_value=200,
    max_value=1000,
    value=399,
    step=10
)

b2b_price_launch = st.sidebar.number_input(
    "B2B price per unit – Launch (AED)",
    min_value=200,
    max_value=1500,
    value=450,
    step=10
)

b2b_cogs = st.sidebar.number_input(
    "B2B COGS per unit – Retrofit (AED)",
    min_value=50,
    max_value=1000,
    value=200,
    step=5,
    help="Assuming upcycling / retrofitting existing boxes."
)

st.sidebar.subheader("🏖️ Product Economics – B2C (NOORSOL MOVE – Beach-Lite)")

b2c_price_pilot = st.sidebar.number_input(
    "B2C price per unit – Pilot (AED)",
    min_value=200,
    max_value=2000,
    value=499,
    step=10
)

b2c_price_launch = st.sidebar.number_input(
    "B2C price per unit – Launch (AED)",
    min_value=200,
    max_value=2500,
    value=599,
    step=10
)

b2c_cogs = st.sidebar.number_input(
    "B2C COGS per unit – Beach-Lite (AED)",
    min_value=50,
    max_value=1500,
    value=305,
    step=5
)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Scenario Adoption Rates (B2B)")

adoption_pess = st.sidebar.slider(
    "Pessimistic adoption of annual bag demand",
    min_value=0.01,
    max_value=0.30,
    value=0.05,
    step=0.01,
    format="%.2f"
)

adoption_base = st.sidebar.slider(
    "Base adoption of annual bag demand",
    min_value=0.05,
    max_value=0.40,
    value=0.10,
    step=0.01,
    format="%.2f"
)

adoption_opt = st.sidebar.slider(
    "Optimistic adoption of annual bag demand",
    min_value=0.10,
    max_value=0.80,
    value=0.20,
    step=0.01,
    format="%.2f"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏦 Fixed Cost Structure (Annual)")

fixed_salaries = st.sidebar.number_input(
    "Salaries & founders' compensation (AED/year)",
    min_value=0,
    max_value=2000000,
    value=360000,
    step=10000
)

fixed_marketing = st.sidebar.number_input(
    "Brand & performance marketing (AED/year)",
    min_value=0,
    max_value=1000000,
    value=90000,
    step=5000
)

fixed_rnd = st.sidebar.number_input(
    "Product development & R&D (AED/year)",
    min_value=0,
    max_value=1000000,
    value=40000,
    step=5000
)

fixed_ops = st.sidebar.number_input(
    "Operations, logistics overhead & office (AED/year)",
    min_value=0,
    max_value=1000000,
    value=120000,
    step=5000
)

fixed_other = st.sidebar.number_input(
    "Other fixed costs (legal, accounting, etc.) (AED/year)",
    min_value=0,
    max_value=500000,
    value=30000,
    step=5000
)

total_fixed_costs = fixed_salaries + fixed_marketing + fixed_rnd + fixed_ops + fixed_other

# ----------------------------
# Helper functions
# ----------------------------
def compute_scenario(
    name: str,
    adoption_rate_b2b: float,
    b2c_units: int,
    use_launch_pricing: bool = True
):
    """
    Compute volumes and financials for a scenario.
    """
    # B2B units are a function of annual bag demand and adoption rate
    b2b_units = annual_bag_demand * adoption_rate_b2b

    # Pricing
    b2b_price = b2b_price_launch if use_launch_pricing else b2b_price_pilot
    b2c_price = b2c_price_launch if use_launch_pricing else b2c_price_pilot

    # Revenues
    b2b_revenue = b2b_units * b2b_price
    b2c_revenue = b2c_units * b2c_price
    total_revenue = b2b_revenue + b2c_revenue

    # COGS
    b2b_cogs_total = b2b_units * b2b_cogs
    b2c_cogs_total = b2c_units * b2c_cogs
    total_cogs = b2b_cogs_total + b2c_cogs_total

    # Gross profit
    gross_profit = total_revenue - total_cogs
    gross_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

    # EBIT (no interest/tax modelling here)
    ebit = gross_profit - total_fixed_costs
    ebit_margin_pct = (ebit / total_revenue * 100) if total_revenue > 0 else 0

    # Contribution margin per unit (weighted)
    total_units = b2b_units + b2c_units
    blended_contribution_per_unit = (gross_profit / total_units) if total_units > 0 else 0

    return {
        "Scenario": name,
        "B2B units": b2b_units,
        "B2C units": b2c_units,
        "Total units": total_units,
        "B2B revenue (AED)": b2b_revenue,
        "B2C revenue (AED)": b2c_revenue,
        "Total revenue (AED)": total_revenue,
        "Total COGS (AED)": total_cogs,
        "Gross profit (AED)": gross_profit,
        "Gross margin (%)": gross_margin_pct,
        "Fixed costs (AED)": total_fixed_costs,
        "EBIT (AED)": ebit,
        "EBIT margin (%)": ebit_margin_pct,
        "Contribution / unit (AED)": blended_contribution_per_unit,
    }

def breakeven_units(contribution_per_unit: float) -> float:
    if contribution_per_unit <= 0:
        return float("inf")
    return total_fixed_costs / contribution_per_unit

# ----------------------------
# Layout – Tabs
# ----------------------------
tab_overview, tab_assumptions, tab_pnl, tab_breakeven, tab_sensitivity = st.tabs(
    ["🏁 Overview", "📑 Raw Data & Assumptions", "📉 Pilot & Year 1 P&L", "⚖️ Breakeven Analysis", "📊 Sensitivity Analysis"]
)

# ----------------------------
# OVERVIEW TAB
# ----------------------------
with tab_overview:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Estimated active delivery bikes in Dubai",
            f"{int(total_bikes):,}"
        )
        st.metric(
            "Annual delivery-bag demand (est.)",
            f"{int(annual_bag_demand):,} bags"
        )

    with col2:
        st.metric(
            "B2B launch price (NOORSOL retrofit)",
            f"{b2b_price_launch:,.0f} AED / unit"
        )
        st.metric(
            "B2B COGS",
            f"{b2b_cogs:,.0f} AED / unit"
        )

    with col3:
        st.metric(
            "B2C launch price (NOORSOL MOVE)",
            f"{b2c_price_launch:,.0f} AED / unit"
        )
        st.metric(
            "B2C COGS",
            f"{b2c_cogs:,.0f} AED / unit"
        )

    st.markdown("---")
    st.subheader("Scenario Snapshot – Year 1 (using launch prices)")

    # Assume simple B2C unit guesses based on scenarios (editable below)
    default_b2c_pess = 600
    default_b2c_base = 900
    default_b2c_opt = 1200

    scenario_data = []
    scenario_data.append(
        compute_scenario("Pessimistic", adoption_pess, default_b2c_pess, use_launch_pricing=True)
    )
    scenario_data.append(
        compute_scenario("Base", adoption_base, default_b2c_base, use_launch_pricing=True)
    )
    scenario_data.append(
        compute_scenario("Optimistic", adoption_opt, default_b2c_opt, use_launch_pricing=True)
    )

    df_scenarios = pd.DataFrame(scenario_data)

    st.dataframe(
        df_scenarios[[
            "Scenario",
            "B2B units",
            "B2C units",
            "Total revenue (AED)",
            "Gross profit (AED)",
            "EBIT (AED)",
        ]].style.format({
            "B2B units": "{:,.0f}",
            "B2C units": "{:,.0f}",
            "Total revenue (AED)": "{:,.0f}",
            "Gross profit (AED)": "{:,.0f}",
            "EBIT (AED)": "{:,.0f}",
        }),
        use_container_width=True
    )

    fig_rev = px.bar(
        df_scenarios,
        x="Scenario",
        y="Total revenue (AED)",
        hover_data=["Gross profit (AED)", "EBIT (AED)"],
        title="Year 1 Revenue by Scenario"
    )
    st.plotly_chart(fig_rev, use_container_width=True)

# ----------------------------
# RAW DATA & ASSUMPTIONS TAB
# ----------------------------
with tab_assumptions:
    st.subheader("📊 Raw Market Data (Dubai)")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            """
            **Delivery Bikes & Riders**

            - Estimated active delivery motorcycles in Dubai: **{:,}** (editable in sidebar)  
            - Average delivery bags used per bike per year: **{:.1f}**  
            - Implied annual bag demand: **{:,} bags**
            """.format(int(total_bikes), bags_per_bike_per_year, int(annual_bag_demand))
        )

    with col_b:
        st.markdown(
            """
            **High-Level Market Context (Assumptive)**  

            - Focus geography: **Dubai only**  
            - TAM driver: online food delivery + quick-commerce + outdoor lifestyle  
            - NOORSOL targets **retrofit of existing delivery boxes** (B2B)  
            - NOORSOL MOVE targets **families & tourists** (B2C)  
            """
        )

    st.markdown("---")
    st.subheader("🔢 Financial Assumptions Summary")

    assumptions = {
        "Parameter": [
            "B2B price – pilot (AED)",
            "B2B price – launch (AED)",
            "B2B COGS – retrofit (AED)",
            "B2C price – pilot (AED)",
            "B2C price – launch (AED)",
            "B2C COGS – Beach-Lite (AED)",
            "Adoption – pessimistic",
            "Adoption – base",
            "Adoption – optimistic",
            "Total fixed costs (AED/year)"
        ],
        "Value": [
            b2b_price_pilot,
            b2b_price_launch,
            b2b_cogs,
            b2c_price_pilot,
            b2c_price_launch,
            b2c_cogs,
            adoption_pess,
            adoption_base,
            adoption_opt,
            total_fixed_costs
        ]
    }

    df_assumptions = pd.DataFrame(assumptions)
    st.dataframe(
        df_assumptions.style.format({
            "Value": "{:,.4g}"
        }),
        use_container_width=True
    )

# ----------------------------
# P&L TAB
# ----------------------------
with tab_pnl:
    st.subheader("📉 Pilot & Year 1 P&L")

    st.markdown("Use the controls below to customise **pilot volumes** and **Year 1 B2C volumes** for each scenario.")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        pilot_b2b_units = st.number_input(
            "Pilot B2B units (retrofit boxes)",
            min_value=0,
            max_value=10000,
            value=400,
            step=50
        )

    with col_p2:
        pilot_b2c_units = st.number_input(
            "Pilot B2C units (Beach-Lite)",
            min_value=0,
            max_value=10000,
            value=200,
            step=50
        )

    with col_p3:
        st.write("Pilot uses **pilot pricing** and is treated as a separate short-term phase (not annualised).")

    # Pilot P&L
    pilot_b2b_rev = pilot_b2b_units * b2b_price_pilot
    pilot_b2c_rev = pilot_b2c_units * b2c_price_pilot
    pilot_rev_total = pilot_b2b_rev + pilot_b2c_rev

    pilot_b2b_cogs_total = pilot_b2b_units * b2b_cogs
    pilot_b2c_cogs_total = pilot_b2c_units * b2c_cogs
    pilot_cogs_total = pilot_b2b_cogs_total + pilot_b2c_cogs_total

    pilot_gross_profit = pilot_rev_total - pilot_cogs_total

    st.markdown("### 🧪 Pilot Phase Summary")
    col_pi1, col_pi2, col_pi3, col_pi4 = st.columns(4)
    with col_pi1:
        st.metric("Pilot revenue (AED)", f"{pilot_rev_total:,.0f}")
    with col_pi2:
        st.metric("Pilot gross profit (AED)", f"{pilot_gross_profit:,.0f}")
    with col_pi3:
        pilot_units_total = pilot_b2b_units + pilot_b2c_units
        gp_per_unit = pilot_gross_profit / pilot_units_total if pilot_units_total > 0 else 0
        st.metric("Gross profit / unit (AED)", f"{gp_per_unit:,.0f}")
    with col_pi4:
        pilot_gm = (pilot_gross_profit / pilot_rev_total * 100) if pilot_rev_total > 0 else 0
        st.metric("Pilot gross margin (%)", f"{pilot_gm:,.1f}%")

    st.markdown("---")
    st.markdown("### 📅 Year 1 Scenario P&L (Launch Pricing)")

    col_y1_1, col_y1_2, col_y1_3 = st.columns(3)

    with col_y1_1:
        y1_b2c_pess = st.number_input(
            "Year 1 B2C units – Pessimistic",
            min_value=0,
            max_value=20000,
            value=600,
            step=50
        )
    with col_y1_2:
        y1_b2c_base = st.number_input(
            "Year 1 B2C units – Base",
            min_value=0,
            max_value=20000,
            value=900,
            step=50
        )
    with col_y1_3:
        y1_b2c_opt = st.number_input(
            "Year 1 B2C units – Optimistic",
            min_value=0,
            max_value=20000,
            value=1200,
            step=50
        )

    scenarios_y1 = [
        compute_scenario("Pessimistic", adoption_pess, y1_b2c_pess, use_launch_pricing=True),
        compute_scenario("Base", adoption_base, y1_b2c_base, use_launch_pricing=True),
        compute_scenario("Optimistic", adoption_opt, y1_b2c_opt, use_launch_pricing=True),
    ]

    df_y1 = pd.DataFrame(scenarios_y1)

    st.dataframe(
        df_y1[[
            "Scenario",
            "B2B units",
            "B2C units",
            "Total revenue (AED)",
            "Total COGS (AED)",
            "Gross profit (AED)",
            "Gross margin (%)",
            "EBIT (AED)",
            "EBIT margin (%)"
        ]].style.format({
            "B2B units": "{:,.0f}",
            "B2C units": "{:,.0f}",
            "Total revenue (AED)": "{:,.0f}",
            "Total COGS (AED)": "{:,.0f}",
            "Gross profit (AED)": "{:,.0f}",
            "Gross margin (%)": "{:,.1f}",
            "EBIT (AED)": "{:,.0f}",
            "EBIT margin (%)": "{:,.1f}",
        }),
        use_container_width=True
    )

    fig_profit = px.bar(
        df_y1,
        x="Scenario",
        y="EBIT (AED)",
        title="EBIT by Scenario – Year 1",
        text_auto=True
    )
    st.plotly_chart(fig_profit, use_container_width=True)

# ----------------------------
# BREAKEVEN TAB
# ----------------------------
with tab_breakeven:
    st.subheader("⚖️ Breakeven Analysis")

    st.markdown(
        """
        Breakeven is calculated as:

        > **Breakeven units = Total fixed costs ÷ Contribution per unit**

        Contribution per unit is based on the **selected scenario** below (Year 1, launch pricing).
        """
    )

    scenario_choice = st.selectbox(
        "Select scenario for breakeven calculation",
        options=["Pessimistic", "Base", "Optimistic"],
        index=1
    )

    # Map choice to our df
    selected_row = df_y1[df_y1["Scenario"] == scenario_choice].iloc[0]
    contribution_per_unit = selected_row["Contribution / unit (AED)"]

    be_units = breakeven_units(contribution_per_unit)

    col_be1, col_be2, col_be3 = st.columns(3)

    with col_be1:
        st.metric("Contribution / unit (AED)", f"{contribution_per_unit:,.0f}")
    with col_be2:
        if np.isinf(be_units):
            be_text = "∞"
        else:
            be_text = f"{be_units:,.0f}"
        st.metric("Breakeven units (total)", be_text)
    with col_be3:
        if not np.isinf(be_units):
            # Assume same B2B/B2C mix as the scenario
            total_units = selected_row["Total units"]
            b2b_units = selected_row["B2B units"]
            b2c_units = selected_row["B2C units"]
            b2b_share = b2b_units / total_units if total_units > 0 else 0
            be_b2b = be_units * b2b_share
            st.metric("Breakeven B2B units (approx.)", f"{be_b2b:,.0f}")
        else:
            st.metric("Breakeven B2B units (approx.)", "N/A")

    st.markdown("---")

    if not np.isinf(be_units):
        # Build cumulative profit curve vs units
        max_units_for_chart = int(be_units * 1.5)
        unit_steps = np.linspace(0, max_units_for_chart, 50)

        cum_profit = (unit_steps * contribution_per_unit) - total_fixed_costs
        df_be = pd.DataFrame({
            "Total units sold": unit_steps,
            "Cumulative profit (AED)": cum_profit
        })

        fig_be = px.line(
            df_be,
            x="Total units sold",
            y="Cumulative profit (AED)",
            title="Cumulative Profit vs. Units Sold"
        )
        fig_be.add_hline(y=0)

        st.plotly_chart(fig_be, use_container_width=True)
    else:
        st.info("Breakeven cannot be computed because contribution per unit is non-positive.")

# ----------------------------
# SENSITIVITY TAB
# ----------------------------
with tab_sensitivity:
    st.subheader("📊 Sensitivity: Adoption Rates vs Financial Outcomes")

    st.markdown(
        """
        This table and chart show how changing **B2B adoption rates** (as a % of annual bag demand in Dubai)
        impacts revenue, gross profit, and EBIT. B2C units are kept constant for comparison.
        """
    )

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        b2c_units_sensitivity = st.number_input(
            "B2C units for sensitivity scenarios (Year 1)",
            min_value=0,
            max_value=50000,
            value=900,
            step=50
        )

    with col_s2:
        st.write("Adoption rates tested: **15%, 25%, 40%** of annual bag demand.")

    adoption_rates = [0.15, 0.25, 0.40]
    rows = []
    for rate in adoption_rates:
        row = compute_scenario(
            name=f"{int(rate*100)}%",
            adoption_rate_b2b=rate,
            b2c_units=b2c_units_sensitivity,
            use_launch_pricing=True
        )
        rows.append(row)

    df_sens = pd.DataFrame(rows)

    st.dataframe(
        df_sens[[
            "Scenario",
            "B2B units",
            "Total revenue (AED)",
            "Gross profit (AED)",
            "EBIT (AED)",
            "EBIT margin (%)"
        ]].style.format({
            "B2B units": "{:,.0f}",
            "Total revenue (AED)": "{:,.0f}",
            "Gross profit (AED)": "{:,.0f}",
            "EBIT (AED)": "{:,.0f}",
            "EBIT margin (%)": "{:,.1f}",
        }),
        use_container_width=True
    )

    fig_sens = px.line(
        df_sens,
        x="Scenario",
        y=["Total revenue (AED)", "Gross profit (AED)", "EBIT (AED)"],
        markers=True,
        title="Impact of Adoption Rate on Revenue, Gross Profit, and EBIT"
    )
    st.plotly_chart(fig_sens, use_container_width=True)

    st.markdown(
        """
        💡 Use this section in your pitch to show investors how **sensitive profitability is to adoption**.
        You can argue that even modest adoption rates in Dubai's delivery ecosystem can generate
        meaningful EBIT once fixed costs are covered.
        """
    )
