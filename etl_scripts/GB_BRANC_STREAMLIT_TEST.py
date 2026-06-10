import pandas as pd
import pyodbc
import time
import os
import datetime
import warnings

import sys

# python.exe "D:\NRL\01_NRootBI_Projects\02_Python_Scripts\Executable_Scripts\PY_MASTER_AFTERSALES.py"
# python.exe "D:\NRL\03_NRoot_Workbench\Vimalesh\Python\Test.py"

warnings.filterwarnings("ignore")         #Ignore Warnings

start_time = datetime.datetime.now() 

today=start_time.strftime('%Y-%m-%d%H:%M:%S')




# Connect to SQL Server using pyodbc
server = 'WIN-7QUI0BGC7TU'
database = 'NRoots_Internal'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Pooling=False'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
Procedure_Name = 'PY_MASTER_COMMON'
Job_Name='VehicleSales'
Control_Table='NRoots_Internal.CONTROL.TABLE_LOAD_CONTROL'
Job_History='NRoots_Internal.CONTROL.JOB_HISTORY'




def get_odbc_connection():

    query = """
    SELECT TOP 1
        DSN,
        USERNAME,
        PASSWORD
    FROM dbo.ODBC_CONFIGURATION
    WHERE IS_ACTIVE = 1
    """

    row = pd.read_sql(query, conn).iloc[0]

    return f"DSN={row['DSN']};UID={row['USERNAME']};PWD={row['PASSWORD']};"


# Establish connection to Kisam ODBC data source
# kisam_conn_str = 'DSN=KeyLoop;UID=nrootlab;PWD=Sql2025@;'


kisam_conn_str = get_odbc_connection()
kisam_conn = pyodbc.connect(kisam_conn_str)



# 1. RDS.GB_BRANC

