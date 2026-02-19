# Computing-Project-AT3
This is my university project. It is "A web application designed to connect and find communities and social groups"


# Back-end
This will store the API's for the application, allowing for easy communication between the front-end and the database. 

This uses the following:
- venv
- flask
- mongoDB
- Python

To setup the application:
1. Create the venv virtural environment
    python -m venv venv
        OR
    py -m venv venv
        OR
    python3 -m venv venv
2. Activate venv
    venv\Scripts\activate
3. Imports
    pip install flask
	pip install python-dotenv (FROM https://pypi.org/project/python-dotenv/)
4. Run file
	py app.py

Blueprints:
    - user-management
        - create-user
        - delete-user
        - user-login
        - user-logout
        - edit-user
    
    - groups
        - create-group
        - delete-group
        - create-post
        - delete-post
        - update-post
        - read-post
        - edit-group
        - report-group
        - report-post
        - create-event
        - edit-event
        - read-event
        - delete-event
        - accept-event
        - reject-event

    - group-search
        - search-by-name
        - search-by-category
        - search-by-location

    - moderation
        - moderator-login
        - moderator-logout
        - view-audit
        - view-reports
        - ban-user
        - delete-post
        - delete-group

# Front-end
This will be used to provide the user with a GUI to interact with the API's. 

This uses the following:
	- Angular/cli@20


To setup the application:
1. Install Angular/cli@20
	npm install -g @angular/cli@20

## -- VERSIONS -- ##

What they mean
- v0 - Inital setup stage (i.e. imports, dataset structure, ensuring connections can be made).
    This is just the initial setup

- v1 - Sprint 1


# version 0.1 - back-end initial setup
This is the initial setup of the back-end, this includes:
1. imports:
    venv
    flask
2. blueprint setup

# version 0.2 - database connections
This version is literally just ensuring I can connect to mongoDB and ping it, nothing special.

I did also move app.py and globals.py outisde of the src folder.

# version 0.3 - angular setup
Basically just installing angular, nothing special yet

# version 1.1.1 - Account creation
This version allows a user to create an account, the backend work is done for registration, but the front end needs developed.

1. Imports:
	bycrypt
	jwt

# version 1.1.2 - User login
This version allows a user to login to their account, the backend work is done, front end needs developed, this will be done in v1.2, v1.1 will focus on the backend for authentication.

# version 1.1.3 - User logout
This version allows a user to logout of their account, the backend work is done, again front end needs developed.

A new collection called blacklist was added, which will store the users session token, preventing the user from using the old session token to access the service.

# version 1.2.1 - Login page
SO, when making this I found a routing issue where it kept returning me to the localhost:4200 url.

To fix this, I went back to the base code and I was able to route successfully to localhost:4200/login.

This commit is just incase I need to revert back to what works

# version 1.2.2 - Login page
Fixed the issue, app.config.ts needed provideHttpClient() as a provider. Once this was added, the page loaded correctly.

API is being accessed and if a user is found, 200 is sent back to the front-end, if not then the user is promted with a message.

The UI is a temp layout just to test the functionality, I will improve it later.

# version 1.2.3 - Control Log
In version 1.1, I forgot to add the control log and audit log. 

As audit log isn't too important (all could just be done through control logs as it shows both errors and changes made), I will focus on the front end for the remainder of v1.2.

Two new collections were addded, "audit" and "logs". 

Additionally, I removed the try-except clause from the logout endpoint, as the user will always be logged out, even if they aren't logged in they'll be logged out.
Still, I could add it back in at a later stage, but I don't think it is needed.

Re-ran all tests and no bugs have appeared.

# version 1.2.4 - Register Front-end
Created a new component allowing users to register for the service. 

With this, the service auth.ts was updated to communicate with the register endpoint.

When a user logs in, it redirects the user to the login page

I did also come accross an issue where some fields, like username, were down as userName, or I typed them as userName instead of username. Just a note for future self to check the API to see how the fields are entered and to keep to that standard.

# version 1.2.5 - Fixed logs
Okay so, when adding the logs feature I came across an issue where I was clueless on how to actually pass the username through the JWT token, so yeah I found a solution.

In flask, there is an import called g (global) which allows you to set global variables to use in any blueprint. So when a jwt token is created, it sets the username for the logged in user automatically.

To call it, all you need to add is:
	g.VARIABLE_NAME
	(of course as well as adding g to the import list for flask)
	
SO HAPPY WITH THIS.

So now all developed auth.py endpoints should contain this. 

Additionally, I did start the group blueprint development, the g import was needed, so there is a small groups.py file, but this isn't the completed version.

After this commit, I will be moving to v1.3, which is souly the groups section.

Additionally, the front end development isn't fully done for the auth.py file, as I can't do delete account or logout yet without more pages, they will come at a later stage.

I am so happy at the moment, Watch this blow up in my face in the future and ruin my day.

# version 1.3.1 - Create group
New blueprint added called groups which will store the group functionality, including posts.

A new endpoint was added to it allowing users to create groups.

# version 1.3.2 - Join group
Okay this was a fun one to create. So a new endpoint was created allowing a user to join or request to join a group.

This isn't the final version of this endpoint, as when a user is banned from a group, they shouldn't be able to join the group. That will need added when the block button comes in

Apart from that it is working. THE FIRST UPDATE METHOD OF THIS PROJECT (I hope, is it bad that I can't remember if I did an update user endpoint last week? I'll blame the tiredness)

Also Steven, please remember that if you delete a group, and create a new one to replace it because you are too lazy to manually update the groups, change the group _id in the postman tests

# version 1.3.3 - Accept/Reject user request to Join
This is just an updated version of 1.3.2 allowing group owners to reject or accept users. Not much else to it

# version 1.3.4 - Leave group
This allows a user to leave a group they are apart of

# version 1.3.5 - Create post and view groups
This version has multiple changes

1) A new endpoint was added allowing a user to view what groups they are a part of. This includes seeing the groups they own.

	This was added for the create posts feature, to send the users groups to the front end so the user can select their group
	
	The returned result is the group name and the id, the username is to be displayed in a list for the user to select, then the id will be sent to the backend api to specify which group the post should go to
	
