/*
  This stores the routes used, and what component the route links to
*/
/// --- IMPORTS ---///
import { Routes } from '@angular/router';
import { UserLogin } from './components/user-login/user-login';
import { UserLogout } from './components/user-logout/user-logout';
import { UserRegister } from './components/user-register/user-register';
import { UserHome } from './components/user-home/user-home';
import { ViewPost } from './components/view-post/view-post';
import { UserGroups } from './components/user-groups/user-groups';
import { GroupHome } from './components/group-home/group-home';
import { MakePost } from './components/make-post/make-post';
import { CreateGroup } from './components/create-group/create-group';
import { EditGroup } from './components/edit-group/edit-group';
import { EditPost } from './components/edit-post/edit-post';
import { Search } from './components/search/search';
import { ManageRequests } from './components/manage-requests/manage-requests';
import { MyCalendar } from './components/my-calendar/my-calendar';

export const routes: Routes = [
  {
    path: '',
    component: UserLogin,
  },

  {
    path: 'login',
    component: UserLogin,
  },

  {
    path: 'register',
    component: UserRegister
  },

  // Users home page once logged in
  {
    path : 'home',
    component : UserHome
  },

  // See Private Group Requests
  {
    path: 'groups/:id/manage-requests',
    component: ManageRequests
  },

  // View one post
  {
    path : "groups/:group_id/:post_id",
    component : ViewPost
  },

  // View user groups
  {
    path: "my_groups",
    component : UserGroups
  },

  // Group page
  {
  path: 'groups/:group_id',
  component: GroupHome
  },

  // Make Post
  {
    path: 'make_post',
    component: MakePost
  },

  // Create Group
  {
    path: 'create_group',
    component: CreateGroup
  },

  // Edit Group
  {
    path : 'edit_group/:id',
    component: EditGroup
  },

  // Edit Post
  { path: 'groups/:group_id/:post_id/edit',
    component: EditPost
  },

  // Search For Group
  {
    path: 'search',
    component: Search
  },

  // User Calendar
  {
    path: 'calendar',
    component: MyCalendar
  }



];
