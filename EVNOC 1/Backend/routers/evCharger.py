from typing import Dict, Optional
import overpy
import requests
from fastapi import APIRouter,BackgroundTasks
from controllers import _logicRealTime,fleetViewService,chargerReset
from pydantic import BaseModel
from typing import List
from models import service
from fastapi.encoders import jsonable_encoder
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.inmemory import InMemoryBackend
import json

router = APIRouter()
 
class StuckData(BaseModel):
    bookingID: str
    evseID: str
    connectorID: str

class Routes(BaseModel):
    source:str
    destination:str

class Pois(BaseModel):
	source:str
	destination:str
 
class Amenity(BaseModel):
    state:str
    filter:str

class ChargerData(BaseModel):
    station: str
    identifier: str
    city: str  

class Onboard(BaseModel):
    chargerType:str  

class acknowledgeCharger(BaseModel):
    chargerID:str        

class highwayPriorityChargers(BaseModel):
    identifier: str

class hardResetCharger(BaseModel):
    identifier: str
    
class InputData(BaseModel):
    identifiers: List[str]


# @router.on_event("startup")
# async def startup():
#     FastAPICache.init(InMemoryBackend())


# @router.get("/clear")
# async def clear():
#     print("cleared cache")
#     return await FastAPICache.clear(namespace='analysischargerhits')


# @router.on_event("shutdown")
# async def shutdown_event():
#     await FastAPICache.clear()

@router.get("/evCharger/new")
async def new_dashboard():
    return  _logicRealTime.NewDashboard().serviceAnalysis


@router.get("/evCharger/popup/{identifier}")
async def new_dashboard(identifier:str):
    return  _logicRealTime.NewDashboardPop(identifier).serviceAnalysis


@router.get("/evCharger/status", tags=["evCharger"])
async def read_users():
    data = _logicRealTime._stateChargerStatus().serviceAnalysis
    return data

@router.get("/evCharger/activity/status", tags=["evCharger"])
async def read_users():
    data = _logicRealTime._activeInactiveCharger().serviceAnalysis
    return data

@router.get("/evCharger/status/state/{state}", tags=["evCharger"])
async def chargerStateWise(state: str):
    return _logicRealTime._stateWiseChargerStatus(state).serviceAnalysis

# To get charger details all india level, state level, city level, pincode level with total, active, inactive, faulted, star chargers
@router.get("/evCharger/status/{country}/", tags=["evCharger"])
# @cache(namespace="chargerdetails",expire=270)
async def chargerStateWise(country: str, chargers :str, state: Optional[str] = None, city: Optional[str] = None, postalcode: Optional[str] = None):
    return _logicRealTime._chargerStatus(country, chargers, state, city, postalcode).serviceAnalysis

# To get charging sessions for all India Level, state, city
@router.get("/evCharger/chargingSession/{requirement}", tags=["evCharger"])
# @cache(namespace="chargingsession",expire=240)
async def chargerStateWise(requirement: str, need: Optional[str] = None, state: Optional[str] = None, city: Optional[str] = None, postalcode: Optional[str] = None):
    return _logicRealTime._ChargingSession(requirement, need, state, city, postalcode).serviceAnalysis
    # return 0

@router.get("/evCharger/occplogs/{identifier}", tags=["evCharger"])
async def chargerStateWise(identifier: str):
    return _logicRealTime._occpLogsIdentifier(identifier).serviceAnalysis

# To get charger details like model, number of location partner, service provider
@router.post("/evCharger/getAllChargerDetails", tags=["evCharger"])
async def chargerStateWise(data: ChargerData):
    return _logicRealTime._mapChargerInactivity(data).serviceAnalysis

@router.get("/evCharger/alarmlogs/{state}/{identifier}", tags=["evCharger"])
# @cache(namespace="alarmlogs",expire=300)
async def chargerStateWise(identifier: str):
    return _logicRealTime._alarmFaultLogs(identifier).serviceAnalysis

