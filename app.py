
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Tribe Hotel | Board BI Dashboard", page_icon="📊", layout="wide")

st.title("Tribe Hotel — Board Business Intelligence Dashboard")
st.caption("Decision-support dashboard based on the Tribe Hotel Board Presentation. Financial and workforce inputs are editable assumptions.")

# ---------------- Sidebar inputs ----------------
st.sidebar.header("Board Inputs")

employees = st.sidebar.number_input("Total employees", min_value=0, value=150, step=1)
monthly_payroll = st.sidebar.number_input("Monthly payroll (KES)", min_value=0.0, value=15000000.0, step=100000.0)
monthly_revenue = st.sidebar.number_input("Monthly revenue (KES)", min_value=0.0, value=50000000.0, step=100000.0)
monthly_service_charge = st.sidebar.number_input("Monthly service charge pool (KES)", min_value=0.0, value=5000000.0, step=100000.0)
outsourced_monthly_cost = st.sidebar.number_input("Current monthly cost of functions proposed for outsourcing (KES)", min_value=0.0, value=3000000.0, step=100000.0)
outsourced_provider_cost = st.sidebar.number_input("Estimated outsourced provider monthly cost (KES)", min_value=0.0, value=2400000.0, step=100000.0)

st.sidebar.subheader("Salary / CBA")
entry_current = st.sidebar.number_input("Entry-level current increment %", min_value=0.0, value=5.0, step=0.5)
general_current = st.sidebar.number_input("General-wage current increment %", min_value=0.0, value=7.0, step=0.5)
entry_proposed = st.sidebar.number_input("Entry-level proposed increment %", min_value=0.0, value=2.5, step=0.5)
general_proposed = st.sidebar.number_input("General-wage proposed increment %", min_value=0.0, value=3.5, step=0.5)

