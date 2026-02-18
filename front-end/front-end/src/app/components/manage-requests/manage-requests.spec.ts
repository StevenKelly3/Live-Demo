import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageRequests } from './manage-requests';

describe('ManageRequests', () => {
  let component: ManageRequests;
  let fixture: ComponentFixture<ManageRequests>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageRequests]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManageRequests);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
