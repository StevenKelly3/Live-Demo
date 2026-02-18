import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { WebService } from '../../services/web-service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-view-post',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './view-post.html',
  styleUrl: './view-post.css',
})
export class ViewPost implements OnInit {
  post: any = {};
  errorMessage: string = "";
  isCreator: boolean = false;
  groupId: string = "";
  postId: string = "";
  currentUserId: string | null = "";
  newCommentText: string = "";
  editingCommentId: string | null = null;
  editedCommentText: string = "";

  constructor(
    private webService: WebService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.groupId = this.route.snapshot.paramMap.get('group_id') || "";
    this.postId = this.route.snapshot.paramMap.get('post_id') || "";
    this.currentUserId = localStorage.getItem('user_id');

    this.loadPost();
  }

  // LOAD THE POST
  loadPost() {
    if (this.groupId && this.postId) {
      this.webService.getSinglePost(this.groupId, this.postId).subscribe({
        next: (data: any) => {
          this.post = data;
          if (this.currentUserId === data.creator) {
            this.isCreator = true;
          }
        },
        error: (err: any) => {
          this.errorMessage = "Could not find this post.";
        }
      });
    }
  }

  // CREATE COMMENT
  submitComment() {
    if (!this.newCommentText.trim()) return;

    this.webService.addComment(this.groupId, this.postId, this.newCommentText).subscribe({
      next: () => {
        this.newCommentText = "";
        this.loadPost(); // Refresh to show new comment
      },
      error: () => this.errorMessage = "Failed to post comment."
    });
  }

  // Update COMMENT
  startEdit(comment: any) {
    this.editingCommentId = comment._id;
    this.editedCommentText = comment.comment_text;
  }

  cancelEdit() {
    this.editingCommentId = null;
    this.editedCommentText = "";
  }

  saveEdit(commentId: string) {
    if (!this.editedCommentText.trim()) return;

    this.webService.updateComment(this.groupId, this.postId, commentId, this.editedCommentText).subscribe({
      next: () => {
        this.editingCommentId = null;
        this.loadPost();
      },
      error: () => this.errorMessage = "Failed to update comment."
    });
  }

  // DELETE COMMENT
  onDeleteComment(commentId: string) {
    if (confirm("Are you sure you want to delete this comment?")) {
      this.webService.removeComment(this.groupId, this.postId, commentId).subscribe({
        next: () => {
          this.loadPost();
        },
        error: () => this.errorMessage = "Failed to delete comment."
      });
    }
  }
}
