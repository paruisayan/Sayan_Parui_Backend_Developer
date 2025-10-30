import { HttpClient } from '@angular/common/http';
import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { Observable, map, startWith,Subject, filter, takeUntil } from 'rxjs';
import { ApiService } from 'src/app/services/api.service';
import { DialogComponent } from '../dialog/dialog.component';


@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  value="";
  //abhishek
  myControl: FormControl = new FormControl();

  options:any = []

  filteredOptions!: Observable<string[]>;
  //abhishek
  
  coordinates = {
    'Andhra Pradesh': [15.9129, 79.7400],
    'Arunachal Pradesh': [28.2180, 94.7278],
    'Assam': [26.2006, 92.9376],
    'Bihar': [25.0961, 85.3131],
    'Chhattisgarh': [21.2787, 81.8661],
    'Delhi': [28.6139, 77.2090],
    'Goa': [15.2993, 74.1240],
    'Gujarat': [22.309425, 72.136230],
    'Haryana': [29.0588, 76.0856],
    'Himachal Pradesh': [31.1048, 77.1734],
    'Jharkhand': [23.6102, 85.2799],
    'Jammu and Kashmir': [33.2778, 75.3412],
    'Karnataka': [15.3173, 75.7139],
    'Kerala': [10.8505, 76.2711],
    'Madhya Pradesh': [22.9734, 78.6569],
    'Maharashtra': [19.7515, 75.7139],
    'Manipur': [24.6637, 93.9063],
    'Meghalaya': [25.4670, 91.3662],
    'Mizoram': [23.1645, 92.9376],
    'Nagaland': [26.1584, 94.5624],
    'Odisha': [20.9517, 85.0985],
    'Punjab': [31.1471, 75.3412],
    'Pondicherry': [11.9139, 79.8145],
    'Rajasthan': [27.0238, 74.2179],
    'Sikkim': [27.5330, 88.5122],
    'Tamil Nadu': [11.1271, 78.6569],
    'Telangana': [18.1124, 79.0193],
    'Tripura': [23.9408, 91.9882],
    'Uttar Pradesh': [26.8467, 80.9462],
    'Uttarakhand': [30.0668, 79.0193],
    'West Bengal': [22.9868, 87.8550]
  }
  firstData: any;
  userData!: any;
  elementArray: any;
  keyword: any;
  input: any;
  totachargerlen: any;
  totaCharger: any;
  totaactivechargerlen: any;
  totaActivechargerlen: any;
  activeChargerCount: any;
  ActiveChargerCount: any;
  totalinactivechargerlen: any;
  totaInactivechargerlen: any;
  inactiveChargerCount: any;
  InActiveChargerCount: any;
  totalfaultchargerlen: any;
  faultchargercount: any;
  totalstarchargerlen: any;
  starchargercount: any;
  totalpublicchargerlen: any;
  publicchargercount: any;
  totalcaptivechargerlen: any;
  cactiveChargerCount: any;
  totalcorporatechargerlen: any;
  corporateChargerCount: any;
  highwaychargerlen: any;
  highwaychargercount: any;
  totalhomechargerlen: any;
  homeChargerCount: any;
  totalonBoardchargerlen: any;
  onBoardChargerCount: any;
  totalconnectorlen: any;
  totalConnetorcount: any;
  totalConnetor: any;
  activeCharger!: number;
  inactiveCharger!: number;
  activeConnetor!: number;
  inactiveConnetor!: number;
  faultedConnetor!: number;
  states: any;
  publicCharger: any;
  homeCharger: any;
  corporateCharger: any;
  response: any;
  mapdata: any;
  cityList:any=[];
  filteredMarker:any;
  _stateCharger:any = [];
  latitude: any=23;
  longitude:any=80;
  zoom:any;
  lat:any;
  lng:any;
  loader = false;
  stuckbookinglen=0;
  ongoinglen=0;
  completelen=0;
  activelen=0;
  inactivelen=0;
  userData1!:any;
  firstData1: any;
  cityList1!: any[];
  _pincode: any;
  maploader!: boolean;
  dataloader!: boolean;
  _city: any;
  _state: any;
  _mapflag!: string;
  _charger!: string;
  completeCharger: any;
  ongoingCharger: any;
  stuckbookingCharger: any;
  markers:any[]=[]
  FaultedArray!: any[];
  StarArray!: any[];
  highwayArray!: any[];
  activeMarker: any;
  inactiveMarker: any;
  selectedState: any='';
  selectedCity: any ='';
  selectedPin: any  ='';
  api: any;
  createAccountForm:any;
  activeuser!: string;

  constructor(private http:HttpClient,private router:Router,public dialog: MatDialog, private _api:ApiService){}
  
  ngOnInit(){
    this.createAccountForm = new FormGroup({
      _states: new FormControl(''),
      cities: new FormControl(''),
      postalcodes: new FormControl('')
    })
    this.selectedState='';
    this.selectedCity ='';
    this.selectedPin='';
    this.zoom= 4.6;
    this.lat= this.latitude;
    this.lng= this.longitude;

    this.markersData();
    this._getCountOfCharger(undefined,undefined)
    this._getinactiveChargerDetails()
    // this._getActiveCount()
    this._getchargingsession()
  
    setInterval(() => {
    //   this.createAccountForm = new FormGroup({
    //     _states: new FormControl(''),
    //     cities: new FormControl(''),
    //     postalcodes: new FormControl('')
    //   })
      this.markersData();
      this._getCountOfCharger(undefined,undefined)
      this._getinactiveChargerDetails()
      // this._getActiveCount()
      this._getchargingsession()
      },1000*300);
  }

  
  filter(val:any) {
    return this.options.filter((option:any) =>
      option.toLowerCase().includes(val.toLowerCase())
      )
  }
  _getinactiveChargerDetails(){
      this._api.getTypeRequest("evCharger/getTodaysInactiveChargers/count").subscribe((res:any)=>{
        this.inactivelen=res[0].count
        this.inactiveCharger = res['inactiveCharger']
      });
  }

  _getActiveCount(){
      this._api.getTypeRequest("evCharger/getTodaysActiveChargerCount").subscribe((res:any)=>{
        this.activelen=res[0].count
      })
  }

  _getchargingsession(){
      this._api.getTypeRequest("evCharger/chargingSession/Completed?need=count").subscribe((res:any)=>{
        this.completelen=res[0].completed_charging_sessions
        this.completeCharger = res['completeCharger']
      });

      this._api.getTypeRequest("evCharger/chargingSession/Charging?need=count").subscribe((res:any)=>{
        this.ongoinglen=res[0].ongoing_charging_sessions
        this.ongoingCharger = res['ongoingCharger']
      });
  
      this._api.getTypeRequest("evCharger/stuck/Booking/count").subscribe((res:any)=>{
        const JSobj = JSON.stringify(res);
        let jsonObj = JSON.parse(JSobj)
        this.stuckbookinglen=jsonObj.stuckBooking
        this.stuckbookingCharger = res ['stuckbookingCharger']
      });
  }

