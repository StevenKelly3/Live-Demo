from flask import Blueprint, request, jsonify, make_response, g
import datetime, globals
from decorators import jwt_required, admin_required
from bson import ObjectId

### --- BLUEPRINT SETUP --- ###
posts_bp = Blueprint("posts_bp", __name__)

### --- COLLECTION DETAILS --- ###
users = globals.db.users
groups = globals.db.groups
controlLogs = globals.db.logs 
groupPosts = globals.db.posts
postComments = globals.db.comments

### --- GLOBAL VARIABLES --- ###
missingFormData = "Missing form data, please check that all the fields have been added successfully"
unableToCreatePost = "Unable to create post"
userNotInGroup = "User is not in the group"
invalidDateFormat = "Date format is incorrect, please try again"
postNotFound = "Can not find the post, please try again"
userIsNotCreator = "Unable to do action, user is not a creator"
canNotFindPost = "Unable to find the post"
unableToDeletePost = "Unable to delete post"

postCreatedSuccessfully = "Successfully created the post"
postEditedSuccessfully = "Successfully edited the post"
successfullyDeletedPost = "Post deleted successfully"

### --- CONNECTION TEST --- ###
def mongo_required():
    try:
        globals.client.admin.command("ping")
        return True, None
    except Exception as e:
        return False, (jsonify({"error": str(e)}), 503)

### --- USER HOME PAGE (VIEW ALL POSTS THAT USER IS A PART OF) --- ###
''' This endpoint will pratically act as the users home page, showing all posts from the groups they are in reverse chronological order

    EXAMPLE URL: http://localhost:5000/api/home
'''

# TODO - PAGINATION NEEDS ADDED
@posts_bp.route("/api/home")
@jwt_required
def user_home_page(user_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Get the user details
        userDetails = users.find_one({"_id" : ObjectId(user_id)}, {"memberOf" : 1, "ownerOf" : 1, "username" : 1})

        userGroups = userDetails.get("memberOf", []) # What the member is in
        ownerGroups = userDetails.get("ownerOf", []) # What the user owns
        

        allGroups = list(set(userGroups + ownerGroups))

        # Find the post and sort them in reverse chronological order
        feedCursor = groupPosts.find(
            {"group_id" : {"$in" : allGroups}}
        ).sort("date_posted", -1)

        # Convert the cursor to a list, and format IDs for JSON
        feedPosts = []
        for post in feedCursor:
            post["_id"] = str(post["_id"])

            # Get creators username
            creator_details = users.find_one({"_id": ObjectId(post["creator"])}, {"username": 1})
            post["creator_username"] = creator_details["username"] if creator_details else "Unknown User"


            # Get group name
            group_details = groups.find_one({"_id": ObjectId(post["group_id"])}, {"group_name": 1})
            post["group_name"] = group_details["group_name"] if group_details else "Deleted Group"

            # Convert dates to strings
            if "date_posted" in post:
                post["date_posted"] = post["date_posted"].isoformat()
            if "event_date" in post and post["event_date"]:
                post["event_date"] = post["event_date"].isoformat()

            feedPosts.append(post)

        return make_response(jsonify({"feed" : feedPosts}), 200)

    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "View Home Page",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)

