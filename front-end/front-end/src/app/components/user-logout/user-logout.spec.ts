import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserLogout } from './user-logout';

describe('UserLogout', () => {
  let component: UserLogout;
  let fixture: ComponentFixture<UserLogout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserLogout]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserLogout);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
