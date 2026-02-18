import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Auth } from '../../services/auth';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-user-login',
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './user-login.html',
  styleUrl: './user-login.css',
})
export class UserLogin {
  loginData = { username: '', password: ''};
  errorMessage = '';

  constructor(private authService: Auth, private router: Router) {}

  onLogin() {
  this.authService.login(this.loginData.username, this.loginData.password).subscribe({
    next: (response) => {
      console.log('Login Success', response);
      this.errorMessage = ''; // Clear the old error
      this.authService.setSession(response.token, response.user_id); // Save token

      // Redirect to your dashboard/home page
      // Make sure 'home' is defined in your app.routes.ts!
      this.router.navigate(['/home']);
    },
    error: (err) => {
      // This only runs if the API fails to log in
      this.errorMessage = 'Invalid username or password';
      console.error(err);
    }
    });
  }
}
