import { Component, OnInit, ViewChild,AfterViewInit } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup } from '@angular/forms';
import {MatSort, Sort} from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ApiService } from 'src/app/services/api.service';
import { MatDialog } from '@angular/material/dialog';
interface PowerFailure{
  id:String;
  manufacturer:String;
  model:String;  
  name:String;
  count:Number;
}

interface logs{
  active:string;
  inactive:string;
  duration:string;
}

@Component({
  selector: 'app-power-failure',
  templateUrl: './power-failure.component.html',
  styleUrls: ['./power-failure.component.css']
})
export class PowerFailureComponent implements OnInit,AfterViewInit {
  
  dateRange = new UntypedFormGroup({
    start: new UntypedFormControl(),
    end: new UntypedFormControl()
  });
  data:any=[];
  Sel_Date:any;
  Sel_Month:any;
  Sel_Year:any;
  start:any;
  end:any;
  show=false;
  logsArray:any=[];
  elementArray:any=[];
  loader=false;
  dataSource!: MatTableDataSource<PowerFailure>;
  dataSource1!: MatTableDataSource<logs>;
  displayedColumns: string[] = ['identifier','chargepointvendor','chargepointmodel','name','count','LOGS'];
  displayedColumns1:string[] = ['inactive','active','duration']
  constructor(private _api:ApiService,public dialog:MatDialog) { }
  @ViewChild(MatSort) sort!: MatSort;
  ngOnInit(): void {
    this.getPowerFailureData()
  }

  getPowerFailureData(){
    this.loader=true;
    this._api.getTypeRequest('evCharger/Analytics/readCSVPowerFailure').subscribe((res:any)=>{
    for(var i=0; i<Object.keys(res).length;i++){
        this.elementArray[i] = res[i];
    } 
    //console.log(this.elementArray)
    const ELEMENT_DATA: PowerFailure[] = this.elementArray;
    this.dataSource = new MatTableDataSource(ELEMENT_DATA) 
 })
  }
  ngAfterViewInit() {
    this.dataSource.sort = this.sort;
  }
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
  getlogs(identifier:any){
    this.loader=false;
    this.logsArray=[]
    this._api.getTypeRequest('evCharger/Analytics/readCSVPowerFailure/viewDetailsPowerFailure/'+identifier.id).subscribe((res:any)=>{
      this.show=true;
      this.loader=true;
      for(var i=0; i<Object.keys(res).length;i++){
        this.logsArray[i] = res[i];
    }
      const log_DATA:logs[]=this.logsArray;
      this.dataSource1=new MatTableDataSource(log_DATA);
    })
  }

}

