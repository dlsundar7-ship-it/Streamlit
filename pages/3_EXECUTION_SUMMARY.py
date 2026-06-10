import streamlit as st
import pandas as pd
import pyodbc


st.set_page_config(
    page_title="Execution Summary",
    layout="wide"
)


st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 250px !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image(
        r"D:\NRL\03_NRoot_Workbench\Vimalesh\Streamlit\LOGO.png",
        width=150
    )


    
st.markdown("""
<style>
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


def get_sql_connection():

    return pyodbc.connect(
        (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=WIN-7QUI0BGC7TU;"
            "DATABASE=Control_Master;"
            "Trusted_Connection=yes;"
        )
    )


st.title("Execution Summary")
st.caption("Monitor ETL job execution status and duration")

from datetime import datetime, timedelta, time


col1, col2 = st.columns(2)


with col1:

    from_date = st.date_input(
        "From Date",
        datetime.today().date(),
        max_value=datetime.today().date()
    )

with col2:

    to_date = st.date_input(
        "To Date",
        datetime.today().date(),
        max_value=datetime.today().date()
    )


window_start = datetime.combine(
    from_date - timedelta(days=1),
    time(21, 0, 0)
)

window_end = datetime.combine(
    to_date,
    time(19, 0, 0)
)

conn = get_sql_connection()



query = f"""
WITH BASE AS
(
    SELECT
        CAST(DATEADD(HOUR,3,START_TIME) AS DATE) AS BUSINESS_DATE,
        JOB_NAME,
        MIN(START_TIME) AS START_TIME,
        MAX(END_TIME) AS END_TIME,
        STATUS
    FROM Control_Master.CONTROL.JOB_HISTORY
    WHERE
        START_TIME >= '{window_start:%Y-%m-%d %H:%M:%S}'
        AND START_TIME <= '{window_end:%Y-%m-%d %H:%M:%S}'
        AND
        (
            PROCEDURE_NAME LIKE 'PY%'
            OR
            (
                PROCEDURE_NAME NOT LIKE 'PY%'
                AND PROCEDURE_NAME NOT IN
                (
                    'SP_MDS_MASTERS',
                    'SP_CONTROL_ALL_TABLES',
                    'SP_CUSTOM_DATE_DIMENSION', 
                    'SP_RDL_BALANCE_SHEET_PERFORMANCE',
                    'SP_BALANCE_SHEET_ADJUSTMENT',
                    'SP_BALANCE_SHEET_ADJUSTMENT',
                    'SP_RDL_BALANCE_SHEET',
                    'SP_PDO_BALANCE_SHEET',
                    'SP_RDL_PROFIT_AND_LOSS_PERFORMANCE',
                    'SP_RDL_PROFIT_AND_LOSS',
                    'SP_PDO_PROFIT_AND_LOSS'
                )
            )
        )
    GROUP BY
        CAST(DATEADD(HOUR,3,START_TIME) AS DATE),
        JOB_NAME,
        STATUS
)

SELECT
    ROW_NUMBER() OVER
    (
        ORDER BY BUSINESS_DATE, START_TIME
    ) AS S_NO,
    BUSINESS_DATE,
    JOB_NAME,
    START_TIME,
    END_TIME,
    CONVERT(
        VARCHAR(8),
        DATEADD(
            SECOND,
            DATEDIFF(
                SECOND,
                START_TIME,
                END_TIME
            ),
            0
        ),
        108
    ) AS DURATION,
    STATUS
FROM BASE
ORDER BY
    BUSINESS_DATE,
    START_TIME
"""


df = pd.read_sql(query, conn)

conn.close()


st.subheader("Execution Summary")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


