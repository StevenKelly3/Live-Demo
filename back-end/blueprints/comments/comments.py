from flask import Blueprint, request, jsonify, make_response, g
import datetime, globals
from decorators import jwt_required, admin_required
from bson import ObjectId

### --- BLUEPRINT SETUP --- ###
comments_bp = Blueprint("comments_bp", __name__)

### --- COLLECTION DETAILS --- ###
users = globals.db.users
groups = globals.db.groups
controlLogs = globals.db.logs 
groupPosts = globals.db.posts
postComments = globals.db.comments

### --- GLOBAL VARIABLES --- ###
missingFormData = "Missing form data, please check that all the fields have been added successfully"
userNotInGroup = "User is not in the group"
invalidDateFormat = "Date format is incorrect, please try again"
postNotFound = "Can not find the post, please try again"
userIsNotCreator = "Unable to do action, user is not a creator"

commentAddedToPostSuccessfully = "Successfully added comment to post"
commentEditedSuccessfully = "Successfully edited comment"
commentDeletedSuccessfully = "Comment Deleted Successfully"

### --- CONNECTION TEST --- ###
def mongo_required():
    try:
        globals.client.admin.command("ping")
        return True, None
    except Exception as e:
        return False, (jsonify({"error": str(e)}), 503)
    

### --- CREATE COMMENT --- ###
'''
    This will allow a user to add a comment to a post.

    To add a comment, the user must be a member of the group

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/add_comment
'''
@comments_bp.route('/api/groups/<group_id>/<post_id>/add_comment', methods = ['POST'])
@jwt_required
def create_comment(user_id, group_id, post_id):
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Verify the user is in the group
        userDetails = users.find_one(
            {"_id" : ObjectId(user_id)},
            {"memberOf" : 1, "ownerOf" : 1}
        )

        userGroups = userDetails.get("memberOf", [])
        ownerGroups = userDetails.get("ownerOf", [])

        if group_id not in userGroups and group_id not in ownerGroups:
            return make_response(jsonify({"error": userNotInGroup}), 403)
        
        # Get the form data
        comment_text = request.form.get("comment_text")

        if not comment_text:
            return make_response(jsonify({"error": missingFormData}), 400)
        
        new_comment = {
            "post_id" : post_id,
            "user_id" : user_id,
            "username" : g.current_username,
            "comment_text" : comment_text,
            "date_posted" : datetime.datetime.now(datetime.UTC)
        }

        result = postComments.insert_one(new_comment)

        # Add to logs
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "Create Comment",
            "Account": g.current_username,
            "Message": commentAddedToPostSuccessfully
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"success": "Comment added", "comment_id": str(result.inserted_id)}), 201)

    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Add comment",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)


### --- EDIT COMMENT --- ###
'''
    This will allow a user to edit their comment
    
    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/<comment_id>/edit

'''
@comments_bp.route('/api/groups/<group_id>/<post_id>/<comment_id>/edit', methods=['PUT'])
@jwt_required
def edit_comment(user_id, group_id, post_id, comment_id):
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Find el comment
        comment = postComments.find_one({"_id": ObjectId(comment_id)})

        if not comment:
            return make_response(jsonify({"error": "Comment not found"}), 404)
        
        # check if user is the comment creator
        if str(comment.get("user_id")) != str(user_id):
            return make_response(jsonify({"error": "User is not the creator"}), 403)
        
        # Get form data
        new_text = request.form.get("comment_text")
        if not new_text:
            return make_response(jsonify({"error": missingFormData}), 400)
        
        postComments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {
                "comment_text": new_text,
                "last_edited": datetime.datetime.now(datetime.UTC)
            }}
        )

        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Edit comment",
            "Account" : g.current_username,
            "Message" : commentEditedSuccessfully
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"success": "Comment updated successfully"}), 200)
    
    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Edit comment",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)


### --- DELETE COMMENT --- ###
'''
    This will allow a user to edit their comment
    
    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/<comment_id>/delete

'''
@comments_bp.route('/api/groups/<group_id>/<post_id>/<comment_id>/delete', methods=['DELETE'])
@jwt_required
def delete_comment(user_id, group_id, post_id, comment_id):
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:

        # Find the comment
        comment = postComments.find_one({"_id": ObjectId(comment_id)})

        if not comment:
            return make_response(jsonify({"error": "Comment not found"}), 404)
        
        # Check if the owner is the creator
        if str(comment.get("user_id")) != str(user_id):
            return make_response(jsonify({"error": userIsNotCreator}), 403)
        
        postComments.delete_one({"_id": ObjectId(comment_id)})

        # Log the deletion
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "Delete Comment",
            "Account": g.current_username,
            "Message": commentDeletedSuccessfully
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({}), 204)


    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Delete comment",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)