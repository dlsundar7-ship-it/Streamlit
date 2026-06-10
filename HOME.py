import streamlit as st
import base64


st.set_page_config(
    page_title="Data Operations Portal",
    layout="wide"
)

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 240px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)




# Sidebar Logo
# with st.sidebar:
#     st.image(
#         r"D:\NRL\03_NRoot_Workbench\Vimalesh\Streamlit\LOGO.png",
#         width=150
#     )



# Custom Styling

st.markdown("""
<style>
.module-card {
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    background-color: rgba(255,255,255,0.02);
    height: 140px;
}

.module-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
}

.module-desc {
    font-size: 14px;
    color: #BFC7D5;
}
</style>
""", unsafe_allow_html=True)


# Header

st.title("ETL Control Center")

# st.caption("Enterprise Data Integration and Monitoring Platform")

st.markdown("")


# Module Overview

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">ODBC Configuration</div>
        <div class="module-desc">
            Configure and test ODBC connection settings.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="module-card">
        <div class="module-title">Execution Summary</div>
        <div class="module-desc">
            View SQL Agent job execution history, duration, and processing status.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">SQL Server Agent Jobs</div>
        <div class="module-desc">
            Monitor and manage SQL Server Agent jobs, schedules, and execution activities.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="module-card">
        <div class="module-title">Control Table</div>
        <div class="module-desc">
            Enable or disable source table  data loads.
        </div>
    </div>
    """, unsafe_allow_html=True)

