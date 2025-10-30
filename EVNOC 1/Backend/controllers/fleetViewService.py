import math
from models import service
import pandas as pd
import json
import requests
import string   
import random 
import asyncio


class _allChargerStatus:
    def __init__(self,country, state, city, postalcode) -> None:
        self.dataCharger = service.getChargerDetails()
        self.dataConnetor = service.getChargerConnetor()
        self.starChargersCount = service.getStarChargersCount(state, city, postalcode)
        self.faultedChargersCount = service.getFaultedChargersCount(state, city, postalcode)
        self.typesChargersCount = service.getChargersTypesCount(state, city, postalcode)
        self.typesChargersCountFromFile = service.getChargersTypesCountFromFile()
        self.highwayChargersCount = service.getHighwayChargersCount()
        self.country = country
        self.state = state
        self.city = city
        self.postalcode = postalcode
        
        # print(len(self.typesChargersCount[self.typesChargersCount['location_type']=='Public']))
    @property
    def serviceAnalysis(self):
        self.dataCharger = self.dataCharger[['identifier','state','type','country','city','postalcode','latitude','cdmstatus','longitude','chargepointvendor']]

        # For Pincode level
        if self.country=='India' and self.postalcode!=None:
            self.dataCharger = self.dataCharger[(self.dataCharger['postalcode']==self.postalcode)]
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = (activeChargerCount/totalCharger) if  totalCharger!=0 else 0
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = (inactiveChargerCount/totalCharger) if  totalCharger!=0 else 0 
            totalConnetor = len(self.dataConnetor)
            publicCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Public'])
            corporateCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Corporate'])
            homeCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Home'])
            captiveCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Captive'])
            starCharger = self.starChargersCount
            faultedCharger = self.faultedChargersCount
            highwayChargersCount = self.highwayChargersCount 
        
        # For City level
        elif self.country=='India' and self.city!=None:
            self.dataCharger = self.dataCharger[(self.dataCharger['city']==self.city)]
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = (activeChargerCount/totalCharger) if  totalCharger!=0 else 0 
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = (inactiveChargerCount/totalCharger) if  totalCharger!=0 else 0
            totalConnetor = len(self.dataConnetor)
            publicCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Public'])
            corporateCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Corporate'])
            homeCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Home'])
            captiveCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Captive'])
            starCharger = self.starChargersCount
            faultedCharger = self.faultedChargersCount
            highwayChargersCount = self.highwayChargersCount 
        
        #  For state Level
        elif self.country=='India' and self.state != None:
            self.dataCharger = self.dataCharger[(self.dataCharger['state']==self.state)]
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = (activeChargerCount/totalCharger) if  totalCharger!=0 else 0 
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = (inactiveChargerCount/totalCharger) if  totalCharger!=0 else 0 
            totalConnetor = len(self.dataConnetor)
            publicCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Public'])
            corporateCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Corporate'])
            homeCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Home'])
            captiveCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Captive'])
            starCharger = self.starChargersCount
            faultedCharger = self.faultedChargersCount
            highwayChargersCount = self.highwayChargersCount 
        else:
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = activeChargerCount/totalCharger 
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = inactiveChargerCount/totalCharger 
            totalConnetor = len(self.dataConnetor)
            publicCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Public'])
            corporateCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Corporate'])
            homeCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Home'])
            captiveCharger = len(self.typesChargersCount[self.typesChargersCount['location_type']=='Captive'])
            starCharger = self.starChargersCount
            faultedCharger = self.faultedChargersCount
            highwayChargersCount = self.highwayChargersCount 
    
        #activeConnetor = len(self.dataConnetor[self.dataConnetor['status']=='Available'])/totalConnetor
        #inactiveConnetor = len(self.dataConnetor[self.dataConnetor['status']=='Unavailable'])/totalConnetor
        #faultedConnetor = len(self.dataConnetor[self.dataConnetor['status']=='Faulted'])/totalConnetor
        result = {
            'totalCharger':totalCharger,
            # 'activeCharger':round(activeCharger,2)*100,
            'activeCharger':(math.floor(activeCharger*100)),        
            # 'inactiveCharger':round(inactiveCharger,2)*100,
            'inactiveCharger':(math.ceil(inactiveCharger*100)),
            'totalConnetor':totalConnetor,
            'activeConnetor':000,#round(activeConnetor,2),
            'inactiveConnetor':000,#round(inactiveConnetor,2),
            'faultedConnetor':000,#round(faultedConnetor,2),
            'starCharger' : starCharger,
            'faultedCharger' : faultedCharger,
            'highwayChargers' : highwayChargersCount,
            'totalactiveCharger' :activeChargerCount,
            'totalinactiveCharger':inactiveChargerCount,
            'publicCharger':publicCharger,
            'corporateCharger':corporateCharger,
            'homeCharger':homeCharger,
            'captiveCharger':captiveCharger,
            'onBoardedChargers':publicCharger+corporateCharger+homeCharger+captiveCharger
        }
        return result




