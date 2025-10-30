from datetime import *
import json
import os
import time
from fastapi import Query
from sqlalchemy import create_engine, true
import urllib
import pandas as pd
import pymysql
from Excel_File_Processing.download_excels import get_charger_counts_df_from_file
from dateutil import *
from dateutil.relativedelta import *
import multiprocessing
from multiprocessing import Pool


# CDM Database connection
psql_engine = create_engine('postgresql+psycopg2://readapp:%s@%s:5432/evmain' % (urllib.parse.quote_plus('re@d@pp#@!'),'172.21.3.11'))

# ODS Database Connection
def create_connection_mysql():
    try:
        mydb = create_engine('mysql+pymysql://odsuser:%s@%s' % (urllib.parse.quote_plus('odsuser'),'172.21.3.42'))
        # mydb = pymysql.connect(
        # host="172.21.3.42",
        # user="odsuser",
        # password="odsuser"
        # )
    except Exception as e:
        print(e)
    return mydb



# mariadb_engine = create_engine('mariadb+mariadbconnector://readapp:%s@%s:5432/evmain' % (urllib.parse.quote_plus('re@d@pp#@!'),'172.21.3.11'))
#psql_engine = create_engine('postgresql+psycopg2://ev_db_write:%s@%s:5432/ev_database' % (urllib.parse.quote_plus('TP123'),'100.70.74.202'))

def universalQueary(query):
    try:
        df = pd.read_sql(query, psql_engine)
        return df
    except Exception as e:
        print(e)

def getChargerDetails():
    try:
       q = "SELECT * FROM ev_charge_point WHERE cdmstatus <> 4 AND devicestatus='Managed'"
    #    q = "select * from ev_charge_point"
       df = pd.read_sql(q,psql_engine)
    #    print("Chager Details", df)
    except Exception as e:
        print(e)
    return df


def new_dashboard_data():
    today_date = date.today().strftime('%Y-%m-%d')
    c_detail_q = "SELECT * FROM ev_charge_point WHERE devicestatus='Managed'"
    pg_df=pd.read_sql(c_detail_q,psql_engine)
    
    with open("/home/evadmin/EV_NOC/Backend/app/controllers/ack.json","r") as file:
        data = pd.read_json(file)
        ack_data = pd.DataFrame(data)
    
    merge_df = pg_df.merge(ack_data,on=['identifier'],how='left',indicator=True)
    pg_df.loc[merge_df['_merge']=="both",'cdmstatus']=5
    pg_df[pg_df['cdmstatus']==5].shape
    
    fault_query = """SELECT distinct ev_ch_pt.identifier, ev_ch_pt.chargepointvendor, ev_ch_pt.latitude, ev_ch_pt.longitude, ev_ch_pt.city, ev_ch_pt.state, ev_ch_pt.country, ev_ch_pt.cdmstatus, ev_flt.status, ev_ch_pt.devicestatus, ev_ch_pt.postalcode, ev_ch_pt.name
                    FROM ev_charge_point ev_ch_pt 
                    inner join ev_fault ev_flt 
                    on ev_ch_pt.identifier = ev_flt.identifier 
                    where ev_ch_pt.cdmstatus = 2 AND ev_flt.status = 'Faulted' AND ev_flt.faultstatus = 'Open';
                    """
    fault_df = pd.read_sql(fault_query,psql_engine)
    merge_fault = pg_df.merge(fault_df,on=['identifier'],how='left',indicator=True)
    pg_df.loc[merge_fault['_merge']=="both",'cdmstatus']=3
    
    filenm_highway= '/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json'
    filenm_priority= '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
    
    with open(filenm_highway,"r") as file:
        data = pd.read_json(file)
        h_data = pd.DataFrame(data)
    
    with open(filenm_priority,"r") as file:
        data = pd.read_json(file)
        p_data = pd.DataFrame(data)
        
    h_merge = pg_df.merge(h_data,on=['identifier'],how='left',indicator=True)
    pg_df.loc[h_merge['_merge']=="both",'cdmstatus']=6
    
    p_merge = pg_df.merge(p_data,on=['identifier'],how='left',indicator=True)
    pg_df.loc[p_merge['_merge']=="both",'cdmstatus']=4
    
    maria_query = """SELECT EVSE_ID as identifier,CDM_SESSION_ID,UNITS,REQ_START_DATE,REQ_END_DATE,CHARGE_PER_UNITS,USAGE_STATUS,BATTERY_PERCENT
    FROM rms_billing.ev_booking_mst WHERE Date(REQ_START_DATE)='"""+today_date+"""' and UNITS>0.2 order by REQ_START_DATE DESC;""" 

    maria_df = pd.read_sql(maria_query,create_connection_mysql())
    # maria_df.rename(columns={'EVSE_ID':'identifier'},inplace=True)
    maria_df['UNITS'] = maria_df['UNITS'].astype('int64')
    # display(maria_df.groupby('identifier')['UNITS'].sum().reset_index())
    
    sessions_count = maria_df.groupby('USAGE_STATUS')['USAGE_STATUS'].count().to_dict()
    top_chargers = maria_df[maria_df['USAGE_STATUS']=="COMPLETED"].groupby('identifier')['UNITS'].count().sort_values(ascending=False).head(10).to_dict()
    top_chargers_list = [key for key in top_chargers.keys()]
    
    agg_maria_df = maria_df.groupby('identifier').agg({
    'CDM_SESSION_ID':'first', 'UNITS':'sum', 'REQ_START_DATE':'first',
       'REQ_END_DATE':'first', 'CHARGE_PER_UNITS':'first', 'USAGE_STATUS':'first', 'BATTERY_PERCENT':'first'
    })
    final_data = pd.merge(pg_df,agg_maria_df,on='identifier',how='left')
    final_data = final_data.astype('str')
    
    states = final_data['state'].unique()
    # state_city_pin = []
    identifiers_list = []
    # data ={}
    # data.update({'counts':final_data.groupby('cdmstatus')['cdmstatus'].count().to_dict()})
    # for state in states:
    #     data.update({"state":state})
    #     cities = list(final_data[final_data['state']==state]['city'].unique())
    #     city_pins =[]
    #     for city in cities:
    #         city_pins.append({'city':city,'pincodes':list(final_data[final_data['city']==city]['postalcode'].unique())})
    #     data.update({"cities":city_pins})
    #     # data.update({"pincodes":final_data[final_data['state']==state]['postalcode'].unique()})
    #     # print(data)
    #     identifiers_list.append(final_data[final_data['state']==state][['identifier','latitude',\
    #         'longitude','state','city','postalcode','address','chargepointvendor', 'chargepointmodel',\
    #             'firmwareversion','cdmstatus','CDM_SESSION_ID','REQ_START_DATE', 'UNITS','CHARGE_PER_UNITS', \
    #                 'USAGE_STATUS', 'BATTERY_PERCENT']].to_dict(orient='records'))
    #     state_city_pin.append(data)
    #     data={}

    # return state_city_pin
    
    states_list = []
    for state in states:
        state_dict = {"name":state,"cities":[]}
        for city in list(final_data[final_data['state']==state]['city'].unique()):
            city_dict = {"name":city,"pincodes":list(final_data[final_data['city']==city]['postalcode'].unique())}
            state_dict['cities'].append(city_dict)
        states_list.append(state_dict)
        
        identifier_dict={"state":state}
        identifier_dict.update({"identifiers":final_data[final_data['state']==state][['identifier','latitude',\
            'longitude','state','city','postalcode','address','chargepointvendor', 'chargepointmodel',\
            'firmwareversion','cdmstatus','CDM_SESSION_ID','REQ_START_DATE', 'UNITS','CHARGE_PER_UNITS', \
            'USAGE_STATUS', 'BATTERY_PERCENT']].to_dict(orient='records')})
        identifiers_list.append(identifier_dict)

    result = [{'count':final_data.groupby('cdmstatus')['cdmstatus'].count().to_dict()},{'sessions_count':sessions_count},{"top_chargers":top_chargers_list},{'states':states_list},{'markers':identifiers_list}]
    
    return result
    # return final_data.to_dict(orient='records')

def new_dashboard_popup(identifier):
    today_date = date.today().strftime('%Y-%m-%d')
    last_transaction_q = """select UNITS,REQ_START_DATE,REQ_END_DATE from rms_billing.ev_booking_mst where EVSE_ID='"""+identifier+"""' and UNITS>0.2 order by REQ_START_DATE desc limit 5"""
    last_transaction = pd.read_sql(last_transaction_q,create_connection_mysql())
    try:
        last_t = last_transaction['REQ_START_DATE'].head(1)[0]
    except:
        last_t=False

    location_partner_query="""SELECT DISTINCT
                evse_code as identifier,
                JSON_UNQUOTE(JSON_EXTRACT(ev_evseeo.connectivity_attrs,'$.gprsConnectivityAttrs.telecomPartner')) AS telecom_partner,
                model,
                JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.contactName') AS name_of_lp,
                JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.email') AS email_of_lp,
                JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.mobileNumber') AS mobile_lp
                -- JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.mobileNumber') AS mobile_number_of_service_provider
                FROM resourceinventory.ev_location_contacteo 
                INNER JOIN  resourceinventory.ev_locationeo_location_partners
                ON ev_location_contacteo.contact_id = ev_locationeo_location_partners.location_partners_contact_id
                INNER JOIN resourceinventory.ev_locationeo
                ON ev_locationeo_location_partners.ev_locationeo_location_id = ev_locationeo.location_id
                INNER JOIN resourceinventory.ev_locationeo_evses
                ON ev_locationeo_evses.ev_locationeo_location_id = ev_locationeo.location_id
                INNER JOIN resourceinventory.ev_evseeo
                ON ev_locationeo_evses.evses_evse_id = ev_evseeo.evse_id 
                -- INNER JOIN ev_locationeo_location_spocs
                -- ON ev_locationeo_location_spocs.ev_locationeo_location_id = ev_locationeo.location_id
                WHERE evse_code ='"""+identifier+"""'"""

    try:
        lp_df = pd.read_sql(location_partner_query,create_connection_mysql())
    except:
        lp_df=[{}]

    alarm_query= """SELECT faultcode,vendorspeceficcode,connectorid,TIMESTAMP,faultstatus,resolutiontime FROM ev_fault WHERE identifier='"""+identifier+"""' ORDER BY id desc LIMIT 5;"""
    try:
        alarm_df = pd.read_sql(alarm_query,psql_engine)
    except:
        alarm_df=[{}]
    return {"last_transaction":last_t,"alarms":alarm_df.to_dict(orient='records'),"location_partner":lp_df.to_dict(orient='records'),"transactions":last_transaction.to_dict(orient='records')}

