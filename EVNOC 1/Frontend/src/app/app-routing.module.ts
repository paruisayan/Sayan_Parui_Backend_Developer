import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AlarmFaultComponent } from './pages/alarm-fault/alarm-fault.component';
import { NetworkIssueComponent } from './pages/network-issue/network-issue.component';
import { PowerFailureComponent } from './pages/power-failure/power-failure.component';
import { ZeroTransactionComponent } from './pages/zero-transaction/zero-transaction.component';
import { ChargingTrendComponent } from './pages/charging-trend/charging-trend.component';
import { WeeklytrendComponent } from './pages/weeklytrend/weeklytrend.component';
import { ChargerTrafficComponent } from './pages/charger-traffic/charger-traffic.component';
import { ChargerReportComponent } from './pages/charger-report/charger-report.component';
import { ChargerConfigComponent } from './pages/charger-config/charger-config.component';
import { BusChargerComponent } from './pages/bus-charger/bus-charger.component';
import { ErrorpageComponent } from './static/errorpage/errorpage.component';


const routes: Routes = [
  { path:'', redirectTo:'login', pathMatch:'full' },
  { path:'login', component:LoginComponent },
  { path:'dashboard', component:DashboardComponent },
  { path:'alarmFault', component:AlarmFaultComponent },
  { path:'network_issue', component:NetworkIssueComponent },
  { path:'power_failure', component:PowerFailureComponent },
  { path:'zero_transaction',component:ZeroTransactionComponent },
  { path:'charging-trend',component:ChargingTrendComponent },
  { path:'weeklyTrend',component:WeeklytrendComponent },
  { path:'chargertraffic', component:ChargerTrafficComponent },
  { path:'report', component:ChargerReportComponent },
  { path:'configuration', component:ChargerConfigComponent },
  { path:'busCharger', component:BusChargerComponent},
  { path:'**', pathMatch:'full', component:ErrorpageComponent, }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