class TypewiseChargerCount:
    def __init__(self) -> None:
       self.typesChargersJson = service.getChargersTypesCountFromFile()
        
        
    @property
    def serviceAnalysis(self):
        publicChargerOnboarded = self.typesChargersJson['publicChargerOnboarded']
        corporateChargerOnboarded = self.typesChargersJson['corporateChargerOnboarded']
        homeChargerOnboarded = self.typesChargersJson['homeChargerOnboarded']
        captiveChargerOnboarded = self.typesChargersJson['captiveChargerOnboarded']
        housingScietyChargerOnboarded = self.typesChargersJson['housingScietyChargerOnboarded']
        busChargerOnboarded = self.typesChargersJson['busChargerOnboarded']
        publicChargerInstalled = self.typesChargersJson['publicChargerInstalled']
        corporateChargerInstalled = self.typesChargersJson['corporateChargerInstalled']
        homeChargerInstalled = self.typesChargersJson['homeChargerInstalled']
        captiveChargerInstalled = self.typesChargersJson['captiveChargerInstalled']
        housingScietyChargerInstalled = self.typesChargersJson['housingScietyChargerInstalled']
        busChargerInstalled = self.typesChargersJson['busChargerInstalled']

        
        result = {
            'publicChargerOnboarded' : publicChargerOnboarded,
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
            'busChargerInstalled' : busChargerInstalled,
            'onBoardedChargers': publicChargerOnboarded+corporateChargerOnboarded+homeChargerOnboarded+captiveChargerOnboarded+housingScietyChargerOnboarded+busChargerOnboarded 
        }
        return result




class _getCitiesFromState:
    def __init__(self, state) -> None:
        self.state = state
        self.data = service.getCities(state)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            self.data = self.data.transpose()
            # print(json.loads(self.data.to_json(orient='records')))
            return json.loads(self.data.to_json(orient='records'))

class _getLatLonState:
    def __init__(self, state) -> None:
        self.state = state
        self.data = service.get_Lat_Lon_state(state)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            self.data = self.data.transpose()
            # print(json.loads(self.data.to_json(orient='records')))
            return json.loads(self.data.to_json(orient='records'))


class _getPincodesFromCity:
    def __init__(self, city) -> None:
        self.city = city
        # print(self.city)
        self.data = service.getPostalCodes(self.city)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            self.data = self.data.transpose()
            # print(json.loads(self.data.to_json(orient='records')))
            return json.loads(self.data.to_json(orient='records'))

# Get charger count which are became active today
class _getTodaysActiveChargerCount:
    def __init__(self) -> None:
        self.data = service.getTodaysActiveChargerCount()

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))


# Get charger details which are became inactive today
class _getTodaysInactiveChargers:
    def __init__(self, requirement, chargerType) -> None:
        self.requirement = requirement
        self.chargerType = chargerType
        self.data = service.getTodaysInactiveChargerDetails(requirement, chargerType)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            if self.requirement == 'count':
                return json.loads(self.data.to_json(orient='records'))
            elif self.requirement == 'details':
                self.data = (self.data.sort_values(by='inactive_duration', ascending = False)).reset_index(drop=True)
                return json.loads(self.data.to_json(orient='records'))


# Gives information about highway as well as priority chargers
class _getHighwayOrPriorityChargers:
    def __init__(self, requirement) -> None:
        self.requirement = requirement
        self.data = service.get_highway_or_priority_chargers(requirement)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))


class _getImportantChargers:
    def __init__(self, state) -> None:
        self.state = state
        self.data = service.getImportantChargers(state)

    @property
    def serviceAnalysis(self):
            return json.loads(self.data.to_json(orient='records'))


