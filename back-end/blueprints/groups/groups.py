from flask import Blueprint, request, jsonify, make_response, g
import datetime, globals
from decorators import jwt_required, admin_required
from bson import ObjectId

### --- BLUEPRINT SETUP --- ###
groups_bp = Blueprint("groups_bp", __name__)

### --- COLLECTION DETAILS --- ###
users = globals.db.users
groups = globals.db.groups
controlLogs = globals.db.logs 
groupPosts = globals.db.posts 

### --- GLOBAL VARIABLES --- ###
databaseNotHealthyMessage = "Database is not responding"
missingFormData = "Missing form data, please check that all the fields have been added successfully"
invalidLocation = "Location must be a string"
userAlreadyInGroup = "Failed to join group, user is already apart of the group"
userAlreadySentRequestToJoin = "Failed to send request, user has already sent a request to join"
joinGroupFail = "Unable to join group"
requestToJoinAcceptedFail = "Failed to accept request to join"
requestToJoinRejectedFail = "Failed to reject"
leaveGroupFail = "Unable to leave group"
userNotInGroup = "User is not in the group"
groupNotFound = "Unable to find the group"
userIsNotCreator = "Unable to do action, user is not a creator"


databaseHealthyMessage = "Database is ok"
groupCreatedSuccessfully = "Group successfully created"
joinedGroupSuccessfully = "Group joined successfully"
requestToJoinSuccessfullySent = "Request to join sent successfully"
requestToJoinAccepted = "Request to join accepted successfully"
requestToJoinRejected = "Successfully rejected user"
leaveGroupSuccessfully = "Successfully left group"
groupUpdatedSuccessfully = "Successfully updates group"
groupDeletedSuccessfully = "Successfully deleted group and all related documents"

### --- CONNECTION TEST --- ###
def mongo_required():
    try:
        globals.client.admin.command("ping")
        return True, None
    except Exception as e:
        return False, (jsonify({"error": str(e)}), 503)
    
@groups_bp.route("/api/database_health", methods = ['GET'])
def database_health():
    ok, err = mongo_required()
    if not ok:
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Database Health Check",
            "Account" : "",
            "Message" : databaseNotHealthyMessage
        }
        result = controlLogs.insert_one(logsMessage)
        return err
    
    logsMessage = {
        "Date/Time" : datetime.datetime.now(datetime.UTC),
        "Action" : "Database Health Check",
        "Account" : "",
        "Message" : databaseHealthyMessage
    }
    result = controlLogs.insert_one(logsMessage)
    return (jsonify({"OK": True}), 200)

### --- CREATE GROUP --- ###
''' This will be used to allow the user to create their own group.
    A group, essentially is just an area where users can interact with other users who have simular interests to them.
    Each group created will have to fill in the following:
        1. Category (i.e. sim racing, social club, football association, etc.)
        2. Location (optional field)
        3. Access (public or private)
        4. Description (whatever the user wants)
        5. Name
    
    EXAMPLE URL: http://localhost:5000/api/create_group
'''
@groups_bp.route("/api/create_group", methods = ['POST'])
@jwt_required
def create_group(user_id):

    ok, err = mongo_required()
    if not ok:
        return err

    try:
        groupName = request.form["groupName"]
        groupLocation = request.form["groupLocation"]
        groupCategory = request.form["groupCategory"]
        groupDescription = request.form["groupDescription"]
        groupAccess = request.form['groupAccess'] # public or private

        # Check if any from data is missing, remember location isn't needed as some users might run online stuff like sim racing
        if not groupName or not groupCategory or not groupDescription or not groupAccess:
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Create Group",
                "Account" : g.current_username,
                "Message" : missingFormData
            }
            result = controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error" : "Missing form data"}), 404)
        

        new_group = {
            "group_name" : groupName,
            "category" : groupCategory,
            "description" : groupDescription,
            "location" : groupLocation,
            "group_access" : groupAccess,
            "group_owner" : user_id,
            "requests" : []
        }

        # Add group to group collection
        new_group_id = groups.insert_one(new_group)

        # Update user document to contain the new group id
        users.update_one(
            {"_id" : ObjectId(user_id)},
            {"$push" : {"ownerOf" : str(new_group_id.inserted_id)}}
        )

        # NOTE - This will only work once the "view group" endpoint is added
        new_group_url = "http://localhost:5000/api/groups/" + str(new_group_id.inserted_id)

        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "Create Group",
           "Account": g.current_username, 
            "Message": groupCreatedSuccessfully
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"message" : "Group was created " + new_group_url}), 201)
         


    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 503)