### --- CREATE POST --- ###
@posts_bp.route("/api/create_post", methods = ['POST'])
@jwt_required
def create_post(user_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:

        # Find the user and see what groups 
        userDetails = users.find_one(
            {'_id':ObjectId(user_id)}, # Filter (what to find)
            {'memberOf' : 1, 'ownerOf' : 1, "_id" : 0} # Projection (what to return)    
        )

        userGroups = userDetails.get('memberOf', [])
        ownerGroups = userDetails.get('ownerOf', [])


        # Grab the form data
        groupId = request.form.get("group_id")
        postTitle = request.form.get("post_title")
        eventButtton = request.form.get("event_button") # If "Yes" then event date should appear, if "No" event date shouldn't appear or should be needed. Default state is "No"
        eventDateStr = request.form.get("event_date")
        postMessage = request.form.get("post_message")

        formattedEventDate = None


        # Check if the user is in the group
        if groupId not in userGroups and groupId not in ownerGroups:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Create Post",
                "Account" : g.current_username,
                "Message" : userNotInGroup
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": userNotInGroup}), 404)


        # Check all fields are correct
        if groupId == None:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Create Post",
                "Account" : g.current_username,
                "Message" : missingFormData
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": "A group must be selected"}), 404)
        
        if eventButtton == "Yes":
            if eventDateStr == None:

                # Add to logs
                logsMessage = {
                    "Date/Time" : datetime.datetime.now(datetime.UTC),
                    "Action" : "Create Post",
                    "Account" : g.current_username,
                    "Message" : missingFormData
                }
                controlLogs.insert_one(logsMessage)

                return make_response(jsonify({"error": "Event date must be provided"}), 404)
            
            try:
                formattedEventDate = datetime.datetime.strptime(eventDateStr, '%Y-%m-%d %H:%M')
            except ValueError:

                # Add to logs
                logsMessage = {
                    "Date/Time" : datetime.datetime.now(datetime.UTC),
                    "Action" : "Create Post",
                    "Account" : g.current_username,
                    "Message" : invalidDateFormat
                }
                controlLogs.insert_one(logsMessage)

                return make_response(jsonify({"error" : invalidDateFormat}), 400)
            
        if postTitle == None or postMessage == None:
            return make_response(jsonify({"error": "Post Title or Post Message is missing"}), 404)
        
        finalPost = {
            "group_id" : groupId,
            "post_title" : postTitle,
            "event_button" : eventButtton,
            "event_date" : formattedEventDate,
            "post_message" : postMessage,
            "creator" : user_id,
            "date_posted" : datetime.datetime.now(datetime.UTC)
        }

        postResult = groupPosts.insert_one(finalPost)

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Create Post",
            "Account" : g.current_username,
            "Message" : postCreatedSuccessfully
        }
        postLogResult = controlLogs.insert_one(logsMessage)


        return make_response(jsonify({"success": "Post has been uploaded successfully"}), 201)

    except Exception as e:

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Create Post",
            "Account" : g.current_username,
            "Message" : unableToCreatePost
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)

### --- VIEW ONE POST --- ###
''' This endpoint will allow a user to view one post, that's really it


    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>
'''
@posts_bp.route("/api/groups/<group_id>/<post_id>")
@jwt_required
def view_one_post(user_id, group_id, post_id):
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Get user details
        userDetails = users.find_one({"_id" : ObjectId(user_id)}, {"memberOf" : 1, "ownerOf" : 1})

        userGroups = userDetails.get("memberOf", [])
        ownerGroups = userDetails.get("ownerOf", [])

        if group_id not in userGroups and group_id not in ownerGroups:
            return make_response(jsonify({"error": userNotInGroup}), 403)
        
        # Find post
        post = groupPosts.find_one({
            "_id" : ObjectId(post_id)
        })

        if not post:
            return make_response(jsonify({"error": postNotFound}), 404)
        
        # Get the creator name
        creator_id = post.get("creator")
        creator_details = users.find_one({"_id": ObjectId(post["creator"])}, {"username": 1})
        post["creator_username"] = creator_details["username"] if creator_details else "Unknown User"

        # Get group details
        group_details = groups.find_one({"_id": ObjectId(post["group_id"])}, {"group_name": 1})
        post["group_name"] = group_details["group_name"] if group_details else "Deleted Group"

        # Get comments
        comments_cursor = postComments.find({"post_id" : post_id}).sort("date_posted", -1)

        comments_list = []
        for comment in comments_cursor:
            comment["_id"] = str(comment["_id"])
            if "date_posted" in comment:
                comment["date_posted"] = comment["date_posted"].isoformat()
            comments_list.append(comment)

            post["comments"] = comments_list
        
        # Format for JSON
        post["_id"] = str(post["_id"])
        
        if "date_posted" in post:
            post["date_posted"] = post["date_posted"].isoformat()
        if "event_date" in post and post["event_date"]:
            post["event_date"] = post["event_date"].isoformat()

        return make_response(jsonify(post), 200)
            

    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "View One Post",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)

