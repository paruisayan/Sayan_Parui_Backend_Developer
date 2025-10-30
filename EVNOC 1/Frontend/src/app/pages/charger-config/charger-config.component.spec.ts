import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargerConfigComponent } from './charger-config.component';

describe('ChargerConfigComponent', () => {
  let component: ChargerConfigComponent;
  let fixture: ComponentFixture<ChargerConfigComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChargerConfigComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChargerConfigComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