# Gives charger details based on the requirement
def get_charger_details(region, chargers):
    filenm_highway= '/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json'
    filenm_priority= '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
    try:
        if region == 'India' and  chargers =='all':
            #query = "select * from ev_database.ev_charge_point"
            query = "select * from ev_charge_point"
            df = pd.read_sql(query, psql_engine)
            # print(df)
        elif region == 'India' and chargers == 'active':
            query = "select * from ev_charge_point where cdmstatus = 1"
            df = pd.read_sql(query, psql_engine)
        elif region == 'India' and chargers == 'inactive':
            query = "select * from ev_charge_point where cdmstatus = 2"
            df = pd.read_sql(query, psql_engine)
        elif region == 'India' and chargers == 'faulted':
            query = """SELECT distinct ev_ch_pt.identifier, ev_ch_pt.chargepointvendor, ev_ch_pt.latitude, ev_ch_pt.longitude, ev_ch_pt.city, ev_ch_pt.state, ev_ch_pt.country, ev_ch_pt.cdmstatus, ev_flt.status, ev_ch_pt.devicestatus, ev_ch_pt.postalcode, ev_ch_pt.name
                    FROM ev_charge_point ev_ch_pt 
                    inner join ev_fault ev_flt 
                    on ev_ch_pt.identifier = ev_flt.identifier 
                    where ev_ch_pt.cdmstatus = 2 AND ev_flt.status = 'Faulted' AND ev_flt.faultstatus = 'Open';
                    """
            df = pd.read_sql(query, psql_engine)
            df['cdmstatus'] = df['cdmstatus'].replace(2,5)
            df['cdmstatus'] = df['cdmstatus'].replace(1,5)
        elif region == 'India' and chargers == 'star':
            today_date = date.today().strftime('%Y-%m-%d')
            date_before_7_days = (date.today() - timedelta(7)).strftime('%Y-%m-%d')
            query = """ SELECT identifier,COUNT(*) AS count FROM ev_transaction where DATE(start_time) 
                BETWEEN '"""+date_before_7_days+"""' and '"""+today_date+"""'  
                AND (stop_meter_value-start_meter_value)>0.2 GROUP BY identifier HAVING COUNT(*)>= 35
                ORDER BY count DESC """
            # print(query)
            df_s= pd.read_sql(query, psql_engine)
            star_identifiers = df_s['identifier'].to_list()

            with open(filenm_priority, 'r') as openfile:
                arr = json.load(openfile)
            priority_chargers = []
            for json_obj in arr:
                priority_chargers.append(json_obj['identifier'])
            req_identifiers = star_identifiers + priority_chargers
            # print(req_identifiers)
            q = "select * from ev_charge_point"
            df_i = pd.read_sql(q, psql_engine) 
            df = (df_i[df_i['identifier'].isin(req_identifiers)]).reset_index().copy()
        elif region == 'India' and chargers == 'highway':
            # print("In highway chargers if else")
            with open(filenm_highway, 'r') as openfile:
                arr = json.load(openfile)
            highway_chargers = []
            for json_obj in arr:
                highway_chargers.append(json_obj['identifier'])
            query = "select * from ev_charge_point"
            df = pd.read_sql(query, psql_engine)
            df = (df[df['identifier'].isin(highway_chargers)]).reset_index(drop=true).copy()
    except Exception as e:
        print(e)
    return df

# This function returns important chargers for particular state
def getImportantChargers(state):
    try:
        if state == 'Kerala':
            q = "select * from ev_charge_point where state='"+state+"'"
            df = pd.read_sql(q, psql_engine)
            return df
        else:
            return {'ImportantChargers': 60}
    except Exception as e:
        print(e)


