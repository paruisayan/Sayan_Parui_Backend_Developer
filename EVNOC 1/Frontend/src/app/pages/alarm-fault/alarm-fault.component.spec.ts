import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlarmFaultComponent } from './alarm-fault.component';

describe('AlarmFaultComponent', () => {
  let component: AlarmFaultComponent;
  let fixture: ComponentFixture<AlarmFaultComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AlarmFaultComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlarmFaultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
