import { Component, OnInit } from '@angular/core';
import { EChartsOption } from 'echarts';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-weeklytrend',
  templateUrl: './weeklytrend.component.html',
  styleUrls: ['./weeklytrend.component.css']
})
export class WeeklytrendComponent implements OnInit {
  day:any;
  day1:any;date0:any;
  day2:any;date1:any;
  day3:any;date2:any;
  day4:any;date3:any;
  day5:any;date4:any;
  day6:any;date5:any;
  day7:any;date6:any;
  day8:any;date7:any;
  day9:any;date8:any;
  day0:any;date9:any;  
  loader=false;
  selected:any;
  buttons=['sunday','monday','tuesday','wednesday','friday','saturday','thursday']
  constructor(private api:ApiService) { }
  eChartOption!:EChartsOption;
  ngOnInit(): void {
    var now=new Date();
    this.selected=now.getDay()-1
    if(this.selected==0){
      this.days('MO')
    }
    else if(this.selected==1){
      this.days('TU')
    }
    else if(this.selected==2){
      this.days('WE')
    }
    else if(this.selected==3){
      this.days('TH')
    }
    else if(this.selected==4){
      this.days('FR')
    }
    else if(this.selected==5){
      this.days('SA')
    }
    else if(this.selected==6){
      this.days('SU')
    }
  }
  days(whichDay:any){
    this.loader=false
    if(whichDay=="MO"){
      this.day='Mondays'
    }
    else if(whichDay=="TU"){
      this.day='Tuesdays'
    }
    else if(whichDay=="WE"){
      this.day='Wednesdays'
    }
    else if(whichDay=="TH"){
      this.day='Thursdays'
    }
    else if(whichDay=="FR"){
      this.day='Fridays'
    }
    else if(whichDay=="SA"){
      this.day='Saturdays'
    }
    else if(whichDay=="SU"){
      this.day="Sundays"
    }
    this.day0,this.day1,this.day2,this.day3,this.day4,this.day5,this.day6,this.day7,this.day8,this.day9=[]
    this.api.getTypeRequest('evCharger/Analytics/chargingSessionTrendWeekly/'+whichDay).subscribe((res:any)=>{
      Object.entries(res).forEach((key,value)=>{
        if(value==0){
          this.day0=key.slice(1)
          this.date0=key[0]
        }
        else if(value==1){
          this.day1=key.slice(1)
          this.date1=key[0]
        }
        else if(value==2){
          this.day2=key.slice(1)
          this.date2=key[0]
        }
        else if(value==3){
          this.day3=key.slice(1)
          this.date3=key[0]
        }
        else if(value==4){
          this.day4=key.slice(1)
          this.date4=key[0]
        }
        else if(value==5){
          this.day5=key.slice(1)
          this.date5=key[0]
        }
        else if(value==6){
          this.day6=key.slice(1)
          this.date6=key[0]
        }
        else if(value==7){
          this.day7=key.slice(1)
          this.date7=key[0]
        }
        else if(value==8){
          this.day8=key.slice(1)
          this.date8=key[0]
        }
        else if(value==9){
          this.day9=key.slice(1)
          this.date9=key[0]
        }
      })
      // //console.log()
      this.loader=true;
    this.setOption()
    })
  }
  setOption(){
    // //console.log(this.day5)
  this.eChartOption={
      title: {
        text: this.day
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: [this.date0,this.date1,this.date2,this.date3,this.date4,this.date5,this.date6,this.date7,this.date8,this.date9]
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      toolbox: {
        feature: {
          saveAsImage: {}
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: this.date0,
          type: 'line',
           
          data: this.day0[0]
        },
        {
          name: this.date1,
          type: 'line',
           
          data: this.day1[0]
        },
        {
          name: this.date2,
          type: 'line',
           
          data: this.day2[0]
        },
        {
          name: this.date3,
          type: 'line',
           
          data: this.day3[0]
        },
        {
          name: this.date4,
          type: 'line',
           
          data: this.day4[0]
        },
        {
          name: this.date5,
          type: 'line',
           
          data: this.day5[0]
        },
        {
          name: this.date6,
          type: 'line',
           
          data: this.day6[0]
        },
        {
          name: this.date7,
          type: 'line',
           
          data: this.day7[0]
        },
        {
          name: this.date8,
          type: 'line',
           
          data: this.day8[0]
        },
        {
          name: this.date9,
          type: 'line',
           
          data: this.day9[0]
        },
      ]
    }
  }
}
