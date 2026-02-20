import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-edit-post',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-post.html',
  styleUrl: './edit-post.css'
})
export class EditPost implements OnInit {
  groupId: string = "";
  postId: string = "";

  post: any = {};

  postData = {
    post_title: '',
    post_message: '',
    event_button: 'No',
    event_date: ''
  };
  errorMessage: string = "";
  isCreator: boolean = false;

  constructor(
    private webService: WebService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    this.groupId = this.route.snapshot.paramMap.get('group_id') || "";
    this.postId = this.route.snapshot.paramMap.get('post_id') || "";
    const currentUserId = localStorage.getItem('user_id');

    this.webService.getSinglePost(this.groupId, this.postId).subscribe({
      next: (data: any) => {
        // Verify ownership
        this.post = data;

        if (currentUserId !== data.creator) {
          this.errorMessage = "You do not have permission to edit this post.";
          return;
        }

        this.isCreator = true;
        this.postData = {
          post_title: data.post_title,
          post_message: data.post_message,
          event_button: data.event_button,
          event_date: data.event_date ? data.event_date.replace('T', ' ').substring(0, 16) : ''        };
      },
      error: (err) => this.errorMessage = "Could not load post details."
    });
  }

  onSubmit() {
    this.webService.editPost(this.groupId, this.postId, this.postData).subscribe({
      next: () => this.router.navigate(['/groups', this.groupId]),
      error: (err) => this.errorMessage = "Failed to update post."
    });
  }

  onDelete() {
    if (confirm("Are you sure you want to delete this post?")) {
      this.webService.deletePost(this.groupId, this.postId).subscribe({
        next: () => this.router.navigate(['/groups', this.groupId]),
        error: (err) => this.errorMessage = "Failed to delete post."
      });
    }
  }

  onCancel() {
    this.router.navigate(['/groups', this.groupId]);
  }
}
