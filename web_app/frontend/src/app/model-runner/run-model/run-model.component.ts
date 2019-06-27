import { Component, OnInit } from '@angular/core';
import { ModelSettingsService } from 'src/services/model-settings.service';
import { ApiService } from 'src/services/api.service';
import { timeout } from 'q';

@Component({
  selector: 'app-run-model',
  templateUrl: './run-model.component.html',
  styleUrls: ['./run-model.component.css', '../model-runner.component.css', '../../shared.css', './loading.css']
})
export class RunModelComponent implements OnInit {

  firstRun: boolean;
  running: boolean;
  gourceUrl: string;
  runs: number;

  constructor(public _modelService: ModelSettingsService, private _apiService: ApiService) { }

  ngOnInit() {
    this.running = false;
    this.firstRun = false;
    this.runs = 0;
  }

  runModel() {
    this.runs += 1;
    this.running = true;
    this.firstRun = true;
    this.gourceUrl = null;
    this._apiService.post('run', this._modelService.modelParams)
    .then((res) => {
      console.log(res);
      this.running = false;

      this.gourceUrl = this._apiService.apiUrl + 
        'file/' + res['gource']['url'] + '?' + 'type=' + res['gource']['type'] + '&runs=' + this.runs + '';

    });
  }
}
