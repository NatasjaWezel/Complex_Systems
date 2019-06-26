/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { ModelSettingsService } from './model-settings.service';

describe('Service: ModelSettings', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ModelSettingsService]
    });
  });

  it('should ...', inject([ModelSettingsService], (service: ModelSettingsService) => {
    expect(service).toBeTruthy();
  }));
});
