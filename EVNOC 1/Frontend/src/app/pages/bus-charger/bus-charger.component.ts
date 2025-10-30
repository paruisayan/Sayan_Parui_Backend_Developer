import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { ApiService } from 'src/app/services/api.service';
import { DialogComponent } from '../dialog/dialog.component';

interface busCharger{
  status:any;
  charger_id:any;
  connector:any;
  startSoc:any;
  endSoc:any;
  remTime:any;
  name:any;
  }

@Component({
  selector: 'app-bus-charger',
  templateUrl: './bus-charger.component.html',
  styleUrls: ['./bus-charger.component.css']
})
export class BusChargerComponent implements OnInit{
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

  show=false;
  stationName:any;
  elementArray:any;
  corporatechargeronboardlen:any;
  housingchargeronboardlen:any;
  captivechargeronboardlen:any;
  homechargeronboardlen:any;
 
  displayedColumns: string[] = ['status','identifier','connector_id','startSoC','CurrentSoC','remTime'];
  completelen=0;
  ongoinglen=0;
  inactivelen=0;
  activelen=0;
  _charger!: string;
  userData: any;
  firstData: any;
  cityList: any;
  BuschargerService: any;
  depolist: any;
  map: any;
  _stateCharger!: any;
  maploader!: boolean;
  loader!: boolean;
  dataloader!: boolean;
  corporatechargeronboardcount: any;
  homechargeronboardcount: any;
  captivechargeronboardcount: any;
  housingchargeronboardcount: any;
  _state: any;
  tdata: any;
  lastInfoWindow: any;

  constructor(private _api:ApiService,private http:HttpClient,private dialog:MatDialog,private fb:FormBuilder) { }

  createAccountForm = new FormGroup({
    _states: new FormControl(''),
    cities: new FormControl(''),
    depos: new FormControl(''),
  })

  dataSource!:MatTableDataSource<busCharger>;
  @ViewChild('paginator') paginator!:MatPaginator;

  ngOnInit(){
    this.getcountofinstalled()
    this.getMarkers()
    this._getchargingsession()
    this._getinactiveChargerDetails()
    this. _getmapChargerDetails("inactive")
    this._charger = 'inactive'
  }

  getMarkers(){
    this._api.getTypeRequest("evCharger/busCharger/getCountConnectorBusDepot").subscribe((res)=>{
      console.log(res);
      this._stateCharger=res;
});
  }
  _getchargingsession() {
    this._api.getTypeRequest("evCharger/busCharger/ChargingSessionBusDepot/Completed?need=count").subscribe((res:any)=>{
      // //console.log("siri21",res[0].completed_charging_sessions)
      this.completelen=res[0].completed_charging_sessions 
      // //console.log(res)
    });
    this._api.getTypeRequest("evCharger/busCharger/ChargingSessionBusDepot/Charging?need=count").subscribe((res:any)=>{
      this.ongoinglen=res[0].ongoing_charging_sessions
    });
  }
  _getinactiveChargerDetails() {
    this._api.getTypeRequest("evCharger/busCharger/getTodaysInactiveChargers/count").subscribe((res:any)=>{
      this.inactivelen=res[0].count
    });
  }
  _getmapChargerDetails(charger:any) {
    this._stateCharger = [];
    this.maploader = false;
    this.loader = false;
    this.dataloader = false;
    this._charger = charger;
  }

  markerClicked(marker: any, index: number, infoWindowRef: any) {
    if (this.lastInfoWindow) {
      this.lastInfoWindow.close();
    }
    this.getStationDetails(marker.locationid)
    this.lastInfoWindow = infoWindowRef;
  }
  
  onMouseOver(infoWindowRef:any) {
      infoWindowRef.open();
  }
  
  onMouseOut(infoWindowRef:any) {
      infoWindowRef.close();
  }

