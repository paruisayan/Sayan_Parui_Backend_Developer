import psycopg2
from psycopg2 import Error
from sqlalchemy import create_engine

#psql_engine_src = create_engine('postgresql+psycopg2://readapp:%s@%s:5432/evmain' % (urllib.parse.quote_plus(password['postgres_pass_tcs_cdm']),server["postgres_tcs_cdm"]))


try:
    # Connect to an existing database
    connection = psycopg2.connect(user="readapp",
                                  password="re@d@pp#@!",
                                  host="172.21.3.11",
                                  port="5432",
                                  database="evmain")

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT version();")
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")