### --- JOIN GROUP --- ###
''' THis will allow users to join a group

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/join
'''
@groups_bp.route("/api/<string:group_id>/join", methods=['PUT'])
@jwt_required
def join_group(user_id, group_id):

    ok, err = mongo_required()
    if not ok:
        return err

    # Find group
    try:
        # Get groups "group_access"
        group_access = groups.find_one(
            {'_id':ObjectId(group_id)}, # Filter (what to find)
            {'group_access': 1} # Projection (what to return)
            )
        
        # Get groups "requests" NOTE - I know this is an added step, but it just makes it easier
        groupRequests = groups.find_one(
            {'_id':ObjectId(group_id)}, # Filter (what to find)
            {'requests': 1, "_id" : 0} # Projection (what to return)
            )
        
        # Find the current user
        current_user = users.find_one(
            {'username':g.current_username},
            {"memberOf" : 1, '_id' : 1}
        )

        # Get the users current groups so we can update the list
        userGroups = current_user.get('memberOf', [])

        # Check if the user is already apart of the group
        if group_id not in userGroups:

            # Check if group is public or private
            if group_access.get("group_access") == "Public":
                

                userGroups.append(group_id)

                # Add user to the group
                result = users.update_one(
                    {"_id" : ObjectId(user_id)}, {
                        "$set" : {"memberOf" : userGroups}
                    }
                )

                if result.matched_count == 1:

                    # Add to logs
                    logsMessage = {
                        "Date/Time" : datetime.datetime.now(datetime.UTC),
                        "Action" : "Join Group",
                        "Account" : g.current_username,
                        "Message" : joinedGroupSuccessfully
                    }
                    logResult = controlLogs.insert_one(logsMessage)

                    return make_response ( jsonify( { "Success" : "Joined Group"} ), 200)
            
            # If the group is private
            else:
                userRequest = groupRequests.get('requests')

                # Check fi the user has already sent a request
                if user_id not in userRequest:
                    userRequest.append(user_id)
                
                else:
                    # Add to logs
                    logsMessage = {
                        "Date/Time" : datetime.datetime.now(datetime.UTC),
                        "Action" : "Join Group",
                        "Account" : g.current_username,
                        "Message" : userAlreadySentRequestToJoin
                    }
                    logResult = controlLogs.insert_one(logsMessage)

                    return make_response ( jsonify( { "error" : "User has already sent a join request" } ), 404)


                result = groups.update_one(
                    {"_id" : ObjectId(group_id)}, {
                        "$set" : {"requests" : userRequest}
                    }
                )

                # Add to logs
                logsMessage = {
                    "Date/Time" : datetime.datetime.now(datetime.UTC),
                    "Action" : "Join Group",
                    "Account" : g.current_username,
                    "Message" : requestToJoinSuccessfullySent
                }
                logResult = controlLogs.insert_one(logsMessage)

                return make_response ( jsonify( { "Success" : "Requested to join group"} ), 200)

          
        else:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Join Group",
                "Account" : g.current_username,
                "Message" : userAlreadyInGroup
            }
            logResult = controlLogs.insert_one(logsMessage)

            return make_response ( jsonify( { "error" : "User is already apart of this group" } ), 404)
        
        
    except:

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Join Group",
            "Account" : g.current_username,
            "Message" : joinGroupFail
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error" : "Can not find/join the group"}), 404)
    
### --- SEE USER REQUEST --- ###
''' This will essentially allow the owner of the group to see who has requested to join

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/requests_to_join
'''
@groups_bp.route("/api/groups/<group_id>/requests_to_join", methods = ['GET'])
@jwt_required
def requests_to_join(user_id, group_id):

    ok, err = mongo_required()
    if not ok:
        return err

    # Find out who the group owner is
    groupDetails = groups.find_one(
        {'_id':ObjectId(group_id)}, # Filter (what to find)
        {'group_owner': 1, "requests" : 1, "_id" : 0} # Projection (what to return)    
    )

    groupOwnerId = groupDetails.get("group_owner")

    # Compares the current user_id to the groupOwnerId
    if user_id not in groupOwnerId:
        return make_response(jsonify({"error" : "Unauthorised Access"}), 401)
    
    try:
        # Get the requests to join the group
        groupRequests = groupDetails.get("requests")

        object_ids = [ObjectId(rid) for rid in groupRequests]

        # Find all users who ID is in the request list
        requesting_users = users.find(
            {"_id": {"$in": object_ids}}, 
            {"username": 1}
        )

        data = []
        for user in requesting_users:
            data.append({
                "user_id": str(user["_id"]),
                "username": user["username"]
            })
            
        return jsonify(data), 200
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 503)
    