#Alarm and Fault table list for a date range 
@router.get("/evCharger/alarmlogs/total/{start_date}/{end_date}", tags=["evCharger"])
# @cache(namespace="alarm_count",expire=300)
async def chargerStateWise(start_date: str,end_date:str):
    return _logicRealTime._alarmTotalFaultLogs(start_date, end_date).serviceAnalysis

#Alarm and Fault Dashboard Count
@router.get("/evCharger/alarmlogs/totalcount/{start_date}/{end_date}", tags=["evCharger"])
async def chargerStateWise(start_date: str,end_date:str):
    return _logicRealTime._alarmTotalFaultLogsCount(start_date, end_date).serviceAnalysis

# To get stuck booking details and count
@router.get("/evCharger/stuck/Booking/{requirement}", tags=["evCharger"])
# @cache(namespace="stuckbooking",expire=240)
async def chargerStateWise(requirement: str, state: Optional[str] = None, city: Optional[str] = None, postalcode: Optional[str] = None):
    return _logicRealTime.stuckBookingDetails(requirement, state, city, postalcode).serviceAnalysis
    # return 0    


@router.get("/evCharger/stuck/Booking/mapView", tags=["evCharger"])
async def stuckBooking():
    return _logicRealTime.stuckBookingMap().serviceAnalysis    


@router.get("/evCharger/server/health/monitoring", tags=["evCharger"])
async def chargerStateWise():
    return _logicRealTime._serverHealth().serviceAnalysis    

@router.get("/evCharger/charger/hardreset", tags=["evCharger"])
async def chargerReset():
    return _logicRealTime.ChargerResetConfiguration().serviceAnalysis   



@router.post("/evCharger/stuck/booking/action", tags=["evCharger"])
async def stuckBookingAction(data: StuckData):
    # print(data)
    return _logicRealTime.stuckBookingActions(data.bookingID,data.evseID,data.connectorID).serviceAnalysis    

# This API is used to hardreset the charger
@router.post("/evCharger/hardreset/action", tags=["evCharger"])
async def stuckBookingAction(data: hardResetCharger):
    # print(data)
    return _logicRealTime.hardResetActions(data.identifier).serviceAnalysis    


@router.post("/evCharger/onboard/charger", tags=["evCharger"])
async def chargerOnboard(data: Onboard):
    # print(data.chargerType)
    return _logicRealTime.chargerOnboard(data.chargerType).serviceAnalysis    

# To get count of all chargers, faulted, star and active inactive 
@router.get("/evCharger/fleetViewChargerStats/{country}", tags=["evCharger"])
# @cache(namespace="count",expire=240)
async def fleetViewsCharger(country: str,  state: Optional[str] = None, city: Optional[str] = None, postalcode: Optional[str] = None):
    return fleetViewService._allChargerStatus(country, state, city, postalcode).serviceAnalysis    

# To get count of all chargers typewise from excel input file
@router.get("/evCharger/getTypewiseChargerCount/", tags=["evCharger"])
async def getTypewiseChargerCount():
    return fleetViewService.TypewiseChargerCount().serviceAnalysis    


# To get cities from state
@router.get("/evCharger/getCities/{state}", tags=["evCharger"])
async def fleetViewsCharger(state: str):
    # print(state)
    return fleetViewService._getCitiesFromState(state).serviceAnalysis    

@router.get("/evCharger/getLatLon/{state}", tags=["evCharger"])
async def fleetViewsCharger(state: str):
    # print(state)
    return fleetViewService._getLatLonState(state).serviceAnalysis 

# To get postalcodes from city
@router.get("/evCharger/getPostalcodes/{city}", tags=["evCharger"])
async def fleetViewsCharger(city: str):
    return fleetViewService._getPincodesFromCity(city).serviceAnalysis    

# Get charger count which are became iactive today
@router.get("/evCharger/getTodaysActiveChargerCount", tags=["evCharger"])
async def fleetViewsCharger():
    return fleetViewService._getTodaysActiveChargerCount().serviceAnalysis  