lastInfoWindow: any;

markersData(){
  this.loader=false;
  this._api.getTypeRequest("evCharger/status/India?chargers=all").subscribe((res:any)=>{
    this.elementArray = Object.keys(res).map(key=>{
      return res[key];
     })
     this.plotmarker('','','');
     this.elementArray.filter((element: { identifier: string; name: string; city: string;state:string},index:any)=>{
      this.options.push(element.identifier+" "+element.name + " "+element.city+" "+element.state+" "+index)
     })

     this.filteredOptions = this.myControl.valueChanges
     .pipe(
       startWith(''),
       map(val => this.filter(val))
     );
  })
}

onOptionSelected(event: MatAutocompleteSelectedEvent): void {
  const selectedValue = event.option.value;
  var array = selectedValue.split(" ");
  console.log("sel arr",array)
  var id = array[0];
  var state,city
  for(let i = 0 ; i < Object.keys(this.coordinates).length ; i++)
  {
    if(array[array.length-2]==Object.keys(this.coordinates)[i])
    {
      state=array[array.length-2];
      city=array[array.length-3];
      break;
    }
    else if((array[array.length-3]+" "+array[array.length-2])==Object.keys(this.coordinates)[i]){
      state=array[array.length-3]+" "+array[array.length-2];
      city=array[array.length-4];
      break;
    }
    else if((array[array.length-4]+" "+array[array.length-3]+" "+array[array.length-2])==Object.keys(this.coordinates)[i]){
      state=array[array.length-4]+" "+array[array.length-3]+" "+array[array.length-2];
      city=array[array.length-5];
      break;
    }
    else{
      continue;
    }
  }
  var index = array[array.length-1]
  this.openWindow(index)
  var main = "";
  for(let i = 1 ; i < array.length-1 ; i++)
  {
    main = main + array[i]
  }
  // console.log("split array",array)
  this._chargingSession(main,id,city,state);
}