### --- ACCEPT/REJECT USER REQUESTS --- ###
''' This will allow a group owner to accept or reject a users request to join.

    If accepted, the request will be removed from the requests array in the groups collection,
    and the users "memberOf" array will be updated

    If rejected, the request will be removed

    This will have two endpoints, I just don't wanna type another whole header and description

    EXAMPLE URL ACCEPTED: http://localhost:5000/api/groups/<group_id>/requests_to_join/<request_id>/accepted

    EXAMPLE URL REJECTED: http://localhost:5000/api/groups/<group_id>/requests_to_join/<request_id>/rejected
'''

## ACCEPTED ##
@groups_bp.route("/api/groups/<group_id>/requests_to_join/<request_id>/accepted", methods = ['PUT'])
@jwt_required
def join_request_accepted(user_id, group_id, request_id):
    
    ok, err = mongo_required()
    if not ok:
        return err
    
    # Variables
    selectedUser = None
    
     # Find out who the group owner is
    groupDetails = groups.find_one(
        {'_id':ObjectId(group_id)}, # Filter (what to find)
        {'group_owner': 1, "requests" : 1, "_id" : 0} # Projection (what to return)    
    )

    groupOwnerId = groupDetails.get("group_owner")

    # Compares the current user_id to the groupOwnerId
    if user_id not in groupOwnerId:
        return make_response(jsonify({"error" : "Unauthorised Access"}), 401)
    
    try:

        # Get the requests to join the group
        groupRequests = groupDetails.get("requests")

        # Check if request id matches the url
        for request in groupRequests:
            if request == request_id:
                selectedUser = request

        #if selectedUser != request_id: 
        #    return make_response ( jsonify( { "error" : "Can not find user request" } ), 404)
        
        # Add user to group
        userResult = users.update_one(
            {"_id" : ObjectId(selectedUser)}, {
                "$push" : {"memberOf" : group_id}
            }
        )

        # Remove request
        groupRequests.remove(selectedUser)
        
        groupResult = groups.update_one(
            {"_id" : ObjectId(group_id)}, {
                "$set" : {"requests" : groupRequests}
            }
        )

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Join Group",
            "Account" : g.current_username,
            "Message" : requestToJoinAccepted
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"Success": "Request to join accepted"}), 201)


    except Exception as e:

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Join Group",
            "Account" : g.current_username,
            "Message" : requestToJoinAcceptedFail
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)
    
## REJECTED ##
@groups_bp.route("/api/groups/<group_id>/requests_to_join/<request_id>/rejected", methods = ['PUT'])
@jwt_required
def join_request_rejected(user_id, group_id, request_id):
    
    ok, err = mongo_required()
    if not ok:
        return err
    
    # Variables
    selectedUser = None
    
     # Find out who the group owner is
    groupDetails = groups.find_one(
        {'_id':ObjectId(group_id)}, # Filter (what to find)
        {'group_owner': 1, "requests" : 1, "_id" : 0} # Projection (what to return)    
    )

    groupOwnerId = groupDetails.get("group_owner")

    # Compares the current user_id to the groupOwnerId
    if user_id not in groupOwnerId:
        return make_response(jsonify({"error" : "Unauthorised Access"}), 401)
    
    try:

        # Get the requests to join the group
        groupRequests = groupDetails.get("requests")

        # Check if request id matches the url
        for request in groupRequests:
            if request == request_id:
                selectedUser = request

        # Remove request
        groupRequests.remove(selectedUser)
        
        groupResult = groups.update_one(
            {"_id" : ObjectId(group_id)}, {
                "$set" : {"requests" : groupRequests}
            }
        )


        ## TODO FIX
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Join Group",
            "Account" : g.current_username,
            "Message" : requestToJoinRejected
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"Success": "User has been rejected"}), 201)


    except Exception as e:

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Join Group",
            "Account" : g.current_username,
            "Message" : requestToJoinRejectedFail
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)
    