# To get today's inactive charger details
@router.get("/evCharger/getTodaysInactiveChargers/{requirement}", tags=["evCharger"])
# @cache(namespace="todayinactive",expire=240)
async def fleetViewsCharger(requirement: str, chargerType : Optional[str] = None):
    return fleetViewService._getTodaysInactiveChargers(requirement, chargerType).serviceAnalysis    


@router.get("/evCharger/{username}", tags=["evCharger"])
async def read_user(username: str):
    return {"username": username}


# To get postalcodes from city
@router.get("/evCharger/getImportantChargers/{state}", tags=["evCharger"])
async def getImportantChargers(state: str):
    return fleetViewService._getImportantChargers(state).serviceAnalysis    


# This method acknowlwdges the charger
@router.post("/evCharger/acknowledge/charger", tags=["evCharger"])
async def chargerOnboard(data:acknowledgeCharger ):
    # print(data.chargerID)
    return _logicRealTime.chargerAcknowledgement(data.chargerID)

# This method removes active charger from acknowlwdged charger
@router.get("/evCharger/acknowledge/removeActiveAck", tags=["evCharger"])
async def chargerOnboard():
    # print("Hello")
    return _logicRealTime.removeActiveAck()


# It adds highway or priority charger to file 
@router.post("/evCharger/addHighwayOrPriorityCharger", tags=["evCharger"])
async def chargerOnboard(data: List[highwayPriorityChargers], charger_type: Optional[str] = None ):
    return _logicRealTime.addChargerToFile(jsonable_encoder(data), charger_type)

# It deltes highway or priority charger from file 
@router.post("/evCharger/deleteHighwayOrPriorityCharger", tags=["evCharger"])
async def chargerOnboard(data: List[highwayPriorityChargers], charger_type: Optional[str] = None ):
    return _logicRealTime.deleteChargerFromFile(jsonable_encoder(data), charger_type)


# To get highway chargers or priority chargers
@router.get("/evCharger/getHighwayOrPriorityChargers/{requirement}", tags=["evCharger"])
# @cache(namespace="priority",expire=240)
async def fleetViewsCharger(requirement: str):
    # print(requirement)
    return fleetViewService._getHighwayOrPriorityChargers(requirement).serviceAnalysis 


@router.get("/evCharger/busCharger/status", tags=["BusCharger"])
async def read_users():
    data = _logicRealTime._stateBusChargerStatus().serviceAnalysis
    return data  


# To get bus charger details all india level, state level, city level with total, active, inactive, faulted chargers
@router.get("/evCharger/busCharger/status/{country}/", tags=["BusCharger"])
async def chargerStateWise(country: str, chargers :str, state: Optional[str] = None, city: Optional[str] = None):
    return _logicRealTime._busChargerStatus(country, chargers, state, city).serviceAnalysis


# To get bus charger details like model, number of location partner, service provider
@router.post("/evCharger/busCharger/getAllChargerDetails", tags=["BusCharger"])
async def chargerStateWise(data: ChargerData):
    return _logicRealTime._mapBusChargerInactivity(data).serviceAnalysis


# To get count of all bus chargers, faulted and active inactive 
@router.get("/evCharger/busCharger/fleetViewChargerStats/{country}", tags=["BusCharger"])
async def fleetViewsCharger(country: str,  state: Optional[str] = None, city: Optional[str] = None):
    return fleetViewService._allBusChargerStatus(country, state, city).serviceAnalysis   

# To get bus cities from state
@router.get("/evCharger/busCharger/getCities/{state}", tags=["BusCharger"])
async def fleetViewsCharger(state: str):
    # print(state)
    return fleetViewService._getBusCitiesFromState(state).serviceAnalysis  

# To get bus depo names from city
@router.get("/evCharger/busCharger/getDepos/{city}", tags=["BusCharger"])
async def fleetViewsCharger(city: str):
    # print(city)
    return fleetViewService._getBusDeposFromCity(city).serviceAnalysis  