markerClicked(marker: any, index: number, infoWindowRef: any) {
  if (this.lastInfoWindow) {
    this.lastInfoWindow.close();
  }
  this.lastInfoWindow = infoWindowRef;
}
isInfoWindowOpen(id:number){
  return this.openedWindow==id
}
openedWindow:any;
openWindow(id: number){
  this.openedWindow=id
}
onMouseOver(infoWindowRef:any) {
    infoWindowRef.open();
}

onMouseOut(infoWindowRef:any) {
    infoWindowRef.close();
}

filterMarker(filteredMarker:any){
  // //console.log(filteredMarker)
  this.markers=[]
  Object.entries(filteredMarker).forEach((key:any,value)=>{
    if(key[1]['cdmstatus']==1){
                    this.markers.push({lat:key[1]['latitude'],
                       lng:key[1]['longitude'],
                       identifier:key[1]['identifier'],
                       name:key[1]['name'],
                       city:key[1]['city'],
                       icon:{url:'assets/images/EV NOC Icons_location green.png',scaledSize: {
                        width:  35,
                        height: 35
                      }}
                      })
    }
    else if (key[1]['cdmstatus']==2){
                  this.markers.push({lat:key[1]['latitude'],
                  lng:key[1]['longitude'],
                  identifier:key[1]['identifier'],
                  name:key[1]['name'],
                  city:key[1]['city'],
                  icon:{url:'assets/images/Red_circle.gif',scaledSize: {
                   width:  35,
                   height: 35
                 }}
                })
    }
    else if (key[1]['cdmstatus']==5){
      this.markers.push({lat:key[1]['latitude'],
      lng:key[1]['longitude'],
      identifier:key[1]['identifier'],
      name:key[1]['name'],
      city:key[1]['city'],
      icon:{url:'assets/images/EV NOC Icons_location purple.png',scaledSize: {
       width:  35,
       height: 35
     }}
    })
  }
else if (key[1]['cdmstatus']==7){
        this.markers.push({lat:key[1]['latitude'],
        lng:key[1]['longitude'],
        identifier:key[1]['identifier'],
        name:key[1]['name'],
        city:key[1]['city'],
        icon:{url:'assets/images/visit.png',scaledSize: {
         width:  35,
         height: 35}}
      })
    }
  })
  // //console.log(this.markers)
  this.loader=true;
}

selectedTab(tabName:any){
  //console.log(this.selectedState)
  if(tabName=='active'){
    this.activeMarker=this.filteredMarker.filter((item:any)=>item.cdmstatus==1)
    this.filterMarker(this.activeMarker);
  }
  else if(tabName=='inactive'){
    this.inactiveMarker=this.filteredMarker.filter((item:any)=>item.cdmstatus==2)
    this.filterMarker(this.inactiveMarker);
  }
  else if(tabName=='faulted'){
    if(!this.selectedState){
    this._api.getTypeRequest("evCharger/status/India/?chargers=faulted").subscribe((res:any)=>{
      this.FaultedArray = Object.keys(res).map(key=>{
        return res[key];
       })
       this.filterMarker(this.FaultedArray);
    })
  }
  else{
    if(this.selectedCity){
      this.api="&state="+this.selectedCity;
    }
    if(this.selectedPin){
      this.api="&postalcode="+this.selectedPin;
    }
    if(this.selectedState){
      this.api="&state="+this.selectedState;
    }
    this._api.getTypeRequest("evCharger/status/India/?chargers=faulted"+this.api).subscribe((res:any)=>{
      this.FaultedArray = Object.keys(res).map(key=>{
        return res[key];
       })
       this.filterMarker(this.FaultedArray);
    })
  }

  }
  else if(tabName=="star"){
    if(!this.selectedState){
    this._api.getTypeRequest("evCharger/status/India/?chargers=star").subscribe((res:any)=>{
      this.StarArray=Object.keys(res).map(key=>{
        return res[key];
       })
       this.filterMarker(this.StarArray);
    })
  }
  else{
    if(this.selectedCity){
      this.api="&state="+this.selectedCity;
    }
    if(this.selectedPin){
      this.api="&postalcode="+this.selectedPin;
    }
    if(this.selectedState){
      this.api="&state="+this.selectedState;
    }
    this._api.getTypeRequest("evCharger/status/India/?chargers=star"+this.api).subscribe((res:any)=>{
      this.StarArray=Object.keys(res).map(key=>{
        return res[key];
       })
       this.filterMarker(this.StarArray);
    })
  }
  }
  else if(tabName=="highway"){
    this._api.getTypeRequest("evCharger/status/India/?chargers=highway").subscribe((res:any)=>{
      this.highwayArray=Object.keys(res).map(key=>{
        return res[key];
      })
      this.filterMarker(this.highwayArray);
    })
  }
  else{
    // this.totalMarker=this.filteredMarker.filter((item:any)=>item)
    this.filterMarker(this.filteredMarker);
  }
}

