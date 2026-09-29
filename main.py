import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Outpatient Data Dashboard",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("outpatient_dashboard_data.csv")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


df = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🏥 Outpatient Data Dashboard")

st.markdown(
    "### Interactive analysis of outpatient records"
)

st.markdown(
    "Use the filters in the sidebar to explore patient visits, "
    "diagnoses, demographics, repeat visits and service utilization."
)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

# Month
months = sorted(df["Month"].dropna().unique())

selected_months = st.sidebar.multiselect(
    "Month",
    options=months,
    default=months
)

# Category
categories = sorted(df["Category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Patient Category",
    options=categories,
    default=categories
)

# Gender
genders = sorted(df["Gender"].dropna().unique())

selected_genders = st.sidebar.multiselect(
    "Gender",
    options=genders,
    default=genders
)

# Diagnosis
diagnoses = sorted(
    df["Diagnosis"]
    .dropna()
    .astype(str)
    .unique()
)

selected_diagnoses = st.sidebar.multiselect(
    "Diagnosis",
    options=diagnoses,
    default=[]
)

# Revisit
revisit_options = sorted(
    df["Revisit"]
    .dropna()
    .astype(str)
    .unique()
)

selected_revisit = st.sidebar.multiselect(
    "Visit Type",
    options=revisit_options,
    default=revisit_options
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    df["Month"].isin(selected_months)
    & df["Category"].isin(selected_categories)
    & df["Gender"].isin(selected_genders)
    & df["Revisit"].isin(selected_revisit)
].copy()

# Diagnosis filter only when selected
if selected_diagnoses:
    filtered_df = filtered_df[
        filtered_df["Diagnosis"].isin(selected_diagnoses)
    ]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_visits = len(filtered_df)

unique_patients = filtered_df["Patient_ID"].nunique()

repeat_patients = (
    filtered_df.groupby("Patient_ID")
    .size()
    .gt(1)
    .sum()
)

unique_diagnoses = filtered_df["Diagnosis"].nunique()

# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------

st.subheader("Key Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Outpatient Visits",
    f"{total_visits:,}"
)

col2.metric(
    "Unique Patients",
    f"{unique_patients:,}"
)

col3.metric(
    "Patients with 2+ Records",
    f"{repeat_patients:,}"
)

col4.metric(
    "Unique Diagnoses",
    f"{unique_diagnoses:,}"
)

st.divider()

# --------------------------------------------------
# MONTHLY VISITS
# --------------------------------------------------

st.subheader("📈 Outpatient Visits Over Time")

monthly = (
    filtered_df
    .groupby("Month")
    .size()
    .reset_index(name="Visits")
)

monthly = monthly.sort_values("Month")

fig_monthly = px.line(
    monthly,
    x="Month",
    y="Visits",
    markers=True,
    title="Monthly Outpatient Visits"
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Number of Visits"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# --------------------------------------------------
# TOP DIAGNOSES
# --------------------------------------------------

st.subheader("🦠 Top 10 Diagnoses")

diagnosis_counts = (
    filtered_df["Diagnosis"]
    .dropna()
    .astype(str)
    .str.strip()
)

diagnosis_counts = (
    diagnosis_counts[
        diagnosis_counts != ""
    ]
    .value_counts()
    .head(10)
    .reset_index()
)

diagnosis_counts.columns = [
    "Diagnosis",
    "Visits"
]

fig_diagnosis = px.bar(
    diagnosis_counts,
    x="Visits",
    y="Diagnosis",
    orientation="h",
    title="Top 10 Diagnoses"
)

fig_diagnosis.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(
    fig_diagnosis,
    use_container_width=True
)

# --------------------------------------------------
# PATIENT CATEGORY
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    category_counts = (
        filtered_df["Category"]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Visits"
    ]

    fig_category = px.bar(
        category_counts,
        x="Category",
        y="Visits",
        title="Visits by Patient Category"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

# --------------------------------------------------
# GENDER
# --------------------------------------------------

with col2:

    gender_counts = (
        filtered_df["Gender"]
        .value_counts()
        .reset_index()
    )

    gender_counts.columns = [
        "Gender",
        "Visits"
    ]

    fig_gender = px.bar(
        gender_counts,
        x="Gender",
        y="Visits",
        title="Visits by Gender"
    )

    st.plotly_chart(
        fig_gender,
        use_container_width=True
    )

# --------------------------------------------------
# AGE GROUP
# --------------------------------------------------

st.subheader("👥 Age Distribution")

age_counts = (
    filtered_df["Age_Group"]
    .dropna()
    .value_counts()
    .sort_index()
    .reset_index()
)

age_counts.columns = [
    "Age Group",
    "Visits"
]

fig_age = px.bar(
    age_counts,
    x="Age Group",
    y="Visits",
    title="Outpatient Visits by Age Group"
)

st.plotly_chart(
    fig_age,
    use_container_width=True
)

# --------------------------------------------------
# REPEAT VISITS
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    revisit_counts = (
        filtered_df["Revisit"]
        .value_counts()
        .reset_index()
    )

    revisit_counts.columns = [
        "Visit Type",
        "Visits"
    ]

    fig_revisit = px.bar(
        revisit_counts,
        x="Visit Type",
        y="Visits",
        title="Repeat Visit Records"
    )

    st.plotly_chart(
        fig_revisit,
        use_container_width=True
    )

# --------------------------------------------------
# SERVICE UTILIZATION
# --------------------------------------------------

with col2:

    status_counts = (
        filtered_df["Status"]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace({
            "NAN": "Not Recorded",
            "": "Not Recorded"
        })
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Service",
        "Visits"
    ]

    fig_status = px.bar(
        status_counts,
        x="Visits",
        y="Service",
        orientation="h",
        title="Service Utilization"
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )

# --------------------------------------------------
# DIAGNOSIS BY GENDER
# --------------------------------------------------

st.subheader("⚕️ Top Diagnoses by Gender")

top_gender_diagnoses = (
    filtered_df[
        filtered_df["Diagnosis"].notna()
    ]
    .groupby(["Diagnosis", "Gender"])
    .size()
    .reset_index(name="Visits")
)

top_diagnosis_names = (
    filtered_df["Diagnosis"]
    .dropna()
    .value_counts()
    .head(10)
    .index
)

top_gender_diagnoses = top_gender_diagnoses[
    top_gender_diagnoses["Diagnosis"].isin(
        top_diagnosis_names
    )
]

fig_gender_diagnosis = px.bar(
    top_gender_diagnoses,
    x="Diagnosis",
    y="Visits",
    color="Gender",
    barmode="group",
    title="Top 10 Diagnoses by Gender"
)

fig_gender_diagnosis.update_layout(
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig_gender_diagnosis,
    use_container_width=True
)

# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------

st.subheader("📋 Filtered Patient Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Outpatient Data Analysis Dashboard | ENGAGE Data Science Project"
)