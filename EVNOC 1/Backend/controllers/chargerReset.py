from models import service
import pandas as pd
import json
import requests
import string   
import random 


class ChargerResetConfiguration:
    def __init__(self) -> None:
        self.chargerDetails = service.getChargerDetails()
        
    @property
    def serviceAnalysis(self):
        self.data = self.data[['name','state','city','identifier','chargepointvendor','chargepointmodel','time','devicestatus','cdmstatus']]
        self.data['cdmstatus'] = self.data['cdmstatus'].apply(lambda x : 'active' if x==1 else 'inactive')
        print(self.data.head())
        data = self.data.transpose()
        return json.loads(data.to_json()) 