plotmarker(state:any,city:any,pin:any){
  if(state.length!=0){
    this.filteredMarker=this.elementArray.filter((items:any)=>items.state==state)
    // //console.log(this.filteredMarker)
    this.filterMarker(this.filteredMarker);
    }
    else if(city.length!=0){
      this.filteredMarker=this.elementArray.filter((item:any)=>item.city==city)
      this.lat=this.filteredMarker[0]['latitude']
      this.lng=this.filteredMarker[0]['longitude']
      this.zoom=8.7;
      this.filterMarker(this.filteredMarker);
    }
    else if(pin.length!=0){
      this.filteredMarker=this.elementArray.filter((item:any)=>item.postalcode==pin)
      this.lat=this.filteredMarker[0]['latitude']
      this.lng=this.filteredMarker[0]['longitude']
      this.zoom=10;
      this.filterMarker(this.filteredMarker)
    }
    else{
      this.filteredMarker=this.elementArray;
      this.zoom= 4.6;
      this.lat= this.latitude;
      this.lng= this.longitude;
      this.filterMarker(this.filteredMarker);
      this.loader=true;
    }
}

onChangeState(event:any){
  Object.entries(this.coordinates).forEach(key => {
    if (key[0] == event.target.value) {
        this.lat=key[1][0]
        this.lng=key[1][1]
        this.zoom=7
      }
    })
  this.selectedState=event.target.value;
  if(!this.selectedState){
    this.plotmarker(event.target.value,'','')
  }
  else{
  this.plotmarker(event.target.value,'','')
  }
  this._api.getTypeRequest('evCharger/getCities/'+event.target.value).subscribe(
    (data:any) => {
      this.userData= data;
        this.firstData= this.userData[0]
        this.cityList=[];
        for( let m in this.firstData)
        {
          this.cityList.push(this.firstData[m]);
        }
  });
}

onChangeCity(event:any) {
  this.selectedCity=event.target.value;
  this.plotmarker('',event.target.value,'')
  this._api.getPostalCode(event.target.value).subscribe(
    data => {
      this.userData1= data;
        this.firstData1 = this.userData1[0]
        this.cityList1=[];
        for( let n in this.firstData1)
        {
          this.cityList1.push(this.firstData1[n]);
        }
        
    });
}

onChangePin(event:any){
  this.selectedPin=event.target.value;
  this.plotmarker('','',event.target.value);
}

