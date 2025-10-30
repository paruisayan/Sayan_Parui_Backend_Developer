import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { ApiService } from 'src/app/services/api.service';
import {MatSort,Sort} from '@angular/material/sort';

@Component({
  selector: 'app-charger-report',
  templateUrl: './charger-report.component.html',
  styleUrls: ['./charger-report.component.css']
})
export class ChargerReportComponent implements OnInit{
  dataSource:any;
  displayedColumns:any = [];

  @ViewChild(MatSort) sort!: MatSort;

  constructor(private _api:ApiService){}

  ngOnInit(){
    this._api.getTypeRequest("evCharger/Analytics/analysisOnChargerHits").subscribe((res:any)=>{
      this.dataSource=res;
      Object.keys(res[0]).forEach(item=>{
        this.displayedColumns.push(item)
      })
    })
  }
}
