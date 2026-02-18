import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-edit-group',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-group.html',
  styleUrl: './edit-group.css'
})
export class EditGroup implements OnInit {
  group_id: string = "";
  groupData = {
    group_name: '',
    description: '',
    category: '',
    location: '',
    is_public: 'Public'
  };
  errorMessage: string = "";

  constructor(
    private webService: WebService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    // Get ID from URL
    this.group_id = this.route.snapshot.paramMap.get('id') || "";

    // Pre-fill the form with current database values
    this.webService.getGroupById(this.group_id).subscribe({
      next: (data: any) => {
        this.groupData = {
          group_name: data.group_name,
          description: data.description,
          category: data.category,
          location: data.location,
          is_public: data.groupAccess || 'Public'
        };
      },
      error: (err) => this.errorMessage = "Could not load group details for editing."
    });
  }

  onSubmit() {
    if (!this.groupData.group_name.trim() || !this.groupData.description.trim()) {
      this.errorMessage = "Group Name and Description cannot be empty.";
      return;
    }

    this.webService.editGroup(this.group_id, this.groupData).subscribe({
      next: (res: any) => {
        // Redirect back to the group home page to see changes
        this.router.navigate(['/groups', this.group_id]);
      },
      error: (err: any) => {
        this.errorMessage = err.error.error || "Failed to update group.";
      }
    });
  }

  onCancel() {
    this.router.navigate(['/groups', this.group_id]);
  }

  // edit-group.ts

  onDelete() {
    const confirmation = confirm("WARNING: This will permanently delete this group, all associated posts, and remove all members. This cannot be undone. Are you sure?");

    if (confirmation) {
      this.webService.deleteGroup(this.group_id).subscribe({
        next: (res: any) => {
          console.log("Group deleted successfully");
          // Redirect the user to their "My Groups" list or Home
          this.router.navigate(['/my_groups']);
        },
        error: (err: any) => {
          this.errorMessage = err.error.error || "Delete failed. Please try again.";
        }
      });
    }
  }
}
