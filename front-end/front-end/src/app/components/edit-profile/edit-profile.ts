import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-edit-profile',
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-profile.html',
  styleUrl: './edit-profile.css',
})
export class EditProfile implements OnInit{

  profileData = {
    firstName: '',
    lastName: '',
    email: ''
  };
  errorMessage: string = "";
  successMessage: string = "";

  constructor(private webService: WebService, private router: Router) {}

  ngOnInit() {
      this.webService.getUserProfile().subscribe({
      next: (data: any) => {
        this.profileData = {
          firstName: data.firstName,
          lastName: data.lastName,
          email: data.email
        };
      },
      error: (err) => this.errorMessage = "Failed to load profile data."
    });
  }

  // Updaing profile
  onSubmit() {
    this.webService.updateProfile(this.profileData).subscribe({
      next: (res: any) => {
        this.successMessage = "Profile updated successfully!";
        this.errorMessage = "";
      },
      error: (err) => {
        this.errorMessage = err.error.error || "Failed to update profile.";
        this.successMessage = "";
      }
    });
  }

  // Deleting profile
  onDelete() {
    if (confirm("WARNING: This will permanently delete your account, all your owned groups, and all your posts. This cannot be undone. Proceed?")) {
      this.webService.deleteAccount().subscribe({
        next: () => {
          localStorage.clear(); // Wipe tokens
          this.router.navigate(['/']); // Send to landing/login
        },
        error: (err) => this.errorMessage = "Failed to delete account."
      });
    }
  }

  // Cancel and return to home
  onCancel() {
    this.router.navigate(['/home']);
  }
}