# It gives charging session count and details statuses charging and compeleted.
def getChargingSession(requirement, need,  state, city, postalcode):
    try:
        today_date = date.today().strftime('%Y-%m-%d')
        if need == 'count' and requirement == 'Charging':
            if state!= None:
                # query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"'"
                q = "select identifier from ev_charge_point where state ='"+state+"'"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            elif city!= None:
                # query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"' and ev_charge_point.city='"+city+"'"
                q = "select identifier from ev_charge_point where city ='"+city+"'"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            elif postalcode != None:
                # query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"' and ev_charge_point.city='"+city+"' and ev_charge_point.postalcode='"+postalcode+"'" 
                q = "select identifier from ev_charge_point where postalcode ='"+postalcode+"'"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            else:
            #    query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '';"       
                q = "select identifier from ev_charge_point;"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            
            df = pd.read_sql(q,psql_engine)
            identifiers = df['identifier'].to_list()
            mydb = create_connection_mysql()
            df_i = pd.read_sql(query, mydb) 
            mydb.dispose()

            df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
            # print(df_i)
            # print(len(df_i))
            df_i['ongoing_charging_sessions'] = len(df_i)
            return df_i[['ongoing_charging_sessions']].head(1)


        elif need == 'details' and requirement == 'Charging':
            if state!= None:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"'"
                q = "select identifier, name, city, state from ev_charge_point where state ='"+state+"'"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            elif city!= None:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"' and ev_charge_point.city='"+city+"'"
                q = "select identifier, name, city, state from ev_charge_point where city ='"+city+"'"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            elif postalcode != None:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"' and ev_charge_point.city='"+city+"' and ev_charge_point.postalcode='"+postalcode+"'" 
                q = "select identifier, name, city, state from ev_charge_point where postalcode ='"+postalcode+"'"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            else:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '';"               
                q = "select identifier, name, city, state from ev_charge_point;"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER,OTP_ATTEMPT,BOOKING_STATUS,BATTERY_PERCENT,UPDATED_ON,UNITS  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"

            df = pd.read_sql(q,psql_engine)
            mydb = create_connection_mysql()
            df_i = pd.read_sql(query, mydb) 
            mydb.dispose()
            df_res = pd.merge(df,df_i, how='inner', on='identifier')
            return df_res

        elif need == 'count' and requirement == 'Completed':
            if state!= None and city== None and postalcode == None:
                q = "select identifier from ev_charge_point where state ='"+state+"'"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and cast(REQ_START_DATE as date) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                # print(len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
            elif state!= None and city!= None and postalcode == None:
                q = "select identifier from ev_charge_point where state ='"+state+"' and city='"+city+"'"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and cast(REQ_START_DATE as date) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                # print(len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
            elif state!= None and city!= None and postalcode != None:
                q = "select identifier from ev_charge_point where state ='"+state+"' and city='"+city+"' and postalcode='"+postalcode+"'"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and cast(REQ_START_DATE as date) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                # print(len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
            else:
                # query = "SELECT count(EVSE_ID) as completed_charging_sessions from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0;"
                q = "select identifier from ev_charge_point;"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and date(REQ_START_DATE) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                print(query,len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
                # query = "SELECT * from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 limit 10;"        
        return df
    except Exception as e:
        print(e) 

def get_charger_other_details(identifier):
    try:
        # print("Getting charger other details for the ", identifier)
        query = """
            SELECT DISTINCT
            evse_code as identifier,
            JSON_UNQUOTE(JSON_EXTRACT(ev_evseeo.connectivity_attrs,'$.gprsConnectivityAttrs.telecomPartner')) AS telecom_partner,
            location_code,
            location_description,
            station_owner,
            make,
            model,
            json_extract(contact_attributes, '$.organizationName') as organization_name,
            JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.contactName') AS name_of_location_partener,
            JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.email') AS email_of_location_partener,
            JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.mobileNumber') AS mobile_number_of_location_partener
            -- JSON_extract(JSON_EXTRACT(contact_attributes, '$.contactDetails'), '$.mobileNumber') AS mobile_number_of_service_provider
            FROM resourceinventory.ev_location_contacteo 
            INNER JOIN  resourceinventory.ev_locationeo_location_partners
            ON ev_location_contacteo.contact_id = ev_locationeo_location_partners.location_partners_contact_id
            INNER JOIN resourceinventory.ev_locationeo
            ON ev_locationeo_location_partners.ev_locationeo_location_id = ev_locationeo.location_id
            INNER JOIN resourceinventory.ev_locationeo_evses
            ON ev_locationeo_evses.ev_locationeo_location_id = ev_locationeo.location_id
            INNER JOIN resourceinventory.ev_evseeo
            ON ev_locationeo_evses.evses_evse_id = ev_evseeo.evse_id 
            -- INNER JOIN ev_locationeo_location_spocs
            -- ON ev_locationeo_location_spocs.ev_locationeo_location_id = ev_locationeo.location_id
            WHERE evse_code = '"""+identifier+"""'"""   

        # query = """SELECT * FROM resourceinventory.ev_locationeo LIMIT 10;"""    
        # print(query)
        mydb = create_connection_mysql()
        df = pd.read_sql(query, mydb) 
        # print(df)
        mydb.dispose()
    except Exception as e:
        print(e)
    return df

# Gives charger status if active or inactive
def get_chager_status(identifier):
    try:
        q = "select cdmstatus from ev_charge_point where identifier = '"+identifier+"'"
        df =  pd.read_sql(q, psql_engine)
        return df['cdmstatus'].iloc[0] 
    except Exception as e:
        print(e)
    
    
# # Gives Star Chargers count
# def getStarChargersCount(state, city, postalcode):
#     try:
#         filenm_priority= '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
#         today_date = date.today().strftime('%Y-%m-%d')
#         date_before_15_days = (date.today() - timedelta(15)).strftime('%Y-%m-%d')
#         query = "SELECT  evse_id, COUNT(*) AS number_of_chargring_sessions FROM rms_billing.ev_booking_mst WHERE  DATE(REQ_START_DATE) >= '"+date_before_15_days+"' and DATE(REQ_START_DATE) <= '"+today_date+"'  and Booking_status = 'COMPLETED' AND units > 0  GROUP BY evse_id HAVING number_of_chargring_sessions > 35 ORDER BY number_of_chargring_sessions DESC;"
#         # query = """SELECT identifier,COUNT(*) AS count FROM ev_transaction where DATE(start_time) 
#         #         BETWEEN '"""+date_before_15_days+"""' and '"""+today_date+"""'  
#         #         AND (stop_meter_value-start_meter_value)>0.2 GROUP BY identifier HAVING COUNT(*)>= 35
#         #         ORDER BY count DESC;"""
#         print(query)
#         mydb = create_connection_mysql()
#         df = pd.read_sql(query, mydb) 
#         if df.empty:
#             return 0
#         else:
#             star_identifiers = df['evse_id'].to_list()
#         mydb.dispose()

#     except Exception as e:
#         print(e)
    
#     try:
#         if  postalcode!=None:
#             # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"' and postalcode = '"+postalcode+"'"
#             q = "select identifier from ev_charge_point where postalcode = '"+postalcode+"'"
#         elif  city!=None:
#             # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"'"
#             q = "select identifier from ev_charge_point where city='"+city+"'"
#         elif state!=None:
#             q = "select identifier from ev_charge_point where state = '"+state+"'"
#         else:
#             q = "select identifier from ev_charge_point"
            
#         df = pd.read_sql(q, psql_engine) 
#         if df.empty:
#             return 0
#         else:
#             inactive_identifiers = df['identifier'].to_list()
#     except Exception as e:
#         print(e)
#     with open(filenm_priority, 'r') as openfile:
#         arr = json.load(openfile)
#     star_chargers_len = len(arr)
#     return (len([value for value in star_identifiers if value in inactive_identifiers]) + star_chargers_len)

# Gives Star Chargers count
def getStarChargersCount(state, city, postalcode):
    try:
        filenm_priority= '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
        today_date = date.today().strftime('%Y-%m-%d')
        date_before_7_days = (date.today() - timedelta(7)).strftime('%Y-%m-%d')
        query = """SELECT identifier,COUNT(*) AS count FROM ev_transaction where DATE(start_time) 
                BETWEEN '"""+date_before_7_days+"""' and '"""+today_date+"""'  
                AND (stop_meter_value::numeric-start_meter_value::numeric)>0.2 GROUP BY identifier HAVING COUNT(*)>= 35
                ORDER BY count DESC;"""
        # print(query)
        df = pd.read_sql(query, psql_engine) 
        if df.empty:
            return 0
        else:
            star_identifiers = df['identifier'].to_list()

    except Exception as e:
        print(e)
    
    try:
        if  postalcode!=None:
            # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"' and postalcode = '"+postalcode+"'"
            q = "select identifier from ev_charge_point where postalcode = '"+postalcode+"'"
        elif  city!=None:
            # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"'"
            q = "select identifier from ev_charge_point where city='"+city+"'"
        elif state!=None:
            q = "select identifier from ev_charge_point where state = '"+state+"'"
        else:
            q = "select identifier from ev_charge_point"
            
        df = pd.read_sql(q, psql_engine) 
        if df.empty:
            return 0
        else:
            identifiers_list = df['identifier'].to_list()
    except Exception as e:
        print(e)
    with open(filenm_priority, 'r') as openfile:
        arr = json.load(openfile)
    star_chargers_len = len(arr)
    return (len([value for value in star_identifiers if value in identifiers_list]) + star_chargers_len)


# Gives Highway Chargers count
def getHighwayChargersCount():
    try:
        filenm_priority= '/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json'
        with open(filenm_priority, 'r') as openfile:
            arr = json.load(openfile)
        highway_chargers_count = len(arr)
        return (highway_chargers_count)
    except Exception as e:
        print(e)
        return 0

# Gives Acknowledged Chargers count
def getAcknowledgedChargersCount():
    try:
        filenm_ack= '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
        with open(filenm_ack, 'r') as openfile:
            arr = json.load(openfile)
        ack_chargers_count = len(arr)
        return (ack_chargers_count)
    except Exception as e:
        print(e)
        return 0

# It gives faulted which are inactive chargers count
def getFaultedChargersCount(state, city, postalcode):
    try:
        today_date =     date.today().strftime('%Y-%m-%d')
        date_before_15_days = (date.today() - timedelta(15)).strftime('%Y-%m-%d')
        # query = "SELECT distinct identifier FROM ev_fault  WHERE DATE(TIMESTAMP) >= '"+date_before_15_days+"' and DATE(TIMESTAMP) <= '"+today_date+"' and status = 'Faulted' AND faultstatus = 'Open';"
        query = "SELECT distinct identifier FROM ev_fault  WHERE  status = 'Faulted' AND faultstatus = 'Open';"
        df = pd.read_sql(query, psql_engine) 
        if df.empty:
            return 0
        else:
            faulted_identifiers = df['identifier'].to_list()
        # print("Faulted identifiers", faulted_identifiers)
    except Exception as e:
        print(e)
    
    try:
        if postalcode!=None:
            # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"' and postalcode = '"+postalcode+"'"
            q = "select identifier from ev_charge_point where cdmstatus = 2 and  postalcode = '"+postalcode+"'"
        elif city!=None:
            # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"'"
            q = "select identifier from ev_charge_point where cdmstatus = 2 and  city='"+city+"'"
        elif state!=None:
            q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"'"
        else:
            q = "select identifier from ev_charge_point where cdmstatus = 2"

        df = pd.read_sql(q, psql_engine) 
        if df.empty:
            return 0
        else:
            inactive_identifiers = df['identifier'].to_list()
        # print("Inactive identifiers", inactive_identifiers)
    except Exception as e:
        print(e)
    return len([value for value in faulted_identifiers if value in inactive_identifiers])

# It gives count of chargers of different types like public, home, captive, corporate
def getChargersTypesCount(state, city, postalcode):
    try:
        # print("in Try block")
        q = "SELECT  distinct location_code, location_type FROM resourceinventory.ev_locationeo_aud;"
        # print(q)
        mydb = create_connection_mysql()
        df = pd.read_sql(q, mydb) 
        if df.empty:
            mydb.dispose()
            return ""
        else:
            # df = df.drop('location_code', axis=1)
            # new_df = df.groupby('location_type').size().reset_index()
            mydb.dispose()
            # print(df)
            return df
    except Exception as e:
        print(e)


# Function returns city names from a given state name
def getCities(state):
    try:
        q = """select distinct city from ev_charge_point where state ='"""+state+"""'"""
        df = pd.read_sql(q, psql_engine)
        # print(df)
    except Exception as e:
        print(e)
    return df

def get_Lat_Lon_state(state):
    try:
        q = """SELECT latitude,longitude from ev_charge_point WHERE state='"""+state+"""' limit 1"""
        df = pd.read_sql(q, psql_engine)
        # print(df)
    except Exception as e:
        print(e)
    return df

# Function returns postalcodes from a given city name
def getPostalCodes(city):
    try:
        q = """select distinct postalcode from ev_charge_point where city ='"""+city+"""'"""
        df = pd.read_sql(q, psql_engine)
        # print(df)
    except Exception as e:
        print(e)
    return df
#Get charger count which are active today
def getTodaysActiveChargerCount():
    today_date = date.today().strftime('%Y-%m-%d')
    try:
        q = "select count(*) as count from ev_charge_point where DATE((time+ (interval '5 hours' + interval '30 minutes'))) = '"+today_date+"' and cdmstatus = '1'"
        # print(q)
        df = pd.read_sql(q,psql_engine)
        return df
    except Exception as e:
        print(e)
    return df


# Get charger details which are became inactive today
def getTodaysInactiveChargerDetails(requirement, chargerType):
    today_date = date.today().strftime('%Y-%m-%d')
    try:
        if chargerType!= None:
            if requirement == "count":
                q = "select count(*) as count from ev_charge_point where DATE((time+ (interval '5 hours' + interval '30 minutes'))) = '"+today_date+"' and cdmstatus = 2 and type = '"+chargerType+"'"
                # print(q)
                df = pd.read_sql(q,psql_engine)
                return df
            elif requirement == "details":
                q = "select identifier, name, city from ev_charge_point where DATE((time+ (interval '5 hours' + interval '30 minutes'))) = '"+today_date+"' and cdmstatus = 2 and type = '"+chargerType+"'"
                df = pd.read_sql(q,psql_engine)
                if df.empty:
                    return pd.DataFrame()
                else:
                    today_inactive_identifiers = df['identifier'].to_list()
                    # print(today_inactive_identifiers)
                    new_df = pd.DataFrame()
                    for identifier in today_inactive_identifiers:
                        inactive_duration = get_inactive_duration(identifier)
                        df_r = get_charger_other_details(identifier)
                        try:
                            if df_r.empty:
                                df_r = pd.DataFrame(columns=['identifier'])
                                # print("Identifier for empty dataframe", identifier)
                                df_r['identifier'] = list([identifier])
                                # print(df_r)
                        except Exception as e:
                            print(e)
                        df_r['inactive_duration'] = round((inactive_duration/60),2)
                        new_df = new_df.append(df_r)
                    # print(len(new_df))
                    # print(len(df))
                    # df_final.loc[df_final['csmstatus'] == 1, 'inactive_duration'] = 'NA'
                    df_final = pd.merge(df,new_df, on='identifier', how='inner')
                    df_final['count'] = len(df_final)
                    # df_final = df_final.sort_values(by='inactive_duration', ascending = False)
                    # print("Printing info of dataframe", df_final.info())
                    # print(df_final)
                    return df_final
        else:
            if requirement == "count":
                q = "select count(*) as count from ev_charge_point where DATE(time) = '"+today_date+"' and cdmstatus = 2"
                df = pd.read_sql(q,psql_engine)
                return df
            elif requirement == 'details':
                q = "select identifier, name, city from ev_charge_point where DATE(time) = '"+today_date+"' and cdmstatus = 2"
                df = pd.read_sql(q,psql_engine)
                today_inactive_identifiers = df['identifier'].to_list()
                # print(today_inactive_identifiers)
                new_df = pd.DataFrame()
                for identifier in today_inactive_identifiers:
                    inactive_duration = get_inactive_duration(identifier)
                    df_r = get_charger_other_details(identifier)
                    try:
                        if df_r.empty:
                            df_r = pd.DataFrame(columns=['identifier'])
                            # print("Identifier for empty dataframe", identifier)
                            df_r['identifier'] = list([identifier])
                            # print(df_r)
                    except Exception as e:
                        print(e)
                    df_r['inactive_duration'] = round((inactive_duration/60),2)
                    new_df = new_df.append(df_r)
                # print(len(new_df))
                # print(len(df))
                df_final = pd.merge(df,new_df, on='identifier', how='inner')
                df_final['count'] = len(df_final)
                return df_final
    except Exception as e:
        print(e)


# Provides inactive duration in minutes for given identifier
def get_inactive_duration(identifier):
    try:
        '''
        query = "select max((EXTRACT(EPOCH from CURRENT_TIMESTAMP) - EXTRACT(EPOCH from TIME))/60)::numeric::integer \
                 as minutes_since_inactive from ev_database.ev_charge_point \
                 where \
                 ev_charge_point.identifier = '" + identifier + "'"
        '''         
        query = "select max((EXTRACT(EPOCH from CURRENT_TIMESTAMP) - EXTRACT(EPOCH from TIME))/60)::numeric::integer \
                 as minutes_since_inactive from ev_charge_point \
                 where \
                 ev_charge_point.identifier = '" + identifier + "'"         
        # print(identifier)
        df = pd.read_sql(query, psql_engine)
        return df['minutes_since_inactive'][0]
    except Exception as e:
        print(e)               

def getAlarmLogs(identifier):
    try:
        # print(identifier)
        #query = "SELECT * FROM ev_database.ev_fault WHERE identifier='"+identifier+"' ORDER BY timestamp DESC LIMIT 50;"
        query = "SELECT * FROM ev_fault WHERE identifier='"+identifier+"' ORDER BY timestamp DESC LIMIT 50;"
        df = pd.read_sql(query, psql_engine)
        # print(df)
        return df        
    except Exception as e:
        print(e)    

#Alarm and Fault Table List with date range
def getFullalarmLogs(start_date, end_date):
    try: 
        query=""" SELECT * FROM ev_fault WHERE DATE(TIMESTAMP) 
        BETWEEN '"""+start_date+"""' AND '"""+end_date+"""'
        """              
        df = pd.read_sql(query, psql_engine)
        return df
    except Exception as e:
        print(e)

#Alarm and Fault dashboard count
def getFullalarmLogsCount(start_date, end_date):
    try:
        q2="""SELECT COUNT(*) AS COUNT FROM ev_fault WHERE DATE(TIMESTAMP) BETWEEN 
        '"""+start_date+"""' AND '"""+end_date+"""'"""
        q3="""SELECT severity as Total, COUNT(*) AS COUNT FROM ev_fault 
        WHERE DATE(TIMESTAMP) BETWEEN '"""+start_date+"""' AND '"""+end_date+"""' 
        GROUP BY severity ORDER BY COUNT DESC"""
        q4="""SELECT faultstatus as Total, COUNT(*) AS COUNT FROM ev_fault 
        WHERE DATE(TIMESTAMP) BETWEEN '"""+start_date+"""' AND '"""+end_date+"""'   
        GROUP BY faultstatus ORDER BY COUNT DESC"""
    
        df2=pd.read_sql(q2,psql_engine)
        df3=pd.read_sql(q3,psql_engine)
        df4=pd.read_sql(q4,psql_engine)

        df2['total']='total'
        first_column = df2.pop('total')
        df2.insert(0, 'total', first_column)

        df2=df2.append(df3, ignore_index = True)
        df2=df2.append(df4, ignore_index = True)
        x=zip(df2['total'],df2['count'])
        data=dict(x)
        new=json.dumps(data)
        return new
    except Exception as e:
        print(e)    

def getBootnotification(identifier):
    try:
        '''
        query = "SELECT COUNT(*) FROM ev_database.ocpp_logs \
                 WHERE DATE(TIME)<='2021-12-07' AND DATE(TIME) >= '2021-12-01' AND\
                 identifier = '"+identifier+"' AND ACTION='Boot Notification Request';" 
        '''         
        query = "SELECT COUNT(*) FROM ocpp_logs \
                 WHERE DATE(TIME)<='2021-12-07' AND DATE(TIME) >= '2021-12-01' AND\
                 identifier = '"+identifier+"' AND ACTION='Boot Notification Request';"                 
        df = pd.read_sql(query, psql_engine)
        return df
    except Exception as e:
        print(e)                 

def chargerOnBoard(ctype):
    try:
        # print(ctype)
        #query = "SELECT * FROM ev_database.ev_charge_point where type = '{}';".format(ctype) 
        query = "SELECT * FROM ev_charge_point where type = '{}';".format(ctype) 
        # print(query)       
        df = pd.read_sql(query,psql_engine)
        return df
    except Exception as e:
        print(e)  

# To get chargers connector count
def getChargerConnetor():
    try:
        #query = "select * from ev_database.ev_connector"
        query = "select * from ev_connector where connector_id > 0 AND charge_point_id > 0;"
        df = pd.read_sql(query, psql_engine)
        return df
    except Exception as e:
        print(e)

# Provides charger model from ODS DB 
def getChargerModel(identifier_list):
    try:
        # print("In charger model model")
        model_for_charger = []
        mydb = create_connection_mysql()
        for charger in identifier_list:
            query = "SELECT model FROM resourceinventory.ev_evseeo WHERE evse_code = '"+charger+"';"
            df = pd.read_sql(query, mydb)
            if df.empty:
                # print("Dataframe is empty")
                model_for_charger.append("")
            else:
                model_for_charger.append(df['model'][0])
        mydb.dispose()
        # print("Models of charger", model_for_charger)
        return model_for_charger         
    except Exception as e:
        print(e)

# Provides identifier list according to state, city, postalcode
def get_identifiers_of_stuck_bookings(state, city, postalcode):
    if state!= None and city== None and postalcode == None:
        q = "select identifier from ev_charge_point where state ='"+state+"'"
        df = pd.read_sql(q,psql_engine)
        identifiers = df['identifier'].to_list()
        return identifiers
    elif state!= None and city!= None and postalcode == None:
        q = "select identifier from ev_charge_point where state ='"+state+"' and city='"+city+"'"
        df = pd.read_sql(q,psql_engine)
        identifiers = df['identifier'].to_list()
        return identifiers
    elif state!= None and city!= None and postalcode != None:
        q = "select identifier from ev_charge_point where state ='"+state+"' and city='"+city+"' and postalcode='"+postalcode+"'"
        df = pd.read_sql(q,psql_engine)
        identifiers = df['identifier'].to_list()
        return identifiers

# Gives response of priority or highway chargers
def get_highway_or_priority_chargers(requirement):
    try:
        if requirement == 'highway':
            file_nm = '/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json'
            with open(file_nm, 'r') as openfile:
                    arr = json.load(openfile)
            highway_chargers = []
            for json_obj in arr:
                highway_chargers.append(json_obj['identifier'])
            query = "select identifier, name, city, state from ev_charge_point"
            df = pd.read_sql(query, psql_engine)
            df = (df[df['identifier'].isin(highway_chargers)]).reset_index(drop=true).copy()
        elif requirement == 'priority':
            # file_nm = '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
            # with open(file_nm, 'r') as openfile:
            #         arr = json.load(openfile)
            # prioriy_chargers = []
            # for json_obj in arr:
            #     prioriy_chargers.append(json_obj['identifier'])
            # query = "select identifier, name, city, state from ev_charge_point"
            query="""SELECT ev_transaction.identifier,ev_charge_point.state,ev_charge_point.city,ev_charge_point.name 
                FROM ev_transaction inner join ev_charge_point
                ON ev_transaction.identifier=ev_charge_point.identifier WHERE 
                DATE(ev_transaction.start_time+(interval '5 hours' + interval '30 minutes'))
                BETWEEN '2023-03-28' AND '2023-04-04'
                AND (ev_transaction.stop_meter_value-ev_transaction.start_meter_value)>0.2
                GROUP BY ev_transaction.identifier,ev_charge_point.state,ev_charge_point.city,ev_charge_point.name
                HAVING COUNT(*)>= 35;"""
            df = pd.read_sql(query, psql_engine)
            # df = (df[df['identifier'].isin(prioriy_chargers)]).reset_index(drop=true).copy()
        return df
    except Exception as e:
        print(e)
    



def gettransactionlogs(identifier):
    try:
        #query = "SELECT * FROM ev_database.ocpp_logs WHERE identifier='"+identifier+"' LIMIT 25;"
        query = "SELECT ocpp_logs.identifier,ocpp_logs.time,ocpp_logs.msg FROM ocpp_logs WHERE identifier='"+identifier+"' and msg != '' LIMIT 100;"
        df = pd.read_sql(query, psql_engine)
        return df
    except Exception as e:
        print(e)


#  It gives count of chargers of different types like public, home, captive, corporate from excel file
def getChargersTypesCountFromFile():
    try:
        # print("Get details of chargers type wise")
        # print("in Try block")
        df = get_charger_counts_df_from_file()
        df = df.fillna(0)
        publicChargerOnboarded = int(df[df['Charger Type'] == 'Public']['Adjusted Onboarded points'][0])
        corporateChargerOnboarded = int(df[df['Charger Type'] == 'Corporate']['Adjusted Onboarded points'][2])
        homeChargerOnboarded = int(df[df['Charger Type'] == 'Home']['Adjusted Onboarded points'][7])
        captiveChargerOnboarded = int(df[df['Charger Type'] == 'Captive']['Adjusted Onboarded points'][1])
        housingScietyChargerOnboarded = int(df[df['Charger Type'] == 'Housing Society']['Adjusted Onboarded points'][3])
        busChargerOnboarded = int(df[df['Charger Type'] == 'Bus']['Adjusted Onboarded points'][5])
        publicChargerInstalled = int(df[df['Charger Type'] == 'Public']['Installed points'][0])
        corporateChargerInstalled = int(df[df['Charger Type'] == 'Corporate']['Installed points'][2])
        homeChargerInstalled = int(df[df['Charger Type'] == 'Home']['Installed points'][7])
        captiveChargerInstalled = int(df[df['Charger Type'] == 'Captive']['Installed points'][1])
        housingScietyChargerInstalled = int(df[df['Charger Type'] == 'Housing Society']['Installed points'][3])
        busChargerInstalled = int(df[df['Charger Type'] == 'Bus']['Installed points'][5])

        res = {'publicChargerOnboarded' : publicChargerOnboarded,
            'corporateChargerOnboarded' : corporateChargerOnboarded,
            'homeChargerOnboarded' : homeChargerOnboarded,
            'captiveChargerOnboarded' : captiveChargerOnboarded,
            'housingScietyChargerOnboarded' : housingScietyChargerOnboarded,
            'busChargerOnboarded' : busChargerOnboarded,
            'publicChargerInstalled' : publicChargerInstalled,
            'corporateChargerInstalled' : corporateChargerInstalled,
            'homeChargerInstalled' : homeChargerInstalled,
            'captiveChargerInstalled' : captiveChargerInstalled,
            'housingScietyChargerInstalled' : housingScietyChargerInstalled,
            'busChargerInstalled' : busChargerInstalled}
        return res
    except Exception as e:
        print(e)



# '''
# def getTicketMgmt():
#     try:
#         query = "SELECT\
#                 ibi.ITEM_ID,wi.ITEM_ASSIGNED_TO As 'Ticket Owner',wi.ITEM_SUB_TYPE_ID as 'Ticket Type',wi.ITEM_STATUS AS 'Status of Ticket',
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.CHARGER_ID')) AS ChargerId,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.OEM_CONATCT_NO')) AS OEM_Contact,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.OEM_MAIL_ID')) AS OEM_Mail,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.STATE')) AS State,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.MAKE')) AS Make,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.MODEL')) AS Model,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.CHARGING_STATION_NAME')) AS ChargingStationName,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.CITY')) AS City,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.STOP_TIME')) AS CommunicationStopTime,
#                 JSON_UNQUOTE(JSON_EXTRACT(ibi.ITEM_BUSINESS_KEYS,'$.ITEM_CREATED_ON')) AS TicketCreatedOn
#                 from crits.item_business_info ibi
#                 inner join crits.worklist_item wi on wi.ITEM_ID=ibi.ITEM_ID
#                 where ibi.ITEM_ID like 'T-%';"
# '''





