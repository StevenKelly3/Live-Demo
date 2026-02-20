import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './change-password.html',
  styleUrl: './../edit-profile/edit-profile.css', // Reusing the same CSS for consistency!
})
export class ChangePassword {
  passwordData = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  };
  errorMessage: string = "";
  successMessage: string = "";

  constructor(private webService: WebService, private router: Router) {}

  onSubmit() {
    this.webService.changePassword(this.passwordData).subscribe({
      next: (res: any) => {
        this.successMessage = "Password updated successfully!";
        this.errorMessage = "";
        // Clear the form
        this.passwordData = { old_password: '', new_password: '', confirm_password: '' };
      },
      error: (err) => {
        this.errorMessage = err.error.error || "Failed to change password.";
        this.successMessage = "";
      }
    });
  }

  onCancel() {
    this.router.navigate(['/home']);
  }
}
