import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { WebService } from '../../services/web-service';


@Component({
  selector: 'app-search',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './search.html',
  styleUrl: './search.css',
})
export class Search implements OnInit {
  searchQuery: string = "";
  searchType: string = "category"; // this is the default search type
  results: any[] = [];
  errorMessage: string = "";
  hasSearched: boolean = false;
  userGroups: string[] = [];
  userOwnedGroups: string[] = [];

  constructor(private webService: WebService) {}
  ngOnInit() {
    this.updateUserStatus();
  }

  updateUserStatus() {
    // Get current user groups
    this.userGroups = JSON.parse(localStorage.getItem('memberOf') || '[]');
    this.userOwnedGroups = JSON.parse(localStorage.getItem('ownerOf') || '[]');
  }

  onSearch() {
    if (!this.searchQuery.trim()) return;

    this.errorMessage = "";
    this.results = [];
    this.hasSearched = true;

    const searchRequest = this.searchType === 'category'
      ? this.webService.searchGroupByCategory(this.searchQuery)
      : this.webService.searchGroupByName(this.searchQuery);

    searchRequest.subscribe({
      next: (data: any) => {
        this.results = data;
      },
      error: (err: any) => {
        this.results = [];
        this.errorMessage = err.error.error || "No results found.";
      }
    });
  }

  joinGroup(groupId: string) {
    this.webService.joinGroup(groupId).subscribe({
      next: () => {
        // Update local storage and view after joining
        this.userGroups.push(groupId);
        localStorage.setItem('memberOf', JSON.stringify(this.userGroups));
        alert("Successfully joined the group");
      },
      error: (err) => alert(err.error.error || "Failed to join group")
    });
  }

  requestToJoin(groupId: string) {
    this.webService.requestToJoinGroup(groupId).subscribe({
      next: () => alert("Request sent to group owner"),
      error: (err) => alert(err.error.error || "Failed to send request")
    });
  }

}