# This function returns important chargers for particular state
def getImportantChargers(state):
    try:
        if state == 'Kerala':
            q = "select * from ev_charge_point where state='"+state+"'"
            df = pd.read_sql(q, psql_engine)
            return df
        else:
            return {'ImportantChargers': 60}
    except Exception as e:
        print(e)

######################################################
# Gives charger last transaction time
def get_charger_last_transaction(identifier):
    try:
        q= """SELECT identifier, 
        (stop_time + (interval '5 hours' + interval '30 minutes')) AS end_time
        FROM ev_transaction WHERE (stop_meter_value-start_meter_value)>0.2 and 
        identifier = '"""+identifier+"""' ORDER BY id DESC LIMIT 5"""
        df =  pd.read_sql(q, psql_engine)
        return df
    except Exception as e:
        print(e)







#######################################################

        
# It gives all the Bus Depot Connector Details
def getBusChargerDetails():
    try:
       q = "SELECT * FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML';"
       df = pd.read_sql(q,psql_engine)
       # print("Bus Chager Details", df)
    except Exception as e:
        print(e)
    return df

# Gives charger details based on the requirement
def get_bus_charger_details(region, chargers):
    try:
        if region == 'India' and  chargers =='all':
            #query = "select * from ev_database.ev_charge_point"
            query = "SELECT * FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML';"
            df = pd.read_sql(query, psql_engine)
            # print(df)
        elif region == 'India' and chargers == 'active':
            query = "SELECT * FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' AND cdmstatus=1"
            df = pd.read_sql(query, psql_engine)
        elif region == 'India' and chargers == 'inactive':
            query = "SELECT * FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' AND cdmstatus=2"
            df = pd.read_sql(query, psql_engine)
        elif region == 'India' and chargers == 'faulted':
            query = """SELECT distinct ev_ch_pt.identifier, ev_ch_pt.chargepointvendor, ev_ch_pt.latitude, ev_ch_pt.longitude, ev_ch_pt.city, ev_ch_pt.state, ev_ch_pt.country, ev_ch_pt.cdmstatus, ev_flt.status, ev_ch_pt.devicestatus, ev_ch_pt.postalcode, ev_ch_pt.name
FROM (SELECT * from ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML') ev_ch_pt inner join ev_fault ev_flt on ev_ch_pt.identifier = ev_flt.identifier 
where ev_ch_pt.cdmstatus = 2 AND ev_flt.status = 'Faulted' AND ev_flt.faultstatus = 'Open';"""
            df = pd.read_sql(query, psql_engine)
            df['cdmstatus'] = df['cdmstatus'].replace(2,5)
            df['cdmstatus'] = df['cdmstatus'].replace(1,5)
    except Exception as e:
        print(e)
    return df


