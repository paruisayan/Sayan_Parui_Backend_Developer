import datetime 
from logging.config import IDENTIFIER
import math
from multiprocessing.dummy import Array
from sqlalchemy import create_engine, true
import urllib
import pymysql

from fastapi import Query
import numpy as np
from models import service
import pandas as pd
import json
import requests
import string   
import random 
import ast

class _stateChargerStatus:
    def __init__(self) -> None:
        self.data = service.getChargerDetails()
        # print('service ')

    @property
    def serviceAnalysis(self):
        self.data = self.data[['identifier','state','type','country','city','latitude','longitude','cdmstatus','chargepointvendor']]
        uniqueSate = self.data['state'].unique()
        # print(uniqueSate)
        result = [{'state':i,\
                   'total':len(self.data[self.data['state']==i]),\
                   'active':len(self.data[(self.data['cdmstatus']==1) & (self.data['state']==i)]),\
                   'inactive':len(self.data[(self.data['cdmstatus']==2) & (self.data['state']==i)])} for i in uniqueSate] 
        totalCharger = len(self.data)
        activeCharger = len(self.data[self.data['cdmstatus']==1])   
        inactiveCharger = len(self.data[self.data['cdmstatus']==2])   
        return {'totalCharger':totalCharger,'activeCharger':activeCharger,'inactiveCharger':inactiveCharger,'data':result}


class _stateWiseChargerStatus:
    def __init__(self,region) -> None:
        self.data = service.getChargerDetails()
        # self.data = service.get_charger_details()
        self.filename = '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
        self.region = region
        # print(self.region)
        
    
    @property
    def serviceAnalysis(self):
        with open(self.filename, 'r') as openfile:
            json_object = json.load(openfile)
        # print(json_object)    
        self.data = self.data[['name','identifier','state','type','country','city','latitude','longitude','cdmstatus','chargepointvendor']]
        if self.region=='India':
            self.data = self.data[self.data['cdmstatus']==2]
            for id in json_object:
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 0, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        else:
            self.data = self.data[(self.data['state']==self.state) & (self.data['cdmstatus']==2)]
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 0, inplace=True)
        # print(self.data.isnull().sum())
        self.data.reset_index(drop=True, inplace=True)
        # print(self.data)
        data = self.data.transpose()
        return json.loads(data.to_json()) 


