import { Component,OnInit, Pipe } from '@angular/core';
import { ApiService } from 'src/app/services/api.service';
import { FormControl, FormGroup } from '@angular/forms';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-charger-traffic',
  templateUrl: './charger-traffic.component.html',
  styleUrls: ['./charger-traffic.component.css']
})

export class ChargerTrafficComponent implements OnInit{
  constructor(private _api: ApiService){}
  length:any;
  index:any=[];
  columns:any=[];
  identifier:any=[];
  name:any=[];
  count:any=[];
  vendor:any=[];
  model:any=[];
  address:any=[];
  city:any=[];
  state:any=[];
  type:any=[];
  today:any;
  data!:boolean;
  
  ngOnInit(): void {
    this.today=new Date();
    this.today.setDate(this.today.getDate()-1)
    var datePipe=new DatePipe("en-US");
    var val=datePipe.transform(this.today,'YYYY-MM-dd')
    this.fetchDetails(val)
  }

  date=new Date()
  selDate=this.date.setDate(this.date.getDate()-1)
  dates = new FormControl(new Date(this.selDate));
  dateRange = new FormGroup({
    start: new FormControl(),
  });

  setDate(event:any){
    var val=event.target.value;
    var datePipe=new DatePipe("en-US");
    this.fetchDetails(datePipe.transform(val,'YYYY-MM-dd'))
  }

  fetchDetails(date:any){
    this.columns=[];
    this.index=[];
  
    this._api.getTypeRequest("evCharger/Analytics/readCSVChargerHits/"+date).subscribe((res:any)=>{
      Object.keys(res[0]).map(key=>{
        return this.columns.push(key);
      })
      this.length=Object.keys(res).length;
      if(this.length>0)
        this.data=true;

      this.identifier.splice(0,this.identifier.length)
      this.name.splice(0,this.name.length)
      this.count.splice(0,this.count.length)
      this.city.splice(0,this.city.length)
      this.state.splice(0,this.state.length)
      this.type.splice(0,this.type.length)
      this.address.splice(0,this.address.length)
      this.model.splice(0,this.model.length)
      this.vendor.splice(0,this.vendor.length)

      for(let i=0;i<Object.keys(res).length;i++){
        this.identifier.push(res[i].identifier)
        this.name.push(res[i].name)
        this.count.push(res[i].count)
        this.vendor.push(res[i].chargepointvendor)
        this.model.push(res[i].chargepointmodel)
        this.address.push(res[i].address)
        this.city.push(res[i].city)
        this.state.push(res[i].state)
        this.type.push(res[i].type)
        this.index.push(i)
      }
    },err=>{
      this.data=false;
    })
  } 
}
