import streamlit as st
import pandas as pd
import pyodbc
import time


st.set_page_config(
    page_title="Table Load Control",
    layout="wide"
)


st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 250px !important;
}
</style>
""", unsafe_allow_html=True)

# with st.sidebar:
#     st.image(
#         r"D:\NRL\03_NRoot_Workbench\Vimalesh\Streamlit\LOGO.png",
#         width=150
#     )

    
st.markdown("""
<style>
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)




st.markdown("""
<style>
div[data-testid="stTextInput"] input {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

st.title("Table Load Control")



st.markdown("""
<style>
[data-baseweb="select"] input {
    cursor: pointer !important;
}

[data-baseweb="select"] div {
    cursor: pointer !important;
}

[data-baseweb="select"] span {
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)




CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=WIN-7QUI0BGC7TU;"
    "DATABASE=NRoots_Internal;"
    "Trusted_Connection=yes;"
)





DEFAULT_QUERY = """
SELECT *
FROM CONTROL.TABLE_LOAD_CONTROL
ORDER BY S_NO
"""



# @st.cache_data(ttl=60)
def fetch_data(sql_query):

    connection = pyodbc.connect(
        CONNECTION_STRING
    )

    dataframe = pd.read_sql(
        sql_query,
        connection
    )

    connection.close()

    return dataframe


if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0


# Session State Initialization


if "table_load_data" not in st.session_state:
    # Load default data only once
    st.session_state.table_load_data = (fetch_data(DEFAULT_QUERY))


if "last_executed_query" not in st.session_state:
    st.session_state.last_executed_query = (DEFAULT_QUERY)


st.subheader("Filters")

filter_data = st.session_state.table_load_data.copy()

if st.session_state.get("table_desc_filter"):
    filter_data = filter_data[
        filter_data["TABLE_DESCRIPTION"].isin(
            st.session_state.table_desc_filter
        )
    ]

if st.session_state.get("table_name_filter"):
    filter_data = filter_data[
        filter_data["TABLE_NAME"].isin(
            st.session_state.table_name_filter
        )
    ]

if st.session_state.get("table_type_filter"):
    filter_data = filter_data[
        filter_data["TABLE_TYPE"].fillna("NA")
        .astype(str)
        .str.strip()
        .replace("", "NA")
        .isin(st.session_state.table_type_filter)
    ]

if st.session_state.get("report_module_filter"):
    filter_data = filter_data[
        filter_data["REPORT_MODULE"].fillna("NA")
        .astype(str)
        .str.strip()
        .replace("", "NA")
        .isin(st.session_state.report_module_filter)
    ]

with st.container(border=True):

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        selected_table_desc = st.multiselect(
            "Table Description",
            sorted(
                filter_data["TABLE_DESCRIPTION"]
                .fillna("NA")
                .astype(str)
                .str.strip()
                .replace("", "NA")
                .unique()
                .tolist()
            ),
            key="table_desc_filter",
            placeholder="Select Table Description"
        )

    with filter_col2:


        selected_table_name = st.multiselect(
            "Table Name",
            sorted(
                filter_data["TABLE_NAME"]
                .fillna("NA")
                .astype(str)
                .str.strip()
                .replace("", "NA")
                .unique()
                .tolist()
            ),
            key="table_name_filter",
            placeholder="Select Table Name"
        )


    filter_col3, filter_col4 = st.columns(2)

    with filter_col3:

        selected_table_type = st.multiselect(
            "Table Type",
            sorted(
                filter_data["TABLE_TYPE"]
                .fillna("NA")
                .astype(str)
                .str.strip()
                .replace("", "NA")
                .unique()
                .tolist()
            ),
            key="table_type_filter",
            placeholder="Select Table Type"
        )

    with filter_col4:

        selected_report_module = st.multiselect(
            "Report Module",
            sorted(
                filter_data["REPORT_MODULE"]
                .fillna("NA")
                .astype(str)
                .str.strip()
                .replace("", "NA")
                .unique()
                .tolist()
            ),
            key="report_module_filter",
            placeholder="Select Report Module"
        )
        
        print(selected_report_module)
        


st.divider()


st.subheader("Control table")
with st.container(border=True):

    table_load_data = (st.session_state.table_load_data)

    table_load_data = table_load_data.copy()

    if selected_table_desc:
        table_load_data = table_load_data[
            table_load_data["TABLE_DESCRIPTION"].isin(selected_table_desc)
        ]

    if selected_table_name:
        table_load_data = table_load_data[
            table_load_data["TABLE_NAME"].isin(selected_table_name)
        ]
                

    if selected_table_type:
        table_load_data = table_load_data[
            table_load_data["TABLE_TYPE"].fillna("NA")
            .astype(str)
            .str.strip()
            .replace("", "NA")
            .isin(selected_table_type)
        ]

    if selected_report_module:
        table_load_data = table_load_data[
            table_load_data["REPORT_MODULE"].fillna("NA")
            .astype(str)
            .str.strip()
            .replace("", "NA")
            .isin(selected_report_module)
        ]


    table_load_data["ENABLED"] = (table_load_data["LOAD_STATUS"] == 1)


    save_col, cancel_col = st.columns(2)

    save_col, cancel_col, _ = st.columns([1, 1, 9])

    with save_col:
        save_changes = st.button("Save Changes", type="primary")

    with cancel_col:
        cancel_changes = st.button("Cancel")


    if cancel_changes:

        st.session_state.table_load_data = fetch_data(
            DEFAULT_QUERY
        )

        st.session_state.editor_version += 1

        st.rerun()


    original_data = table_load_data.copy()

    disabled_columns = [
        col
        for col in table_load_data.columns
        if col not in ["ENABLED"]
    ]

    edited_data = st.data_editor(
        table_load_data.drop(columns=["LOAD_STATUS"]), 
        key=f"control_table_editor_{st.session_state.editor_version}",
        hide_index=True,
        use_container_width=True,
        disabled=disabled_columns
    )



    if save_changes:

        changed_rows = edited_data[
            edited_data["ENABLED"] !=
            original_data["ENABLED"]
        ]
        
        print('changed_rows', changed_rows)

        connection = pyodbc.connect(
            CONNECTION_STRING,
            autocommit=True
        )

        cursor = connection.cursor()

        enabled_df = changed_rows[
            changed_rows["ENABLED"] == True
        ]

        disabled_df = changed_rows[
            changed_rows["ENABLED"] == False
        ]

        print("enabled_df", enabled_df) 
        print("disabled_df", disabled_df) 

        enabled_tables = enabled_df["TABLE_NAME"].tolist()

        disabled_tables = disabled_df["TABLE_NAME"].tolist()

        if enabled_tables:

            enabled_list = "','".join(enabled_tables)

            cursor.execute(
                f"""
                UPDATE CONTROL.TABLE_LOAD_CONTROL
                SET LOAD_STATUS = 1
                WHERE TABLE_NAME IN ('{enabled_list}')
                """
            )

        if disabled_tables:

            disabled_list = "','".join(disabled_tables)

            cursor.execute(
                f"""
                UPDATE CONTROL.TABLE_LOAD_CONTROL
                SET LOAD_STATUS = 0
                WHERE TABLE_NAME IN ('{disabled_list}')
                """
            )

        if cursor:
            cursor.close()

        if connection:
            connection.close()
            
        if len(enabled_tables) > 0 or len(disabled_tables) > 0:

            st.session_state.table_load_data = fetch_data(
                DEFAULT_QUERY
            )

            st.session_state.editor_version += 1

            st.toast(
                "Changes saved successfully.",
                icon="✅"
            )

            st.rerun()