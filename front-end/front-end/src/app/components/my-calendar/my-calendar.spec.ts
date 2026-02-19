import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyCalendar } from './my-calendar';

describe('MyCalendar', () => {
  let component: MyCalendar;
  let fixture: ComponentFixture<MyCalendar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyCalendar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyCalendar);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
