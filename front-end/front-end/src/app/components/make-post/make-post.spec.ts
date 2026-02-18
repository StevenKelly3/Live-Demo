import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MakePost } from './make-post';

describe('MakePost', () => {
  let component: MakePost;
  let fixture: ComponentFixture<MakePost>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MakePost]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MakePost);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
