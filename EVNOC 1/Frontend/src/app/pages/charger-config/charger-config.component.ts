import { Component,OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { ApiService } from 'src/app/services/api.service';
import { MatTabChangeEvent } from '@angular/material/tabs';
import { FormControl, FormGroup } from '@angular/forms';

export interface PeriodicElement {
  name: string,
  state: string,
  city: string,
  identifier: string,
  checkbox:any,
  checkbox1:any,
}

@Component({
  selector: 'app-charger-config',
  templateUrl: './charger-config.component.html',
  styleUrls: ['./charger-config.component.css']
})
export class ChargerConfigComponent implements OnInit{
  
  displayedColumns: string[] = ['name', 'state', 'city', 'identifier','checkbox','checkbox1'];
  displayedColumns1: string[] = ['name', 'state', 'city', 'identifier','checkbox'];
  displayedColumns2: string[] = ['name', 'state', 'city', 'identifier','checkbox1'];
  dataSource:any;
  dataSource1:any;
  dataSource2:any;
  elementArray:any= [];
  elementArray1:any=[];
  elementArray2:any=[];
  display!: boolean;
  exist=true;
  
  identi: any;
  prioritychargers: any = [];
  highwaychargers: any =[];
  requirement: any;
  deletepriority: any =[];
  deleteHighway: any =[];
  
  search = new FormGroup({
    searchbar: new FormControl('')
  })

  constructor(private _api:ApiService) { }

  ngOnInit(): void {
    this._getChargingSessionDetails();
    this._getPriorityChargerDetails();
   this._getHighwayChargerDetails();
    /*setInterval(() => {
      this._getChargingSessionDetails();
    }, 5000);*/
  }
  _getChargingSessionDetails(){
    this._api.getTypeRequest("evCharger/check/starHighway").subscribe((res:any)=>{
      //console.log(res)
       this.elementArray=[]; 
       for(var i=0; i<Object.keys(res).length;i++){
         
          this.elementArray[i] = res[i];
         
        } 
        // //console.log(this.elementArray)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource = new MatTableDataSource(ELEMENT_DATA)     
    });
  }

  _getPriorityChargerDetails(){
    this._api.getTypeRequest("evCharger/getHighwayOrPriorityChargers/priority").subscribe((res:any)=>{
      this.elementArray1=[];
       for(var i=0; i<Object.keys(res).length;i++){
         
          this.elementArray1[i] = res[i];
         
        } 
        // //console.log(this.elementArray1)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray1;
        this.dataSource1 = new MatTableDataSource(ELEMENT_DATA)   
    });
  }

  _getHighwayChargerDetails(){
    this._api.getTypeRequest("evCharger/getHighwayOrPriorityChargers/highway").subscribe((res:any)=>{
        // //console.log(res);
        this.elementArray2=[];
       for(var i=0; i<Object.keys(res).length;i++){
         
          this.elementArray2[i] = res[i];
         
        } 
        // //console.log(this.elementArray2)
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray2;
        this.dataSource2 = new MatTableDataSource(ELEMENT_DATA); 
        this.identi=this.dataSource2._data._value[0].identifier;    
    });
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
  update(){
    if(this.requirement == 'priority')
    {
      var arr = []
      //console.log(this.prioritychargers);
      for( let n in this.prioritychargers)
      {
        arr.push({"identifier":this.prioritychargers[n]})
      } 
      //console.log("qwert"+JSON.stringify(arr))
      this._api.postTypeRequest('evCharger/addHighwayOrPriorityCharger?charger_type=priority',JSON.stringify(arr)).subscribe((res)=>{
        //console.log(res)   
      });
    }
    else if(this.requirement == 'highway')
    {
      var arr = []
      //console.log(this.highwaychargers);
      for( let n in this.highwaychargers)
      {
        arr.push({"identifier":this.highwaychargers[n]})
      } 
      //console.log("qwerty"+arr)
      this._api.postTypeRequest('evCharger/addHighwayOrPriorityCharger?charger_type=highway',JSON.stringify(arr)).subscribe((res)=>{
        //console.log(res)   
      });
    }
    
  }






  addPriorityChargers(event:any, requirement:any){
    //console.log(event);
    this.prioritychargers.push(event);
    //console.log(this.prioritychargers);
    this.requirement = requirement
    //console.log(this.requirement);
  }


  addHighwayChargers(event:any, requirement:any){
    //console.log(event);
    this.highwaychargers.push(event);
    //console.log(this.highwaychargers);
    this.requirement = requirement
    //console.log(this.requirement);
  }


  deletechargers(){
    if(this.requirement == 'priority')
    {
      var arr = []
      //console.log(this.deletepriority);
      for( let n in this.deletepriority)
      {
        arr.push({"identifier":this.deletepriority[n]})
      } 
      //console.log(arr)
      this._api.postTypeRequest('evCharger/deleteHighwayOrPriorityCharger?charger_type=priority',JSON.stringify(arr)).subscribe((res)=>{
        //console.log(res)   
      });
    }
    else if(this.requirement == 'highway')
    {
      var arr = []
      //console.log(this.deleteHighway);
      for( let n in this.deleteHighway)
      {
        arr.push({"identifier":this.deleteHighway[n]})
      } 
      //console.log(arr)
      this._api.postTypeRequest('evCharger/deleteHighwayOrPriorityCharger?charger_type=highway',JSON.stringify(arr)).subscribe((res)=>{
        //console.log(res)   
      });
    }
    
  }

  deletePriorityChargers(event:any, requirement:any){
    //console.log(event);
    this.deletepriority.push(event);
    //console.log(this.deletepriority);
    this.requirement = requirement
    //console.log(this.requirement);
  }
  
  deleteHighwayChargers(event:any, requirement:any){
    //console.log(event);
    this.deleteHighway.push(event);
    //console.log(this.deleteHighway);
    this.requirement = requirement
    //console.log(this.requirement);
  }
  onTabChanged(event: MatTabChangeEvent) 
  {
    //console.log(event);


    
    if(event.index == 1)
    {
        this._getPriorityChargerDetails();//Or whatever name the method is called
       
        
    }
  
    else if(event.index == 2)
    {
        this._getHighwayChargerDetails(); //Or whatever name the method is called
    }
    else if(event.index == 0)
    {
      this._getChargingSessionDetails();
    }
  }

}
