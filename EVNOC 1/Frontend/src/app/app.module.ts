import { NgModule,CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { LoginComponent } from './pages/login/login.component';
import { HeaderComponent } from './static/header/header.component';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { MatSnackBarModule} from '@angular/material/snack-bar';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import {MatMenuModule} from '@angular/material/menu';
import { DialogComponent } from './pages/dialog/dialog.component';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatButtonModule} from '@angular/material/button';
import {MatDialogModule} from '@angular/material/dialog';
import { MatToolbarModule } from '@angular/material/toolbar';
import {MatIconModule} from '@angular/material/icon';
import {MatFormFieldModule} from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AgmCoreModule } from '@agm/core';
import { AlarmFaultComponent } from './pages/alarm-fault/alarm-fault.component';
import { MatTableExporterModule } from 'mat-table-exporter';
import {MatTableModule} from '@angular/material/table';
import {MatDatepickerModule} from '@angular/material/datepicker';
import { WeeklytrendComponent } from './pages/weeklytrend/weeklytrend.component';
import { ZeroTransactionComponent } from './pages/zero-transaction/zero-transaction.component';
import { ChargerTrafficComponent } from './pages/charger-traffic/charger-traffic.component';
import { ChargerReportComponent } from './pages/charger-report/charger-report.component';
import { PowerFailureComponent } from './pages/power-failure/power-failure.component';
import { NetworkIssueComponent } from './pages/network-issue/network-issue.component';
import { ChargingTrendComponent } from './pages/charging-trend/charging-trend.component';
import { MatNativeDateModule } from '@angular/material/core';
import {MatTabsModule} from '@angular/material/tabs';
import { ChargerConfigComponent } from './pages/charger-config/charger-config.component';
import { BusChargerComponent } from './pages/bus-charger/bus-charger.component';
import {MatPaginatorModule} from '@angular/material/paginator';
import { NgxEchartsModule } from 'ngx-echarts';
import { ErrorpageComponent } from './static/errorpage/errorpage.component';
import {MatCheckboxModule} from '@angular/material/checkbox';
import { environment } from 'src/environments/environment';


@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    HeaderComponent,
    DashboardComponent,
    DialogComponent,
    AlarmFaultComponent,
    WeeklytrendComponent,
    ZeroTransactionComponent,
    ChargerTrafficComponent,
    ChargerReportComponent,
    PowerFailureComponent,
    NetworkIssueComponent,
    ChargingTrendComponent,
    ChargerConfigComponent,
    BusChargerComponent,
    ErrorpageComponent,

  ],
  imports: [
    BrowserModule,        CommonModule,               MatCheckboxModule,
    AppRoutingModule,     BrowserAnimationsModule,
    HttpClientModule,     ReactiveFormsModule,        FormsModule,
    NgxEchartsModule.forRoot({echarts:()=>import('echarts')}),
    MatSnackBarModule,    MatTableExporterModule,
    MatMenuModule,        MatFormFieldModule,         MatInputModule,
    MatAutocompleteModule,MatIconModule,
    MatButtonModule,      MatDialogModule,            MatToolbarModule,
    MatTableModule,       MatDatepickerModule,        MatNativeDateModule,
    AgmCoreModule.forRoot({apiKey:environment.mapkey}),
    MatTabsModule,        MatPaginatorModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
  schemas:[CUSTOM_ELEMENTS_SCHEMA]
})

export class AppModule { }