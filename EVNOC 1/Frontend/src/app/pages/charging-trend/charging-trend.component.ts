import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { EChartsOption } from 'echarts/types/dist/echarts';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-charging-trend',
  templateUrl: './charging-trend.component.html',
  styleUrls: ['./charging-trend.component.css']
})
export class ChargingTrendComponent implements OnInit,AfterViewInit {
  dates = new FormControl(new Date());
  today=new Date();
  count:number[]=[];
  options:any;
  eChartOption!:EChartsOption;
  dateRange = new FormGroup({
    start: new FormControl(),
  });
  data:any=[];
  Sel_Date:any;
  Sel_Month:any;
  Sel_Year:any;
  start:any;
  end:any;
  loader=false;
  constructor(private api:ApiService) { }
  ngAfterViewInit(): void {
  }
  getStartDate(type: string, event: MatDatepickerInputEvent<Date>){
    this.Sel_Date=event.value?.getDate();
    this.Sel_Month=event.value?.getMonth();
    this.Sel_Year=event.value?.getFullYear();
    this.start=this.Sel_Year+'-'+(this.Sel_Month+1)+'-'+this.Sel_Date;
 } 
  ngOnInit(): void {
    var fulldate=new Date();
  
    this.Sel_Date=fulldate.getDate();
    this.Sel_Month=fulldate.getMonth()+1;
    this.Sel_Year=fulldate.getFullYear();
    var date=this.Sel_Year+'-'+this.Sel_Month+'-'+this.Sel_Date;
    this.api.getTypeRequest('evCharger/Analytics/chargingSessionTrendDaily/'+date).subscribe((res:any)=>{
      for(var i=0;i<Object.entries(res).length;i++){
          this.count.push(res[i]['count'])
      }
      this.setOptions();
      this.loader=true
    })
  }
  trendsCount(){
    this.count=[]
    this.loader=false;
    this.api.getTypeRequest('evCharger/Analytics/chargingSessionTrendDaily/'+this.start).subscribe((res:any)=>{
      for(var i=0;i<Object.entries(res).length;i++){
          this.count.push(res[i]['count'])
      }
      this.setOptions();
      this.loader=true;
    })
  }
setOptions(){
  this.eChartOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    legend:{
      data:['Maximum','Minimum']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        name:'Hour',
        data: ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23'],
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name:'Count'
      }
    ],
    series: [
      {
        name: 'Count',
        type: 'bar',
        barWidth: '60%',
        data: this.count
      },
    ]
  };
}
}