# Gives Bus charger status if active or inactive
def get_bus_chager_status(identifier):
    try:
        q = "SELECT cdmstatus FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' and identifier = '"+identifier+"'"
        df =  pd.read_sql(q, psql_engine)
        return df['cdmstatus'].iloc[0] 
    except Exception as e:
        print(e)

# It gives faulted Bus Charger Connectors which are inactive chargers count
def getFaultedBusChargersCount(state, city):
    try:
        today_date =     date.today().strftime('%Y-%m-%d')
        date_before_15_days = (date.today() - timedelta(15)).strftime('%Y-%m-%d')
        # query = "SELECT distinct identifier FROM ev_fault  WHERE DATE(TIMESTAMP) >= '"+date_before_15_days+"' and DATE(TIMESTAMP) <= '"+today_date+"' and status = 'Faulted' AND faultstatus = 'Open';"
        query = "SELECT distinct ev_flt.identifier FROM ev_fault ev_flt INNER JOIN (SELECT identifier from ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML') ev_ch_pt on ev_flt.identifier = ev_ch_pt.identifier WHERE  ev_flt.status = 'Faulted' AND ev_flt.faultstatus = 'Open';"
        df = pd.read_sql(query, psql_engine) 
        if df.empty:
            return 0
        else:
            faulted_identifiers = df['identifier'].to_list()
        # print("Faulted identifiers", faulted_identifiers)
    except Exception as e:
        print(e)
    
    try:
        if city!=None:
            # q = "select identifier from ev_charge_point where cdmstatus = 2 and state = '"+state+"' and city='"+city+"'"
            q = "SELECT identifier FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' AND cdmstatus=2 and city='"+city+"'"
        elif state!=None:
            q = "SELECT identifier FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' AND cdmstatus=2 and state = '"+state+"'"
        else:
            q = "SELECT identifier FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' AND cdmstatus=2"

        df = pd.read_sql(q, psql_engine) 
        if df.empty:
            return 0
        else:
            inactive_identifiers = df['identifier'].to_list()
        # print("Inactive identifiers", inactive_identifiers)
    except Exception as e:
        print(e)
    return len([value for value in faulted_identifiers if value in inactive_identifiers])

# Function returns city names from a given state name in bus depot
def getBusCities(state):
    try:
        q = """SELECT DISTINCT city FROM ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid ~* 'Fleet_TML' AND state ='"""+state+"""'"""
        df = pd.read_sql(q, psql_engine)
        # print(df)
    except Exception as e:
        print(e)
    return df

# Function returns depo names from a given city name in bus depot
def getBusDepos(city):
    try:
        q = """SELECT DISTINCT locationid,latitude,longitude FROM ev_charge_point INNER JOIN ev_connector 
        ON ev_charge_point.id= ev_connector.charge_point_id 
        WHERE locationid ~* 'Fleet_TML' AND city='"""+city+"""'"""
        df = pd.read_sql(q, psql_engine)
        # print(df)
    except Exception as e:
        print(e)
    return df

# Get Bus charger connector details which have became inactive today
def getTodaysInactiveBusChargerDetails(requirement, chargerType):
    today_date = date.today().strftime('%Y-%m-%d')
    try:
        if chargerType!= None:
            if requirement == "count":
                q = "select count(*) as count from ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id where DATE((ev_charge_point.time+ (interval '5 hours' + interval '30 minutes')))= '"+today_date+"' and locationid ~* 'Fleet_TML' and cdmstatus = 2 and type = '"+chargerType+"'"
                # print(q)
                df = pd.read_sql(q,psql_engine)
                return df
            elif requirement == "details":
                q = "select identifier,connector_id, name, city from ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id where DATE((ev_charge_point.time+ (interval '5 hours' + interval '30 minutes')))= '"+today_date+"' and locationid ~* 'Fleet_TML' and cdmstatus = 2 and type = '"+chargerType+"'"
                df = pd.read_sql(q,psql_engine)
                if df.empty:
                    return pd.DataFrame()
                else:
                    today_inactive_identifiers = df['identifier'].to_list()
                    # print(today_inactive_identifiers)
                    new_df = pd.DataFrame()
                    for identifier in today_inactive_identifiers:
                        inactive_duration = get_inactive_duration(identifier)
                        df_r = get_charger_other_details(identifier)
                        try:
                            if df_r.empty:
                                df_r = pd.DataFrame(columns=['identifier'])
                                # print("Identifier for empty dataframe", identifier)
                                df_r['identifier'] = list([identifier])
                                # print(df_r)
                        except Exception as e:
                            print(e)
                        df_r['inactive_duration'] = round((inactive_duration/60),2)
                        new_df = new_df.append(df_r)
                    # print(len(new_df))
                    # print(len(df))
                    # df_final.loc[df_final['csmstatus'] == 1, 'inactive_duration'] = 'NA'
                    df_final = pd.merge(df,new_df, on='identifier', how='inner')
                    df_final['count'] = len(df_final)
                    # df_final = df_final.sort_values(by='inactive_duration', ascending = False)
                    # print("Printing info of dataframe", df_final.info())
                    # print(df_final)
                    return df_final
        else:
            if requirement == "count":
                q = "select count(*) as count from ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id where DATE((ev_charge_point.time+ (interval '5 hours' + interval '30 minutes')))= '"+today_date+"' and locationid ~* 'Fleet_TML' and cdmstatus = 2"
                df = pd.read_sql(q,psql_engine)
                return df
            elif requirement == 'details':
                q = "select identifier,connector_id, name, city from ev_charge_point INNER JOIN ev_connector ON ev_charge_point.id= ev_connector.charge_point_id where DATE((ev_charge_point.time+ (interval '5 hours' + interval '30 minutes')))= '"+today_date+"' and locationid ~* 'Fleet_TML' and cdmstatus = 2"
                df = pd.read_sql(q,psql_engine)
                today_inactive_identifiers = df['identifier'].to_list()
                # print(today_inactive_identifiers)
                new_df = pd.DataFrame()
                for identifier in today_inactive_identifiers:
                    inactive_duration = get_inactive_duration(identifier)
                    df_r = get_charger_other_details(identifier)
                    try:
                        if df_r.empty:
                            df_r = pd.DataFrame(columns=['identifier'])
                            # print("Identifier for empty dataframe", identifier)
                            df_r['identifier'] = list([identifier])
                            # print(df_r)
                    except Exception as e:
                        print(e)
                    df_r['inactive_duration'] = round((inactive_duration/60),2)
                    new_df = new_df.append(df_r)
                # print(len(new_df))
                # print(len(df))
                df_final = pd.merge(df,new_df, on='identifier', how='inner')
                df_final['count'] = len(df_final)
                return df_final
    except Exception as e:
        print(e)


