import { HttpHeaderResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
    date:Date=new Date();
    time=new Date();
    intervalId:any;
    isVisible:boolean=true;
    
    constructor(private router:Router) { }

    ngOnInit(): void {

    setInterval(()=>{
      this.time=new Date();
      },1000);
    }
    ngOnDestroy(){
      clearInterval(this.intervalId);
    }
    OnLoggedoff()
  {
    localStorage.removeItem('username');
     this.router.navigate(["/login"]);
  }
  }