import streamlit as st
import pyodbc

st.title("SQL Server Connection Test")

try:
    conn = pyodbc.connect(
        (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=128.9.15.28,1433;"
            "DATABASE=NRoots_Internal;"
            "UID=Airflow_User;"
            "PWD=Biuser@2025;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )
    )

    st.success("✅ SQL Server Connected Successfully")

    cursor = conn.cursor()
    cursor.execute("SELECT @@SERVERNAME")

    row = cursor.fetchone()

    st.write("Server Name:")
    st.code(str(row[0]))

    conn.close()

except Exception as e:
    st.error("❌ Connection Failed")
    st.code(str(e))