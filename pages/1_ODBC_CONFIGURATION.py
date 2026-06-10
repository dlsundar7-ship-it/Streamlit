import streamlit as st
import pandas as pd
import pyodbc


st.set_page_config(
    page_title="ODBC Configuration",
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


st.markdown("""
<style>
[data-testid="InputInstructions"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)



def get_sql_connection():
    return pyodbc.connect(
        (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=WIN-7QUI0BGC7TU;"
            "DATABASE=NRoots_Internal;"
            "Trusted_Connection=yes;"
        ),
        autocommit=True
    )


def load_configuration():
    conn = get_sql_connection()
    query = """
    SELECT TOP 1
        ID,
        DSN,
        USERNAME,
        PASSWORD
    FROM dbo.ODBC_CONFIGURATION 
    WHERE IS_ACTIVE = 1
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def save_configuration(dsn, username, password):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        EXEC dbo.SP_ODBC_CONFIGURATION
            @DSN = ?,
            @USERNAME = ?,
            @PASSWORD = ?
        """,
        (dsn, username, password)
    )

    # Remove existing linked server login mapping
    cursor.execute("""
    EXEC master.dbo.sp_droplinkedsrvlogin
        @rmtsrvname = ?,
        @locallogin = NULL
    """, ('TEST',))

    # Add new linked server login mapping
    cursor.execute("""
    EXEC master.dbo.sp_addlinkedsrvlogin
        @rmtsrvname = ?,
        @useself = 'False',
        @locallogin = NULL,
        @rmtuser = ?,
        @rmtpassword = ?
    """, (
        'TEST',
        username,
        password
    ))

    conn.commit()
    cursor.close()
    conn.close()



def test_connection(dsn, username, password):
    conn_str = (
        f"DSN={dsn};"
        f"UID={username};"
        f"PWD={password};"
    )
    conn = pyodbc.connect(conn_str, timeout=5)
    conn.close()

# Initialize session state
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

st.title("ODBC Configuration")

df = load_configuration()

# Main content
if df.empty:
    st.info("No active ODBC configuration found. Please create a new one below.", icon="ℹ️")
    
    with st.container(border=True):
        st.subheader("New Connection Setup")
        
        dsn = st.text_input(
            "DSN",
            placeholder="DSN Name"
        )

        username = st.text_input(
            "Username",
            placeholder="ODBC Username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="ODBC Password"
        )

        
        # Action buttons
        st.divider()
        btn_col1, btn_col2, _ = st.columns([2, 2, 4])
        
        with btn_col1:
            if st.button("Test Connection",  type="secondary", use_container_width=True):

                if not dsn.strip() or not username.strip() or not password.strip():
                    st.warning("Please fill all fields.")
                else:
                    try:
                        test_connection(dsn, username, password)
                        st.toast("✅ ODBC test connection  successful!", )
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")
        
        with btn_col2:
            if st.button("Save Configuration", type="primary", use_container_width=True):
                if not dsn.strip() or not username.strip() or not password.strip():
                    st.warning("Please fill all fields.")
                else:
                    try:
                        save_configuration(dsn, username, password)
                        st.success("Configuration saved successfully!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save: {str(e)}")

else:
    row = df.iloc[0]
    
    st.subheader("Configured Connection")
    
    # Display card for current config
    with st.container(border=True):
        col_info, col_actions = st.columns([3, 1])
        
        with col_info:
            st.markdown(f"### {row['DSN']}")
            st.markdown(f"**Username:** `{row['USERNAME']}`")
            st.markdown(f"**Password:** `{'●' * min(len(row['PASSWORD']), 12)}`")
        
        with col_actions:
            test_btn = st.button(
                "Test",
                key="test_current",
                use_container_width=True
            )

            edit_btn = st.button(
                "Edit",
                key="edit_current",
                use_container_width=True
            )

        if edit_btn:
            st.session_state.edit_mode = True
            st.rerun()
        
        if test_btn:
            try:
                test_connection(
                    row["DSN"],
                    row["USERNAME"],
                    row["PASSWORD"]
                )
                st.toast("ODBC test connection  successful!", icon="✅")
            except Exception as e:
                st.error(str(e))

        # Edit mode
        if st.session_state.edit_mode:
            
            st.divider()
            st.subheader("Edit Connection")

            with st.form("edit_form"):
                new_dsn = st.text_input(
                    "DSN",
                    value=row["DSN"],
                    key="new_dsn"
                )
                new_username = st.text_input(
                    "Username",
                    value=row["USERNAME"],
                    key="new_username"
                )
                new_password = st.text_input(
                    "Password",
                    value=row["PASSWORD"],
                    type="password",
                    key="new_password"
                )
                
                form_col1, form_col2 = st.columns(2)
                
                with form_col1:
                    save_changes = st.form_submit_button(
                        "Save Changes",
                        type="primary",
                        use_container_width=True
                    )
                    # save_changes = st.form_submit_button(
                    #         "Save Changes",
                    #         icon=":material/save:",
                    #         type="primary",
                    #         use_container_width=True
                    #     )
                    
                with form_col2:
                    cancel = st.form_submit_button(
                        "Cancel",
                        use_container_width=True
                    )
                
                    # cancel = st.form_submit_button(
                    #         "Cancel",
                    #         icon=":material/cancel:",
                    #         use_container_width=True
                    #     )
                    
                if save_changes:
                    if not new_dsn.strip() or not new_username.strip() or not new_password.strip():
                        st.warning("Please fill all fields.")
                    else:
                        try:
                            save_configuration(
                                new_dsn,
                                new_username,
                                new_password
                            )
                            st.success("Configuration updated successfully!", icon="✅")
                            st.session_state.edit_mode = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {str(e)}")
                
                if cancel:
                    st.session_state.edit_mode = False
                    st.rerun()