### --- EDIT POST --- ###
''' This will allow a user to edit the post they created

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/edit_post
'''
@posts_bp.route("/api/groups/<group_id>/<post_id>/edit_post", methods = ['PUT'])
@jwt_required
def edit_post(user_id, group_id, post_id):
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        userDetails = users.find_one({"_id" : ObjectId(user_id)}, {"memberOf" : 1, "ownerOf" : 1})

        userGroups = userDetails.get("memberOf", [])
        ownerGroups = userDetails.get("ownerOf", [])
        
        # Find post
        post = groupPosts.find_one({
            "_id" : ObjectId(post_id),
            "group_id" : group_id
        })

        if not post:
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Edit Post",
                "Account" : g.current_username,
                "Message" : canNotFindPost
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": postNotFound}), 404)

        postCreatorId = post.get('creator')


         # Check if the user is in the group
        if group_id not in userGroups and group_id not in ownerGroups:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Edit Post",
                "Account" : g.current_username,
                "Message" : userNotInGroup
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": "User is not a part of this group"}), 404)


        # Check if the user is the creator
        if str(postCreatorId) != str(user_id):

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Edit Post",
                "Account" : g.current_username,
                "Message" : userIsNotCreator
            }
            controlLogs.insert_one(logsMessage)
            
            return make_response(jsonify({"error": userIsNotCreator}), 403)
        
        # Grab the form data
        postTitle = request.form.get("post_title")
        eventButtton = request.form.get("event_button") # If "Yes" then event date should appear, if "No" event date shouldn't appear or should be needed. Default state is "No"
        eventDateStr = request.form.get("event_date")
        postMessage = request.form.get("post_message")

        formattedEventDate = None

        # Check all fields are correct
        if eventButtton == "Yes":
            if eventDateStr == None:

                # Add to logs
                logsMessage = {
                    "Date/Time" : datetime.datetime.now(datetime.UTC),
                    "Action" : "Edit Post",
                    "Account" : g.current_username,
                    "Message" : missingFormData
                }
                controlLogs.insert_one(logsMessage)

                return make_response(jsonify({"error": "Event date must be provided"}), 404)
            
            try:
                formattedEventDate = datetime.datetime.strptime(eventDateStr, '%Y-%m-%d %H:%M')
            except ValueError:

                # Add to logs
                logsMessage = {
                    "Date/Time" : datetime.datetime.now(datetime.UTC),
                    "Action" : "Edit Post",
                    "Account" : g.current_username,
                    "Message" : invalidDateFormat
                }
                controlLogs.insert_one(logsMessage)

                return make_response(jsonify({"error" : invalidDateFormat}))
            
        if postTitle == None or postMessage == None:
            return make_response(jsonify({"error": "Post Title or Post Message is missing"}), 404)
        
        finalPost = groupPosts.update_one( \
        {"_id" : ObjectId(post_id)}, {
            "$set" : {"group_id" : group_id,
            "post_title" : postTitle,
            "event_button" : eventButtton,
            "event_date" : formattedEventDate,
            "post_message" : postMessage,
          }})

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Edit Post",
            "Account" : g.current_username,
            "Message" : postEditedSuccessfully
        }
        postLogResult = controlLogs.insert_one(logsMessage)


        return make_response(jsonify({"success": "Post has been updated successfully"}), 201)


        
    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Edit post",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503) 

### --- DELETE POST --- ###
''' This will allow a user to delete the post they created

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/delete_post
'''
@posts_bp.route("/api/groups/<group_id>/<post_id>/delete_post", methods = ['DELETE'])
@jwt_required
def delete_post(user_id, group_id, post_id):
    ok, err = mongo_required()
    if not ok:
        return err
    

    try:
        userDetails = users.find_one({"_id" : ObjectId(user_id)}, {"memberOf" : 1, "ownerOf" : 1})

        userGroups = userDetails.get("memberOf", [])
        ownerGroups = userDetails.get("ownerOf", [])
        
        # Find post
        post = groupPosts.find_one({
            "_id" : ObjectId(post_id),
            "group_id" : group_id
        })

        if not post:
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Delete Post",
                "Account" : g.current_username,
                "Message" : canNotFindPost
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": postNotFound}), 404)

        postCreatorId = post.get('creator')


         # Check if the user is in the group
        if group_id not in userGroups and group_id not in ownerGroups:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Delete Post",
                "Account" : g.current_username,
                "Message" : userNotInGroup
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": "User is not a part of this group"}), 404)


        # Check if the user is the creator
        if str(postCreatorId) != str(user_id):

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Delete Post",
                "Account" : g.current_username,
                "Message" : userIsNotCreator
            }
            controlLogs.insert_one(logsMessage)
            
            return make_response(jsonify({"error": userIsNotCreator}), 403)
        
        # Delete the post
        result = groupPosts.delete_one({"_id" : ObjectId(post_id)})
        
        if result.deleted_count == 1:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Delete Post",
                "Account" : g.current_username,
                "Message" : successfullyDeletedPost
            }
            controlLogs.insert_one(logsMessage)

            return make_response( jsonify( { } ), 204 )
        
        else:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Delete Post",
                "Account" : g.current_username,
                "Message" : unableToDeletePost
            }
            controlLogs.insert_one(logsMessage)


            return make_response( jsonify( { "error" : "Invalid business ID" } ), 404)

        
    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Delete post",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)