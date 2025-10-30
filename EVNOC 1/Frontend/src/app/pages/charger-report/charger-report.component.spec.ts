import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargerReportComponent } from './charger-report.component';

describe('ChargerReportComponent', () => {
  let component: ChargerReportComponent;
  let fixture: ComponentFixture<ChargerReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChargerReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChargerReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