class _chargerStatus:
    def __init__(self,country, chargers, state, city, postalcode) -> None:
        # self.data = service.getChargerDetails()
        self.country = country
        # print(self.country)
        self.chargers = chargers
        # print(self.chargers)
        self.state = state
        # print(self.state)
        self.city = city
        # print(self.city)
        self.postalcode = postalcode
        # print(self.postalcode)
        self.data = service.get_charger_details(country, chargers)
        self.filename = '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
        
        
    @property
    def serviceAnalysis(self):
        with open(self.filename, 'r') as openfile:
            json_object = json.load(openfile)
        self.data = self.data[self.data['devicestatus'] == 'Managed']
        # print(json_object) 
        if self.country=='India' and self.chargers == 'faulted':
            self.data = self.data[['identifier','country','city','state','name','postalcode','cdmstatus','latitude','longitude','status']]
        else:  
            self.data = self.data[['identifier','country','city','state','name','postalcode','cdmstatus','latitude','longitude','time']]

        # For pincode level
        if self.country=='India' and self.chargers == 'all' and self.postalcode!= None:
            self.data = self.data[(self.data['postalcode'] == self.postalcode)]
            self.data['charger_status'] = 0
            # for id in json_object:
            #     self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active' and self.postalcode!= None:
            self.data = self.data[(self.data['cdmstatus']==1)  & (self.data['postalcode'] == self.postalcode)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive' and self.postalcode!= None:
            self.data = self.data[(self.data['cdmstatus']==2) &  (self.data['postalcode'] == self.postalcode)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted' and self.postalcode!= None:
            self.data = self.data[(self.data['cdmstatus']==5) &  (self.data['postalcode'] == self.postalcode)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'star' and self.postalcode!= None:
            self.data = self.data[(self.data['postalcode'] == self.postalcode)]
            self.data['charger_status'] = 0
            self.data['charger_status'] = self.data['charger_status'].replace(0,6)

         # For city level
        elif self.country=='India' and self.chargers == 'all' and self.city!= None:
            self.data = self.data[ (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
            # for id in json_object:
            #     self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active' and self.city!= None:
            self.data = self.data[(self.data['cdmstatus']==1) & (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive' and self.city!= None:
            self.data = self.data[(self.data['cdmstatus']==2) & (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted' and self.city!= None:
            self.data = self.data[(self.data['cdmstatus']==5) & (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'star' and self.city!= None:
            self.data = self.data[(self.data['city'] == self.city)]
            self.data['charger_status'] = 0
            self.data['charger_status'] = self.data['charger_status'].replace(0,6)

        # For all India and state level chargers
        elif self.country=='India' and self.chargers == 'all' and self.state!=None:
            self.data['charger_status'] = 0
            self.data = self.data[self.data['state'] == self.state]
            # for id in json_object:
            #     self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active' and self.state!=None:
            self.data = self.data[(self.data['cdmstatus']==1) & (self.data['state'] == self.state)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive' and self.state!=None:
            self.data = self.data[(self.data['cdmstatus']==2) & (self.data['state'] == self.state)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted'and self.state!=None:
            self.data = self.data[(self.data['cdmstatus']==5) & (self.data['state'] == self.state)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'star' and self.state!=None:
            self.data['charger_status'] = 0
            self.data = self.data[(self.data['state'] == self.state)]
            self.data['charger_status'] = self.data['charger_status'].replace(0,6)


        # For All India Level Statastics
        elif self.country=='India' and self.chargers == 'all':
            self.data['charger_status'] = 0
            for id in json_object:
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active':
            self.data = self.data[(self.data['cdmstatus']==1)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive':
            self.data = self.data[(self.data['cdmstatus']==2)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted':
            # print("All india Level Faulted Chargers:", self.data)
            self.data['charger_status'] = 0
            self.data = self.data[(self.data['cdmstatus']==5)]
        elif self.country=='India' and self.chargers == 'star':
            self.data['charger_status'] = 0
            self.data['charger_status'] = self.data['charger_status'].replace(0,6)
            for id in json_object:
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
                
        elif self.country=='India' and self.chargers == 'highway':
            self.data['charger_status'] = 0
            self.data['charger_status'] = self.data['charger_status'].replace(0,8)
            
            for id in json_object:
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
                
        self.data.reset_index(drop=True, inplace=True)
        data = self.data.transpose()
        return json.loads(data.to_json()) 



class _ChargingSession:
    def __init__(self,requirement, need, state, city, postalcode) -> None:
        self.requirement = requirement
        self.data = service.getChargingSession(self.requirement, need, state, city, postalcode)
        # print(self.data)

    @property
    def serviceAnalysis(self):
        data = self.data
        data = data.transpose()
        return json.loads(data.to_json())

class _mapChargerInactivity:
    def __init__(self,identifier) -> None:
        self._id = identifier
        self.data = service.get_inactive_duration(self._id.identifier)
        self.data1 = service.get_charger_other_details(self._id.identifier)
        self.data2 = service.get_chager_status(self._id.identifier)
        
        self.data3=service.get_charger_last_transaction(self._id.identifier)

    @property
    def serviceAnalysis(self):
        # print(self._id.identifier)
        # print("Main charger details", self.data)
        # print("Charger details like model :", self.data1)
        # print(self.data1)
        # print("Charger Model :", self.data1['model'][0])
        # json_data1 = json.loads(self.data1.transpose())
        # print("json Data", json_data1 )
        #print(self.bootRequest)

        # if self.data2 == 2:
        #     self.data = 'NA'
        if self.data1.empty:
            res = {
            'identifier':self._id,
            'inactive': int(self.data/60),
            'power':int(56),
            'network':int(44),
            }
        elif self.data3.empty:
            res = {
                'identifier':self._id,
                'inactive':int(self.data/60),
                'model' : self.data1['model'][0],
                'telecom_partner' : self.data1['telecom_partner'][0],
                'name_of_location_partener' : self.data1['name_of_location_partener'][0],
                'email_of_location_partner' : self.data1['email_of_location_partener'][0],
                'mobile_no_of_location_partner' : self.data1['mobile_number_of_location_partener'][0],
                'last_transaction': "No transaction found",
                'power':int(56),
                'network':int(44)
            }
        else:
            res = {
                'identifier':self._id,
                'inactive':int(self.data/60),
                'model' : self.data1['model'][0],
                'telecom_partner' : self.data1['telecom_partner'][0],
                'name_of_location_partener' : self.data1['name_of_location_partener'][0],
                'email_of_location_partner' : self.data1['email_of_location_partener'][0],
                'mobile_no_of_location_partner' : self.data1['mobile_number_of_location_partener'][0],
                'last_transaction': self.data3['end_time'][0],
                'power':int(56),
                'network':int(44)
            }
        return res 


class _occpLogsIdentifier:
    def __init__(self,identifier) -> None:
        self._id = identifier
        # print(self._id)
        self.data = service.gettransactionlogs(identifier)
    @property
    def serviceAnalysis(self):
        print(self._id)
        self.data['time'] = self.data['time'].apply(lambda x: str(x))
        data = self.data.transpose()
        return json.loads(data.to_json())           

class _alarmFaultLogs:
    def __init__(self,identifier) -> None:
        self.data = service.getAlarmLogs(identifier) 
    
    @property
    def serviceAnalysis(self):
        # print(self.data)
        self.data = self.data[['faultcode','faultdescription','severity','status','timestamp','resolutiontime','faultstatus']]
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp']).dt.strftime('%m/%d/%Y , %r')
        self.data['resolutiontime'] = pd.to_datetime(self.data['resolutiontime']).dt.strftime('%m/%d/%Y , %r')
        data = self.data.transpose()
        return json.loads(data.to_json())       

class _alarmTotalFaultLogs:
    def __init__(self, start_date, end_date) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.data = service.getFullalarmLogs(start_date, end_date)

    @property
    #def serviceAnalysis(self):
    #     if (self.data).empty:
    #         return None
    #     else:
    #         return json.loads(self.data.to_json(orient='records'))
    def serviceAnalysis(self):
        self.data = self.data[['name','state','city','identifier','connectorid','model','faultcode',\
                               'faultdescription','severity','faultstatus'\
                               ,'timestamp','resolutiontime']]
        self.data = self.data.drop(self.data[self.data['identifier']=='D82110387340001'].index,axis=0)
        self.data = self.data.reset_index(drop=True)  
        self.data['year'] = pd.to_datetime(self.data['timestamp']).dt.year 
        self.data = self.data[self.data['year'] != 2106] 
        self.data = self.data.reset_index(drop=True)                  
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'],errors='coerce').dt.strftime('%m/%d/%Y , %r')
        self.data['resolutiontime'] = pd.to_datetime(self.data['resolutiontime']).dt.strftime('%m/%d/%Y , %r')
        # print(self.data)
        data = self.data.transpose()
        return json.loads(data.to_json()) 
     
class _alarmTotalFaultLogsCount:
    def __init__(self, start_date, end_date) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.data = service.getFullalarmLogsCount(start_date, end_date)

    @property
    def serviceAnalysis(self):
        if (len(self.data))==0:
            return None
        else:
            return json.loads(self.data)
                                 

class stuckBookingDetails:
    def __init__(self, requirement, state, city, postalcode) -> None:
        self.requirement = requirement
        self.identifiers = service.get_identifiers_of_stuck_bookings(state, city, postalcode)
        
        headers = {
"Accept": "*/*",
"Accept-Encoding": "gzip, deflate, br, zstd",
"Accept-Language": "en-US,en;q=0.9",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Host": "ezcharge.tatapower.com",
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "none",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
"sec-ch-ua": "Chromium;v=124, Google Chrome;v=124, Not-A.Brand;v=99",
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Windows"
}
        
        self.data = requests.get('https://ezcharge.tatapower.com/OperationUIService/getAllActiveStuckBooking',headers=headers)          
           
    @property
    def serviceAnalysis(self):
        if self.requirement == 'count':
            res = self.data.content
            encoding = 'utf-8'
            res = res.decode(encoding)
            res = json.loads(res)
            return {"stuckBooking":len(res['response']['responseObject'])}
        elif self.requirement == 'details':
            res = self.data.content
            encoding = 'utf-8'
            res = res.decode(encoding)
            res = json.loads(res)
            return res['response']['responseObject']


class NewDashboard:
    def __init__(self):
        self.data = service.new_dashboard_data()
        
    @property
    def serviceAnalysis(self):
        data = self.data
        return data
    
class NewDashboardPop:
    def __init__(self,identifier):
        self.data = service.new_dashboard_popup(identifier)
        
    @property
    def serviceAnalysis(self):
        data = self.data
        return data


class stuckBookingMap:
    def __init__(self) -> None:
        self.data = requests.get('https://ezcharge.tatapower.com/OperationUIService/getAllActiveStuckBooking')          
           
    @property
    def serviceAnalysis(self): 
        res = self.data.content
        d = json.loads(res)
        d = d['response']['responseObject']
        df = pd.DataFrame(d)
        df = df[['EVSE_ID','USAGE_STATUS']]
        df.rename(columns = {'EVSE_ID':'identifier'}, inplace = True)
        identifier = ','.join(["'"+str(m)+"'" for m in df['identifier'].values])
        query = "select identifier,latitude,longitude,name from ev_charge_point WHERE identifier IN"+"("+identifier+");" 
        df1 = service.universalQueary(query)
        inner_merged_total = pd.merge(df, df1, on=["identifier"])
        inner_merged_total['cdmstatus'] = 3
        inner_merged_total.loc[inner_merged_total.USAGE_STATUS == 'DELAYED_PROCESSING', 'cdmstatus'] = 4
        data = inner_merged_total.transpose()
        return json.loads(data.to_json())           

# for showing inactive chargers 
class _activeInactiveCharger:
    def __init__(self) -> None:
        self.data = service.getChargerDetails()

    @property
    def serviceAnalysis(self):
        self.data = self.data[['name','state','city','identifier','chargepointvendor','chargepointmodel','time','cdmstatus']]
        self.data = self.data[self.data['cdmstatus']==2]
        self.data = self.data.reset_index(drop=True)
        identifier_list = self.data['identifier'].to_list()
        charger_model_list = service.getChargerModel(identifier_list)
        self.data['inactive_time'] = pd.to_datetime(self.data['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        self.data['inactive_duration'] =  ((pd.to_datetime('now') - self.data.time).dt.seconds)/3600.0
        self.data['inactive_duration'] = self.data['inactive_duration'].apply(np.ceil)
        self.data['charger_model'] = charger_model_list
        self.data = (self.data).sort_values(['inactive_duration'], ascending = [False])
        self.data = self.data.reset_index(drop=True)
        # print(self.data)
        final_data = self.data.transpose()
        # print(final_data)
        return json.loads(final_data.to_json())     

class _serverHealth:
    def __init__(self) -> None:
        self.data = requests.get('https://ezcharge.tatapower.com/OperationUIService/fetchServerDetails') 

    @property
    def serviceAnalysis(self):          
        return json.loads(self.data.content) 
        

class hardResetActions():
        def __init__(self,identifier) -> None:
            self.random_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
            # print(self.random_key)
            self.url = "https://ezcharge.tatapower.com/HobsIntegration/syncRequestHandler?transid="+self.random_key+"&service=CDM_CHARGER_HARD_RESET"
            # self.payload = "{\r\n\r\n\"bookingId\":\"d2cd0d43-5848-475c-bac3-053c57ac8951\",\r\n\"evseId\":\"JDJ201300910W0\",\r\n\"connectorId\":\"1\"\r\n\r\n}\r\n"
            self.payload = {"identifier":identifier}
            self.headers = {
                'Authorization': 'Basic NDUzNDY5VFBMOnNhZG1wd2Q=',
                'Content-Type': 'application/json'
                }
            # print(identifier) 

        @property
        def serviceAnalysis(self):
            response = requests.request("POST", self.url, headers=self.headers, data=self.payload,verify=True)
            # print(response.text)
            return response.text


class stuckBookingActions:
    def __init__(self,bookingID,evseID,connectorID) -> None:
        self.random_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
        # print(self.random_key)
        self.url = "https://ezcharge.tatapower.com/HobsIntegration/syncRequestHandler?transid="+self.random_key+"&service=CLEAR_STUCK_BOOKING"
        #self.payload = "{\r\n\r\n\"bookingId\":\"d2cd0d43-5848-475c-bac3-053c57ac8951\",\r\n\"evseId\":\"JDJ201300910W0\",\r\n\"connectorId\":\"1\"\r\n\r\n}\r\n"
        self.payload = {"bookingId":bookingID,"evseId":evseID,"connectorId":connectorID}
        self.headers = {
            'Authorization': 'Basic NDUzNDY5VFBMOnNhZG1wd2Q=',
            'Content-Type': 'application/json'
            }
        # print(bookingID) 

    @property
    def serviceAnalysis(self):
        response = requests.request("POST", self.url, headers=self.headers, data=self.payload,verify=True)
        # print(response.text)
        return response.text


class chargerResetActions:
    def __init__(self,bookingID,evseID,connectorID) -> None:
        self.random_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
        # print(self.random_key)
        self.url = "https://ezcharge.tatapower.com/HobsIntegration/syncRequestHandler?transid="+self.random_key+"&service=CLEAR_STUCK_BOOKING"
        #self.payload = "{\r\n\r\n\"bookingId\":\"d2cd0d43-5848-475c-bac3-053c57ac8951\",\r\n\"evseId\":\"JDJ201300910W0\",\r\n\"connectorId\":\"1\"\r\n\r\n}\r\n"
        self.payload = {"bookingId":bookingID,"evseId":evseID,"connectorId":connectorID}
        self.headers = {
            'Authorization': 'Basic NDUzNDY5VFBMOnNhZG1wd2Q=',
            'Content-Type': 'application/json'
            }
        # print(bookingID) 

    @property
    def serviceAnalysis(self):
        response = requests.request("POST", self.url, headers=self.headers, data=self.payload,verify=True)
        # print(response.text)
        return response.text


class getChargingSession:
    def __init__(self) ->None:
        self.data = service.getChargingSession()
        # print('Charging Session')
    
    @property
    def serviceAnalysis(self):
        # # print(self.data.head())
        # # print(self.data.isna().sum())
        # print("----------------------------------- Charging session data -------------------------", json.loads(self.data))
        return json.loads(self.data)    

class chargerOnboard:
    def __init__(self,ctype) -> None:
        # print(ctype)
        self.data = service.getChargerDetails()#service.chargerOnBoard(ctype) 

    @property
    def serviceAnalysis(self):
        publicCharger = len(self.data[self.data['type']=='Public'])
        corporateCharger = len(self.data[self.data['type']=='Corporate'])
        homeCharger = len(self.data[self.data['type']=='Home'])
        result = {'Public':{'value':publicCharger},'Corporate':{'value':corporateCharger},'Home':{'value':homeCharger}}
        # print(result)
        #self.data = self.data.transpose()
        return result

class ChargerResetConfiguration:
    def __init__(self) -> None:
        self.chargerDetails = service.getChargerDetails()
        
    @property
    def serviceAnalysis(self):
        self.chargerDetails = self.chargerDetails[['name','state','city','identifier','chargepointvendor','chargepointmodel','time','devicestatus','cdmstatus']]
        self.chargerDetails['cdmstatus'] = self.chargerDetails['cdmstatus'].apply(lambda x : 'active' if x==1 else 'inactive')
        # print(self.chargerDetails['time'].head())
        identifier_list = self.chargerDetails['identifier'].to_list()
        charger_model_list = service.getChargerModel(identifier_list)
        self.chargerDetails['time'] = pd.to_datetime(self.chargerDetails['time'])
        self.chargerDetails['time'] = pd.to_datetime(self.chargerDetails['time']).dt.strftime('%m/%d/%Y, %r')
        self.chargerDetails['InactiveTime'] = pd.to_datetime(pd.datetime.now().date()) -pd.to_datetime(self.chargerDetails['time'])
        # print(self.chargerDetails['time'].head())
        self.chargerDetails['time'] = self.chargerDetails['time'].apply(lambda x: str(x))
        self.chargerDetails['InactiveTime'] = self.chargerDetails['InactiveTime'].apply(lambda x: str(x))
        # print(self.chargerDetails['time'].head())
        self.chargerDetails['charger_model'] = charger_model_list
        data = self.chargerDetails.transpose()
        return json.loads(data.to_json())   

# Adds charger in acknowledged charger file when user acknowledges the charger
def chargerAcknowledgement(identifier):
    filename = '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
    entry = {'identifier': identifier}
    with open(filename, "r+") as file:
        data = json.load(file)
        if any(d1['identifier'] == identifier for d1 in data):
            # print("Data already present", identifier)
            pass
        else:
            data.append(entry)
            file.seek(0)
            json.dump(data, file,indent=2)

        # query="""select identifier,cdmstatus from ev_charge_point """"
        # df = pd.read_sql(query, psql_engine)
        # for identifier in 
    return 0   

try:
    # CDM Database connection
    psql_engine = create_engine('postgresql+psycopg2://readapp:%s@%s:5432/evmain' 
                % (urllib.parse.quote_plus('re@d@pp#@!'),'172.21.3.11'), pool_size=10,
                max_overflow=2,
                pool_recycle=300,
                pool_pre_ping=True,
                pool_use_lifo=True)
except Exception as e:
    print(e)


def create_connection_mysql():
    try:
        mydb = create_engine('mysql+pymysql://odsuser:%s@%s' 
        % (urllib.parse.quote_plus('odsuser'),'172.21.3.42'))

    except Exception as e:
        print(e)
    return mydb

# This method removes active charger from acknowlwdged charger
def removeActiveAck():
    filename = '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
    query="""select identifier,cdmstatus from ev_charge_point """
    df = pd.read_sql(query, psql_engine)
    li=df['identifier'].to_list()
    duplicate=[]
    with open(filename, "r+") as file:
        data = json.load(file)
        # print(len(data))
    dump=data
    # print(data)
    for i in data:
        if i['identifier'] in li:
            duplicate.append(i)
    # print(len(duplicate))
    
    with open('/home/evadmin/EV_NOC/Backend/app/controllers/ack.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(duplicate, indent=2))
    
    with open(filename, "r+") as file:
        data = json.load(file)
            
    for i in data:
        if df.set_index('identifier').loc[i['identifier'],'cdmstatus'] == 1 :
            for id,obj in enumerate(data):
                if obj['identifier']==i['identifier']:
                    data.pop(id)
                    with open('/home/evadmin/EV_NOC/Backend/app/controllers/ack.json', 'w', encoding='utf-8') as f:
                        f.write(json.dumps(data, indent=2))
    # print(len(data))
    return 0

# Adds highway or priority charger in the file based on the requirement.
def addChargerToFile(data, charger_type):
    if charger_type == 'highway':
        filename = '/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json'
        json_data = json.dumps(data)
        json_data = json.loads(json_data)
        for json_obj in json_data:
            entry = {'identifier': json_obj['identifier']}
            with open(filename, "r+") as file:
                data = json.load(file)
                if any(d1['identifier'] == json_obj['identifier'] for d1 in data):
                    # print("Data already present")
                    pass
                else:
                    data.append(entry)
                    file.seek(0)
                    json.dump(data, file)
        return 0
    elif charger_type == 'priority':
        filename = '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
        json_data = json.dumps(data)
        json_data = json.loads(json_data)
        for json_obj in json_data:
            entry = {'identifier': json_obj['identifier']}
            with open(filename, "r+") as file:
                data = json.load(file)
                if any(d1['identifier'] == json_obj['identifier'] for d1 in data):
                    # print("Data already present")
                    pass
                else:
                    data.append(entry)
                    file.seek(0)
                    json.dump(data, file)
        return 0


# Deletes highway or priority charger in the file based on the requirement.
def deleteChargerFromFile(data, charger_type):
    if charger_type == 'highway':
        filename = '/home/evadmin/EV_NOC/Backend/app/controllers/highway_chargers.json'
        json_data = json.dumps(data)
        json_data = json.loads(json_data)
        with open(filename, "r+") as file:
                data = json.load(file)
        for json_obj in json_data:
            for idx, dictionary in enumerate(data):
                if dictionary['identifier'] == json_obj['identifier']:
                    # print("Deleting for",json_obj['identifier'])
                    data.pop(idx)
                    # print("Data Deleted")
                else:
                    # print("No data found")
                    pass
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, indent=2))
            # print("Data written to file")
        return 0
               
    elif charger_type == 'priority':
        filename = '/home/evadmin/EV_NOC/Backend/app/controllers/priority_chargers.json'
        json_data = json.dumps(data)
        json_data = json.loads(json_data)
        with open(filename, "r+") as file:
                data = json.load(file)
        for json_obj in json_data:
            for idx, dictionary in enumerate(data):
                if dictionary['identifier'] == json_obj['identifier']:
                    # print("Deleting for",json_obj['identifier'])
                    data.pop(idx)
                    # print("Data Deleted")
                else:
                    # print("No data found")
                    pass
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, indent=2))
            # print("Data written to file")
        return 0




class _stateBusChargerStatus:
    def __init__(self) -> None:
        self.data = service.getBusChargerDetails()
        # print('service ')

    @property
    def serviceAnalysis(self):
        self.data = self.data[['identifier','state','type','country','city','latitude','longitude','cdmstatus','chargepointvendor']]
        uniqueSate = self.data['state'].unique()
        # print(uniqueSate)
        result = [{'state':i,\
                   'total':len(self.data[self.data['state']==i]),\
                   'active':len(self.data[(self.data['cdmstatus']==1) & (self.data['state']==i)]),\
                   'inactive':len(self.data[(self.data['cdmstatus']==2) & (self.data['state']==i)])} for i in uniqueSate] 
        totalCharger = len(self.data)
        activeCharger = len(self.data[self.data['cdmstatus']==1])   
        inactiveCharger = len(self.data[self.data['cdmstatus']==2])   
        return {'totalCharger':totalCharger,'activeCharger':activeCharger,'inactiveCharger':inactiveCharger,'data':result}

class _stateWiseBusChargerStatus:
    def __init__(self,region) -> None:
        self.data = service.getBusChargerDetails()
        # self.data = service.get_charger_details()
        self.filename = '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
        self.region = region
        # print(self.region)
        
    
    @property
    def serviceAnalysis(self):
        with open(self.filename, 'r') as openfile:
            json_object = json.load(openfile)
        # print(json_object)    
        self.data = self.data[['name','identifier','state','type','country','city','latitude','longitude','cdmstatus','chargepointvendor']]
        if self.region=='India':
            self.data = self.data[self.data['cdmstatus']==2]
            for id in json_object:
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 0, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        else:
            self.data = self.data[(self.data['state']==self.state) & (self.data['cdmstatus']==2)]
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 0, inplace=True)
        # print(self.data.isnull().sum())
        self.data.reset_index(drop=True, inplace=True)
        # print(self.data)
        data = self.data.transpose()
        return json.loads(data.to_json()) 

# for showing inactive bus chargers 
class _activeInactiveBusCharger:
    def __init__(self) -> None:
        self.data = service.getBusChargerDetails()

    @property
    def serviceAnalysis(self):
        self.data = self.data[['name','state','city','identifier','chargepointvendor','chargepointmodel','time','cdmstatus']]
        self.data = self.data[self.data['cdmstatus']==2]
        self.data = self.data.reset_index(drop=True)
        identifier_list = self.data['identifier'].to_list()
        charger_model_list = service.getChargerModel(identifier_list)
        self.data['inactive_time'] = pd.to_datetime(self.data['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        self.data['inactive_duration'] =  ((pd.to_datetime('now') - self.data.time).dt.seconds)/3600.0
        self.data['inactive_duration'] = self.data['inactive_duration'].apply(np.ceil)
        self.data['charger_model'] = charger_model_list
        self.data = (self.data).sort_values(['inactive_duration'], ascending = [False])
        self.data = self.data.reset_index(drop=True)
        # print(self.data)
        final_data = self.data.transpose()
        # print(final_data)
        return json.loads(final_data.to_json())

class _busChargerStatus:
    def __init__(self,country, chargers, state, city) -> None:
        # self.data = service.getChargerDetails()
        self.country = country
        # print(self.country)
        self.chargers = chargers
        # print(self.chargers)
        self.state = state
        # print(self.state)
        self.city = city
        # print(self.city)
        self.data = service.get_bus_charger_details(country, chargers)
        self.filename = '/home/evadmin/EV_NOC/Backend/app/controllers/ack.json'
        
    @property
    def serviceAnalysis(self):
        with open(self.filename, 'r') as openfile:
            json_object = json.load(openfile)
        self.data = self.data[self.data['devicestatus'] == 'Managed']
        # print(json_object) 
        if self.country=='India' and self.chargers == 'faulted':
            self.data = self.data[['identifier','country','city','state','name','postalcode','cdmstatus','latitude','longitude','status']]
        else:  
            self.data = self.data[['identifier','country','city','state','name','postalcode','cdmstatus','latitude','longitude']]

         # For city level
        if self.country=='India' and self.chargers == 'all' and self.city!= None:
            self.data = self.data[ (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
            # for id in json_object:
            #     self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active' and self.city!= None:
            self.data = self.data[(self.data['cdmstatus']==1) & (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive' and self.city!= None:
            self.data = self.data[(self.data['cdmstatus']==2) & (self.data['city'] == self.city)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted' and self.city!= None:
            self.data = self.data[(self.data['cdmstatus']==5) & (self.data['city'] == self.city)]
            self.data['charger_status'] = 0

        # For all India and state level chargers
        elif self.country=='India' and self.chargers == 'all' and self.state!=None:
            self.data['charger_status'] = 0
            self.data = self.data[self.data['state'] == self.state]
            # for id in json_object:
            #     self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active' and self.state!=None:
            self.data = self.data[(self.data['cdmstatus']==1) & (self.data['state'] == self.state)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive' and self.state!=None:
            self.data = self.data[(self.data['cdmstatus']==2) & (self.data['state'] == self.state)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted'and self.state!=None:
            self.data = self.data[(self.data['cdmstatus']==5) & (self.data['state'] == self.state)]
            self.data['charger_status'] = 0

        # For All India Level Statastics
        elif self.country=='India' and self.chargers == 'all':
            self.data['charger_status'] = 0
            for id in json_object:
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
            self.data = self.data.dropna(how='any',axis=0) 
        elif self.country=='India' and self.chargers == 'active':
            self.data = self.data[(self.data['cdmstatus']==1)]
            self.data['charger_status'] = 0
        elif self.country=='India' and self.chargers == 'inactive':
            self.data = self.data[(self.data['cdmstatus']==2)]
            self.data['charger_status'] = 0
            for id in json_object:
                # print(id['identifier'])
                self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        elif self.country=='India' and self.chargers == 'faulted':
            # print("All india Level Faulted Chargers:", self.data)
            self.data['charger_status'] = 0
            self.data = self.data[(self.data['cdmstatus']==5)]
        # elif self.country=='India' and self.chargers == 'star':
        #     self.data['charger_status'] = 0
        #     self.data['charger_status'] = self.data['charger_status'].replace(0,6)
        #     for id in json_object:
        #         # print(id['identifier'])
        #         self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        #         # print(self.data[self.data['identifier'] == id['identifier']]['cdmstatus'])
        # # print(self.data.isnull().sum())
        # elif self.country=='India' and self.chargers == 'highway':
        #     self.data['charger_status'] = 0
        #     self.data['charger_status'] = self.data['charger_status'].replace(0,8)
        #     for id in json_object:
        #         # print(id['identifier'])
        #         self.data['cdmstatus'].mask(self.data['identifier'] == id['identifier'], 7, inplace=True)
        #         # print(self.data[self.data['identifier'] == id['identifier']]['cdmstatus'])
        # self.data.reset_index(drop=True, inplace=True)
        # # print(self.data)
        # data = self.data.transpose()
        self.data.reset_index(drop=True, inplace=True)
        # print(self.data)
        data = self.data.transpose()
        return json.loads(data.to_json()) 
        


class _mapBusChargerInactivity:
    def __init__(self,identifier) -> None:
        self._id = identifier
        self.data = service.get_inactive_duration(self._id.identifier)
        self.data1 = service.get_charger_other_details(self._id.identifier)
        self.data2 = service.get_bus_chager_status(self._id.identifier)
    
    @property
    def serviceAnalysis(self):
        # print(self._id.identifier)
        # print("Main charger details", self.data)
        # print("Charger details like model :", self.data1)
        # print(self.data1)
        # print("Charger Model :", self.data1['model'][0])
        # json_data1 = json.loads(self.data1.transpose())
        # print("json Data", json_data1 )
        #print(self.bootRequest)

        # if self.data2 == 2:
        #     self.data = 'NA'
        if self.data1.empty:
            res = {
            'identifier':self._id,
            'inactive': int(self.data/60),
            'power':int(56),
            'network':int(44)
            }
        else:
            res = {
                'identifier':self._id,
                'inactive':int(self.data/60),
                'model' : self.data1['model'][0],
                'telecom_partner' : self.data1['telecom_partner'][0],
                'name_of_location_partener' : self.data1['name_of_location_partener'][0],
                'email_of_location_partner' : self.data1['email_of_location_partener'][0],
                'mobile_no_of_location_partner' : self.data1['mobile_number_of_location_partener'][0],
                'power':int(56),
                'network':int(44)
            }
        return res 
    
######################################

# Bus Depot

class _ChargingSessionBusDepot:
    def __init__(self,requirement, need, state, city) -> None:
        self.requirement = requirement
        self.data = service.getChargingSessionBusDepot(self.requirement, need, state, city)
        # print(self.data)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            data = self.data
            data = data.transpose()
            return json.loads(data.to_json())
       