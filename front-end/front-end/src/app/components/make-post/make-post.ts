import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-make-post',
  imports: [CommonModule, FormsModule],
  templateUrl: './make-post.html',
  styleUrl: './make-post.css',
})
export class MakePost implements OnInit{
  // Form model
  postData = {
      group_id: '',
      post_title: '',
      post_message: '',
      event_button: 'No',
      event_date: ''
    };

    // variables
    userGroups: any[] = []
    errorMessage: string = "";

    constructor(private webService: WebService, private router: Router) {}

    ngOnInit() {
        // Fetch the groups so the user can select one in the dropdown
        this.webService.getUserGroups().subscribe({
          next: (data: any) => {
            // Combine joined and owned groups for the selection list
            this.userGroups = [...data.joined_groups, ...data.owned_groups];
          }
        });
    }

    onSubmit() {
      this.errorMessage = "";

      this.errorMessage = "";

      // Check for empty fields (Strings only)
      if (!this.postData.group_id) {
        this.errorMessage = "Please select a group.";
        return;
      }

      if (!this.postData.post_title.trim()) {
        this.errorMessage = "Post title cannot be empty.";
        return;
      }

      if (!this.postData.post_message.trim()) {
        this.errorMessage = "Post message cannot be empty.";
        return;
      }

      // Check if the post is for an event
      if (this,this.postData.event_button == 'Yes') {
        // regex for date and time. In order from left to right, it requires
        /*
          - 4 digits for the year (i.e. 2026)
          - a dash (-)
          - 2 digits for the month (i.e. 03 for March)
          - a dash (-)
          - 2 digits for the day (i.e. 02)
          - a space ( )
          - 2 digits for the hour (i.e. 14)
          - a colon(:)
          - 2 digits for the minute (i.e. 37)
        */
        const dateRegex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/;
      }


      // Call the service
      this.webService.makePost(this.postData).subscribe({
        next: (res: any) => {
          // Redirect to home after success
          this.router.navigate(['/home'])
        },
        error: (err) => {
          this.errorMessage = err.error.error || "Failed to create post";
        }
      });

    }

    onCancel() {
        this.router.navigate(['/home']);
      }
}