2) The create post endpoint was created allowing users to create posts for their group. Not much special to it. 

	This might need adjusted in the future
	
3) Edited a few endpoints to add a new value, ownerOf, to the user documents, so at times when I need to find the owner, I can also reference the users collection instead of doing constant outer joins

# version 1.3.6 - See posts

1) Fixed an issue where the user was not able to create posts, it was because an or statement was used instead of an and

2) Created a new endpoint allowing users to see their groups posts in reverse chronological order

3) Created a new endpoint allowing users to see posts that their group have uploaded

4) Created a new endpoint allowing users to see one post that their group have uploaded

# version 1.3.7 - Edit posts

This version allows a post creator to edit their post. Nothing special, all tests passed really.

# version 1.3.8 - Delete posts

Finishing off the CRUD operations for the posts section, this new endpoint allows a post creator to delete their post. 

All of the endpoints will need edited to add the comments part, but I want to start the front end first as the comments part will take less time than the groups/posts part

This sprint has been longer than the others as I have gone off the sprint cycle slightly, as it stands I am meant to be on the first day of sprint 2, however, when developing the groups part, I realised it would be easier to develop both groups and posts together as when a group is removed all their posts will need to be removed.
I do understand that in the end, I will need to come back to edit the delete groups part to include deleting the comments, but with the post and group removed, it will reduce or even eliminate the possibility of a bug occurring

All that is left to do in v1.3 is edit and delete group (which will fall under v1.3.9. I do have comments in for seeing the groups members and removing/banning them, but they are not of interest in this sprint as I want to get the front end started

# version 1.3.9 - Edit and Delete group

This version now allows a creator to edit and delete their groups, when a group is deleted, all of their posts are deleted and all of their members are forced to leave the group. 

A few other changes have been made:
	1) Updated View Group Home Page so it returns the group details, forgot to add that originally. Kept it simple and just joined the feed part into the group details and returned the group details. 
		Feel like I will have to update more so I can pass the groups name for viewing posts, but I'll check that later
	2) Moved all post endpoints to the posts.py blueprint as the groups.py blueprint was getting bulky
	3) Updated app.py to include posts.py
	
# version 1.4.1 - User Home page

Now I'm back to the front-end development. In this version I created a new component allowing users to view their home page (main feed). This shows all of the posts from the users groups.

There was also a backend change needed to app.py, specifically this line
	CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}}, 
     allow_headers=["Authorization", "Content-Type", "x-access-token"])
	 
