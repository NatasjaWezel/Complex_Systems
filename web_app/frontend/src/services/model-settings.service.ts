import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ModelSettingsService {

modelParams = {
  'p_c_class': 0.1,
  'p_cr_method': 0.1,
  'p_ca_method': 0.4,
  'p_u_method': 0.45,
  'p_d_method': 0.05,
  'its': 2500
};

constructor() { }

  getProbaSum() {
    return this.modelParams['p_cr_method'] +
          this.modelParams['p_d_method'] +
          this.modelParams['p_ca_method'] +
          this.modelParams['p_u_method'];
  }

}
