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
  isGenerating: boolean = false;

  constructor(private scenarioService: ScenarioService) {}

  async onSubmit(): Promise<void> {
    if (this.validateInput()) {
      this.updateModel();
      this.isGenerating = true;
      let input=this.inputText;
      let context=this.context;
      await this.scenarioService.requestScenarioGeneration('initial',input, context);
      
      this.isGenerating = false;
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
    this.inputText = '';
  }

  updateModel(): void {
    // TODO: Update the component's model with the current form values.
  }
}
