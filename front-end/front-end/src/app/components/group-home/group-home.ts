import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink, Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-group-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './group-home.html',
  styleUrl: './group-home.css'
})
export class GroupHome implements OnInit {
  group: any = {};
  feed: any[] = [];
  errorMessage: string = "";
  isOwner: boolean = false;
  groupId: string = "";

  constructor(private webService: WebService,
    private route: ActivatedRoute,
    private router: Router) {}

  ngOnInit() {
    this.groupId = this.route.snapshot.paramMap.get('group_id') || "";
    this.loadGroupData();
  }

  loadGroupData() {
    this.webService.getGroupById(this.groupId).subscribe({
      next: (data: any) => {
        this.group = data;
        this.feed = data.feed || [];

        const currentUserId = localStorage.getItem('user_id');
        if (currentUserId === data.group_owner) {
          this.isOwner = true;
        }
      },
      error: (err) => {
        this.errorMessage = "Unable to load group content.";
      }
    });
  }

  onLeaveGroup() {
    if (confirm("Are you sure you want to leave this community?")) {
      this.webService.leaveGroup(this.groupId).subscribe({
        next: () => {
          // Update local storage so Search reflects the change
          let memberOf = JSON.parse(localStorage.getItem('memberOf') || '[]');
          memberOf = memberOf.filter((id: string) => id !== this.groupId);
          localStorage.setItem('memberOf', JSON.stringify(memberOf));

          alert("Successfully left the group.");
          this.router.navigate(['/home']);
        },
        error: (err) => {
          alert(err.error?.Error || "Failed to leave group.");
        }
      });
    }
  }
}
