from sqlalchemy import create_engine
import pandas as pd


db_connection_str = 'mysql+pymysql://odsuser:odsuser@172.21.3.42/hobs_int'
db_connection = create_engine(db_connection_str)

def serverHealth():
    try:
        query = "SELECT * FROM server_health_details limit 10"
        df = pd.read_sql(query, con=db_connection)
        return df
    except Exception as e:
        print(e)
