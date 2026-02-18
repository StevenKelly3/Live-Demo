import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-user-home',
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './user-home.html',
  styleUrl: './user-home.css',
})
export class UserHome implements OnInit {

  // Variables to hold data
  feed: any = [];
  errorMessage: string = "";

  constructor(private webService : WebService) {}

  // Runs when the page loads, this will subscribe to the feed
  // Or in other words, it will connect to the api and grab all the post information sent to it as long as the session token is valid
  ngOnInit() {
      this.webService.getHomeFeed().subscribe({
        next: (response: any) => {
          this.feed = response.feed;
        },
        error: (error: any) => {
          this.errorMessage = "Unable to load feed"
        }
      });
  }

}
