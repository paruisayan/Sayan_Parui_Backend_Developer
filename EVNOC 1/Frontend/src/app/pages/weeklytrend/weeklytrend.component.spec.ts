import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WeeklytrendComponent } from './weeklytrend.component';

describe('WeeklytrendComponent', () => {
  let component: WeeklytrendComponent;
  let fixture: ComponentFixture<WeeklytrendComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeeklytrendComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WeeklytrendComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
