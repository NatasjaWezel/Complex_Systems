import { Component, OnInit } from '@angular/core';
import { ModelSettingsService } from 'src/services/model-settings.service';
import { ApiService } from 'src/services/api.service';

@Component({
  selector: 'app-run-model',
  templateUrl: './run-model.component.html',
  styleUrls: ['./run-model.component.css', '../model-runner.component.css', '../../shared.css']
})
export class RunModelComponent implements OnInit {

  constructor(private _modelService: ModelSettingsService, private _apiService: ApiService) { }

  ngOnInit() {
  }

  runModel() {
    this._apiService.post('run', this._modelService.modelParams)
  }

}
