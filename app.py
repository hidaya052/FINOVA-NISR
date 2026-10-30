import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Finova — Financial Inclusion & Poverty Dashboard",
    page_icon="🇷🇼",
    layout="wide"
)

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    national = pd.read_csv(DATA_DIR / "national_indicators.csv")
    vup = pd.read_csv(DATA_DIR / "vup_beneficiaries.csv")
    district = pd.read_csv(DATA_DIR / "district_poverty.csv")
    return national, vup, district

national_df, vup_df, district_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("Finova")
st.sidebar.caption("Financial Inclusion & Poverty Dynamics in Rwanda")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 National Overview",
        "🗺️ District Vulnerability Map",
        "🛡️ Social Protection (VUP)",
        "💡 Policy Insights",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Data sources: EICV7 2023/24, VUP Thematic Report 2023/24, "
    "FinScope 2024 (NISR). Prototype for NISR 2026 Big Data Hackathon."
)

# ---------- PAGE 1: NATIONAL OVERVIEW ----------
if page == "🏠 National Overview":
    st.title("🇷🇼 Finova — National Overview")
    st.markdown(
        "An integrated view of **financial inclusion**, **poverty**, and "
        "**social protection** outcomes in Rwanda, built on NISR data."
    )

    def get(indicator):
        return national_df.loc[national_df["indicator"] == indicator, "value"].values[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monetary Poverty", f"{get('Monetary poverty rate')}%", "EICV7 2023/24")
    c2.metric("Financial Inclusion", f"{get('Financial inclusion (overall)')}%", "FinScope 2024")
    c3.metric("Fully Excluded Adults", f"{int(get('Financially excluded adults')):,}", "FinScope 2024")
    c4.metric("VUP Households in Poverty", f"{get('VUP households in poverty')}%", "VUP 2023/24")

    st.markdown("---")
    st.subheader("Poverty: Rural vs Urban")

    rural = get("Rural poverty rate")
    urban = get("Urban poverty rate")
    fig = go.Figure(data=[
        go.Bar(name="Poverty rate (%)", x=["Rural", "Urban"], y=[rural, urban],
               marker_color=["#d62728", "#1f77b4"])
    ])
    fig.update_layout(yaxis_title="Poverty rate (%)", height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"Rural poverty (**{rural}%**) remains nearly double urban poverty "
        f"(**{urban}%**). Financial exclusion follows the same geography: "
        f"the vast majority of the ~316,000 fully excluded adults live in rural areas."
    )

    st.markdown("---")
    st.subheader("Key National Indicators")
    st.dataframe(
        national_df[["indicator", "value", "unit", "year", "source"]],
        use_container_width=True,
        hide_index=True,
    )

# ---------- PAGE 2: DISTRICT MAP ----------
elif page == "🗺️ District Vulnerability Map":
    st.title("🗺️ District Vulnerability Map")
    st.markdown(
        "Districts ranked by poverty rate. Use this to target financial "
        "inclusion and social protection interventions to the highest-need areas."
    )

    province = st.selectbox(
        "Filter by province",
        ["All"] + sorted(district_df["province"].unique().tolist()),
    )
    df = district_df if province == "All" else district_df[district_df["province"] == province]
    df = df.sort_values("poverty_rate_pct", ascending=True)

    fig = px.bar(
        df,
        x="poverty_rate_pct",
        y="district",
        orientation="h",
        color="poverty_rate_pct",
        color_continuous_scale="Reds",
        labels={"poverty_rate_pct": "Poverty rate (%)", "district": ""},
    )
    fig.update_layout(height=max(400, 22 * len(df)), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    top5 = district_df.nlargest(5, "poverty_rate_pct")[["district", "province", "poverty_rate_pct"]]
    st.subheader("Top 5 highest-poverty districts")
    st.dataframe(top5, use_container_width=True, hide_index=True)

# ---------- PAGE 3: VUP ----------
elif page == "🛡️ Social Protection (VUP)":
    st.title("🛡️ Social Protection — VUP Beneficiaries")
    st.markdown(
        "Vision 2020 Umurenge Programme (VUP) beneficiaries by component "
        "and poverty status. **41% of VUP households remain in poverty** — "
        "the core gap Finova is designed to help close."
    )

    fig = px.bar(
        vup_df,
        x="component",
        y="share_pct",
        color="poverty_status",
        barmode="group",
        labels={"share_pct": "Share (%)", "component": "VUP component"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Interpretation")
    st.markdown(
        """
        - **Direct Support** and **Public Works** households both show high
          poverty incidence — transfers reduce immediate hardship but do not
          systematically break the poverty cycle.
        - **Coverage remains limited** relative to need, and targeting errors
          (inclusion of non-poor / exclusion of poor) persist in some sectors.
        - **Benefit adequacy** is constrained by payment delays and limited
          public-works days, especially for women with care responsibilities.
        """
    )

# ---------- PAGE 4: POLICY INSIGHTS ----------
else:
    st.title("💡 Policy Insights & Recommendations")

    st.subheader("1. Close the financial inclusion–social protection gap")
    st.markdown(
        "Automatically open **transactional mobile-money accounts** for all "
        "VUP beneficiaries, enabling digital transfer receipt and optional "
        "e-payment rails. Immediately links 316,000 excluded adults into the "
        "formal financial system."
    )

    st.subheader("2. Layer micro-savings and micro-insurance on transfers")
    st.markdown(
        "Introduce **flexible goal-based micro-savings** (school fees, health "
        "shocks) and **simple parametric micro-insurance** for vulnerable "
        "households, co-designed with SACCOs and mobile-money operators."
    )

    st.subheader("3. Financial capability + peer support")
    st.markdown(
        "Community-based training via agents, MDCs and local leaders — "
        "focused on budgeting, digital skills and product use for "
        "low-education and PWD groups."
    )

    st.subheader("4. Real-time poverty monitoring dashboard")
    st.markdown(
        "Combine NISR financial-cycle indicators with social-protection "
        "administrative data to track inclusion, usage and resilience "
        "outcomes. **Finova IS this dashboard.**"
    )

    st.markdown("---")
    st.caption(
        "Finova • NISR 2026 Big Data Hackathon • Track 2: Financial Inclusion "
        "& Poverty Reduction • Prototype build"
    )