class _allBusChargerStatus:
    def __init__(self,country, state, city) -> None:
        self.dataCharger = service.getBusChargerDetails()
        self.faultedChargersCount = service.getFaultedBusChargersCount(state, city)
        self.country = country
        self.state = state
        self.city = city
        
    @property
    def serviceAnalysis(self):
        self.dataCharger = self.dataCharger[['identifier','state','type','country','city','postalcode','latitude','cdmstatus','longitude','chargepointvendor']]

        
        # For City level
        if self.country=='India' and self.city!=None:
            self.dataCharger = self.dataCharger[(self.dataCharger['city']==self.city)]
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = (activeChargerCount/totalCharger) if  totalCharger!=0 else 0 
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = (inactiveChargerCount/totalCharger) if  totalCharger!=0 else 0
            # totalConnetor = len(self.dataConnetor)
            faultedCharger = self.faultedChargersCount
        
        #  For state Level
        elif self.country=='India' and self.state != None:
            self.dataCharger = self.dataCharger[(self.dataCharger['state']==self.state)]
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = (activeChargerCount/totalCharger) if  totalCharger!=0 else 0 
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = (inactiveChargerCount/totalCharger) if  totalCharger!=0 else 0 
            faultedCharger = self.faultedChargersCount
        else:
            self.dataCharger = self.dataCharger.dropna(how='any',axis=0) 
            totalCharger = len(self.dataCharger)
            activeChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==1])
            activeCharger = activeChargerCount/totalCharger 
            inactiveChargerCount = len(self.dataCharger[self.dataCharger['cdmstatus']==2])
            inactiveCharger = inactiveChargerCount/totalCharger 
            faultedCharger = self.faultedChargersCount
    
        #activeConnetor = len(self.dataConnetor[self.dataConnetor['status']=='Available'])/totalConnetor
        #inactiveConnetor = len(self.dataConnetor[self.dataConnetor['status']=='Unavailable'])/totalConnetor
        #faultedConnetor = len(self.dataConnetor[self.dataConnetor['status']=='Faulted'])/totalConnetor
        result = {
            'totalCharger':totalCharger,
            # 'activeCharger':round(activeCharger,2)*100,
            # 'activeCharger':(math.floor(activeCharger*100)),        
            # 'inactiveCharger':round(inactiveCharger,2)*100,
            # 'inactiveCharger':(math.ceil(inactiveCharger*100)),
            'faultedCharger' : faultedCharger,
            'totalactiveCharger' :activeChargerCount,
            'totalinactiveCharger':inactiveChargerCount,
        }
        return result

class _getBusCitiesFromState:
    def __init__(self, state) -> None:
        self.state = state
        self.data = service.getBusCities(state)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            self.data = self.data.transpose()
            # print(json.loads(self.data.to_json(orient='records')))
            return json.loads(self.data.to_json(orient='records'))

# This class returns depo names when city is entred       
class _getBusDeposFromCity:
    def __init__(self, city) -> None:
        self.city = city
        self.data = service.getBusDepos(city)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            self.data = self.data.transpose()
            # print(json.loads(self.data.to_json(orient='records')))
            return json.loads(self.data.to_json(orient='records'))

class _getTodaysInactiveBusChargers:
    def __init__(self, requirement, chargerType) -> None:
        self.requirement = requirement
        self.chargerType = chargerType
        self.data = service.getTodaysInactiveBusChargerDetails(requirement, chargerType)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            if self.requirement == 'count':
                return json.loads(self.data.to_json(orient='records'))
            elif self.requirement == 'details':
                self.data = (self.data.sort_values(by='inactive_duration', ascending = False)).reset_index(drop=True)
                return json.loads(self.data.to_json(orient='records'))


# This class returns count of connectors against each bus depot
class _getCountConnectorBusDepot:
    def __init__(self) -> None:
        self.data = service.getCountConnectorBusDepot()
        
    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
        
        
# This class returns the CIDS Dashboard
class _dashboardCIDS:
    def __init__(self, stationName) -> None:
        self.stationName = stationName
        self.data = service.dashboardCIDS(stationName)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
        
# Test case
class _TestBus:
    def __init__(self) -> None:
        self.data = service.TestBus()

    @property
    def serviceAnalysis(self):
        # if (self.data).empty:
        #     return None
        # else:
        return json.loads(self.data.to_json(orient='records'))


####################################################

##Analytics

