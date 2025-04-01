import { Component } from '@angular/core';
import { StorageService } from 'src/app/core/storage.service';

@Component({
  selector: 'app-saved-scenarios',
  templateUrl: './saved-scenarios.component.html',
  styleUrls: ['./saved-scenarios.component.css']
})
export class SavedScenariosComponent {
  // savedScenarios: Scenario[] = [];

  constructor(private storageService: StorageService) {}

  ngOnInit(): void {
    this.getSavedScenarios();
  }

  getSavedScenarios(): void {
    // TODO: Fetch saved scenarios from StorageService and update the view.
  }

  onSelectScenario(scenarioId: string): void {
    // TODO: Navigate to ScenarioDetailsComponent for the selected scenario.
  }

  removeSavedScenario(scenarioId: string): void {
    // TODO: Delete the scenario from storage using StorageService.
  }

  refreshSavedList(): void {
    // TODO: Reload the list of saved scenarios (after deletion or update).
  }
}