  onChangeState(state:any){
    Object.entries(this.coordinates).forEach(key => {

      if (key[0] == state.target.value) {

      }

    })
    // //console.log(state.target.value)
    this._api.getCities(state.target.value).subscribe(
      data => {
        this.userData= data;
        // var lat=data[1][0];
        // var lng=data[2][0];
        // for( let i in this.userData)
        // {
          this.firstData= this.userData[0]
          // //console.log(this.firstData);
          this.cityList=[];
          for( let m in this.firstData)
          {
            this.cityList.push(this.firstData[m]);
          }
          // this.map.setView(new L.LatLng(lat,lng),7.5);
      }
    );
  }

  onChangeCity(city:any){
    this._api.getDepos(city.target.value).subscribe((data:any)=>{
      this.depolist=[];
      console.log(data)
      var lat=data[1][0];
      var lng=data[2][0];
      Object.entries(data[0]).forEach(key=>{
        this.depolist.push(key[1])
      })
    })
  }

  getDepoDetails(depo:any){
    this.getStationDetails(depo.target.value);
  }
  getStationDetails(depo: any) {
    this._api.cidsGetRequest("evCharger/busCharger/CIDS_details/"+depo).subscribe((res:any)=>{
      this.stationName=res[0].name;
      this.tdata=res;
      this.show=true;
      this.elementArray=[];
      for(var i=0; i<Object.keys(res).length;i++){
        this.elementArray[i] = res[i];
      } 
      this.dataSource=new MatTableDataSource(this.elementArray);
      this.dataSource.paginator=this.paginator;
  })
  }

  _viewDetailsComplete(){
    this._api.getTypeRequest('evCharger/busCharger/ChargingSessionBusDepot/Charging?need=details').subscribe((res)=>{
      this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick2'}}); 
  })
  }

  getcountofinstalled()
  {
  
    
    this._api.getTypeRequest("evCharger/busCharger/fleetViewChargerStats/India").subscribe((res:any)=>{
      // //console.log(res);
      
      const JSobj = JSON.stringify(res);
  
     
      let jsonObj = JSON.parse(JSobj)
  
    
  
       this.corporatechargeronboardlen=jsonObj.totalCharger
      //  //console.log(this.corporatechargeronboardlen);
       
       this.corporatechargeronboardcount = res ['corporatechargeronboardcount']
  
       this.homechargeronboardlen=jsonObj.totalactiveCharger
      //  //console.log(this.homechargeronboardlen);
       
       this.homechargeronboardcount = res ['homechargeronboardcount']
  
       this.captivechargeronboardlen=jsonObj.totalinactiveCharger
      //  //console.log(this.captivechargeronboardlen);
       
       this.captivechargeronboardcount = res ['captivechargeronboardcount']
  
       this.housingchargeronboardlen=jsonObj.faultedCharger
      //  //console.log(this.housingchargeronboardlen);
       
       this.housingchargeronboardcount = res ['housingchargeronboardcount']
  
      
  
    });
  }
  
  getcountofinstalled1(state:any)
  {
  this._state=state.target.value;
    
    this._api.getTypeRequest("evCharger/busCharger/fleetViewChargerStats/India?state="+this._state).subscribe((res:any)=>{
      // //console.log(res);
      
      const JSobj = JSON.stringify(res);
  
     
      let jsonObj = JSON.parse(JSobj)
  
    
  
       this.corporatechargeronboardlen=jsonObj.totalCharger
      //  //console.log(this.corporatechargeronboardlen);
       
       this.corporatechargeronboardcount = res ['corporatechargeronboardcount']
  
       this.homechargeronboardlen=jsonObj.activeCharger
      //  //console.log(this.homechargeronboardlen);
       
       this.homechargeronboardcount = res ['homechargeronboardcount']
  
       this.captivechargeronboardlen=jsonObj.totalinactiveCharger
      //  //console.log(this.captivechargeronboardlen);
       
       this.captivechargeronboardcount = res ['captivechargeronboardcount']
  
       this.housingchargeronboardlen=jsonObj.faultedCharger
      //  //console.log(this.housingchargeronboardlen);
       
       this.housingchargeronboardcount = res ['housingchargeronboardcount']
  
      
  
    });
  }

  viewDetails(){
    this._api.getTypeRequest('evCharger/busCharger/getTodaysInactiveChargers/details').subscribe((res)=>{
      this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick1'}});
    })
  }
}