import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-my-calendar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './my-calendar.html',
  styleUrl: './my-calendar.css',
})
export class MyCalendar implements OnInit {
  calendarEvents: any[] = [];
  errorMessage: string = "";
  isLoading: boolean = true;

  constructor(private webService: WebService) {}

  ngOnInit() {
    this.loadCalendar();
  }

  loadCalendar() {
    this.webService.getMyCalendar().subscribe({
      next: (data: any) => {
        this.calendarEvents = data.calendar || [];
        this.isLoading = false;
      },
      error: (err: any) => {
        this.errorMessage = "Unable to load your calendar at this time.";
        this.isLoading = false;
      }
    });
  }
}
