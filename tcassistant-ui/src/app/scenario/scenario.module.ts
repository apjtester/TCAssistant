import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ScenarioRoutingModule } from './scenario-routing.module';
import { ScenarioInputComponent } from './scenario-input/scenario-input.component';
import { ScenarioOutputComponent } from './scenario-output/scenario-output.component';
import { SavedScenariosComponent } from './saved-scenarios/saved-scenarios.component';
import { ScenarioDetailsComponent } from './scenario-details/scenario-details.component';
import { HttpClientModule } from '@angular/common/http';
import { MarkdownModule } from 'ngx-markdown';


@NgModule({
  declarations: [
    ScenarioInputComponent,
    ScenarioOutputComponent,
    SavedScenariosComponent,
    ScenarioDetailsComponent
  ],
  imports: [
    CommonModule,
    ScenarioRoutingModule,
    FormsModule,
    HttpClientModule,
    MarkdownModule.forRoot()
  ],
  exports:[
    SavedScenariosComponent,
    ScenarioDetailsComponent
  ]
})
export class ScenarioModule { }
