# NOORSOL Dubai Financial Dashboard

This repository contains a Streamlit-based financial dashboard for **NOORSOL**, a solar-powered smart delivery and outdoor box concept targeting **Dubai's delivery ecosystem and outdoor lifestyle market**.

The dashboard is designed to support an MBA/business-school pitch and early-stage investor conversations. It allows you to:

- Present **raw market data** (delivery-bike base, implied annual bag demand).
- Adjust **core assumptions** (prices, COGS, adoption rates, fixed costs).
- Run **scenario analysis** (Pessimistic, Base, Optimistic).
- View **Pilot and Year 1 P&L** for B2B (retrofit boxes) and B2C (NOORSOL MOVE).
- Perform **breakeven analysis** based on contribution per unit.
- Explore a **sensitivity analysis** of different B2B adoption rates (15%, 25%, 40%).

## 🔧 Files

- `app.py` – main Streamlit application.
- `requirements.txt` – Python dependencies.
- `README.md` – this documentation.

## 🚀 How to Run Locally

1. **Clone** this repository or download & unzip the project folder.

2. In a terminal/command prompt, navigate to the project folder:

   ```bash
   cd noorsol_financial_dashboard
   ```

3. (Optional but recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Streamlit app**:

   ```bash
   streamlit run app.py
   ```

6. Open the URL that appears in your terminal (usually `http://localhost:8501`) in your browser.

## 🧮 What You Can Do in the Dashboard

### 1. Adjust Core Assumptions
Use the left sidebar to set:

- Estimated **active delivery bikes in Dubai**.
- Average **bags per bike per year**.
- B2B & B2C **prices and COGS**.
- **Adoption rates** for pessimistic, base, and optimistic scenarios.
- Annual **fixed costs** (salaries, marketing, R&D, ops, other).

### 2. View Raw Data & Assumptions
The **"Raw Data & Assumptions"** tab:

- Summarizes the **implied annual delivery-bag demand**.
- Shows key financial assumption values in a compact table.

### 3. Analyse Pilot & Year 1 P&L
The **"Pilot & Year 1 P&L"** tab lets you:

- Set pilot volumes for B2B and B2C.
- See pilot-phase revenue and gross profit.
- Specify Year 1 B2C volumes per scenario.
- Compare total revenue, gross profit, and EBIT across Pessimistic, Base, and Optimistic cases.

### 4. Explore Breakeven
The **"Breakeven Analysis"** tab:

- Lets you select a scenario.
- Computes **contribution per unit** and **breakeven units**.
- Plots **cumulative profit vs. units sold**.

### 5. Run Sensitivity Analysis
The **"Sensitivity Analysis"** tab:

- Fixes a single B2C unit assumption.
- Varies B2B adoption rates (15%, 25%, 40% of annual bag demand).
- Shows how **revenue, gross profit, and EBIT** change with adoption.

Use this in your pitch to demonstrate how even modest adoption of NOORSOL in Dubai can lead to attractive financial outcomes.

## 🌍 Notes

- All numbers are designed as **smart guesstimates** focused on **Dubai**.  
- You can update assumptions dynamically as you gather real data from pilots or interviews with delivery platforms.
- This dashboard is meant to be a **living financial model** that evolves with your startup.

## 📫 Contact

You can customise this further by adding:
- Cash-flow projections
- Capex & depreciation modelling
- Multi-country expansions (e.g., Abu Dhabi, Sharjah)

Happy pitching with **NOORSOL**! 🚀
