import { AfterViewInit,Component, Input, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import {MatPaginator} from '@angular/material/paginator';
import { ApiService } from 'src/app/services/api.service';
import {Inject} from '@angular/core';
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';


export interface PeriodicElement {
  //identifier: string,
  msg: any,
  time: number,
  name: any,
  city: any,
  identifier: any,
  telecom_partner: any,
  inactive_duration: any,
  model: any,
  name_of_location_partener: any,
  email_of_location_partener: any,
  mobile_number_of_location_partener: any,
  connector_id: any;
  state: any
  }



@Component({
  selector: 'app-dialog',
  templateUrl: './dialog.component.html',
  styleUrls: ['./dialog.component.css']
})
export class DialogComponent{
    dataSource3:any;
    region:any;
    dataSource2:any;
    dataSource1:any;

    displayedColumns: string[] = ['time','msg'];
    displayedColumns1: string[] = ['name','city','identifier','make','model','inactive_duration','name_of_location_partener','email_of_location_partener','mobile_number_of_location_partener','telecom_partner'];
    displayedColumns2: string[] = ['SOURCE_IDENTIFIER','name','state','city','identifier','CONNECTOR_ID']
    displayedColumns3: string[] = ['SOURCE_IDENTIFIER','REQ_START_DATE','REQ_END_DATE','USAGE_STATUS','CDM_SESSION_ID','UNITS','ACTION','LOGS']
    dataSource:any;
    elementArray:any = [];

    @ViewChild(MatPaginator) paginator!: MatPaginator;
  publicchargeronboardlen: any;
  publicchargeronboardcount: any;
  corporatechargeronboardlen: any;
  corporatechargeronboardcount: any;
  homechargeronboardlen: any;
  homechargeronboardcount: any;
  captivechargeronboardlen: any;
  captivechargeronboardcount: any;
  housingchargeronboardlen: any;
  housingchargeronboardcount: any;
  buschargeronboardlen: any;
  buschargeronboardcount: any;
  publicchargerinstalledlen: any;
  publicchargerinstalledcount: any;
  corporatechargerinstalledlen: any;
  corporatechargerinstalledcount: any;
  homechargerinstalledlen: any;
  homechargerinstalledcount: any;
  captivechargerinstalledlen: any;
  captivechargerinstalledcount: any;
  hosingchargerinstalledlen: any;
  housingchargerinstalledcount: any;
  buschargerinstalledlen: any;
  buschargerinstalledcount: any;

    ngAfterViewInit() {
      this.dataSource3.paginator = this.paginator;
    }


    constructor(@Inject(MAT_DIALOG_DATA) public data:any, private router:Router, private _api:ApiService,
                        public dialog: MatDialog)
    {   
      this.region = data
      //console.log(this.region)
      //console.log(this.region['datakey'])
      this.tableCreation(this.region['datakey'])
      this.tableCreation1(this.region['datakey'])
      this.tableCreation2(this.region['datakey'])
      this.tableCreation3(this.region['datakey'])
    }

    _acknowledgement(_identifier: { [x: string]: any; }){

      if(confirm("Do you want to acknowledge for "+_identifier['identifier']+" ?")){
        this._api.postTypeRequest('evCharger/acknowledge/charger',JSON.stringify({"chargerID":_identifier['identifier']})).subscribe((res)=>{
          //console.log(res)  
          let currentUrl = this.router.url;
          //console.log(this.router.url);
          //console.log(this._api.selectedtab);
          
          this.router.navigateByUrl('/', {skipLocationChange: true}).then(() => {
            this.router.navigate([currentUrl]);
            //console.log(currentUrl);
          });      
        });
      }
      


    }

    _alertShow(_identifier: { [x: string]: any; }){

      //console.log(_identifier['identifier'])
      this.router.navigate(['alertView'], {queryParams: {data :_identifier['identifier']}});
      
    }

    tableCreation(data: any){
      for(var i=0; i<Object.keys(data).length;i++){
        this.elementArray[i] = data[i];
        } 
        //console.log(this.elementArray)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource = new MatTableDataSource(ELEMENT_DATA)    
    }

    clearstuckbooking(_id: any){
     
      var hardResetData = {
        'identifier':_id
      }
  
      alert('You want to proceed with given identifier to clear stuck booking: '+ hardResetData['identifier'])
  
      this._api.postTypeRequest('evCharger/hardreset/action',hardResetData).subscribe((res)=>{
          alert(res)
          this._getStuckBookingDetails();
      })
    }

    viewStucklogs(_id: string){
      // this._api.getTypeRequest('evCharger/occplogs/'+_id).subscribe((res)=>{
      //   //console.log(res)  
      //   this.region.condition = 'mapAlertClick'   
      //   this.tableCreation(res)
      //})
     if(  confirm(_id)){
        this._api.getTypeRequest('evCharger/occplogs/'+_id).subscribe((res)=>{
          //console.log(res)
          this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick'}});
          
     })}

        // this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick'}});    
    }

    
    tableCreation1(data: any[]){
      for(var i=0; i<Object.keys(data).length;i++){
        this.elementArray[i] = data[i];
        } 
        //console.log(this.elementArray)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource1 = new MatTableDataSource(ELEMENT_DATA)    
    }

    _viewDetails(){
      // this._api.getTypeRequest('evCharger/occplogs/'+_id).subscribe((res)=>{
      //   //console.log(res)  
      //   this.region.condition = 'mapAlertClick'   
      //   this.tableCreation(res)
      //})
        
        this._api.getTypeRequest('evCharger/getTodaysInactiveChargers/details').subscribe((res)=>{
          //console.log(res)
          this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick1'}});
          
     })

        // this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick'}});    
    }



    tableCreation2(data: any[]){
      for(var i=0; i<Object.keys(data).length;i++){
        this.elementArray[i] = data[i];
        } 
        //console.log(this.elementArray)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource2 = new MatTableDataSource(ELEMENT_DATA)    
    }

    _viewDetailsComplete(){
      // this._api.getTypeRequest('evCharger/occplogs/'+_id).subscribe((res)=>{
      //   //console.log(res)  
      //   this.region.condition = 'mapAlertClick'   
      //   this.tableCreation(res)
      //})
        
        this._api.getTypeRequest('evCharger/chargingSession/Charging?need=details').subscribe((res)=>{
          //console.log(res)
          this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick2'}});
          
     })

        // this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick'}});    
    }
    tableCreation3(data: any[]){
      for(var i=0; i<Object.keys(data).length;i++){
        this.elementArray[i] = data[i];
        } 
        //console.log(this.elementArray)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource3 = new MatTableDataSource(ELEMENT_DATA)    
    }
    _viewDetailsstuck(){
      // this._api.getTypeRequest('evCharger/occplogs/'+_id).subscribe((res)=>{
      //   //console.log(res)  
      //   this.region.condition = 'mapAlertClick'   
      //   this.tableCreation(res)
      //})
        
        this._api.getTypeRequest('evCharger/stuck/Booking/details').subscribe((res)=>{
          //console.log(res)
          this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick3'}});
          
     })

        // this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick'}});    
    }
    getlogs(id: string){
     // alert(id)
      this._api.getTypeRequest('evCharger/occplogs/'+id).subscribe((res)=>{
           //console.log(res)
           this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick'}});      
      })
    }
 _getStuckBookingDetails(){
    this._api.getTypeRequest("evCharger/stuck/Booking").subscribe((res:any)=>{
       //console.log(res)
       //console.log(res["response"]["responseObject"])
       for(var i=0; i<Object.keys(res['response']['responseObject']).length;i++){
        this.elementArray[i] = res['response']['responseObject'][i];
        } 
        //console.log(this.elementArray)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource = new MatTableDataSource(ELEMENT_DATA)     
    });
  }
    stuckAction(BOOKING_ID: any,EVSE_ID: any,CONNECTOR_ID: any){
      var stuckData = {
        'bookingID':BOOKING_ID,
        'evseID':EVSE_ID,
        'connectorID':CONNECTOR_ID
      }
  
   if( confirm('Do you want to clear the Booking: '+ stuckData['bookingID']))
   {
  
      this._api.postTypeRequest('evCharger/stuck/booking/action',stuckData).subscribe((res)=>{
          alert(res)
          this._getStuckBookingDetails();
      })}
  
    }

    closeDialog() {
      this.dialog.closeAll()
    }

    getcountofinstalled()
{
  this._api.getTypeRequest("evCharger/getTypewiseChargerCount/").subscribe((res:any)=>{
    this.dialog.open(DialogComponent,{data:{datakey:res,condition:'mapAlertClick5'}})
    const JSobj = JSON.stringify(res);
   
    let jsonObj = JSON.parse(JSobj)

    this.publicchargeronboardlen=jsonObj.publicChargerOnboarded
    //console.log(this.publicchargeronboardlen);
    
     this.publicchargeronboardcount = res ['publicchargeronboardcount']

     this.corporatechargeronboardlen=jsonObj.corporateChargerOnboarded
     this.corporatechargeronboardcount = res ['corporatechargeronboardcount']

     this.homechargeronboardlen=jsonObj.homeChargerOnboarded
     this.homechargeronboardcount = res ['homechargeronboardcount']

     this.captivechargeronboardlen=jsonObj.captiveChargerOnboarded
     this.captivechargeronboardcount = res ['captivechargeronboardcount']

     this.housingchargeronboardlen=jsonObj.housingScietyChargerOnboarded
     this.housingchargeronboardcount = res ['housingchargeronboardcount']

     this.buschargeronboardlen=jsonObj.busChargerOnboarded
     this.buschargeronboardcount = res ['buschargeronboardcount']

     this.publicchargerinstalledlen=jsonObj.publicChargerInstalled
     this.publicchargerinstalledcount = res ['publicchargerinstalledcount']

     this.corporatechargerinstalledlen=jsonObj.corporateChargerInstalled
     this.corporatechargerinstalledcount = res ['corporatechargerinstalledcount']

     this.homechargerinstalledlen=jsonObj.homeChargerInstalled
     this.homechargerinstalledcount = res ['homechargerinstalledcount']

     this.captivechargerinstalledlen=jsonObj.captiveChargerInstalled
     this.captivechargerinstalledcount = res ['captivechargerinstalledcount']

     this.hosingchargerinstalledlen=jsonObj.housingScietyChargerInstalled
     this.housingchargerinstalledcount = res ['housingchargerinstalledcount']

     this.buschargerinstalledlen=jsonObj.busChargerInstalled
     this.buschargerinstalledcount = res ['buschargerinstalledcount']




  });
}
}
