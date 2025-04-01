import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StorageService {

  constructor() { }
  saveScenario(scenario: any): void {
    // TODO: Save the given scenario to local storage or a backend.
  }
}
