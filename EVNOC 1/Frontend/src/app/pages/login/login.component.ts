import { Component, OnInit } from '@angular/core'; 
import { FormBuilder, FormGroup, Validators } from '@angular/forms'; 
import { MatSnackBar,MatSnackBarHorizontalPosition,MatSnackBarVerticalPosition } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { ApiService } from 'src/app/services/api.service';
 
@Component({ 
  selector: 'app-login', 
  templateUrl: './login.component.html', 
  styleUrls: ['./login.component.css'] 
}) 
export class LoginComponent implements OnInit { 
  form!: FormGroup;
  iLogin:ILogin=new ILogin();
  horizontalPosition: MatSnackBarHorizontalPosition = 'right';
  verticalPosition: MatSnackBarVerticalPosition = 'bottom';

  constructor(public fb: FormBuilder,private _api:ApiService,private router:Router,
    private snackBar:MatSnackBar
    ) { }

  ngOnInit(): void {
    this.form = this.fb.group({ 
      username: ['', Validators.required], 
      password:['', Validators.required] 
    });

  }

  onLogin(){ 
    let b = this.form.value; 
    if (b.username == "admin" && b.password == "admin")
    {
      this.router.navigate(['/dashboard']);
    }
    else{
      this.snackBar.open("Wrong Username and Password","X",{
        horizontalPosition:this.horizontalPosition,
        verticalPosition:this.verticalPosition
      });
    }
  }
}
  export class ILogin
  {
    Username:string="";
    Password:string="";
  } 