import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScenarioOutputComponent } from './scenario-output.component';

describe('ScenarioOutputComponent', () => {
  let component: ScenarioOutputComponent;
  let fixture: ComponentFixture<ScenarioOutputComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ScenarioOutputComponent]
    });
    fixture = TestBed.createComponent(ScenarioOutputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