This allows for the x-access-token to be added to the header, without this, the user wouldn't be able to load anything as they would be an unauthorized user

Other changes included:
	1) login component - Changed the html format and added css
	2) register component - Changed the html format and added css
	
# version 1.4.2 - See One post

This version allows users to see a single post


Other changes:
	1) Added a nav-bar
	2) Edited user home page so each post shows the creator username and the groups name
	3) Changed posts.py so the creators username and the group name are sent
	
# version 1.4.3 - My Groups and See Group

Created a new component allowing a user to view their group list

Created a new component allowing a user to view a groups page


Other changes:
	1) Edited auth.py to set the session token expiry to 60 mins after login
	

# verion 1.4.4 - Make post
This was a bulky change, so now users can make posts for the groups they are in. A check has been put in place to ensure the user types in the correct information, and a regex check has also been added to ensure the user types the correct date format.

Nothing really else to report

Other changes
	1) Edited user-groups.html as the manage groups button isn't needed
	2) posts.py updated to check the date format being sent is correct
	

# version 1.4.5 - Create Group
Added the ability for users to create new groups. Users can set their group to private or public. No issues spotted

Other changes
	1) Had to edit user_groups.html and css as when a user owns a group, the create group button disappears. Changed it so there is always a create group button
	

# version 1.4.6 - Edit Group & Delete group
EDIT GROUP:
	This was a complex update, mostly because I messed up (not my prefered use of words).
	
	To get the edit button working, I had to make sure the user was an owner before it shows the edit button, but I couldn't get it working initially.
	
	The issue was to do with both the python file, and the login component and auth service. As the creator_id wasn't passed I wasn't able to compare the creator id to the users id.
	
	Now this is resolved and updates can happen
	
	Additionally, the delete option has been added into the edit component, no need for a delete component


Other changes
	1) Editied auth.ts, and nav-bar.html and css to add in logout functionality. 
	2) Editied the jwt decorator in decorators.py so when a user logs out, their session token will be blacklisted
	3) Other changes as explained above
	

# verison 1.4.7 - Edit & Delete post
Added an edit post component allowing users to edit and delete posts. No other changes made apart from adding the routing and updating web-services

# version 1.4.8 - Search For group
This involves both a front end and backend change, in order of development.

1) Created a new endpont allowing users to serach for groups by their name using regex
2) Created a new endpoint (copy and paste of 1) allowing users to search for groups using the groups category
3) Created a new component allowing for both search functions to work in the front end

# version 1.4.8 - Comments
This involves both front-end and back-end changes, as the backend was almost a copy and paste of the post functionality

1) Created a new blueprint for comments
2) Created a new endpoint allowing users to create Comments
3) Edit the view_one_post endpoint to show Comments
4) Added a new endpoint allowing users to edit their comments
5) Added a new endpoint allowing users to delete their comments
6) Edited view-post component to allow users to view, add, remove, adn edit their comments

# version 1.4.9 - Join/Request to join group
1) Edited the search component to work with the join endpoint. 
2) Edited the see join requests endpoint to allow owners to see the username of who requested to Join
3) Edited the group-home component to allow owners to see their requests
4) Added a new component allowing owners of private groups to accept or reject user requests

ADDITIONAL CHANGES:
	1) Edited group-home component to allow users to leave a group 
	
# version 1.5.1 - Minor Security Changes

1) Added an .env file and .gitignore file, to ensure that the secret key isn't stored in the globals.py file. This is to make the website more secure preventing bad actors from making their own jwt tokens using the secret key
	pip install python-dotenv
	Got it from https://pypi.org/project/python-dotenv/
2) Added a .gitignore file to ignore the .env file
3) Updated globals to ensure that the secret key is grabbed from the .env file

# version 1.5.2 - RSVP and Calendar

1) Created a new blueprint allowing users to RSVP to events, and view their Calendar
2) Created a new component allowing users to see their events
3) Edited view_post to allow event creators to see who is going to their event

# version 1.5.3 - Mobile Design 

So, In version 1.5.1, I used hostinger's VSP service to host the website, if you are reading this and I forget to tell you in AT4, the link is below.

https://alchemaxdemo.co.uk/ (YES I GOT A DOMAIN TOO, I SET IT UP WRONG ORIGINALLY)

Whilst testing (and getting some friends to test it), one responce that was clear was the mobile format was ugly.

This version just is changes to the .css file to fix this. No real big changes, just additions