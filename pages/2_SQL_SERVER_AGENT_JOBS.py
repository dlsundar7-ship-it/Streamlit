import streamlit as st
import pandas as pd
import pyodbc


st.set_page_config(
    page_title="SQL Server Agent Jobs",
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


st.title("SQL Server Agent Jobs")


connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=WIN-7QUI0BGC7TU;"
    "DATABASE=msdb;"
    "Trusted_Connection=yes;"
)

# Fetch jobs 
query = """
SELECT
    j.name AS JobName,
    CASE j.enabled
        WHEN 1 THEN 'Enabled'
        WHEN 0 THEN 'Disabled'
    END AS Status,
    s.schedule_id,
    s.freq_type,
    s.freq_interval,
    s.active_start_time
FROM msdb.dbo.sysjobs j
LEFT JOIN msdb.dbo.sysjobschedules js
    ON j.job_id = js.job_id
LEFT JOIN msdb.dbo.sysschedules s
    ON js.schedule_id = s.schedule_id
-- WHERE j.name = 'STREAMLIT_TEST_GB_BRANC'
ORDER BY j.name;
"""



conn = pyodbc.connect(connection_string)
jobs = pd.read_sql(query, conn)
conn.close()


def format_weekly_days(freq_interval):
    if pd.isna(freq_interval):
        return ""
    freq_interval = int(freq_interval)
    days = [(1, 'Sun'), (2, 'Mon'), (4, 'Tue'), (8, 'Wed'),
            (16, 'Thu'), (32, 'Fri'), (64, 'Sat')]
    selected = [name for bit, name in days if freq_interval & bit]

    if not selected:
        return ""
    
    # group consecutive days
    day_to_idx = {'Sun':0,'Mon':1,'Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6}
    result = []
    temp = [selected[0]]
    
    for prev, curr in zip(selected, selected[1:]):
        if day_to_idx[curr] == day_to_idx[prev]+1:
            temp.append(curr)
        else:
            if len(temp) > 1:
                result.append(f"{temp[0]}–{temp[-1]}")
            else:
                result.append(temp[0])
            temp = [curr]
    if len(temp) > 1:
        result.append(f"{temp[0]}–{temp[-1]}")
    else:
        result.append(temp[0])
    return ", ".join(result)

def format_schedule(row):
    if pd.isna(row['freq_type']):
        return "Manual"

    # Safely convert active_start_time to int
    active_start_time = int(row['active_start_time'])
    time_str = str(active_start_time).zfill(6)

    hh = int(time_str[:2])
    mm = int(time_str[2:4])

    # Convert to 12-hour format
    am_pm = "AM" if hh < 12 else "PM"
    display_hour = hh % 12
    if display_hour == 0:
        display_hour = 12

    time_formatted = f"{display_hour}:{mm:02d} {am_pm}"

    # Format based on frequency type
    if row['freq_type'] == 4:
        return f"Daily {time_formatted}"
    
    elif row['freq_type'] == 8:
        days_text = format_weekly_days(row['freq_interval'])
        return f"{days_text} {time_formatted}"
    
    elif row['freq_type'] == 16:
        day_of_month = (
            int(row['freq_interval'])
            if pd.notna(row['freq_interval'])
            else 1
        )
        return f"Monthly on Day {day_of_month} at {time_formatted}"

# Display jobs
if jobs.empty:
    st.warning("No jobs found.")
else:
    for _, row in jobs.iterrows():
        schedule_text = format_schedule(row)
        with st.container(border=True):
            col1, col2 = st.columns([6, 1])

            with col1:
                st.subheader(row["JobName"])
                st.write(f"**Schedule:** {schedule_text}")
                st.write(f"**Status:** {row['Status']}")

            with col2:
                if st.button("Run", key=f"run_{row['JobName']}", use_container_width=True):
                    run_conn = pyodbc.connect(connection_string)
                    run_cursor = run_conn.cursor()
                    run_cursor.execute("EXEC msdb.dbo.sp_start_job @job_name = ?", row["JobName"])
                    run_conn.commit()
                    run_cursor.close()
                    run_conn.close()
                    st.toast(f"Started {row['JobName']}", icon="▶️")

                if st.button("Edit", key=f"edit_{row['JobName']}", use_container_width=True):
                    st.session_state["edit_job"] = row["JobName"]

            # inside your job loop
            if "edit_job" in st.session_state and st.session_state["edit_job"] == row["JobName"]:

                with st.container(border=True):

                    st.subheader("Edit Job")

                    st.text_input(
                        "Job Name",
                        value=row["JobName"],
                        disabled=True,
                        key=f"jobname_{row['JobName']}"
                    )

                    enabled = st.checkbox(
                        "Enabled",
                        value=(row["Status"] == "Enabled"),
                        key=f"enabled_{row['JobName']}"
                    )

                    st.divider()

                    st.subheader("Schedule")

                    schedule_type_map = {
                        1: "One-time",
                        4: "Daily",
                        8: "Weekly",
                        16: "Monthly"
                    }

                    current_schedule_type = schedule_type_map.get( int(row["freq_type"]) if pd.notna(row["freq_type"]) else 4, "Daily") # ---

                    schedule_options = ["Daily", "Weekly", "Monthly"]

                    if current_schedule_type not in schedule_options:
                        current_schedule_type = "Daily"

                    schedule_type = st.selectbox(
                        "Schedule Type",
                        schedule_options,
                        index=schedule_options.index(current_schedule_type),
                        key=f"schedule_type_{row['JobName']}"
                    )

                    # For weekly schedule, allow selecting weekdays
                    if schedule_type == "Weekly":
                        # Map current freq_interval to selected days for UI
                        bit_to_day = {
                            1: 'Sun', 2: 'Mon', 4: 'Tue', 8: 'Wed',
                            16: 'Thu', 32: 'Fri', 64: 'Sat'
                        }
                        day_to_bit = {v: k for k, v in bit_to_day.items()}

                        current_freq_interval = int(row['freq_interval']) if pd.notna(row['freq_interval']) else 2  # default Monday
                        selected_days = [day for bit, day in bit_to_day.items() if current_freq_interval & bit]

                        # UI multiselect for weekly schedule
                        selected_days = st.multiselect(
                            "Select Days",
                            list(day_to_bit.keys()),
                            default=selected_days,
                            key=f"weekly_days_{row['JobName']}"
                        )

                        # Convert selected days to SQL bitmask
                        freq_interval_val = sum(day_to_bit[day] for day in selected_days)
                        freq_recurrence_factor = 1  # weekly recurrence
                    
                    elif schedule_type == "Monthly":

                        current_day = (
                            int(row["freq_interval"])
                            if pd.notna(row["freq_interval"])
                            else 1
                        )

                        monthly_day = st.selectbox(
                            "Day of Month",
                            list(range(1, 32)),
                            index=current_day - 1,
                            key=f"monthly_day_{row['JobName']}"
                        )

                        freq_interval_val = monthly_day
                        freq_recurrence_factor = 1

                    else:
                        freq_interval_val = 1
                        freq_recurrence_factor = 1


                    active_start_time = (
                        int(row["active_start_time"])
                        if pd.notna(row["active_start_time"])
                        else 0
                    )

                    time_str = str(active_start_time).zfill(6)

                    schedule_time_text = st.text_input(
                        "Start Time (HH:MM:SS)",
                        value=f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}",
                        key=f"time_{row['JobName']}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "Save Changes",
                            key=f"save_{row['JobName']}",
                            type="primary",
                            use_container_width=True
                        ):

                            freq_type_map = {
                                "Daily": 4,
                                "Weekly": 8,
                                "Monthly": 16
                            }

                            new_freq_type = freq_type_map[schedule_type]

                            hh, mm, ss = schedule_time_text.split(":")

                            new_start_time = int(
                                f"{int(hh):02d}"
                                f"{int(mm):02d}"
                                f"{int(ss):02d}"
                            )

                            conn = pyodbc.connect(connection_string)
                            cursor = conn.cursor()

                            # Update Job Enabled/Disabled
                            cursor.execute(
                                """
                                EXEC msdb.dbo.sp_update_job
                                    @job_name = ?,
                                    @enabled = ?
                                """,
                                row["JobName"],
                                1 if enabled else 0
                            )

                            # Update Schedule
                            if pd.notna(row["schedule_id"]):

                                # Calculate freq_interval for weekly
                                if schedule_type == "Weekly":
                                    freq_interval_val = sum(day_to_bit[day] for day in selected_days)

                                elif schedule_type == "Monthly":
                                    freq_interval_val = monthly_day

                                else:
                                    freq_interval_val = 1

                            cursor.execute(
                                """
                                EXEC msdb.dbo.sp_update_schedule
                                    @schedule_id = ?,
                                    @freq_type = ?,
                                    @active_start_time = ?,
                                    @freq_recurrence_factor = ?,
                                    @freq_interval = ?
                                """,
                                int(row["schedule_id"]),
                                new_freq_type,
                                new_start_time,
                                freq_recurrence_factor,
                                freq_interval_val
                            )

                            conn.commit()

                            cursor.close()
                            conn.close()

                            st.toast(
                                f"{row['JobName']} updated successfully",
                                icon="✅"
                            )

                            del st.session_state["edit_job"]

                            st.rerun()

                    with col2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{row['JobName']}",
                            use_container_width=True
                        ):

                            del st.session_state["edit_job"]

                            st.rerun()