import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BusChargerComponent } from './bus-charger.component';

describe('BusChargerComponent', () => {
  let component: BusChargerComponent;
  let fixture: ComponentFixture<BusChargerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BusChargerComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BusChargerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
