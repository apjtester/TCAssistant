import { Component } from '@angular/core';
import { Subscription } from 'rxjs/internal/Subscription';
import { MarkdownService } from 'ngx-markdown';
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
  htmlText: string = "";
constructor(private scenarioService: ScenarioService,private markdownService: MarkdownService) {}
ngOnInit(): void {
  // Subscribe to the text observable.
  this.subscription = this.scenarioService.text$.subscribe(updatedText => {  
    let parsedText=this.markdownService.parse(updatedText);
    if(typeof parsedText=="string")
      this.htmlText = parsedText
    else
      parsedText.then(value=>this.htmlText=value);
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
