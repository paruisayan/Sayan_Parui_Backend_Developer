import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargingTrendComponent } from './charging-trend.component';

describe('ChargingTrendComponent', () => {
  let component: ChargingTrendComponent;
  let fixture: ComponentFixture<ChargingTrendComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChargingTrendComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChargingTrendComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
