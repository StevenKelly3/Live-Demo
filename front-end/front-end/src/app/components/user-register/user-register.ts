import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Auth } from '../../services/auth';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-user-register',
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './user-register.html',
  styleUrl: './user-register.css',
})
export class UserRegister {

  regData = {
    firstName: '',
    lastName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  };
  message = '';

  constructor(private authService: Auth, private router: Router) {}

  onRegister() {
    this.authService.register(this.regData).subscribe({
      next: (res) => {
        console.log('Registration success', res);
        this.message = 'Account created! Redirecting to login...';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.message = err.error?.error || 'Registration failed';
        console.error(err);
      }
    });
  }
}
