import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ZeroTransactionComponent } from './zero-transaction.component';

describe('ZeroTransactionComponent', () => {
  let component: ZeroTransactionComponent;
  let fixture: ComponentFixture<ZeroTransactionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ZeroTransactionComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ZeroTransactionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
