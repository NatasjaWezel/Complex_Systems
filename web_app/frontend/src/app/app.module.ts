import { BrowserModule } from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { LandingComponent } from './landing/landing.component';
import { FirstPageComponent } from './first-page/first-page.component';
import { SecondPageComponent } from './second-page/second-page.component';
import { TheoryPageComponent } from './theory-page/theory-page.component';
import { ThirdPageComponent } from './third-page/third-page.component';
import { FourthPageComponent } from './fourth-page/fourth-page.component';
import { ModelRunnerComponent } from './model-runner/model-runner.component';
import { RunModelComponent } from './model-runner/run-model/run-model.component';
import { SimulationsPageComponent } from './simulations-page/simulations-page.component';
import { ResultsPageComponent } from './results-page/results-page.component';
import { MoreResultsPageComponent } from './results-page/more-results-page/more-results-page.component';
import { DiscussionPageComponent } from './discussion-page/discussion-page.component';

// External
import { Ng5SliderModule } from 'ng5-slider';

@NgModule({
   declarations: [
      AppComponent,
      LandingComponent,
      FirstPageComponent,
      SecondPageComponent,
      TheoryPageComponent,
      ThirdPageComponent,
      FourthPageComponent,
      ModelRunnerComponent,
      RunModelComponent,
      SimulationsPageComponent,
      ResultsPageComponent,
      MoreResultsPageComponent,
      DiscussionPageComponent
   ],
   imports: [
      BrowserModule,
      FormsModule,
      HttpClientModule,
      BrowserAnimationsModule,
      Ng5SliderModule
   ],
   providers: [],
   bootstrap: [
      AppComponent
   ]
})
export class AppModule { }