### --- LEAVE GROUP --- ###
''' This will allow a user to leave a group they are in.

    To keep things simple (mostly just to avoid bugs where owners accept a user right as the user removes their request), users will not be allowed to remove their request to join

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/leave
'''
@groups_bp.route("/api/groups/<group_id>/leave", methods = ['PUT'])
@jwt_required
def leave_group(user_id, group_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
    
        # Find the user
        userDetails = users.find_one(
            {'_id':ObjectId(user_id)}, # Filter (what to find)
            {'memberOf' : 1, "_id" : 0} # Projection (what to return)    
        )

        # Grab the memberOf data
        userGroups = userDetails.get("memberOf")

        for group in userGroups:
            if group == group_id:
                # Remove group

                result = userGroups.remove(group)

                groupResult = users.update_one(
                {"_id" : ObjectId(user_id)}, {
                    "$set" : {"memberOf" : userGroups}
                })

                # Add to logs
                logsMessage = {
                    "Date/Time" : datetime.datetime.now(datetime.UTC),
                    "Action" : "Leave Group",
                    "Account" : g.current_username,
                    "Message" : leaveGroupSuccessfully
                }
                result = controlLogs.insert_one(logsMessage)

                return make_response(jsonify({"Success": "Successfully left group"}), 201)
        

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Leave Group",
            "Account" : g.current_username,
            "Message" : leaveGroupFail
        }
        result = controlLogs.insert_one(logsMessage)
        return make_response(jsonify({"Error": "Can not find the group"}), 404)




    except Exception as e:

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Leave Group",
            "Account" : g.current_username,
            "Message" : leaveGroupFail
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)
    

### --- CREATE POST / VIEW USER GROUPS LIST --- ###
''' This allows a user to create a post for their group, they select the group when they are creating it

    To do this, it requires two endpoints
        1) Return list of groups the user is in (this could be used for other features)
        2) A way to submit the post

    EXAMPLE URL SUBMIT: http://localhost:5000/api/get_user_groups
    
    EXAMPLE URL SUBMIT: http://localhost:5000/api/create_post
'''

## GET GROUPS THE USER IS IN ##
@groups_bp.route("/api/get_user_groups")
@jwt_required
def get_user_groups(user_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:

        # Pipeline
        pipeline = [
            # Find the user
            {"$match" : {"_id" : ObjectId(user_id)}},

            # Join the groups collection using a left outer join
            {
                "$lookup": {
                    "from" : "groups",
                    "let" : {"user_member_list" : "$memberOf"},
                    "pipeline" : [
                        {
                            "$match" : {
                                "$expr" : {
                                    "$in" : [
                                        {"$toString" : "$_id"}, # converts Group ID to string
                                        "$$user_member_list" # Check if it's in your list
                                    ]
                                }
                            }
                        }
                    ],
                    "as" : "user_groups"
                }
            },

            # Join for owner list
            {
                "$lookup" : {
                    "from" : "groups",
                    "let" : {"owner_list" : "$ownerOf"},
                    "pipeline" : [
                        {"$match" : {"$expr" : {"$in" : [{"$toString" : "$_id"}, "$$owner_list"]}}}
                    ],
                    "as" : "owner_group_details"
                }
            },

            # Projection
            {"$project" : {
                "_id" : 0,
                "joined_groups" : {
                    "$map" : {
                        "input" : "$user_groups",
                        "as" : "g",
                        "in" : {
                            "_id" : { "$toString" : "$$g._id"},
                            "group_name" : "$$g.group_name"
                        }
                    }
                },
                "owned_groups" : {
                    "$map" : {
                        "input" : "$owner_group_details",
                        "as" : "g",
                        "in" : {
                            "_id" : { "$toString" : "$$g._id"},
                            "group_name" : "$$g.group_name"
                        }
                    }
                }
            }}
        ]

        result = list(users.aggregate(pipeline))

        # If the user exists grab the array; otherwise empty list
        if result:
            output = {
                "joined_groups" : result[0].get("joined_groups", []),
                "owned_groups" : result[0].get("owned_groups", [])
            }

        else:
            output = {"joined": [], "owned": []}

        return make_response(jsonify(output), 200)
        
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 503)
    

### --- GROUP HOME PAGE (SEE ALL POSTS THAT THE GROUP HAS UPLOADED) --- ###
''' This endpoint will pratically act as the groups home page, showing all posts from the group in reverse chronological order

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>
'''

