import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-user-groups',
  imports: [CommonModule, RouterLink],
  templateUrl: './user-groups.html',
  styleUrl: './user-groups.css',
})
export class UserGroups implements OnInit{

  //variables
  memberGroups: any = [];
  ownerGroups: any = [];

  constructor(private webService : WebService) {}

  ngOnInit() {
      this.webService.getUserGroups().subscribe({
        next : (data : any) => {
          this.memberGroups = data.joined_groups;
          this.ownerGroups = data.owned_groups;
        },

        error: (err) => {
        console.error("Error fetching groups", err);
        }
      });
  }

}
