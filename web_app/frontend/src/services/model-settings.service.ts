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
  'its': 500
};

constructor() { }

}
