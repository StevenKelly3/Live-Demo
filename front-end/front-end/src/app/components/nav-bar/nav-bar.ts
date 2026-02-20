import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, Router} from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'nav-bar',
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
})
export class NavBar {

  showDropdown: boolean = false;

  constructor(private authService: Auth, private router: Router) {}

  isLoggedIn(): boolean {
    // returns true if the token exists in local storage
    return localStorage.getItem('token') !== null;
  }

  toggleDropdown() {
    this.showDropdown = !this.showDropdown;
  }

  onLogout() {
    this.showDropdown = false;
    this.authService.logout().subscribe({
      next: () => {
        localStorage.removeItem('token'); // Clear locally AFTER backend blacklists it
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.log("Logout failed on server, but clearing local session anyway");
        localStorage.removeItem('token');
        this.router.navigate(['/login']);
      }
    })

    this.router.navigate(['/login']);
  }

}