st.sidebar.subheader("Service Charge")
org_share = st.sidebar.number_input("Organization share %", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
mgmt_share = st.sidebar.number_input("Management share %", min_value=0.0, max_value=100.0, value=5.0, step=1.0)
employee_share = 100.0 - org_share - mgmt_share

# ---------------- Calculations ----------------
payroll_ratio = monthly_payroll / monthly_revenue * 100 if monthly_revenue else 0
outsourcing_saving = max(0, outsourced_monthly_cost - outsourced_provider_cost)
annual_outsourcing_saving = outsourcing_saving * 12
current_salary_factor = (1 + entry_current/100)
proposed_salary_factor = (1 + entry_proposed/100)
entry_delta = entry_current - entry_proposed
general_delta = general_current - general_proposed
employee_service_charge = monthly_service_charge * employee_share/100
org_service_charge = monthly_service_charge * org_share/100
mgmt_service_charge = monthly_service_charge * mgmt_share/100

# ---------------- Tabs ----------------
tabs = st.tabs([
    "Executive Dashboard", "CBA & Salary", "Service Charge",
    "Outsourcing", "Manpower", "Legal Risk", "Roadmap", "Data Export"
])

with tabs[0]:
    st.subheader("Executive Board Dashboard")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Employees", f"{employees:,}")
    c2.metric("Labour Cost / Revenue", f"{payroll_ratio:.1f}%")
    c3.metric("Annual Outsourcing Saving", f"KES {annual_outsourcing_saving:,.0f}")
    c4.metric("Employee Service Charge", f"KES {employee_service_charge:,.0f}")

    st.markdown("### Strategic decision signals")
    signals = pd.DataFrame({
        "Area":["CBA / Salary","Service Charge","Outsourcing","Manpower"],
        "Current / baseline":[
            f"{entry_current:.1f}% entry; {general_current:.1f}% general",
            f"{org_share:.0f}% org / {mgmt_share:.0f}% management / {employee_share:.0f}% employees",
            f"KES {outsourced_monthly_cost:,.0f} monthly",
            f"{employees:,} employees"
        ],
        "Proposed / target":[
            f"{entry_proposed:.1f}% entry; {general_proposed:.1f}% general",
            "20% organization / 5% management / 75% employees (source proposal)",
            f"KES {outsourced_provider_cost:,.0f} monthly",
            "Evidence-based rationalization; non-compulsory routes first"
        ]
    })
    st.dataframe(signals, use_container_width=True, hide_index=True)

    st.info("Source position: proposed changes should proceed through appropriate legal, contractual and consultative processes rather than unilateral variation.")

with tabs[1]:
    st.subheader("CBA & Salary Analytics")
    col1,col2 = st.columns(2)
    salary_df = pd.DataFrame({
        "Category":["Entry level","General wages"],
        "Current %":[entry_current,general_current],
        "Proposed %":[entry_proposed,general_proposed]
    })
    with col1:
        fig = px.bar(salary_df, x="Category", y=["Current %","Proposed %"], barmode="group",
                     title="Current vs Proposed Salary Review Percentages")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        delta_df = salary_df.copy()
        delta_df["Reduction (pp)"] = delta_df["Current %"] - delta_df["Proposed %"]
        st.dataframe(delta_df, use_container_width=True, hide_index=True)
        st.metric("Entry-level reduction", f"{entry_delta:.1f} percentage points")
        st.metric("General-wage reduction", f"{general_delta:.1f} percentage points")

    st.markdown("**Board considerations from the report:** economic sustainability, good-faith bargaining, disclosure of relevant information, consultation, written notification, and avoidance of unilateral variation.")

with tabs[2]:
    st.subheader("Service Charge Analytics")
    shares = pd.DataFrame({
        "Recipient":["Organization","Management","Employees"],
        "Share %":[org_share,mgmt_share,employee_share],
        "Monthly KES":[org_service_charge,mgmt_service_charge,employee_service_charge]
    })
    col1,col2 = st.columns(2)
    with col1:
        fig = px.pie(shares, names="Recipient", values="Share %", title="Service Charge Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(shares, use_container_width=True, hide_index=True)
        st.metric("Total pool", f"KES {monthly_service_charge:,.0f}")
    st.caption("The source report proposes 20% retained by the organization, 5% to management, and the remainder to employees.")

with tabs[3]:
    st.subheader("Outsourcing Business Case")
    funcs = st.multiselect(
        "Functions identified in the report",
        ["Laundry","Cleaning of common areas","Security"],
        default=["Laundry","Cleaning of common areas","Security"]
    )
    col1,col2,col3 = st.columns(3)
    col1.metric("Current monthly cost", f"KES {outsourced_monthly_cost:,.0f}")
    col2.metric("Estimated provider cost", f"KES {outsourced_provider_cost:,.0f}")
    col3.metric("Monthly saving", f"KES {outsourcing_saving:,.0f}")
    st.metric("Projected annual saving", f"KES {annual_outsourcing_saving:,.0f}")

    risk = pd.DataFrame({
        "Risk":["Continuing employment characterization","Unfair labour practice / unlawful transfer",
                "Discriminatory outsourcing","Union / CBA challenge"],
        "Mitigation":["Genuinely independent contractor with own management, systems and capital",
                      "Express employee acceptance and settlement of accrued obligations",
                      "Consistent treatment of comparable roles and documented rationale",
                      "Prior union consultation and negotiated CBA amendments where required"]
    })
    st.dataframe(risk, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Manpower Rationalization")
    rooms = st.number_input("Hotel rooms (optional input)", min_value=0, value=137, step=1)
    staff_per_room = employees / rooms if rooms else 0
    c1,c2,c3 = st.columns(3)
    c1.metric("Staff per room", f"{staff_per_room:.2f}")
    c2.metric("Monthly labour cost", f"KES {monthly_payroll:,.0f}")
    c3.metric("Labour cost / revenue", f"{payroll_ratio:.1f}%")

    scenario = pd.DataFrame({
        "Scenario":["Current","5% reduction","10% reduction","15% reduction","20% reduction"],
        "Employees":[employees, round(employees*.95), round(employees*.90), round(employees*.85), round(employees*.80)],
        "Annual payroll saving":[0, monthly_payroll*.05*12, monthly_payroll*.10*12, monthly_payroll*.15*12, monthly_payroll*.20*12]
    })
    fig = px.bar(scenario, x="Scenario", y="Annual payroll saving", title="Illustrative Payroll-Saving Scenarios")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(scenario, use_container_width=True, hide_index=True)
    st.warning("Illustrative scenario only. The source report calls for an evidence-based business case and prioritizes natural attrition, voluntary separation, genuine redundancy, or mutually agreed exits before compulsory routes.")

with tabs[5]:
    st.subheader("Legal & Industrial Relations Risk Matrix")
    risk_df = pd.DataFrame({
        "Issue":["Unilateral change to CBA / employment terms","Outsourcing without employee acceptance",
                 "Discriminatory outsourcing","Service charge changed without consultation",
                 "Misclassification of management employees","Fixed-term contracts used to circumvent CBA"],
        "Probability":["High","High","Medium","Medium","Medium","Medium"],
        "Impact":["High","High","High","High","High","High"],
        "Priority Score":[9,9,6,6,6,6],
        "Primary mitigation":["Consult, negotiate, document and register agreed changes",
                              "Settle obligations and obtain express acceptance",
                              "Apply consistent criteria and document rationale",
                              "Consult and amend contractual/CBA framework",
                              "Functional job analysis; consult and document",
                              "Use fixed-term model lawfully and avoid systematic circumvention"]
    })
    st.dataframe(risk_df, use_container_width=True, hide_index=True)
    fig = px.scatter(risk_df, x="Probability", y="Impact", size="Priority Score",
                     hover_name="Issue", title="Qualitative Risk Map")
    st.plotly_chart(fig, use_container_width=True)

with tabs[6]:
    st.subheader("Implementation Roadmap")
    roadmap = pd.DataFrame({
        "Step":[1,2,3,4,5,6,7,8],
        "Action":[
            "Give union 90 days' notice of proposed amendments",
            "Negotiate on behalf of the Association with KUDHEIHA",
            "Register agreed negotiations",
            "Process any redundancy in line with Separation and Placement Agreement",
            "Draft/update internal policies",
            "Draft new service-provider agreements",
            "Conduct HR Audit",
            "Participate in union, employee and management discussions as required"
        ],
        "Status":["Not started"]*8
    })
    edited = st.data_editor(roadmap, use_container_width=True, hide_index=True,
                            column_config={"Status": st.column_config.SelectboxColumn(
                                options=["Not started","In progress","Complete","At risk"]
                            )})
    completed = (edited["Status"]=="Complete").sum()
    progress = completed/len(edited)*100
    st.progress(progress/100, text=f"Roadmap completion: {progress:.0f}%")
    st.caption("The source report also calls for alignment of employment contracts, HR manuals and internal policies with negotiated CBA, service-charge and outsourcing changes.")

with tabs[7]:
    st.subheader("Board Data Export")
    export = pd.DataFrame({
        "Metric":["Employees","Monthly Payroll","Monthly Revenue","Labour Cost / Revenue",
                  "Monthly Service Charge Pool","Organization Service Charge","Management Service Charge",
                  "Employee Service Charge","Current Outsourcing Cost","Provider Cost",
                  "Annual Outsourcing Saving","Entry Current %","Entry Proposed %",
                  "General Current %","General Proposed %"],
        "Value":[employees,monthly_payroll,monthly_revenue,payroll_ratio,monthly_service_charge,
                 org_service_charge,mgmt_service_charge,employee_service_charge,
                 outsourced_monthly_cost,outsourced_provider_cost,annual_outsourcing_saving,
                 entry_current,entry_proposed,general_current,general_proposed]
    })
    st.dataframe(export, use_container_width=True, hide_index=True)
    csv = export.to_csv(index=False).encode("utf-8")
    st.download_button("Download Board KPI CSV", csv, "tribe_hotel_board_kpis.csv", "text/csv")

st.divider()
st.caption("Prepared as a decision-support prototype from the uploaded Tribe Hotel Board Presentation. Legal conclusions should be verified against the applicable current law and official records before external use.")
