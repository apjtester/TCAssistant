import { Component } from '@angular/core';
import { ScenarioService } from 'src/app/core/scenario.service';

@Component({
  selector: 'app-scenario-input',
  templateUrl: './scenario-input.component.html',
  styleUrls: ['./scenario-input.component.css']
})
export class ScenarioInputComponent {
  ac: string = '';
  context: string = '';
  inputText: string="";

  constructor(private scenarioService: ScenarioService) {}

  onSubmit(): void {
    if (this.validateInput()) {
      this.updateModel();
      this.scenarioService.requestScenarioGeneration('initial',this.inputText, this.context);
      console.log("Scenario generation requested.");
      this.resetForm();
    } else {
      //Inform the user that the input is invalid.
  }
}

  validateInput(): boolean {
    // TODO: Validate that the Acceptance Criteria is provided and that the optional context is valid.
    return true;
  }

  resetForm(): void {
    // TODO: Clear form fields and reset the model.
    this.ac = '';
    this.context = '';
  }

  updateModel(): void {
    // TODO: Update the component's model with the current form values.
  }
}