try:
    schema_name = 'RDS.'
    table_name = 'GB_BRANC'
    table_desc = 'GB_BRANC'

    # Define the chunk size
    chunksize = 100000

    # Set up the ODBC connections (replace with your own connection strings)
    kisam_conn = pyodbc.connect(kisam_conn_str)
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    

    # Truncate the table
    TRUNCATE_query = f'''TRUNCATE TABLE {schema_name}{table_name}'''
    cursor.execute(TRUNCATE_query)
    conn.commit()

    # SQL query to get table names from the control master table
    table_query = F"""
    SELECT TABLE_NAME 
    FROM {Control_Table}
    WHERE TABLE_DESCRIPTION='{table_desc}' AND LOAD_STATUS=1
    """

    # Execute the query and fetch the results
    tables = [row[0] for row in cursor.execute(table_query)]

    # Log the start of the job
    LOG_query = f''' 
    INSERT INTO {Job_History}
    VALUES ('{Job_Name}', '{Procedure_Name}', '{table_name}', GETDATE(), NULL, NULL, 'Running', NULL, SUSER_NAME(), GETDATE(), NULL, NULL, 'Master') 
    '''
    cursor.execute(LOG_query)
    conn.commit()

    # Iterate over each table and select data from it
    for table in tables:
        try:
            # Get today's date
            today = time.strftime('%Y-%m-%d%H:%M:%S')  # Assuming you need today's date

            # Define the SQL query for fetching data
            query = f"""
            SELECT GB_BR_BRANCH,GB_BR_ADDRESS_001,GB_BR_ADDRESS_002,GB_BR_ADDRESS_003,GB_BR_ADDRESS_004,GB_BR_ADDRESS_005,GB_BR_POSTCODE,GB_BR_TELNO
        	      ,GB_BR_FAXNO,GB_BR_MANAGER,GB_BR_SAACC,GB_BR_ACTIVE,GB_BR_CASHACC,GB_BR_CASHALAS,GB_BR_COSTING,GB_BR_ACBRANCH,GB_BR_NAME_001,GB_BR_NAME_002
        		  ,GB_BR_WAREHOUS,GB_BR_IBSUPP_001,GB_BR_IBSUPP_002,GB_BR_IBPICKP,GB_BR_IBADVP,GB_BR_IBINVP,GB_BR_BBPICKP,GB_BR_BBADVP,GB_BR_BBINVP,GB_BR_AREA
        		  ,GB_BR_REGION,GB_BR_DIVISION,GB_BR_HOLDATES,GB_BR_SQPICKP,GB_BR_PARENT,GB_BR_SQGRNP,GB_BR_SQRETP,GB_BR_SQNOTP,GB_BR_SQTIKP,GB_BR_EXSTKOMR_001
        		  ,GB_BR_EXSTKOMR_002,GB_BR_DIRECOMR_001,GB_BR_DIRECOMR_002,GB_BR_POSTXREF_001,GB_BR_POSTXREF_002,GB_BR_WDOWNACC,GB_BR_IBCUST_001,GB_BR_IBCUST_002
            	  ,GB_BR_IBCUST_003,GB_BR_IBCUST_004,GB_BR_IBCUST_005,GB_BR_IBCUST_006,GB_BR_IBCUST_007,GB_BR_IBCUST_008,GB_BR_IBCUST_009,GB_BR_IBCUST_010
        		  ,GB_BR_SHORT,GB_BR_WSFILE,GB_BR_ALWAYSP,GB_BR_IBBKORDR,GB_BR_RESTRICT,GB_BR_ACCOMP,GB_BR_TRANSFERS,GB_BR_PKCATGRY,GB_BR_WASTE,GB_BR_SITE
        		  ,GB_BR_KDBTIME,GB_BR_KDBUSER,GB_BR_INTERNET,GB_BR_CALLCENTRE,GB_BR_PLACC,GB_BR_BRANCHINSEARCH,GB_BR_STOCKCTRL,GB_BR_ACDIVISION,GB_BR_PARENTLEVEL
        		  ,GB_BR_ACCOUNTSONLY,GB_BR_WFMANAGER,GB_BR_TRANSBO,GB_BR_FAXSPOOL,GB_BR_EMAILSPOOL,GB_BR_EBSPOOL,GB_BR_ACBRANCHGROUP,GB_BR_BATCHCTRL,GB_BR_WMS
        		  ,GB_BR_TABLESPACE,GB_BR_DEPTBUDGETS,GB_BR_VISIBILITY,GB_BR_INVBRAND,GB_BR_SRCHBRAND,GB_BR_FORCECRM,GB_BR_RETAILVAL_001,GB_BR_RETAILVAL_002
        		  ,GB_BR_FCAST,GB_BR_FBRANCH,GB_BR_WMSSETUP,GB_BR_RMSPOOL,GB_BR_BATCHCOSTS,GB_BR_STKSPLIT,GB_BR_PRSFILE,GB_BR_HUBBRANCH,GB_BR_PRINTTEXT
        		  ,GB_BR_CERTTEXT,GB_BR_DEFMANUFACT,GB_BR_VISIBLE,GB_BR_LEGACY,GB_BR_CHKORDERVALUE,GB_BR_STOCKPROF,GB_BR_AGPRINTER,GB_BR_LEGACYCODE
            	  ,GB_BR_CUSTPSID,GB_BR_CUSTNPSID,GB_BR_ADMINSPOOL,GB_BR_FAXCOVERPAGE,GB_BR_SMSSPOOL,GB_BR_AGENTACTIVE,GB_BR_DIRECTIONS,GB_BR_NOTES,GB_BR_OPEN_001
        		  ,GB_BR_OPEN_002,GB_BR_OPEN_003,GB_BR_OPEN_004,GB_BR_OPEN_005,GB_BR_OPEN_006,GB_BR_OPEN_007,GB_BR_CLOSE_001,GB_BR_CLOSE_002,GB_BR_CLOSE_003
        		  ,GB_BR_CLOSE_004,GB_BR_CLOSE_005,GB_BR_CLOSE_006,GB_BR_CLOSE_007,GB_BR_CLOSEDALLDAY_001,GB_BR_CLOSEDALLDAY_002,GB_BR_CLOSEDALLDAY_003
        		  ,GB_BR_CLOSEDALLDAY_004,GB_BR_CLOSEDALLDAY_005,GB_BR_CLOSEDALLDAY_006,GB_BR_CLOSEDALLDAY_007,GB_BR_CALLCLASSID,GB_BR_CALREGION,GB_BR_ACPOSTBRANCH
        		  ,GB_BR_BUDGET,GB_BR_COMPANYREGNO,GB_BR_RS_ME_NAME,GB_BR_RS_ME_ADDRESS_001,GB_BR_RS_ME_ADDRESS_002,GB_BR_RS_ME_ADDRESS_003,GB_BR_RS_ME_ADDRESS_004
        		  ,GB_BR_RS_ME_ADDRESS_005,GB_BR_COMPANY,GB_BR_LOCATION
             FROM "{table}" 
            """

            # Start time tracking for the overall process
            overall_start_time = time.time()

            # Initialize values_to_insert as an empty list
            values_to_insert = []

            # Read data in chunks from source and process it
            for chunk_counter, chunk in enumerate(pd.read_sql(query, kisam_conn, chunksize=chunksize)):
                # Start time for processing each chunk
                chunk_start_time = time.time()

                # Process and bulk insert data
                chunk['TABLE_NAME'] = table  # Add the table name to the chunk
                columns = chunk.columns.tolist()

                # Create the INSERT statement dynamically
                insert_query = f"INSERT INTO {schema_name}{table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"

                # Iterate over rows in the DataFrame and add to batch
                for i, row in chunk.iterrows():
                    values_to_insert.append(tuple(row))

                    # Insert in batches
                    if len(values_to_insert) >= chunksize:
                        cursor.executemany(insert_query, values_to_insert)
                        conn.commit()
                        values_to_insert = []  # Reset for next batch

                # Insert any remaining records if batch size is not reached
                if values_to_insert:
                    cursor.executemany(insert_query, values_to_insert)
                    conn.commit()

                # End time for processing each chunk
                chunk_end_time = time.time()

                # Calculate and display time taken for the chunk
                chunk_duration = chunk_end_time - chunk_start_time
                print(f"Chunk {chunk_counter + 1} processing time: {chunk_duration:.2f} seconds")

        except Exception as e:
            # Handle the exception and log the error message in PyJOB_HISTORY table
            error_message = str(e)

            # Log the error message in the CONTROL table (PyJOB_HISTORY)
            LOG_query = F"""
            UPDATE {Job_History}
            SET 
            END_TIME = GETDATE(),
            DURATION = 
                        CAST(DATEDIFF(SECOND, START_TIME, GETDATE()) / 3600 AS VARCHAR) + ' Hours, ' +
                        CAST((DATEDIFF(SECOND, START_TIME, GETDATE()) % 3600) / 60 AS VARCHAR) + ' Minutes, ' +
                        CAST(DATEDIFF(SECOND, START_TIME, GETDATE()) % 60 AS VARCHAR) + ' Seconds',
            ERROR_MESSAGE = ?,
            STATUS = 'Failure'
            WHERE TABLE_NAME = ? 
            AND STATUS = 'Running'
            AND START_TIME = (
						  SELECT	MAX(START_TIME) 
							FROM	NRoots_Internal.CONTROL.JOB_HISTORY 
						   WHERE	TABLE_NAME = ?
						     AND	STATUS <> 'Failure'
						);
            """
            cursor.execute(LOG_query, (error_message, table_name, table_name))
            conn.commit()

            # Continue to the next table
            print(f"Error occurred for table {table}: {error_message}")
            continue  # Skip the current iteration and proceed with the next table

    # Log the completion of the job
    LOG_query = f''' 
    UPDATE {Job_History}
    SET 
    END_TIME = GETDATE(),
    DURATION = 
        CAST(DATEDIFF(SECOND, START_TIME, GETDATE()) / 3600 AS VARCHAR) + ' Hours, ' +
        CAST((DATEDIFF(SECOND, START_TIME, GETDATE()) % 3600) / 60 AS VARCHAR) + ' Minutes, ' +
        CAST(DATEDIFF(SECOND, START_TIME, GETDATE()) % 60 AS VARCHAR) + ' Seconds',
    STATUS = 'Success'
    WHERE 
    TABLE_NAME = '{table_name}' 
    AND STATUS = 'Running'
    AND START_TIME = (
						  SELECT	MAX(START_TIME) 
							FROM	NRoots_Internal.CONTROL.JOB_HISTORY 
						   WHERE	TABLE_NAME = '{table_name}'
						     AND	STATUS <> 'Failure'
						);
    '''
    cursor.execute(LOG_query)
    conn.commit()


    Table_Load_Control_query = f''' 
    UPDATE {Control_Table}
    SET 
    LAST_LOADED = GETDATE()
    WHERE 
        TABLE_DESCRIPTION = '{table_desc}' AND LOAD_STATUS = 1
    '''
    cursor.execute(Table_Load_Control_query)
    conn.commit()
    # Close the cursor and connection
    cursor.close()
    conn.close()

    # End time tracking for overall process
    overall_end_time = time.time()

    # Calculate and display total time taken for the whole process
    overall_duration = overall_end_time - overall_start_time
    print("Data transfer COMPLETED!")
    print(f"Overall Process Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(overall_start_time))}")
    print(f"Overall Process End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(overall_end_time))}")
    print(f"Total Duration for all chunks: {overall_duration:.2f} seconds")

except Exception as e:
    print(f"Error during job execution: {e}")

    if cursor:
        cursor.close()

    if conn:
        conn.close()

    sys.exit(1)




