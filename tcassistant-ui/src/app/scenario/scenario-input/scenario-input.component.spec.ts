import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScenarioInputComponent } from './scenario-input.component';

describe('ScenarioInputComponent', () => {
  let component: ScenarioInputComponent;
  let fixture: ComponentFixture<ScenarioInputComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ScenarioInputComponent]
    });
    fixture = TestBed.createComponent(ScenarioInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
