import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PowerFailureComponent } from './power-failure.component';

describe('PowerFailureComponent', () => {
  let component: PowerFailureComponent;
  let fixture: ComponentFixture<PowerFailureComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PowerFailureComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PowerFailureComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