# TODO - PAGINATION NEEDS ADDED
@groups_bp.route("/api/groups/<group_id>")
@jwt_required
def group_page(user_id, group_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Get the user details
        userDetails = users.find_one({"_id" : ObjectId(user_id)}, {"memberOf" : 1, "ownerOf" : 1})

        userGroups = userDetails.get("memberOf", []) # What the member is in
        ownerGroups = userDetails.get("ownerOf", []) # What the user owns

        if group_id not in userGroups and group_id not in ownerGroups:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "View Group Page",
                "Account" : g.current_username,
                "Message" : userNotInGroup
            }
            controlLogs.insert_one(logsMessage)

            return make_response(jsonify({"error": "User is not a part of this group"}), 404)


        # Find the post and sort them in reverse chronological order
        feedCursor = groupPosts.find(
            {"group_id" : group_id}
        ).sort("date_posted", -1)

        # Convert the cursor to a list, and format IDs for JSON
        feedPosts = []
        for post in feedCursor:
            post["_id"] = str(post["_id"])

            # Get post creator names
            creator_details = users.find_one({"_id": ObjectId(post["creator"])}, {"username": 1})
            post["creator_username"] = creator_details["username"] if creator_details else "Unknown"

            # Convert dates to strings
            if "date_posted" in post:
                post["date_posted"] = post["date_posted"].isoformat()
            if "event_date" in post and post["event_date"]:
                post["event_date"] = post["event_date"].isoformat()

            feedPosts.append(post)

        
        # Get the group details
        groupDetails = groups.find_one({"_id" : ObjectId(group_id)}, {"group_name": 1, "description": 1, "category": 1, "location": 1, "group_owner" : 1})

        if not groupDetails:
            return make_response(jsonify({"error" : groupNotFound}), 404)
        
        # set the _id to a string
        groupDetails["_id"] = str(groupDetails["_id"])

        # Combine feed and group details
        groupDetails["feed"] = feedPosts


        return make_response(jsonify(groupDetails), 200)

    
    except Exception as e:

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "View Group Page",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        result = controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)

### --- EDIT GROUP --- ###
''' This will allow a user to edit the post they created

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/settings/edit_group
'''
@groups_bp.route("/api/groups/<group_id>/settings/edit_group", methods = ['PUT'])
@jwt_required
def edit_group(user_id, group_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Find the groups details
        groupDetails = groups.find_one({"_id" : ObjectId(group_id)})

        if not groupDetails:
            return make_response(jsonify({"error" : groupNotFound}), 404)
        
        # Check if the user is the owner
        if str(groupDetails.get("group_owner")) != str(user_id):

            logsMessage = {
                "Date/Time": datetime.datetime.now(datetime.UTC),
                "Action": "Edit Group",
                "Account": g.current_username,
                "Message": userIsNotCreator
            }
            controlLogs.insert_one(logsMessage)
            return make_response(jsonify({"error": "Unauthorized: Only the owner can edit the group"}), 403)
        
        # Grab the form data with the updates
        groupName = request.form.get("groupName")
        groupLocation = request.form.get("groupLocation")
        groupCategory = request.form.get("groupCategory")
        groupDescription = request.form.get("groupDescription")
        groupAccess = request.form.get("groupAccess")

        if not groupName or not groupCategory or not groupDescription or not groupAccess:
            return make_response(jsonify({"error": missingFormData}), 400)
        
        # Update the group document
        groups.update_one(
            {"_id" : ObjectId(group_id)},
            {
                "$set" : {
                    "group_name" : groupName,
                    "location" : groupLocation,
                    "category" : groupCategory,
                    "description" : groupDescription,
                    "group_access" : groupAccess
                }
            }
        )

        # Add to logs
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "Edit Group",
            "Account": g.current_username,
            "Message": groupUpdatedSuccessfully
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"success": "Group updated successfully"}), 200)


    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Edit Group",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)


        return make_response(jsonify({"error": str(e)}), 503) 
    

    
