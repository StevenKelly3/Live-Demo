import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { WebService } from '../../services/web-service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-manage-requests',
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './manage-requests.html',
  styleUrl: './manage-requests.css',
})
export class ManageRequests implements OnInit{

  groupId: string = "";
  requests: any[] = [];
  errorMessage: string = "";
  loading: boolean = true;

  constructor(
    private webService: WebService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.groupId = this.route.snapshot.paramMap.get('id') || "";
    if (this.groupId) {
      this.fetchRequests();
    }
  }

  fetchRequests() {
    this.loading = true;
    this.webService.getJoinRequests(this.groupId).subscribe({
      next: (data: any) => {
        this.requests = data;
        this.loading = false;
      },
      error: (err) => {
        this.errorMessage = "Unable to load requests. Ensure you are the owner.";
        this.loading = false;
      }
    });
  }

  onAccept(requestId: string) {
    this.webService.acceptRequest(this.groupId, requestId).subscribe({
      next: () => {
        // Remove from local list to avoid a full re-fetch
        this.requests = this.requests.filter(r => r.user_id !== requestId);
      },
      error: (err) => alert("Error accepting request.")
    });
  }

  onReject(requestId: string) {
    if(confirm("Are you sure you want to reject this user?")) {
      this.webService.rejectRequest(this.groupId, requestId).subscribe({
        next: () => {
          this.requests = this.requests.filter(r => r.user_id !== requestId);
        },
        error: (err) => alert("Error rejecting request.")
      });
    }
  }
}
