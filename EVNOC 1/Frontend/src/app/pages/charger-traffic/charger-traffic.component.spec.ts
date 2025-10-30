import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargerTrafficComponent } from './charger-traffic.component';

describe('ChargerTrafficComponent', () => {
  let component: ChargerTrafficComponent;
  let fixture: ComponentFixture<ChargerTrafficComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChargerTrafficComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChargerTrafficComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
