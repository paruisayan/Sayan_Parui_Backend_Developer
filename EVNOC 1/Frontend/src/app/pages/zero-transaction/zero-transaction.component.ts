import { Component, OnInit, ViewChild,AfterViewInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ApiService } from 'src/app/services/api.service';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { DialogComponent } from '../dialog/dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';


interface ZeroTransaction{
  identifier:String;
  count:Number;
  name:String;
  chargepointvendor:String;
  chargepointmodel:String;
}

@Component({
  selector: 'app-zero-transaction',
  templateUrl: './zero-transaction.component.html',
  styleUrls: ['./zero-transaction.component.css']
})

export class ZeroTransactionComponent implements OnInit,AfterViewInit {
  dates = new FormControl(new Date());
  dateRange:FormGroup = new FormGroup({
    start: new FormControl(''),
    end: new FormControl('')
  });
  data:any=[];
  Sel_Date:any;
  Sel_Month:any;
  Sel_Year:any;
  start:any;
  end:any;
  date:any;
  elementArray:any=[];
  dataSource!: MatTableDataSource<ZeroTransaction>;
  displayedColumns: string[] = ['identifier','name','chargepointvendor','chargepointmodel','count'];
  constructor(private _api:ApiService,public dialog:MatDialog) {
    var fulldate=new Date();
    
    this.Sel_Date=fulldate.getDate();
    this.Sel_Month=fulldate.getMonth()+1;
    this.Sel_Year=fulldate.getFullYear();
    this.date=this.Sel_Year+'-'+this.Sel_Month+'-'+this.Sel_Date;
    
    this._api.getTypeRequest('evCharger/getZeroTransactionAnalytics/'+this.date+'/'+this.date).subscribe((res:any)=>{
      for(var i=0; i<Object.keys(res).length;i++){
          this.elementArray[i] = res[i];
      } 
      //console.log(this.elementArray);
      //console.log(res);
      const ELEMENT_DATA: ZeroTransaction[] = this.elementArray;
      this.dataSource = new MatTableDataSource(ELEMENT_DATA) 
      // this.dataSource = new MatTableDataSource(this.elementArray);
      this.dataSource.paginator = this.paginator;
   })
  }

  @ViewChild('paginator') paginator!: MatPaginator;

  ngAfterViewInit() {
    this.dataSource = new MatTableDataSource(this.elementArray);
    this.dataSource.paginator = this.paginator;
  }
  ngOnInit(): void {
    
  }
  getStartDate(type: string, event: MatDatepickerInputEvent<Date>){
    this.Sel_Date=event.value?.getDate();
    this.Sel_Month=event.value?.getMonth();
    this.Sel_Year=event.value?.getFullYear();
 }
  getEndDate(type: string, event: any){
    //console.log(event.value);
    // var endMonth=event.value.getMonth();
    this.start=this.Sel_Year+'-'+(this.Sel_Month+1)+'-'+this.Sel_Date;
    this.end=event.value?.getFullYear()+'-'+(event.value.getMonth()+1)+'-'+event.value?.getDate();
  }
  
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
  viewDetails(){
    this._api.getTypeRequest('evCharger/getZeroTransactionAnalytics/'+this.start+'/'+this.end).subscribe((res:any)=>{
      for(var i=0; i<Object.keys(res).length;i++){
          this.elementArray[i] = res[i];
      } 
      //console.log(this.elementArray)
      const ELEMENT_DATA: ZeroTransaction[] = this.elementArray;
      this.dataSource = new MatTableDataSource(ELEMENT_DATA) 
   })
  }

}
