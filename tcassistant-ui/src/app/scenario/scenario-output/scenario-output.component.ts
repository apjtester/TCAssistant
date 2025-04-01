import { Component } from '@angular/core';
import { Subscription } from 'rxjs/internal/Subscription';
import { ScenarioService } from 'src/app/core/scenario.service';

@Component({
  selector: 'app-scenario-output',
  templateUrl: './scenario-output.component.html',
  styleUrls: ['./scenario-output.component.css']
})
export class ScenarioOutputComponent {
// scenarios: Scenario[] = [];
  private subscription!: Subscription;
isLoading: boolean = false;
text: string = "";
constructor(private scenarioService: ScenarioService) {}
ngOnInit(): void {
  // Subscribe to the text observable.
  this.subscription = this.scenarioService.text$.subscribe(updatedText => {
    this.text = updatedText;
    console.log(this.text)
  }
   );
}

ngOnDestroy(): void {
  // Unsubscribe to prevent memory leaks.
  if (this.subscription) {
    this.subscription.unsubscribe();
  }
}
displayScenarios(scenarios: any[]): void {
  // TODO: Render a list of scenario cards or items in the view.
}

onRegenerate(): void {
  // TODO: Invoke ScenarioService to regenerate test scenarios.
}

onGenerateMore(): void {
  // TODO: Request additional test scenarios from ScenarioService.
}

setLoadingState(isLoading: boolean): void {
  // TODO: Manage UI loading state (e.g., show/hide a spinner).
  this.isLoading = isLoading;
}

viewScenarioDetails(scenarioId: string): void {
  // TODO: Navigate to the ScenarioDetailsComponent to display detailed info and sources.
}
}
