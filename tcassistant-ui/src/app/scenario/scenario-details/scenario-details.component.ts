import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SourceService } from 'src/app/core/source.service';

@Component({
  selector: 'app-scenario-details',
  templateUrl: './scenario-details.component.html',
  styleUrls: ['./scenario-details.component.css']
})
export class ScenarioDetailsComponent {
  scenarioId!: string;
  // scenario: Scenario;
  // sources: Source[] = [];

  constructor(
    // private route: ActivatedRoute,
    private router: Router,
    private sourceService: SourceService
  ) {}

  ngOnInit(): void {
    // this.scenarioId = this.route.snapshot.paramMap.get('id') || '';
    // this.loadScenarioDetails(this.scenarioId);
  }

  loadScenarioDetails(scenarioId: string): void {
    // TODO: Retrieve and display all details for the given scenario.
    // Optionally, fetch source information using SourceService.
  }

  viewSource(sourceId: string): void {
    // TODO: Open or display detailed source information for the selected source.
  }

  backToList(): void {
    // TODO: Navigate back to the scenario list or saved scenarios view.
    this.router.navigate(['/scenario']);
  }
}