# To get today's inactive bus charger details
@router.get("/evCharger/busCharger/getTodaysInactiveChargers/{requirement}", tags=["BusCharger"])
async def fleetViewsCharger(requirement: str, chargerType : Optional[str] = None):
    return fleetViewService._getTodaysInactiveBusChargers(requirement, chargerType).serviceAnalysis

# To return count of connectors against each bus depot
@router.get("/evCharger/busCharger/getCountConnectorBusDepot", tags=["BusCharger"])
async def fleetViewsCharger():
    return fleetViewService._getCountConnectorBusDepot().serviceAnalysis

# This will return CIDS Dashboard
@router.get("/evCharger/busCharger/CIDS_details/{stationName}", tags=["BusCharger"])
async def fleetViewsCharger(stationName: str):
    return fleetViewService._dashboardCIDS(stationName).serviceAnalysis

#Star & highwayCharger check uncheck
@router.get("/evCharger/check/starHighway", tags=["BusCharger"])
# @cache(namespace="starhighway",expire=86400)
async def fleetViewsCharger():
    return fleetViewService._StarHighwayChargers().serviceAnalysis

# To get charging sessions for all  bus depots at India Level, state, city
@router.get("/evCharger/busCharger/ChargingSessionBusDepot/{requirement}", tags=["BusCharger"])
async def chargerStateWise(requirement: str, need: Optional[str] = None, state: Optional[str] = None, city: Optional[str] = None):
    return _logicRealTime._ChargingSessionBusDepot(requirement, need, state, city).serviceAnalysis


#Test
@router.get("/evCharger/check/TestBus", tags=["BusCharger"])
async def fleetViewsCharger():
    return fleetViewService._TestBus().serviceAnalysis


    #######################################
    ##Analytics



# To get zero transaction unit count
@router.get("/evCharger/getZeroTransactionAnalytics/{start_date}/{end_date}", tags=["evCharger"])
# @cache(namespace="zerotransaction",expire=300)
async def fleetViewsCharger(start_date: str, end_date : str):
    return fleetViewService._getZeroTransactionAnalytics(start_date,end_date).serviceAnalysis 


# To get inactive chargers count due on csv to network issues
@router.get("/evCharger/Analytics/getInactiveCountNetworkIssues", tags=["evCharger"])
async def fleetViewsCharger():
    return fleetViewService._getInactiveCountNetworkIssues().serviceAnalysis 

# Read the csv of Inactive Chargers due to Network Issues
@router.get("/evCharger/Analytics/readCSVNetworkIssues", tags=["evCharger"])
# @cache(namespace="networkfailure",expire=86400)
async def fleetViewsCharger():
    return fleetViewService._readCSVNetworkIssues().serviceAnalysis

# Get the view details for inatcive chargers due to Network Issues
@router.get("/evCharger/Analytics/readCSVNetworkIssues/viewDetailsNetworkIssues/{identifier}", tags=["evCharger"])
async def fleetViewsCharger(identifier: str):
    return fleetViewService._viewDetailsNetworkIssues(identifier).serviceAnalysis

# To get inactive chargers count due on csv to Power Failure
@router.get("/evCharger/Analytics/getInactiveCountPowerFailure", tags=["evCharger"])
async def fleetViewsCharger():
    return fleetViewService._getInactiveCountPowerFailure().serviceAnalysis 

# Read the csv of Inactive Chargers due to Power Failure
@router.get("/evCharger/Analytics/readCSVPowerFailure", tags=["evCharger"])
# @cache(namespace="csvpowerfailure",expire=86400)
async def fleetViewsCharger():
    return fleetViewService._readCSVPowerFailure().serviceAnalysis

# Get the view details for inatcive chargers due to Power Failure
@router.get("/evCharger/Analytics/readCSVPowerFailure/viewDetailsPowerFailure/{identifier}", tags=["evCharger"])
async def fleetViewsCharger(identifier: str):
    return fleetViewService._viewDetailsPowerFailure(identifier).serviceAnalysis

