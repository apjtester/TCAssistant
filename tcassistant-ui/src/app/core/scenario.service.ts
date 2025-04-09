import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, tap } from 'rxjs';
import { LlmService } from './llm.service'; // Adjust the path as necessary
import { ScenarioOutputComponent } from '../scenario/scenario-output/scenario-output.component';

@Injectable({
  providedIn: 'root'
})
export class ScenarioService {
  constructor(private llmService: LlmService) {}
  private output = new BehaviorSubject<string>("");
  isGenerating=false;
  text$ = this.output.asObservable();
  processInput(ac: string, context?: string): any {
    // TODO: Preprocess and validate the provided Acceptance Criteria and optional context.
    // Return an InputData object.
    return {};
  }

async requestScenarioGeneration(
  mode: 'initial' | 'regenerate' | 'more',
  ac: string,
  context?: string
) {
  switch (mode) {
    case 'initial':
      this.output.next("");
      try {
        const scenarioStream = this.llmService.generateScenarios(ac, context);
        await scenarioStream.forEach((chunk: any) => {
          console.log(chunk);
          // Append each chunk as it arrives.
          this.output.next(this.output.value + chunk);
        });
        console.log('Streaming complete.');
      } catch (error) {
        console.error('Error streaming from Ollama API:', error);
      }
      break;
    case 'regenerate':
      await this.llmService.regenerateScenarios(ac, context);
      break;
    case 'more':
      await this.llmService.generateMoreScenarios(ac, context);
      break;
    default:
      break;
  }
}

  
//  requestScenarioGeneration(
//   mode: 'initial' | 'regenerate' | 'more',
//   ac: string,
//   context?: string
// ) {
//   switch (mode) {
//     // case 'initial':
//     // return this.llmService.generateScenarios(ac, context);
//     case 'initial':
//       this.output.next("");
//       this.llmService.generateScenarios(ac, context).subscribe({
//         next: (chunk) => {
//           console.log(chunk);
//           // Append each chunk as it arrives.
//           this.output.next(this.output.value+ chunk);
//         },
//         error: (error) => {
//           console.error('Error streaming from Ollama API:', error);
//         },
//         complete: () => {
//           console.log('Streaming complete.');
//         }
//       });
//       break;
//   case 'regenerate':
//      this.llmService.regenerateScenarios(ac, context);
//      break;
//   case 'more':
//      this.llmService.generateMoreScenarios(ac, context);
//      break;
//   default:
//      break;
//   }
// }

  mergeScenarios(existingScenarios: any[], additionalScenarios: any[]): any[] {
    // TODO: Merge new scenarios with existing ones, removing duplicates if necessary.
    return [...existingScenarios, ...additionalScenarios];
  }

  getScenarioById(scenarioId: string): any {
    // TODO: Retrieve a scenario by its unique identifier from a local cache or backend.
    return {};
  }
}
