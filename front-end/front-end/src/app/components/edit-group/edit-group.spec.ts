import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditGroup } from './edit-group';

describe('EditGroup', () => {
  let component: EditGroup;
  let fixture: ComponentFixture<EditGroup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditGroup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditGroup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