#This gives count of connector against each bus depot
def getCountConnectorBusDepot():
    ldf=[]
    try:
        q="""select distinct locationid from ev_charge_point WHERE locationid ~* 'Fleet_TML' """
        df = pd.read_sql(q,psql_engine)
        locationid_list=df['locationid'].to_list()
        # print(locationid_list)
        
        for i in locationid_list:
            query=""" SELECT locationid,longitude,latitude,COUNT(connector_id) FROM ev_charge_point INNER JOIN ev_connector 
            ON ev_charge_point.id= ev_connector.charge_point_id WHERE locationid='"""+i+"""' GROUP BY 
            locationid,longitude,latitude """
            df2 = pd.read_sql(query,psql_engine)
            ldf.append(df2)
        locid_df = pd.concat([*ldf],ignore_index=True)
        # print(locid_df)
        return locid_df       
    except Exception as e:
        print(e)
        

# This is a CIDS Dashboard
def dashboardCIDS(stationName):
    inde=[]
    today_date = date.today().strftime('%Y-%m-%d')
    tdf=[]
    q=""" SELECT name,cdmstatus,identifier,connector_id,status FROM ev_charge_point INNER JOIN ev_connector 
    ON ev_charge_point.id= ev_connector.charge_point_id 
    WHERE locationid='"""+stationName+"""'; """ 
    df = pd.read_sql(q, psql_engine)
    df['startSoC']=0
    df['CurrentSoC']=0
    df['remTime']=0
    # print(df)
    # print('xxxxxxxxxxxxxxxx')
    l=len(df.loc[(df.cdmstatus==1) & (df.status=='Charging')])
    id=df.loc[(df.cdmstatus==1) & (df.status=='Charging')]
    # print(l)
    if l>0:
        identifier_list = id['identifier'].to_list()
        # print(identifier_list)
        transaction_id_df=pd.DataFrame()

        # print(identifier_list)
        for i in identifier_list:
            query=""" SELECT transactionid,identifier,connectorid,start_time FROM ev_transaction WHERE
            identifier='"""+i+"""' and date(start_time)='"""+today_date+"""' order by start_time desc limit 1; """
            df2 = pd.read_sql(query, psql_engine)
            tdf.append(df2)
        transaction_id_df = pd.concat([*tdf],ignore_index=True)
        # print(transaction_id_df)
        for j in range(len(transaction_id_df)):
            # print(transaction_id_df.iloc[j]['identifier'])
            q=""" SELECT identifier,TIME,
            substring(msg from 'Connector Id: (\d+)') AS connector_id,
            substring(msg from 'Wh SoC: (\d+)') AS SoC,
            substring(msg from 'Transaction Id: (\d+)') AS transaction_id
            FROM ocpp_logs WHERE identifier='"""+str(transaction_id_df.iloc[j]['identifier'])+ """'
            and msg ~* 'SoC' AND 
            substring(msg from 'Transaction Id: (\d+)')='"""+str(transaction_id_df.iloc[j]['transactionid'])+"""'
            ORDER BY TIME desc; """ 
            df3=pd.read_sql(q, psql_engine)
            # print(q)
            # print(df3)
            if len(df3)>0:
                start_soc=df3.iloc[-1]
                end_soc=df3.iloc[0]
                # print('start_soc=',start_soc['soc'])
                # print('end_soc=',end_soc['soc'])
                
                i=df.loc[(df['identifier']==transaction_id_df.iloc[j]['identifier']) & df['connector_id']==transaction_id_df.iloc[j]['connectorid']].index.values
                df.loc[i,'startSoC']=start_soc['soc']
                df.loc[i,'CurrentSoC']=end_soc['soc']
                if int(end_soc['soc']) <= 85:
                    df.loc[i,'remTime']=(85-int(end_soc['soc'])) + 30
                elif int(end_soc['soc']) > 85 and int(end_soc['soc']) <= 95:
                    df.loc[i,'remTime']=((95-int(end_soc['soc'])) * 2 + 10)
                else:  df.loc[i,'remTime']="Completing..."
    # print (df.columns)
    return df

def getChargingSessionBusDepot(requirement, need,  state, city):
    try:
        today_date = date.today().strftime('%Y-%m-%d')
        if need == 'count' and requirement == 'Charging':
            if state!= None:
                # query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"'"
                q = "select identifier from ev_charge_point where state ='"+state+"' and locationid ~* 'Fleet_TML'"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            elif city!= None:
                # query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"' and ev_charge_point.city='"+city+"'"
                q = "select identifier from ev_charge_point where city ='"+city+"' and locationid ~* 'Fleet_TML'"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            else:
            #    query = "SELECT count(ev_charge_point.identifier) as ongoing_charging_sessions from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '';"       
                q = "select identifier from ev_charge_point where locationid ~* 'Fleet_TML';"
                query = "SELECT distinct EVSE_ID AS identifier  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"

            df = pd.read_sql(q,psql_engine)
            identifiers = df['identifier'].to_list()
            mydb = create_connection_mysql()
            df_i = pd.read_sql(query, mydb) 
            mydb.dispose()
            df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
            # print(df_i)
            # print(len(df_i))
            df_i['ongoing_charging_sessions'] = len(df_i)
            return df_i[['ongoing_charging_sessions']].head(1)
        elif need == 'details' and requirement == 'Charging':
            if state!= None:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"'"
                q = "select identifier, name, city, state from ev_charge_point where state ='"+state+"' and locationid ~* 'Fleet_TML'"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            elif city!= None:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '' and ev_charge_point.state = '"+state+"' and ev_charge_point.city='"+city+"'"
                q = "select identifier, name, city, state from ev_charge_point where city ='"+city+"' and locationid ~* 'Fleet_TML'"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"        
            else:
                # query = "SELECT ev_charge_point.name,ev_charge_point.state,ev_charge_point.city, ev_charge_point.identifier, ev_connector.connector_id from ev_charge_point, ev_connector where ev_connector.status = 'Charging' and ev_charge_point.id=ev_connector.charge_point_id and ev_charge_point.state != '';"               
                q = "select identifier, name, city, state from ev_charge_point where locationid ~* 'Fleet_TML';"
                query = "SELECT distinct EVSE_ID AS identifier, CONNECTOR_ID, SOURCE_IDENTIFIER  FROM rms_billing.ev_booking_mst where USAGE_STATUS = 'CHARGING_INPROGRESS';"
            df = pd.read_sql(q,psql_engine)
            mydb = create_connection_mysql()
            df_i = pd.read_sql(query, mydb) 
            mydb.dispose()
            df_res = pd.merge(df,df_i, how='inner', on='identifier')
            # print (df_res)
            return df_res
        elif need == 'count' and requirement == 'Completed':
            if state!= None and city== None:
                q = "select identifier from ev_charge_point where state ='"+state+"' and locationid ~* 'Fleet_TML'"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and cast(REQ_START_DATE as date) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                # print(len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
            elif state!= None and city!= None:
                q = "select identifier from ev_charge_point where state ='"+state+"' and city='"+city+"' and locationid ~* 'Fleet_TML'"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and cast(REQ_START_DATE as date) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                # print(len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
            else:
                # query = "SELECT count(EVSE_ID) as completed_charging_sessions from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0;"
                q = "select identifier from ev_charge_point where locationid ~* 'Fleet_TML';"
                df = pd.read_sql(q,psql_engine)
                identifiers = df['identifier'].to_list()
                query = "SELECT EVSE_ID as identifier from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 and cast(REQ_START_DATE as date) ='"+today_date+"'"
                mydb = create_connection_mysql()
                df_i = pd.read_sql(query, mydb) 
                mydb.dispose()
                df_i = (df_i[df_i['identifier'].isin(identifiers)]).reset_index(drop=true).copy()
                # print(df_i)
                # print(len(df_i))
                df_i['completed_charging_sessions'] = len(df_i)
                return df_i[['completed_charging_sessions']].head(1)
                # query = "SELECT * from rms_billing.ev_booking_mst where USAGE_STATUS = 'Completed' and UNITS > 0 limit 10;"        
        # print (df)
        return df
    except Exception as e:
        print(e) 
        

def TestBus():
    q=""" select distinct locationid from ev_charge_point WHERE locationid ~* 'Fleet_TML' """
    # print(q,type(q))
    df=pd.read_sql(q,psql_engine)
    # print(df,type(df))
    return df

################################################################

## Analytics


# Get Zero Transaction unit counts
def getZeroTransactionAnalytics(start_date, end_date):
    try:
        q=""" SELECT ev_transaction.identifier,ev_charge_point.chargepointvendor,
        ev_charge_point.chargepointmodel,ev_charge_point.name,ev_charge_point.state,
		  ev_charge_point.city,COUNT(*) 
        FROM ev_transaction inner join ev_charge_point on 
        ev_charge_point.identifier = ev_transaction.identifier 
        WHERE ev_transaction.stop_meter_value IS NOT NULL AND 
        (ev_transaction.stop_meter_value::numeric - ev_transaction.start_meter_value::numeric)=0 
        AND Date((ev_transaction.start_time + (interval '5 hours' + interval '30 minutes'))) 
        BETWEEN '"""+start_date+"""' AND '"""+end_date+"""' 
        GROUP BY ev_transaction.identifier,ev_charge_point.chargepointvendor,
        ev_charge_point.chargepointmodel,ev_charge_point.name,ev_charge_point.state,
		  ev_charge_point.city ORDER BY COUNT desc """
        # print(q)
        df = pd.read_sql(q,psql_engine)
        # print(df)
        if df.empty:
            return pd.DataFrame()
        else:
            return df
    except Exception as e:
        print(e)

# Get inative charger count on csv due to network issues
def getInactiveCountNetworkIssues():
    q="""SELECT distinct identifier FROM analytics_msg_logs
    WHERE ACTION='Status Notification Request' AND connector_id='0'
    AND errorcode='NoError' AND status='Available' """
    
    df=pd.read_sql(q,psql_engine)
    identifer_list=df['identifier'].to_list()
    # print (identifer_list)
    pool=multiprocessing.Pool(processes=8)
    data=pool.map(worker,identifer_list)
    df1=pd.DataFrame(data)
    return df1.to_csv('/home/evadmin/EV_NOC/Backend/app/Analytics/NetworkIssue.csv',index=False)

def worker(identifier):
    return NetworkIssue(identifier)

