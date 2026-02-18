import { Component } from '@angular/core'; // Didn't include OnInit as it isn't needed, nothing is being grabbed from the API to create the group
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-create-group',
  imports: [CommonModule, FormsModule],
  templateUrl: './create-group.html',
  styleUrl: './create-group.css',
})
export class CreateGroup {
  groupData = {
    group_name : '',
    description : '',
    category: '',
    location: '',
    is_public: 'Public'
  };

  errorMessage: string = "";

  constructor(private webService: WebService, private router: Router) {}

  onSubmit() {
    this.errorMessage = "";

    if (!this.groupData.group_name.trim() || !this.groupData.description.trim() ||
        !this.groupData.category.trim() || !this.groupData.location.trim()) {
          this.errorMessage = "All fields are required";
          return;
        }

        this.webService.createGroup(this.groupData).subscribe({
          next: (res: any) => {
            // Redirect to my_groups
            this.router.navigate(['/my_groups']);
          },
          error: (err: any) => {
            this.errorMessage = err.error.error || "Failed to create group";
          }
        });
  }

  onCancel() {
    this.router.navigate(['/my_groups']);
  }

}