# Get Weekly Charging Session Trend
@router.get("/evCharger/Analytics/chargingSessionTrendWeekly/{day}", tags=["evCharger"])
async def fleetViewsCharger(day:str):
    return fleetViewService._chargingSessionTrendWeekly(day).serviceAnalysis 

# Get Charging Session Trend for one day before
@router.get("/evCharger/Analytics/chargingSessionTrendDaily/{start_date}", tags=["evCharger"])
async def fleetViewsCharger(start_date: str):
    return fleetViewService._chargingSessionTrendDaily(start_date).serviceAnalysis 

@router.get("/evCharger/busCharger/CIDS/{depo}")
async def cidsDepos(depo:str):
    r=requests.get(url="http://172.21.3.11:8080/CIDS/getChargersforloaction/"+depo)
    data=r.json()
    # print(data)
    return data


#############################
#Charger Hits
# Get charger hits daily
@router.get("/evCharger/Analytics/chargerHitsDaily", tags=["evCharger"])
async def fleetViewsCharger(background_tasks: BackgroundTasks):
    background_tasks.add_task(service.performChargerHits)
    return {"msg":"task is running in background"}

# Read the csv of charger hits daily
@router.get("/evCharger/Analytics/readCSVChargerHits/{select_date}", tags=["evCharger"])
# @cache(namespace="csvchargerhits",expire=86400)
async def fleetViewsCharger(select_date: str):
    return fleetViewService._readCSVChargerHits(select_date).serviceAnalysis

#Perform analysis on cahrger hits
@router.get("/evCharger/Analytics/analysisOnChargerHits", tags=["evCharger"])
# @cache(namespace="analysischargerhits",expire=1)
async def fleetViewsCharger():
    return fleetViewService._analysisOnChargerHits().serviceAnalysis

#get fault details of the chargers --- CALLCENTER
@router.get("/evCharger/callCentre/faultDetails/{identifier}", tags=["evCharger"])
async def fleetViewsCharger(identifier: str):
    return fleetViewService._getFaultDetails(identifier).serviceAnalysis

@router.get("/evCharger/callCentre/otherDetails/{identifier}",tags=["evCharger"])
async def callCenterDetails(identifier:str):
    return fleetViewService._getOtherDetails(identifier).serviceAnalysis

# @router.post("/evCharger/callcenter/lepton/routes")
# async def getRoutes(routes:Routes):
#     try:
#         res=requests.post(url="https://api.leptonsoftware.com:9962/directions",
#                   headers={"accept":"application/json","Content-Type":"application/json"},
#                   data=json.dumps({"origin":routes.source,"destination":routes.destination,"decoded":"true"}))
#         # print(res.text)
#         return res.json()
#     except:
#         print("error",routes)
#         return False

@router.post("/evCharger/callcenter/lepton/routes")
async def getPois(poi_loc:Pois):
    # print(poi_loc)
    try:
        res=requests.post(url='https://api.leptonmaps.com/v1/tata_power/directions',
		    headers={"accept":"application/json","Content-Type":"application/json"},
		    data=json.dumps({"origin":poi_loc.source,"destination":poi_loc.destination,"decoded":True}))
        return res.json()
    except:
        return {"message":"unable to fetch data from lepton"}
    
#abhishek-start  
@router.post("/evCharger/modeltype")
async def getModelType(data: InputData):
    return fleetViewService._getChargerModelAndType(data).serviceAnalysis
#abhishek-end

@router.post("/evCharger/callcenter/amenities")
async def amenities(amenity:Amenity):
    overpass_api_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
        [out:json];
        (
            area["name"~'"""+amenity.state+"""']->.a;
            node(area.a)[amenity~'"""+amenity.filter+"""'];
        );
        out center;
    """
    try:
        api = overpy.Overpass(url=overpass_api_url)
        result = api.query(overpass_query)
        data=[]
        for node in result.nodes:
            data.append({"tags":node.tags,"latitude":node.lat,"longitude":node.lon})
        # print(data)
        return data
    except:
        return {"error":"unable to fetch data"}