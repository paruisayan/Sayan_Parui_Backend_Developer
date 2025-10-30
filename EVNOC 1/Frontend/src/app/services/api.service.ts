import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { map } from 'rxjs/operators'; 
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private api_server = environment.apiUrl;

  constructor(private httpClient:HttpClient) { }
  selectedtab="allMapView";

  cidsGetRequest(url: string){
    return this.httpClient.get(this.api_server+url).pipe(map(res=>{
      return res;
    }));
  }
  getTypeRequest(url: string) { 
    return this.httpClient.get(this.api_server+url).pipe(map(res => { 
      return res; 
    })); 
  } 
  getTypeRequest1(url: string) { 
    return this.httpClient.get(url).pipe(map(res => { 
      return res; 
    })); 
  } 
 
  postTypeRequest(url: string, payload: any) { 
    return this.httpClient.post(this.api_server+url, payload).pipe(map(res => { 
      return res; 
    })); 
  }
  getCities(state: string){
    //console.log(state)
    // return this.http.get(`${this.apiBaseUrl}evCharger/status/India?chargers=all&state=${state}`)
    return this.httpClient.get(`${this.api_server}evCharger/getCities/${state}`)
}
getPostalCode( city: string){
    //console.log(city)
    //console.log("In postal code method")
    // //console.log(`${this.apiBaseUrl}evCharger/status/India?chargers=all&state=${state}&city=${city}`)
    return this.httpClient.get(`${this.api_server}evCharger/getPostalcodes/${city}`)
}
getLatLon(state:string){
    return this.httpClient.get(`${this.api_server}evCharger/getLatLon/${state}`);
  }
  getDepos(city:string){
    return this.httpClient.get(`${this.api_server}evCharger/busCharger/getDepos/${city}`);
  }
}