### --- DELETE GROUP --- ###
''' This allows a group owner to delete their group.

    To do this, firstly each user will need to be removed from the group to ensure no one can upload while the group is being deleted

    Secondly all posts need to be removed doesn't matter who posted it

    Lastly, the group need to be removed

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/settings/delete_group
'''
@groups_bp.route("/api/groups/<group_id>/settings/delete_group", methods = ['DELETE'])
@jwt_required
def delete_group(user_id, group_id):
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Get the group details
        groupDetails = groups.find_one({"_id" : ObjectId(group_id)})
        if not groupDetails:
            return make_response(jsonify({"error": "Group not found"}), 404)
        
        # Check if the user is the owner
        if str(groupDetails.get("group_owner")) != str(user_id):
            return make_response(jsonify({"error": "Unauthorized Access"}), 403)
        
        # Remove the users from the group by removing the group_id from each user
        users.update_many(
            {"memberOf" : group_id},
            {"$pull" : {"memberOf" : group_id}}
        )

        # Remove the group id from the owners 'ownerOf' array in the users collection
        users.update_one(
            {"_id" : ObjectId(user_id)},
            {"$pull" : {"ownerOf" : group_id}}
        )

        # Remove all posts associated with this group
        groupPosts.delete_many({"group_id" : group_id})

        # Delete group - FINAL STEP
        groups.delete_one({"_id" : ObjectId(group_id)})

        # Add to logs
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "Delete Group",
            "Account": g.current_username,
            "Message": groupDeletedSuccessfully
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"success": "Group and all associated data deleted successfully"}), 200)

    
    except Exception as e:
        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Delete Group",
            "Account" : g.current_username,
            "Message" : str(e)
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error": str(e)}), 503)
    
### --- SEARCH FOR GROUP (BY NAME)--- ###
''' This will allow a user to search for a group

    Users will have to pass the group_name in the <group_name> field

    EXAMPLE URL: http://localhost:5000/api/search_for_groups/group_name/<group_name>
'''
@groups_bp.route("/api/search_for_groups/group_name/<group_name>")
@jwt_required
def search_by_name(user_id, group_name):

    ## -- PAGINATION SETUP -- ##
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num -1))
    
    # Regex check
    '''        
        In matching_recipes we find:
            1) $regex - This is mongoDBs' operator for regular expression matching, it calls regex_pattern to get that.
            2) $options : 'i' - This makes the match case sensitive, so chr, CHR, and Chr all match say "Christmas".        
    '''
    regex_pattern = group_name

    # Projection
    projection = {'group_name' : 1,
                  'category' : 1,
                  'description' : 1,
                  'location' : 1,
                  'group_access' : 1}
    
    matching_groups = groups.find( { 'group_name' : { '$regex' : regex_pattern, '$options' : 'i'}}, projection)

    data_to_return = []

    for group in matching_groups.skip(page_start).limit(page_size):
        group['_id'] = str(group['_id'])
        group['url'] = "http://localhost:5000/api/groups/" + group['_id']

        data_to_return.append(group)

    if data_to_return:
        return make_response (jsonify (data_to_return), 200)
    else:
        return make_response (jsonify ( {"error" : f"No groups found with the name: {group_name}"}), 404)
    
    
### --- SEARCH FOR GROUP (BY CATEGORY)--- ###
''' This will allow a user to search for a group by category

    Users will have to pass the category in the <category> field

    EXAMPLE URL: http://localhost:5000/api/search_for_groups/category/<category>
'''
@groups_bp.route("/api/search_for_groups/category/<category>")
@jwt_required
def search_by_category(user_id, category):

    ## -- PAGINATION SETUP -- ##
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num -1))
    
    # Regex check
    '''        
        In matching_recipes we find:
            1) $regex - This is mongoDBs' operator for regular expression matching, it calls regex_pattern to get that.
            2) $options : 'i' - This makes the match case sensitive, so chr, CHR, and Chr all match say "Christmas".        
    '''
    regex_pattern = category

    # Projection
    projection = {'group_name' : 1,
                  'category' : 1,
                  'description' : 1,
                  'location' : 1,
                  'group_access' : 1}
    
    matching_groups = groups.find( { 'category' : { '$regex' : regex_pattern, '$options' : 'i'}}, projection)

    data_to_return = []

    for group in matching_groups.skip(page_start).limit(page_size):
        group['_id'] = str(group['_id'])
        group['url'] = "http://localhost:5000/api/groups/" + group['_id']

        data_to_return.append(group)

    if data_to_return:
        return make_response (jsonify (data_to_return), 200)
    else:
        return make_response (jsonify ( {"error" : f"No groups found with the category: {category}"}), 404)
    