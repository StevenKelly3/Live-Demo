### --- IMPORTS --- ###
from flask import Blueprint, request, jsonify, make_response, g
from bson.objectid import ObjectId
import globals, datetime
from decorators import jwt_required

calendar_bp = Blueprint('calendar', __name__)

### --- COLLECTION DETAILS --- ###
users = globals.db.users
groups = globals.db.groups
controlLogs = globals.db.logs 
groupPosts = globals.db.posts
postComments = globals.db.comments

### --- GLOBAL VARIABLES --- ###
mongoError = "Service Unavailable: Database connection failed"
alreadyRSVPd = "User has already RSVP'd to this event"
rsvpSuccess = "Successfully RSVP'd to the event"
postNotFound = "Unable to find the post"
notAnEvent = "RSVP failed: This post is not marked as an event"
userIsNotCreator = "Unable to do action, user is not a creator"

### --- CONNECTION TEST --- ###
def mongo_required():
    try:
        globals.client.admin.command("ping")
        return True, None
    except Exception as e:
        return False, (jsonify({"error": str(e)}), 503)

### --- RSVP EVENT --- ###
''' 
    This will allow a user to RSVP to an event. 

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/rsvp
'''
@calendar_bp.route("/api/groups/<group_id>/<post_id>/rsvp", methods=['PUT'])
@jwt_required
def rsvp_event(user_id, group_id, post_id):
    
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Check that the post exists
        p_id = ObjectId(post_id)
        u_id = ObjectId(user_id)

        post = groupPosts.find_one({"_id": p_id, "group_id" : group_id})

        if not post:
            return make_response(jsonify({"error": postNotFound}), 404)
        
        # Check if the post in an event
        if post.get("event_button") != "Yes":
            return make_response(jsonify({"error": notAnEvent}), 400)
        
        # Check for duplicate RSVP
        if user_id in post.get("attendees", []):
            return make_response(jsonify({"message": alreadyRSVPd}), 409)
        
        # Update user and post document
        groupPosts.update_one(
            {"_id": ObjectId(p_id)},
            {"$addToSet": {"attendees": user_id}}
        )

        users.update_one(
            {"_id": ObjectId(u_id)},
            {"$addToSet": {"my_events": post_id}}
        )

        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "RSVP Event",
            "Account": g.current_username,
            "Message": f"User {g.current_username} RSVP'd to post {post_id}"
        }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"success": rsvpSuccess}), 200)

    except Exception as e:
        # Log the crash
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "RSVP Event",
            "Account": g.current_username,
            "Message": str(e)
        }
        controlLogs.insert_one(logsMessage)
        return make_response(jsonify({"error": str(e)}), 503)
    
### --- SEE ATTENDEES --- ###
'''
    Allows the post creator to see a list of the usernames attending the event

    EXAMPLE URL: http://localhost:5000/api/groups/<group_id>/<post_id>/attendees
'''
@calendar_bp.route("/api/groups/<group_id>/<post_id>/attendees", methods=['GET'])
@jwt_required
def view_attendees(user_id, group_id, post_id):

    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Find the post
        post = groupPosts.find_one({"_id": ObjectId(post_id), "group_id": group_id})

        if not post:
            return make_response(jsonify({"error": postNotFound}), 404)
        
        # See if the user is the creator of the post
        if str(post.get("creator")) != str(user_id):
            return make_response(jsonify({"error": userIsNotCreator}), 403)
        
        # Get the attendees ID's
        attendee_ids = post.get("attendees", [])

        if not attendee_ids:
            return make_response(jsonify({"attendees": [], "count": 0}), 200)
        
        obj_ids = [ObjectId(id_str) for id_str in attendee_ids]

        attendee_details = users.find(
            {"_id": {"$in": obj_ids}},
            {"username": 1, "_id": 0}
        ) # To get the username, because who is gonna know who is who when who is a number and not a username

        attendee_list = [u['username'] for u in attendee_details]

        return make_response(jsonify({
            "event_title": post.get("post_title"),
            "count": len(attendee_list),
            "attendees": attendee_list
        }), 200)

    except Exception as e:
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "View Attendees",
            "Account": g.current_username,
            "Message": str(e)
        }
        controlLogs.insert_one(logsMessage)
        return make_response(jsonify({"error": str(e)}), 503)
    

### --- VIEW USER CALENDAR --- ###
'''
    Allows a user to see all events that they rsvp'd to.
    
    If an event occurred before the current date, it will not be returned

    EXAMPLE URL: http://localhost:5000/api/my_calendar
'''
@calendar_bp.route("/api/my_calendar", methods=['GET'])
@jwt_required
def view_my_calendar(user_id):
    
    ok, err = mongo_required()
    if not ok:
        return err
    
    try:
        # Get the user's list of events
        user = users.find_one({"_id": ObjectId(user_id)}, {"my_events": 1})

        if not user or "my_events" not in user:
            return make_response(jsonify({"calendar": []}), 200)
        
        # Get the event _id from the user list
        event_ids = [ObjectId(eid) for eid in user.get("my_events", [])]

        # Get midnight time (start_of_today)
        now = datetime.datetime.now(datetime.UTC)
        start_of_today = datetime.datetime(now.year, now.month, now.day)

        # Find posts that are in the user's list and are scheduled for today or later
        calendar_cursor = groupPosts.find({
            "_id": {"$in": event_ids},
            "event_date": {"$gte": start_of_today}
        }).sort("event_date", 1)

        my_calendar = []
        for event in calendar_cursor:
            event["_id"] = str(event["_id"])

            # Get the creator and group name
            creator = users.find_one({"_id": ObjectId(event["creator"])}, {"username": 1})
            group = groups.find_one({"_id": ObjectId(event["group_id"])}, {"group_name": 1})
            
            event["creator_username"] = creator["username"] if creator else "Unknown"
            event["group_name"] = group["group_name"] if group else "Deleted Group"

            # Format dates to ISO strings
            if event.get("event_date"):
                event["event_date"] = event["event_date"].isoformat()
            if event.get("date_posted"):
                event["date_posted"] = event["date_posted"].isoformat()

            my_calendar.append(event)

        return make_response(jsonify({"calendar": my_calendar}), 200)

    
    except Exception as e:
        logsMessage = {
            "Date/Time": datetime.datetime.now(datetime.UTC),
            "Action": "View My Calendar Error",
            "Account": g.current_username,
            "Message": str(e)
        }
        controlLogs.insert_one(logsMessage)
        return make_response(jsonify({"error": str(e)}), 503)