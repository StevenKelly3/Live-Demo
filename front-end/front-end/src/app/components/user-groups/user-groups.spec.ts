import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserGroups } from './user-groups';

describe('UserGroups', () => {
  let component: UserGroups;
  let fixture: ComponentFixture<UserGroups>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserGroups]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserGroups);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
