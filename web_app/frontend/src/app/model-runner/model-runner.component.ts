import { Component, OnInit } from '@angular/core';

import { Options } from 'ng5-slider';
import { ModelSettingsService } from 'src/services/model-settings.service';

@Component({
  selector: 'app-model-runner',
  templateUrl: './model-runner.component.html',
  styleUrls: ['./model-runner.component.css', '../shared.css']
})
export class ModelRunnerComponent implements OnInit {

  p_c_class = 0.1;
  p_cr_method = 0.1;
  p_ca_method = 0.4;
  p_u_method = 0.45;
  p_d_method = 0.05;

  its = 2500;

  options: Options = {
    floor: 0,
    ceil: 1,
    step: 0.01,
    animate: false,
  };

  optionsIts: Options = {
    floor: 10,
    ceil: 5000,
    step: 10,
    animate: false,
  };

  constructor(public _modelService: ModelSettingsService) { }

  ngOnInit() {
  }

  valChange(val: number, key: string) {
    this._modelService.modelParams[key] = val;
  }

}
