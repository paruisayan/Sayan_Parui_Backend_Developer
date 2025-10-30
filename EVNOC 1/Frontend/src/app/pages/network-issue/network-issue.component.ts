import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { animate,state,style,transition,trigger } from '@angular/animations';

import { MatTableDataSource } from '@angular/material/table';
import { ApiService } from 'src/app/services/api.service';
import { MatDialog } from '@angular/material/dialog';

interface NetworkIssue{
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
  selector: 'app-network-issue',
  templateUrl: './network-issue.component.html',
  styleUrls: ['./network-issue.component.css']
})
export class NetworkIssueComponent implements OnInit {
  dates = new FormControl(new Date());
  createAccountForm!: FormGroup;
  dateRange = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });
  data:any=[];
  Sel_Date:any;
  Sel_Month:any;
  Sel_Year:any;
  start:any;
  end:any;
  elementArray:any=[];
  dataSource!: MatTableDataSource<NetworkIssue>;
  dataSource1!:MatTableDataSource<logs>;
  displayedColumns: string[] = ['identifier','chargepointvendor','chargepointmodel','name','count','LOGS'];
  displayedColumns1:string[] = ['inactive','active','duration']
  state!: string;
  show:boolean=false;
  loader=false;
  logs:any;
  logsArray:any=[];
  constructor(private _api:ApiService,public dialog:MatDialog) { }

  ngOnInit(): void {
    this.getNetworkData()
  }

  getNetworkData(){
    this.loader=true;
    this._api.getTypeRequest('evCharger/Analytics/readCSVNetworkIssues').subscribe((res:any)=>{
      for(var i=0; i<Object.keys(res).length;i++){
          this.elementArray[i] = res[i];
      }
      //console.log(this.elementArray)
      const ELEMENT_DATA: NetworkIssue[] = this.elementArray;
      this.dataSource = new MatTableDataSource(ELEMENT_DATA) 
   })
  }
  
  
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
  getlogs(identifier:any){
    this.loader=false;
    this.logsArray=[]
    this._api.getTypeRequest('evCharger/Analytics/readCSVNetworkIssues/viewDetailsNetworkIssues/'+identifier.id).subscribe((res:any)=>{
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