def NetworkIssue(identifier):
    count=0
    dict={}
    # print(count)
    q1="""select identifier,time,action from analytics_msg_logs
            where identifier='"""+identifier+"""'
            and ACTION='Connection Lost/Disconnected'"""
    q2="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            and ACTION='Connection Initiated'"""
    q3="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            AND ACTION='Status Notification Request' AND connector_id='0'
            AND errorcode='NoError' AND status='Available'"""
    df3=pd.read_sql(q3,psql_engine)
    if df3.empty :
        pass
        # return 0
    else:
        df =pd.read_sql(q1,psql_engine)
        df2=pd.read_sql(q2,psql_engine)
        df4=[df,df2,df3]
        res=pd.concat(df4, join='inner')
        temp=res.sort_values(by=['time']).reset_index(drop=True)
        #print(temp)
        res=pd.concat(df4).sort_values(by=['time']).reset_index(drop=True)
        for i in range(len(temp)):
            if temp.iloc[i,2]=='Connection Lost/Disconnected':
                i=i+1
                if i<len(temp) and temp.iloc[i,2]=='Connection Initiated':
                    i=i+1
                    if i<len(temp) and temp.iloc[i,2]=='Status Notification Request':
                        # print(temp.iloc[i-2,1],temp.iloc[i-2,2])
                        # print(temp.iloc[i-1,1],temp.iloc[i-1,2])
                        # print(temp.iloc[i,1],temp.iloc[i,2])
                        count=count+1
                        
        # print (count)
        
        q4="select name,chargepointvendor,chargepointmodel,city from ev_charge_point where identifier='"+identifier+"'"
        df5=pd.read_sql(q4,psql_engine)
        dict['id']=identifier
        dict['name']=df5.iloc[0,0]
        dict['manufacturer']=df5.iloc[0,1]
        dict['model']=df5.iloc[0,2]
        dict['city']=df5.iloc[0,3]
        dict['count']=count
    return dict

# Read the csv of Inactive Chargers due to Network Issues
def readCSVNetworkIssues():
    data=pd.read_csv('/home/evadmin/EV_NOC/Backend/app/Analytics/NetworkIssue.csv')
    sorted_data = data.sort_values(by=["count"], ascending=False)

    return sorted_data

# Get the view details for inatcive chargers due to Network Issues
def viewDetailsNetworkIssues(identifier):
    # count=0
    list=[]
    details=pd.DataFrame()
    dict={}
    q1="""select identifier,time,action from analytics_msg_logs
            where identifier='"""+identifier+"""'
            and ACTION='Connection Lost/Disconnected'"""
    q2="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            and ACTION='Connection Initiated'"""
    q3="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            AND ACTION='Status Notification Request' AND connector_id='0'
            AND errorcode='NoError' AND status='Available' """
    df3=pd.read_sql(q3,psql_engine)
    if df3.empty :
        pass
        # return 0
    else:
        df =pd.read_sql(q1,psql_engine)
        df2=pd.read_sql(q2,psql_engine)
        df4=[df,df2,df3]
        res=pd.concat(df4, join='inner')
        temp=res.sort_values(by=['time']).reset_index(drop=True)
        #print(temp)
        res=pd.concat(df4).sort_values(by=['time']).reset_index(drop=True)
        for i in range(len(temp)):
            if temp.iloc[i,2]=='Connection Lost/Disconnected':
                i=i+1
                if i<len(temp) and temp.iloc[i,2]=='Connection Initiated':
                    i=i+1
                    if i<len(temp) and temp.iloc[i,2]=='Status Notification Request':
                        # print(temp.iloc[i-2,1],temp.iloc[i-2,2])
                        # print(temp.iloc[i-1,1],temp.iloc[i-1,2])
                        # print(temp.iloc[i,1],temp.iloc[i,2])
                        # count=count+1
                        dict['inactive']=str(temp.iloc[i-2,1])
                        dict['active']=str(temp.iloc[i-1,1])
                        duration=temp.iloc[i-1,1]-temp.iloc[i-2,1]
                        d=str(duration)
                        dict['duration']=d[7:]
                        details=pd.DataFrame.from_dict(dict,orient='index')
                        details=details.transpose()
                        list.append(details)
        details_final_df = pd.concat([*list],ignore_index=True)                

    return details_final_df



# Get inative charger count on csv due to Power Failure
def getInactiveCountPowerFailure():
    q="""SELECT distinct identifier FROM analytics_msg_logs
    WHERE ACTION='Boot Notification Request' """
    
    df=pd.read_sql(q,psql_engine)
    identifer_list=df['identifier'].to_list()
    # print (identifer_list)
    pool=multiprocessing.Pool(processes=8)
    data=pool.map(worker2,identifer_list)
    df1=pd.DataFrame(data)
    return df1.to_csv('/home/evadmin/EV_NOC/Backend/app/Analytics/PowerFailure.csv',index=False)

def worker2(identifier):
    return PowerFailure(identifier)

def PowerFailure(identifier):
    count=0
    dict={}
    # print(count)
    q1="""select identifier,time,action from analytics_msg_logs
            where identifier='"""+identifier+"""'
            and ACTION='Connection Lost/Disconnected'"""
    q2="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            and ACTION='Connection Initiated'"""
    q3="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            AND ACTION='Boot Notification Request' """
    df3=pd.read_sql(q3,psql_engine)
    if df3.empty :
        pass
        # return 0
    else:
        df =pd.read_sql(q1,psql_engine)
        df2=pd.read_sql(q2,psql_engine)
        df4=[df,df2,df3]
        res=pd.concat(df4, join='inner')
        temp=res.sort_values(by=['time']).reset_index(drop=True)
        #print(temp)
        res=pd.concat(df4).sort_values(by=['time']).reset_index(drop=True)
        for i in range(len(temp)):
            if temp.iloc[i,2]=='Connection Lost/Disconnected':
                i=i+1
                if i<len(temp) and temp.iloc[i,2]=='Connection Initiated':
                    i=i+1
                    if i<len(temp) and temp.iloc[i,2]=='Boot Notification Request':
                        # print(temp.iloc[i-2,1],temp.iloc[i-2,2])
                        # print(temp.iloc[i-1,1],temp.iloc[i-1,2])
                        # print(temp.iloc[i,1],temp.iloc[i,2])
                        count=count+1
        # print(count)
        q4="select name,chargepointvendor,chargepointmodel,city from ev_charge_point where identifier='"+identifier+"'"
        df5=pd.read_sql(q4,psql_engine)
        dict['id']=identifier
        dict['name']=df5.iloc[0,0]
        dict['manufacturer']=df5.iloc[0,1]
        dict['model']=df5.iloc[0,2]
        dict['city']=df5.iloc[0,3]
        dict['count']=count
    return dict

# Read the csv of Inactive Chargers due to Power Failure
def readCSVPowerFailure():
    data=pd.read_csv('/home/evadmin/EV_NOC/Backend/app/Analytics/PowerFailure.csv')
    sorted_data = data.sort_values(by=["count"], ascending=False)

    return sorted_data

# Get the view details for inatcive chargers due to Power Failure
def viewDetailsPowerFailure(identifier):
    # count=0
    list=[]
    details=pd.DataFrame()
    dict={}
    q1="""select identifier,time,action from analytics_msg_logs
            where identifier='"""+identifier+"""'
            and ACTION='Connection Lost/Disconnected'"""
    q2="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            and ACTION='Connection Initiated'"""
    q3="""select identifier,time,action from analytics_msg_logs 
            where identifier='"""+identifier+"""'
            AND ACTION='Boot Notification Request'"""
    df3=pd.read_sql(q3,psql_engine)
    if df3.empty :
        pass
        # return 0
    else:
        df =pd.read_sql(q1,psql_engine)
        df2=pd.read_sql(q2,psql_engine)
        df4=[df,df2,df3]
        res=pd.concat(df4, join='inner')
        temp=res.sort_values(by=['time']).reset_index(drop=True)
        #print(temp)
        res=pd.concat(df4).sort_values(by=['time']).reset_index(drop=True)
        for i in range(len(temp)):
            if temp.iloc[i,2]=='Connection Lost/Disconnected':
                i=i+1
                if i<len(temp) and temp.iloc[i,2]=='Connection Initiated':
                    i=i+1
                    if i<len(temp) and temp.iloc[i,2]=='Boot Notification Request':
                        # print(temp.iloc[i-2,1],temp.iloc[i-2,2])
                        # print(temp.iloc[i-1,1],temp.iloc[i-1,2])
                        # print(temp.iloc[i,1],temp.iloc[i,2])
                        # count=count+1
                        dict['inactive']=str(temp.iloc[i-2,1])
                        dict['active']=str(temp.iloc[i-1,1])
                        duration=temp.iloc[i-1,1]-temp.iloc[i-2,1]
                        d=str(duration)
                        dict['duration']=d[7:]
                        details=pd.DataFrame.from_dict(dict,orient='index')
                        details=details.transpose()
                        list.append(details)
        details_final_df = pd.concat([*list],ignore_index=True)                

    return details_final_df

# Get Weekly Charging Session Trend
def chargingSessionTrendWeekly(day):
    da={}
    list1=[]
    list2=[]
    weekday_mapping = {
        "MO": rrule.MO,
        "TU": rrule.TU,
        "WE": rrule.WE,
        "TH": rrule.TH,
        "FR": rrule.FR,
        "SA": rrule.SA,
        "SU": rrule.SU
    }
    whichday=weekday_mapping[day]
    # df2=pd.DataFrame()
    today = date.today()
    list2.clear()
    for i in range (1,11):
        list2.append((today + relativedelta(weekday=whichday(-i))).strftime('%Y-%m-%d'))
    
    for days in list2:
        query="""  SELECT EXTRACT (HOUR FROM (start_time + (interval '5 hours' + interval '30 minutes'))) 
                AS HOUR, COUNT(*) from ev_transaction WHERE 
                DATE((start_time + (interval '5 hours' + interval '30 minutes')))='"""+days+"""' 
                and (stop_meter_value::numeric-start_meter_value::numeric)>0.2
                GROUP BY HOUR ORDER BY HOUR; """
        df1=pd.read_sql(query,psql_engine)
        da[days] = df1['count'].to_list()

    # max_len = max([len(da[key]) for key in da.keys()])

    # # pad the lists with zeros to match the length of the longest list
    # for key in da.keys():
    #     da[key].extend([0] * (max_len - len(da[key])))

    # # calculate the mean
    # mean = [sum([da[key][i] for key in da.keys()]) / len(da.keys()) for i in range(max_len)]

    # print(mean)

    # list1.append(list2)
    # tuple1=tuple(list2)
    # pool = multiprocessing.Pool()
    # pool = multiprocessing.Pool(processes=7)
    # data = pool.map(worker,list2)
    # df2=pd.DataFrame(data)
    # print(type(data))
    return da

