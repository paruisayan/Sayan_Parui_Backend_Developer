import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from 'src/app/services/api.service';
import { MatTableDataSource } from '@angular/material/table';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { FormControl, FormGroup} from '@angular/forms';


export interface PeriodicElement {
  name: string,
  state: string,
  city: string,
  identifier: string,
  connectorid: number,
  model: string,
  faultcode: string,
  faultdescription: string,
  severity:string,
  faultstatus: string,
  timestamp: string,
  resolutiontime: string
}

@Component({
  selector: 'app-alarm-fault',
  templateUrl: './alarm-fault.component.html',
  styleUrls: ['./alarm-fault.component.css']
})
export class AlarmFaultComponent implements OnInit {
  dates = new FormControl(new Date());
  constructor(private _api:ApiService){}
  displayedColumns: string[] = ['Name', 'State', 'City', 'Identifier','Connector_ID','Model','Generic_Code','Generic_Description','Severity','Status','Timestamp','Resolution'];
  dataSource:any;
  elementArray:any = [];
  countArray:any=[0,0,0,0,0,0,0];

  dateRange = new FormGroup({
    start: new FormControl(),
  });
  data:any=[];
  Sel_Date:any;
  Sel_Month:any;
  Sel_Year:any;
  start:any;
  end:any;
  total   :any;
  medium  :any;
  critical:any;
  high    :any;
  low     :any;
  resolved:any;
  loader=false;
  open    :any;

  ngOnInit(): void {
    var fulldate=new Date();
    this.Sel_Date=fulldate.getDate();
    this.Sel_Month=fulldate.getMonth()+1;
    this.Sel_Year=fulldate.getFullYear();
    var date=this.Sel_Year+'-'+this.Sel_Month+'-'+this.Sel_Date;
    var i=0;
    this.totalCount(date,date);
    this._gettotalFaultDetails(date,date);
  }

  _gettotalFaultDetails(start:any,end:any){
    this.loader=false;
    this._api.getTypeRequest("evCharger/alarmlogs/total/"+start+"/"+end).subscribe((res:any)=>{
       this.loader=true;
       for(var i=0; i<Object.keys(res).length;i++){
        this.elementArray[i] = res[i];
        } 
        const ELEMENT_DATA: PeriodicElement[] = this.elementArray;
        this.dataSource = new MatTableDataSource(ELEMENT_DATA)     
    });
  }

  totalCount(start:any,end:any) {
    var i=0;
    this._api.getTypeRequest('evCharger/alarmlogs/totalcount/'+start+"/"+end).subscribe((res:any)=>{
      Object.entries(res).forEach(key=>{
        this.countArray[i]=key[1];
        i++;
      })
    })
  }
  


  getStartDate(type: string, event: MatDatepickerInputEvent<Date>){
    this.Sel_Date=event.value?.getDate();
    this.Sel_Month=event.value?.getMonth();
    this.Sel_Year=event.value?.getFullYear();
    this.start=this.Sel_Year+'-'+(this.Sel_Month+1)+'-'+this.Sel_Date;
    this.end=this.start;
    this._gettotalFaultDetails(this.start,this.end);
    this.totalCount(this.start,this.end);
 }

  applyFilter(event:any) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue;
  }
  filterEvent(buttonType:any){
    this.dataSource.filter=buttonType;
  }

}
