import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  apiUrl: string;

  constructor(private _http: HttpClient) {
    this.apiUrl = 'http://localhost:8080/';
  }

  /**
   * The main get request function that returns a promise containing the response of the API
   * @param query Query for the API to call a get method on
   * @returns Returns promise of the requested API endpoint
   */
  async get(query: string): Promise<void | Object> {
    const url = this.apiUrl + query;
    return await this._http
      .get(url, {})
      .toPromise()
      .catch(err => { this.handle_error(err); });
  }

  /**
   * The main post request function that returns a promise containing the response of the API
   *
   * @param query API endpoint
   * @param obj object to post to API
   */
  async post(query: string, obj: Object): Promise<void | Object> {
    const url = this.apiUrl + query;
    return await this._http
      .post(url, obj, {})
      .toPromise()
      .catch(err => { this.handle_error(err); });
  }

  handle_error(err) {
    console.log(err);
  }


}