# def worker(date):
#     query=""" SELECT EXTRACT (HOUR FROM (start_time + (interval '5 hours' + interval '30 minutes'))) 
#     AS HOUR,COUNT(*) from ev_transaction WHERE 
#     DATE((start_time + (interval '5 hours' + interval '30 minutes')))='"""+date+"""' 
#     and (stop_meter_value-start_meter_value)>0.2
#     GROUP BY HOUR ORDER BY HOUR; """
#     df1=pd.read_sql(query,psql_engine)
#     new_data = {}
#     new_data[date] = df1['count'].to_list()
#     return new_data
    # return df1

# Get Charging Session Trend for one day before
def chargingSessionTrendDaily(start_date):
    # sd=ist_toUTC(start_date+' 00:00:00')
    # end_date=sd+timedelta(1)
    # print(sd)
    # print(end_date)
    # start_date = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    try:
        query="""SELECT EXTRACT(HOUR FROM (start_time + INTERVAL '5 hours 30 minutes')) AS hour, 
                  COUNT(*) FROM ev_transaction WHERE DATE((start_time + INTERVAL '5 hours 30 minutes')) = '"""+start_date+"""'
    AND (stop_meter_value::numeric - start_meter_value::numeric) > 0.2 GROUP BY hour ORDER BY hour;"""
        df1=pd.read_sql(query,psql_engine)
        return df1
    except Exception as e:
        print(e)

def ist_toUTC(start_date):
    utc_zone = tz.gettz('UTC')
    local_zone = tz.gettz('Asia/Kolkata')
    local_time = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    utc_time = local_time.astimezone(utc_zone)
    return utc_time

def StarHighway():
    # print(time)
    query = "select name,state,city,identifier from ev_charge_point where name is not null"
    df = pd.read_sql(query, psql_engine)
    df['isStar']=False
    df['isHighWay']=False
    with open('/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json', 'r') as f:
        data = json.load(f)
    for i in data:
        ind=df.loc[df['identifier']==i['identifier']].index.values[0]
        df.loc[ind,'isStar']=True
        # print(df.iloc[ind])
    with open('/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json', 'r') as f:
        dataHighway=json.load(f)
    for j in dataHighway:
        if (df.loc[df['identifier']==j['identifier']].index.values)>0:
            ind=df.loc[df['identifier']==j['identifier']].index.values[0]
            # print(ind)
            df.loc[ind,'isHighWay']=True
    return df

#############

#Charger Hits

def getIdentifierBatches():
    
    q="""SELECT * FROM ev_charge_point WHERE cdmstatus <> 4 AND devicestatus='Managed'"""
    # print(q)
    df =pd.read_sql(q,psql_engine)
    # print (df)
    identifiers= df['identifier'].to_list()
    batch_size = len(identifiers)//2
    
    batch1 = identifiers[:batch_size]
    batch2 = identifiers[batch_size:]
    
    # Create a dictionary to hold the batches
    data = {
        "batch1": batch1,
        "batch2": batch2
    }
    id_batches="/home/evadmin/EV_NOC/Backend/app/controllers/identifier_batch.json"
    with open(id_batches, "w") as json_file:
        json.dump(data, json_file)
    
    performChargerHits()
    

def performChargerHits():
    newlist=[]
    final_df=pd.DataFrame()
    id_batches="/home/evadmin/EV_NOC/Backend/app/controllers/identifier_batch.json"
    with open(id_batches, "r") as json_file:
        data=json.load(json_file)
    # print(data["batch1"])
    # print(len(data))
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    folder_path = os.path.join('/home/evadmin/EV_NOC/Backend/app/controllers/ChargerHits', current_date)
    os.makedirs(folder_path, exist_ok=True)
    
    
    
    if len(data)==0:
        getIdentifierBatches()
    else:    
        keys=list(data.keys())
        new_batch_size=40
        identifier_batches = [data[keys[0]][i:i+new_batch_size] for i in range(0, len(data[keys[0]]), new_batch_size)]
        
        tup_le=""
     
        for i in identifier_batches:
            # print(i[4])
            if len(i)==1:
                tup_le=str(tuple(i)).replace(",","")
            else:
                tup_le=str(tuple(i))

            q1=""" select ecp.identifier, ecp.name,ollogs.count,  ecp.chargepointvendor, ecp.chargepointmodel, ecp.address, ecp.city, ecp.state, ecp.type from ev_charge_point ecp, 
            (select identifier, count(identifier) as count from ocpp_logs ol WHERE ol.time BETWEEN CURRENT_DATE - (interval '5 hours' + '30 minutes') AND CURRENT_DATE + (INTERVAL '18 hours' + '30 minutes') 
             AND identifier in """+tup_le+"""
            group by ol.identifier order by count(ol.identifier) desc limit 40) ollogs
            where ecp.identifier = ollogs.identifier """
            
            print("running ",q1)
            dfnew =pd.read_sql(q1,psql_engine)
            newlist.append(dfnew)
        final_df = pd.concat(newlist,ignore_index=True)
        # final_df.to_excel('/datadrive/EV_NOC/Backend_DEV/app/Testing_BKE/HitsSheet.xlsx')
        if os.path.isfile(folder_path+"//chargerHits.csv"):
            final_df.to_csv(folder_path+"//chargerHits.csv", index=False, mode='a', header=False)
        else:
            final_df.to_csv(folder_path+"//chargerHits.csv", index=False, mode='a', header=True)
            # print(final_df)
        
        del data[keys[0]]
        with open(id_batches, "w") as json_file:
            json.dump(data, json_file)
            
    return ("successful")


# Read the csv of daily charger hits
def readCSVChargerHits(select_date):
    folder_path = os.path.join('/home/evadmin/EV_NOC/Backend/app/controllers/ChargerHits', select_date)
    os.makedirs(folder_path, exist_ok=True)
    
    data=pd.read_csv(folder_path+"//chargerHits.csv")
    sorted_data = data.sort_values(by=["count"], ascending=False)

    return sorted_data

#### Analysis on Charger Hits

def analysisOnChargerHits():
    dir = os.listdir('/home/evadmin/EV_NOC/Backend/app/controllers/ChargerHits/')
    path='/home/evadmin/EV_NOC/Backend/app/controllers/ChargerHits/'
    li=[]
    today = datetime.now().date()
    end_date = today - timedelta(days=1)
    df=pd.DataFrame()
    for i in range(1,16):
        end_date = today - timedelta(days=i)
        # print(end_date)
        try:
            df=pd.read_csv(path+str(end_date)+"/chargerHits.csv")
            df['date']=str(end_date)
            li.append(df.nlargest(25,'count'))
        except:
            # df['date']=str(end_date)
            # li.append(pd.DataFrame({'count':[0]*25}))
            print('exception')
            pass
    
    new_df=pd.concat(li,ignore_index=True)
    grouped_df = new_df.groupby('identifier')['count'].agg(sum='sum', occurrence='size')
    grouped_df['average']=grouped_df["sum"]/grouped_df["occurrence"]
    # print(grouped_df)
    pivoted_df=new_df.pivot_table(index='identifier', columns='date', values='count').fillna(0)
    # pivoted_df = new_df.pivot(index='identifier', columns='date', values='count').fillna(0)
    # Rename the columns to remove the 'date' level
    pivoted_df.columns = pivoted_df.columns.get_level_values('date')
    # Reset the index to bring 'id' back as a column
    pivoted_df = pivoted_df.reset_index()
    # Display the pivoted DataFrame
    # print(pivoted_df.columns.get_level_values('date'))
    merge_df=pd.merge(grouped_df,pivoted_df,on='identifier',how='inner')
    
    merge_df.sort_values(by='average',ascending=False,inplace=True)
    # print(merge_df)
    
    return merge_df

def getFaultDetails(identifier):
    
    q1=""" select name,state,city,identifier,vendorspeceficcode,faultcode,faultdescription,vendorspeceficdescription,
            TIMESTAMP + (interval '5 hours' + interval '30 minutes')
            AS time_IST FROM ev_fault where faultstatus='Open' 
            and identifier='"""+identifier+"""' order by id Desc limit 5;"""
    df =pd.read_sql(q1,psql_engine)
    # print(q1)
    # print (df)
    return df

def getOtherDetails(identifier):
    q="""SELECT (EXTRACT(EPOCH from CURRENT_TIMESTAMP)-EXTRACT(EPOCH from TIME))/60
        as minutes_since_inactive,identifier,NAME,city
        FROM ev_charge_point WHERE ev_charge_point.identifier='"""+identifier+"""'"""
        
    df=pd.read_sql(q,psql_engine)
    query = """
            SELECT model
            FROM resourceinventory.ev_location_contacteo 
            INNER JOIN  resourceinventory.ev_locationeo_location_partners
            ON ev_location_contacteo.contact_id = ev_locationeo_location_partners.location_partners_contact_id
            INNER JOIN resourceinventory.ev_locationeo
            ON ev_locationeo_location_partners.ev_locationeo_location_id = ev_locationeo.location_id
            INNER JOIN resourceinventory.ev_locationeo_evses
            ON ev_locationeo_evses.ev_locationeo_location_id = ev_locationeo.location_id
            INNER JOIN resourceinventory.ev_evseeo
            ON ev_locationeo_evses.evses_evse_id = ev_evseeo.evse_id 
            -- INNER JOIN ev_locationeo_location_spocs
            -- ON ev_locationeo_location_spocs.ev_locationeo_location_id = ev_locationeo.location_id
            WHERE evse_code = '"""+identifier+"""'""" 
    
    mydb = create_connection_mysql()
    df1 = pd.read_sql(query, mydb) 
    mydb.dispose()
    df['chargepointmodel']= df1["model"]      
    return df

# abhishek - start
def fetchData(evsecode):
    conn=create_connection_mysql()
    query=f"""SELECT evse_code,model,location_type
            FROM resourceinventory.ev_location_contacteo 
            INNER JOIN  resourceinventory.ev_locationeo_location_partners
            ON ev_location_contacteo.contact_id = ev_locationeo_location_partners.location_partners_contact_id
            INNER JOIN resourceinventory.ev_locationeo
            ON ev_locationeo_location_partners.ev_locationeo_location_id = ev_locationeo.location_id
            INNER JOIN resourceinventory.ev_locationeo_evses
            ON ev_locationeo_evses.ev_locationeo_location_id = ev_locationeo.location_id
            INNER JOIN resourceinventory.ev_evseeo
            ON ev_locationeo_evses.evses_evse_id = ev_evseeo.evse_id 
            WHERE evse_code IN """+str(tuple(evsecode))
    result = pd.read_sql(query,conn)
    result=result.fillna('')
    final_result=result.to_dict(orient='records')
    return final_result
def modeltype(data):
    final_results=fetchData(data.identifiers)
    return final_results
# abhishek - end 
