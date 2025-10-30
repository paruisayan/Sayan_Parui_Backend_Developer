import { Component, OnInit } from '@angular/core';
import { Router,NavigationStart } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'EV NOC';
  showHead: boolean = false;

  constructor(private router:Router){
    router.events.forEach((event)=>{
      if (event instanceof NavigationStart){
        if (event['url']=='/evnoc/login'){
          console.log(event['url'])
          this.showHead=false;
        }
        else if(event['url']=='/login' || event['url']=='/'){
          this.showHead=false;
        }
        else{
          console.log(event['url'])
          this.showHead=true;
        }
      }
    })
  }
  
}