_getCountOfCharger(input:any,keyword:any){
  if(typeof(input) === 'object' || typeof(input) === 'string')
  {
    this.keyword=keyword
    this.input = input.target.value
     if(this.input == '')
    {
      this._api.getTypeRequest("evCharger/fleetViewChargerStats/India").subscribe((res:any)=>{
      const JSobj = JSON.stringify(res);
       let jsonObj = JSON.parse(JSobj)
       this.totachargerlen=jsonObj.totalCharger
       this.totaCharger = res['totaCharger']
       this.totaactivechargerlen=jsonObj.activeCharger
       this.totaActivechargerlen=jsonObj.totalactiveCharger
       this.activeChargerCount = res['activeChargerCount']
       this.ActiveChargerCount = res['ActiveChargerCount']
       this.totalinactivechargerlen=jsonObj.inactiveCharger
       this.totaInactivechargerlen=jsonObj.totalinactiveCharger
       this.inactiveChargerCount = res['inactiveChargerCount']
       this.InActiveChargerCount = res['InActiveChargerCount']
       this.totalfaultchargerlen=jsonObj.faultedCharger
       this.faultchargercount = res ['faultchargercount']
       this.totalstarchargerlen=jsonObj.starCharger
       this.starchargercount = res ['starchargercount']
       this.totalpublicchargerlen=jsonObj.publicCharger
       this.publicchargercount = res ['publicchargercount']
       this.totalcaptivechargerlen=jsonObj.captiveCharger
       this.cactiveChargerCount = res ['cactiveChargerCount']
       this.totalcorporatechargerlen=jsonObj.corporateCharger
       this.corporateChargerCount = res ['corporateChargerCount']
       this.highwaychargerlen=jsonObj.highwayChargers
       this.highwaychargercount = res ['highwaychargercount']
       this.totalhomechargerlen=jsonObj.homeCharger
       this.homeChargerCount = res ['homeChargerCount']
       this.totalonBoardchargerlen=jsonObj.onBoardedChargers
       this.onBoardChargerCount = res ['onBoardChargerCount']
       this.totalconnectorlen=jsonObj.totalConnetor
       this.totalConnetorcount = res ['totalConnetorcount']
       this.totalConnetor = res['totalConnetor']
       this.activeCharger = Math.round(res['activeCharger']*100)
       this.inactiveCharger = Math.round(res['inactiveCharger']*100)
       this.activeConnetor = res['activeConnetor']*100
       this.inactiveConnetor = res['inactiveConnetor']*100
       this.faultedConnetor = res['faultedConnetor']*100
       this.states = res['state']
       this.inactiveChargerCount = res['totalinactiveCharger']
       this.publicCharger = res['publicCharger']
       this.homeCharger = res['homeCharger']
       this.corporateCharger = res['corporateCharger']
      });
    }   
 else  if(this.input!== undefined && keyword==='state' )
    {
      this._api.getTypeRequest("evCharger/fleetViewChargerStats/India?state="+this.input).subscribe((res:any)=>{
       this.response=res;
       const JSobj = JSON.stringify(res);
       let jsonObj = JSON.parse(JSobj)
       this.totachargerlen=jsonObj.totalCharger
       this.totaCharger = res['totaCharger']
       this.totaactivechargerlen=jsonObj.activeCharger
       this.totaActivechargerlen=jsonObj.totalactiveCharger
       this.activeChargerCount = res['activeChargerCount']
       this.ActiveChargerCount = res['ActiveChargerCount']
       this.totalinactivechargerlen=jsonObj.inactiveCharger
       this.totaInactivechargerlen=jsonObj.totalinactiveCharger
       this.inactiveChargerCount = res['inactiveChargerCount']
       this.InActiveChargerCount = res['InActiveChargerCount']
       this.totalfaultchargerlen=jsonObj.faultedCharger
       this.faultchargercount = res ['faultchargercount']
       this.totalstarchargerlen=jsonObj.starCharger
       this.starchargercount = res ['starchargercount']
       this.totalpublicchargerlen=jsonObj.publicCharger
       this.publicchargercount = res ['publicchargercount']
       this.totalcaptivechargerlen=jsonObj.captiveCharger
       this.cactiveChargerCount = res ['cactiveChargerCount']
       this.totalcorporatechargerlen=jsonObj.corporateCharger
       this.corporateChargerCount = res ['corporateChargerCount']
       this.totalhomechargerlen=jsonObj.homeCharger
       this.homeChargerCount = res ['homeChargerCount']
       this.totalonBoardchargerlen=jsonObj.onBoardedChargers
       this.onBoardChargerCount = res ['onBoardChargerCount']
       this.totalConnetor = res['totalConnetor']
       this.activeCharger = Math.round(res['activeCharger']*100)
       this.inactiveCharger = Math.round(res['inactiveCharger']*100)
       this.activeConnetor = res['activeConnetor']*100
       this.inactiveConnetor = res['inactiveConnetor']*100
       this.faultedConnetor = res['faultedConnetor']*100
       this.states = res['state']
       this.inactiveChargerCount = res['totalinactiveCharger']
       this.publicCharger = res['publicCharger']
       this.homeCharger = res['homeCharger']
       this.corporateCharger = res['corporateCharger'] 
    });
  }
  else  if(this.input!== undefined && keyword==='city' )
    {
      this._api.getTypeRequest("evCharger/fleetViewChargerStats/India?city="+this.input).subscribe((res:any)=>{
       this.response=res;
       const JSobj = JSON.stringify(res);
       let jsonObj = JSON.parse(JSobj)
       this.totachargerlen=jsonObj.totalCharger
       this.totaCharger = res['totaCharger']
       this.totaactivechargerlen=jsonObj.activeCharger
       this.totaActivechargerlen=jsonObj.totalactiveCharger
       this.activeChargerCount = res['activeChargerCount']
       this.ActiveChargerCount = res['ActiveChargerCount']
       this.totalinactivechargerlen=jsonObj.inactiveCharger
       this.totaInactivechargerlen=jsonObj.totalinactiveCharger
       this.inactiveChargerCount = res['inactiveChargerCount']
       this.InActiveChargerCount = res['InActiveChargerCount']
       this.totalfaultchargerlen=jsonObj.faultedCharger
       this.faultchargercount = res ['faultchargercount']
       this.totalstarchargerlen=jsonObj.starCharger
       this.starchargercount = res ['starchargercount']
       this.totalpublicchargerlen=jsonObj.publicCharger
       this.publicchargercount = res ['publicchargercount']
       this.totalcaptivechargerlen=jsonObj.captiveCharger
       this.cactiveChargerCount = res ['cactiveChargerCount']
       this.totalcorporatechargerlen=jsonObj.corporateCharger
       this.corporateChargerCount = res ['corporateChargerCount']
       this.totalhomechargerlen=jsonObj.homeCharger
       this.homeChargerCount = res ['homeChargerCount']
       this.totalonBoardchargerlen=jsonObj.onBoardedChargers
       this.onBoardChargerCount = res ['onBoardChargerCount']
       this.totalConnetor = res['totalConnetor']
       this.activeCharger = Math.round(res['activeCharger']*100)
       this.inactiveCharger = Math.round(res['inactiveCharger']*100)
       this.activeConnetor = res['activeConnetor']*100
       this.inactiveConnetor = res['inactiveConnetor']*100
       this.faultedConnetor = res['faultedConnetor']*100
       this.states = res['state']
       this.inactiveChargerCount = res['totalinactiveCharger']
       this.publicCharger = res['publicCharger']
       this.homeCharger = res['homeCharger']
       this.corporateCharger = res['corporateCharger']  
    });
  }
  else if(this.input!== undefined && keyword==='postalcode' )
    {
      this._api.getTypeRequest("evCharger/fleetViewChargerStats/India?postalcode="+this.input).subscribe((res:any)=>{
       this.response=res;
       const JSobj = JSON.stringify(res);
       let jsonObj = JSON.parse(JSobj)
       this.totachargerlen=jsonObj.totalCharger
       this.totaCharger = res['totaCharger']
       this.totaactivechargerlen=jsonObj.activeCharger
       this.totaActivechargerlen=jsonObj.totalactiveCharger
       this.activeChargerCount = res['activeChargerCount']
       this.ActiveChargerCount = res['ActiveChargerCount']
       this.totalinactivechargerlen=jsonObj.inactiveCharger
       this.totaInactivechargerlen=jsonObj.totalinactiveCharger
       this.inactiveChargerCount = res['inactiveChargerCount']
       this.InActiveChargerCount = res['InActiveChargerCount']
       this.totalfaultchargerlen=jsonObj.faultedCharger
       this.faultchargercount = res ['faultchargercount']
       this.totalstarchargerlen=jsonObj.starCharger
       this.starchargercount = res ['starchargercount']
       this.totalpublicchargerlen=jsonObj.publicCharger
       this.publicchargercount = res ['publicchargercount']
       this.totalcaptivechargerlen=jsonObj.captiveCharger
       this.cactiveChargerCount = res ['cactiveChargerCount']
       this.totalcorporatechargerlen=jsonObj.corporateCharger
       this.corporateChargerCount = res ['corporateChargerCount']
       this.totalhomechargerlen=jsonObj.homeCharger
       this.homeChargerCount = res ['homeChargerCount']
       this.totalonBoardchargerlen=jsonObj.onBoardedChargers
       this.onBoardChargerCount = res ['onBoardChargerCount']
       this.totalConnetor = res['totalConnetor']
       this.activeCharger = Math.round(res['activeCharger']*100)
       this.inactiveCharger = Math.round(res['inactiveCharger']*100)
       this.activeConnetor = res['activeConnetor']*100
       this.inactiveConnetor = res['inactiveConnetor']*100
       this.faultedConnetor = res['faultedConnetor']*100
       this.states = res['state']
       this.inactiveChargerCount = res['totalinactiveCharger']
       this.publicCharger = res['publicCharger']
       this.homeCharger = res['homeCharger']
       this.corporateCharger = res['corporateCharger'] 
    });
  }
}
else{
       this.keyword=keyword
       this.input=input
       this._api.getTypeRequest("evCharger/fleetViewChargerStats/India").subscribe((res:any)=>{
       const JSobj = JSON.stringify(res);
       let jsonObj = JSON.parse(JSobj)
       this.totachargerlen=jsonObj.totalCharger
       this.totaCharger = res['totaCharger']
       this.totaactivechargerlen=jsonObj.activeCharger
       this.totaActivechargerlen=jsonObj.totalactiveCharger
       this.activeChargerCount = res['activeChargerCount']
       this.ActiveChargerCount = res['ActiveChargerCount']
       this.totalinactivechargerlen=jsonObj.inactiveCharger
       this.totaInactivechargerlen=jsonObj.totalinactiveCharger
       this.inactiveChargerCount = res['inactiveChargerCount']
       this.InActiveChargerCount = res['InActiveChargerCount']
       this.totalfaultchargerlen=jsonObj.faultedCharger
       this.faultchargercount = res ['faultchargercount']
       this.totalstarchargerlen=jsonObj.starCharger
       this.starchargercount = res ['starchargercount']
       this.totalpublicchargerlen=jsonObj.publicCharger
       this.publicchargercount = res ['publicchargercount']
       this.totalcaptivechargerlen=jsonObj.captiveCharger
       this.cactiveChargerCount = res ['cactiveChargerCount']
       this.totalcorporatechargerlen=jsonObj.corporateCharger
       this.corporateChargerCount = res ['corporateChargerCount']
       this.highwaychargerlen=jsonObj.highwayChargers
       this.highwaychargercount = res ['highwaychargercount']
       this.totalhomechargerlen=jsonObj.homeCharger
       this.homeChargerCount = res ['homeChargerCount']
       this.totalonBoardchargerlen=jsonObj.onBoardedChargers
       this.onBoardChargerCount = res ['onBoardChargerCount']
       this.totalconnectorlen=jsonObj.totalConnetor
       this.totalConnetorcount = res ['totalConnetorcount']
       this.totalConnetor = res['totalConnetor']
       this.activeCharger = Math.round(res['activeCharger']*100)
       this.inactiveCharger = Math.round(res['inactiveCharger']*100)
       this.activeConnetor = res['activeConnetor']*100
       this.inactiveConnetor = res['inactiveConnetor']*100
       this.faultedConnetor = res['faultedConnetor']*100
       this.states = res['state']
       this.inactiveChargerCount = res['totalinactiveCharger']
       this.publicCharger = res['publicCharger']
       this.homeCharger = res['homeCharger']
       this.corporateCharger = res['corporateCharger'] 
    });
  }
}

_chargingSession(name:any,identifier:any,city:any,state:any){
  var data = {
    'station':name,
    'identifier':identifier,
    'city':city
    }
    Object.entries(this.coordinates).forEach(([key, value]) => {
      if (key.startsWith(state)) {
        this.lat=value[0]
        this.lng=value[1]
        this.zoom=8
      }
    });
  this._api.postTypeRequest('evCharger/getAllChargerDetails',data).subscribe((res)=>{
    this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapiconClick'}});  
  });
}

pressme()
  {
    this.router.navigateByUrl('/onboard-installed');
  }

  _viewDetailsComplete(){
      this._api.getTypeRequest('evCharger/chargingSession/Charging?need=details').subscribe((res)=>{
        this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick2'}});   
   })    
}
  _viewDetailsstuck(){
      this._api.getTypeRequest('evCharger/stuck/Booking/details').subscribe((res)=>{
      this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick3'}});
   })    
  }
  _viewDetails(){
      this._api.getTypeRequest('evCharger/getTodaysInactiveChargers/details').subscribe((res)=>{
      this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick1'}});    
   })    
  }
 
}