# To get zero transaction unit counts
class _getZeroTransactionAnalytics:
    def __init__(self, start_date,end_date) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.data = service.getZeroTransactionAnalytics(start_date,end_date)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
            #if self.start_date==start_date and self.end_date==end_date:
            #     return json.loads(self.data.to_json(orient='records'))
            # elif self.requirement == 'details':
        else:
            #self.data = (self.data.sort_values(by='COUNT', ascending = False)).reset_index(drop=True)
            return json.loads(self.data.to_json(orient='records'))

# To get inactive charger count on csv due to network issues
class _getInactiveCountNetworkIssues:
    def __init__(self) -> None:
        self.data = service.getInactiveCountNetworkIssues()

    @property
    def serviceAnalysis(self):
            return 1
        
# Read the csv of Inactive Chargers due to Network Issues
class _readCSVNetworkIssues:
    def __init__(self) -> None:
        self.data = service.readCSVNetworkIssues()

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
        
# Get the view details for inatcive chargers due to Network Issues
class _viewDetailsNetworkIssues:
    def __init__(self, identifier) -> None:
        self.identifier=identifier
        self.data = service.viewDetailsNetworkIssues(identifier)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
        
# To get inactive charger count on csv due to Power Failure
class _getInactiveCountPowerFailure:
    def __init__(self) -> None:
        self.data = service.getInactiveCountPowerFailure()

    @property
    def serviceAnalysis(self):
            return 1
        
# Read the csv of Inactive Chargers due to Power Failure
class _readCSVPowerFailure:
    def __init__(self) -> None:
        self.data = service.readCSVPowerFailure()

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))

# Get the view details for inatcive chargers due to Power Failure
class _viewDetailsPowerFailure:
    def __init__(self, identifier) -> None:
        self.identifier=identifier
        self.data = service.viewDetailsPowerFailure(identifier)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))

# Get Weekly Charging Session Trend
class _chargingSessionTrendWeekly:
    def __init__(self,day) -> None:
        self.day=day
        self.data = service.chargingSessionTrendWeekly(day)

    @property
    def serviceAnalysis(self):
        # if len(self.data)==0:
        #     return None
        # else:
        return self.data

        

# Get Charging Session Trend for one day before
class _chargingSessionTrendDaily:
    def __init__(self,start_date) -> None:
        self.start_date=start_date
        self.data = service.chargingSessionTrendDaily(start_date)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
        
class _StarHighwayChargers:
    def __init__(self) -> None:
        self.data = service.StarHighway()

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))


#####################
#Charger Hits

# Get charger hits daily
class _performChargerHits:
    def __init__(self) -> None:
        self.data = service.performChargerHits()

    @property
    def serviceAnalysis(self):
        # if len(self.data)==0:
        #     return None
        # else:
        return self.data 
    
# Read the csv of daily charger hits
class _readCSVChargerHits:
    def __init__(self,select_date) -> None:
        self.select_date=select_date
        self.data = service.readCSVChargerHits(select_date)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
  
  
### Charger Hits Analysis

#Performing analysis on charger hits
class _analysisOnChargerHits:
    def __init__(self) -> None:
        self.data = service.analysisOnChargerHits()

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))
        
              
#Faults

#get fault details of the chargers
class _getFaultDetails:
    def __init__(self,identifier) -> None:
        self.identifier=identifier
        self.data = service.getFaultDetails(identifier)

    @property
    def serviceAnalysis(self):
        if (self.data).empty:
            return None
        else:
            return json.loads(self.data.to_json(orient='records'))

class _getOtherDetails:
    def __init__(self,identifier) -> None:
        self.identifier = identifier
        self.faultData = service.getFaultDetails(identifier)
        self.transactionData = service.get_charger_last_transaction(identifier)
        self.otherData = service.getOtherDetails(identifier)
        
    @property
    def serviceAnalysis(self):
        res={
            "inactive":self.otherData["minutes_since_inactive"][0],
            "identifier":self.otherData["identifier"][0],
            "name":self.otherData["name"][0],
            "city":self.otherData["city"][0],
            "chargepointmodel":self.otherData["chargepointmodel"][0],
            "transaction":self.transactionData,
            "faults":self.faultData
            }
        return res
    
#abhishek-start
class _getChargerModelAndType:
    def __init__(self,identifiers) -> None:
        self.identifiers=identifiers
        self.final_result=service.modeltype(identifiers)
    @property
    def serviceAnalysis(self):
        res={
            "result": self.final_result
            }
        return res
# abhishek -end 