/// --- IMPORTS --- ///
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class WebService {

  constructor(private http: HttpClient, public router: Router) {}

  // Connects the front end to Flask (back-end) to retrieve the users home feed
  getHomeFeed() {
    // get the jwt token stored in the browser during login
    const sessionToken = localStorage.getItem('token');
    console.log("Current Token ", sessionToken)

    // attach token to the "Authorization" header, allows @jwt_required to accept the call
    const headers = new HttpHeaders().set(`x-access-token`, `${sessionToken}`);

    // Make the GET request
    return this.http.get('https://alchemaxdemo.co.uk/api/home', { headers: headers });
  }

  // Get a single post from Flask
  getSinglePost(groupId : string, postId : string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', `${token}`);

    return this.http.get(`https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}`, { headers: headers });
  }

  // Get the users groups
  getUserGroups() {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', `${token}`);

    return this.http.get('https://alchemaxdemo.co.uk/api/get_user_groups', { headers: headers });
  }

  // Gets the group home page
  getGroupById(id: string) {
    const headers = new HttpHeaders().set('x-access-token', localStorage.getItem('token') || '');

    return this.http.get(`https://alchemaxdemo.co.uk/api/groups/${id}`, { headers });
  }

  // Allows a user to upload a post to their groups page, aka it sends a request to the backend to upload the post
  makePost(postData: any) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set(`x-access-token`, `${token}`);
    const formData = new FormData();

    formData.append('group_id', postData.group_id);
    formData.append('post_title', postData.post_title);
    formData.append('post_message', postData.post_message);
    formData.append('event_button', postData.event_button);

    if (postData.event_button === 'Yes' && postData.event_date) {
      formData.append('event_date', postData.event_date);
    }

  return this.http.post("https://alchemaxdemo.co.uk/api/create_post", formData, {headers: headers});
  }

  // This allows for a user to create a group
  createGroup(groupData : any) {
    const token = localStorage.getItem('token')
    const headers = new HttpHeaders().set('x-access-token', token || '');

    const formData = new FormData();
    formData.append('groupName', groupData.group_name);
    formData.append('groupLocation', groupData.location);
    formData.append('groupCategory', groupData.category);
    formData.append('groupDescription', groupData.description);
    formData.append('groupAccess', groupData.is_public);

    return this.http.post('https://alchemaxdemo.co.uk/api/create_group', formData, { headers });
  }

  // Allow a user to edit a group
  editGroup(id: string, groupData: any) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    const formData = new FormData();
    formData.append('groupName', groupData.group_name);
    formData.append('groupLocation', groupData.location);
    formData.append('groupCategory', groupData.category);
    formData.append('groupDescription', groupData.description);
    formData.append('groupAccess', groupData.is_public);

    return this.http.put(`https://alchemaxdemo.co.uk/api/groups/${id}/settings/edit_group`, formData, { headers });
  }

  // Allows a user to delete a group
  deleteGroup(id: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.delete(`https://alchemaxdemo.co.uk/api/groups/${id}/settings/delete_group`, { headers });
  }

  // Allows a user to edit their post
  editPost(groupId: string, postId: string, postData: any) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    const formData = new FormData();
    formData.append('post_title', postData.post_title);
    formData.append('post_message', postData.post_message);
    formData.append('event_button', postData.event_button);
    if (postData.event_button === 'Yes' && postData.event_date) {
      formData.append('event_date', postData.event_date);
    }

    return this.http.delete(`https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/delete_post`, { headers });
  }

  // Delete an existing post
  deletePost(groupId: string, postId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.delete(`https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/delete_post`, { headers });
  }

  // Search for a group by name
  searchGroupByName(name: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');
    return this.http.get(`https://alchemaxdemo.co.uk/api/search_for_groups/group_name/${name}`, {headers});
  }

  // Search for a group by cateogry
  searchGroupByCategory(category: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');
    return this.http.get(`https://alchemaxdemo.co.uk/api/search_for_groups/category/${category}`, {headers});
  }

  // Create comment
  addComment(groupId: string, postId: string, text: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    const formData = new FormData();
    formData.append('comment_text', text);

    return this.http.post(
      `https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/add_comment`,
      formData,
      { headers }
    );
  }

  // Edit comment
  updateComment(groupId: string, postId: string, commentId: string, text: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    const formData = new FormData();
    formData.append('comment_text', text);

    return this.http.put(
      `https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/${commentId}/edit`,
      formData,
      { headers }
    );
  }

  // Delete comment - NO GOING BACK IF DONE
  removeComment(groupId: string, postId: string, commentId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.delete(
      `https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/${commentId}/delete`,
      { headers }
    );
  }

  // Join Public Group
  joinGroup(groupId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.put(`https://alchemaxdemo.co.uk/api/${groupId}/join`, {}, { headers });
  }

  // Request To Join Private Group
  requestToJoinGroup(groupId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.put(`https://alchemaxdemo.co.uk/api/${groupId}/join`, {}, { headers });
  }

  // See join requests
  getJoinRequests(groupId: string) {
    const headers = new HttpHeaders().set('x-access-token', localStorage.getItem('token') || '');
    return this.http.get(`https://alchemaxdemo.co.uk/api/groups/${groupId}/requests_to_join`, { headers });
  }

  // Accept join request
  acceptRequest(groupId: string, requestId: string) {
    const headers = new HttpHeaders().set('x-access-token', localStorage.getItem('token') || '');
    return this.http.put(`https://alchemaxdemo.co.uk/api/groups/${groupId}/requests_to_join/${requestId}/accepted`, {}, { headers });
  }

  // Reject join request
  rejectRequest(groupId: string, requestId: string) {
    const headers = new HttpHeaders().set('x-access-token', localStorage.getItem('token') || '');
    return this.http.put(`https://alchemaxdemo.co.uk/api/groups/${groupId}/requests_to_join/${requestId}/rejected`, {}, { headers });
  }

  // Leave Group
  leaveGroup(groupId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    // Matches: @groups_bp.route("/api/groups/<group_id>/leave", methods = ['PUT'])
    return this.http.put(`https://alchemaxdemo.co.uk/api/groups/${groupId}/leave`, {}, { headers });
  }

  // Add to calender / RSVP to event
  rsvpToEvent(groupId: string, postId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.put(`https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/rsvp`, {}, {headers});
  }

  // Get the attendees to event post
  getAttendees(groupId: string, postId: string) {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.get(`https://alchemaxdemo.co.uk/api/groups/${groupId}/${postId}/attendees`, {headers});
  }

  // Get users calendar
  getMyCalendar() {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('x-access-token', token || '');

    return this.http.get('https://alchemaxdemo.co.uk/api/my_calendar', { headers });
  }

}
