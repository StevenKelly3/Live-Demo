/*
  This is a data service to handle the http calls for logging in
*/

/// --- IMPORTS --- ///
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class Auth {
  // Basically the url to access the API
  private apiUrl = 'http://localhost:5000/api'

  constructor(private http: HttpClient) {}

  // Login
  login(username : string, password: string): Observable<any> {
    // 'btoa' is a javascript method that encodes a string into a base64 encoded ASC11 string.
    // it is used to convert binary data into a text format
    const credentials = btoa(`${username}:${password}`);
    const headers = new HttpHeaders({
      'Authorization' : `Basic ${credentials}`
    });

    return this.http.get(`${this.apiUrl}/login`, {headers});

  }

  // Register
  register(userData: any) : Observable<any> {
    const postData = new FormData();
    postData.append('firstName', userData.firstName);
    postData.append('lastName', userData.lastName);
    postData.append('username', userData.username);
    postData.append('email', userData.email);
    postData.append('password', userData.password);
    postData.append('confirmPassword', userData.confirmPassword);

    // return statement
    return this.http.post(`${this.apiUrl}/register`, postData);
  }

  // Save token
  setSession(token: string, user_id: string) {
    localStorage.setItem('token', token);
    localStorage.setItem('user_id', user_id);
  }

  //logout
  logout() {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.get(`${this.apiUrl}/logout`, { headers });
  }

}
