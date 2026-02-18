''' This blueprint will be used to:
    1) Allow the user to login
    2) Allow users to logout
    3) Register
    4) Delete User
    5) Admin Delete User Account
    6) Create Admin Account with admin logged in 
'''
### --- IMPORTS --- ###
from flask import Blueprint, request, jsonify, make_response, g
import datetime, globals, bcrypt, jwt
from decorators import jwt_required, admin_required
from bson import ObjectId

### --- BLUEPRINT SETUP --- ###
auth_bp = Blueprint("auth_bp", __name__)

### --- COLLECTION DETAILS --- ###
users = globals.db.users # where the user details are stored of course :)
blacklist = globals.db.blacklist # for storing old session tokens when a user logs out
controlLogs = globals.db.logs # for storing detials of what each user did, i.e. user logged in at (time)
auditLogs = globals.db.audit # for storing any issues that happen, i.e. user failed login, giving the exact detail of why


### --- GLOBAL VARIABLES --- ###
'''
    This is basically just for messages that I will be using constantly, i.e. log messages
'''

# TODO - Add more when needed

# Fails
loginFailMessage = "Login unsuccessful, incorrect details entered"
usernameTakenMessage = "Registration fail, username already taken"
passwordsDontMatchMessage = "Registration fail, passwords do not match"
emailInUseMessage = "Registration fail, email already in use"
databaseNotHealthyMessage = "Database is not responding"
logoutFailMessage = "Logout fail"
deleteAccountUnableToFindAccountMessage = "Can not find account"
deleteAccountUnableToDelete = "Error, unable to delete account"


# Success
loginSuccessMessage = "Login successful"
registrationSuccessMessage = "Registration successful"
deleteAccountMessage = "Account successfully deleted"
accountChangesMadeMessage = "Account successfully edited"
databaseHealthyMessage = "Database is ok"
logoutSuccessMessage = "Logout successful"


### --- CONNECTION TEST --- ###
## TODO - This could be done through a blueprint, for the test I won't do it
''' This will check if mongoDB is available before running the rest of the program, this will:
        1) Return True if Mongo is reacable
        2) Return False if there is an error
'''
def mongo_required():
    try:
        globals.client.admin.command("ping")
        return True, None

    except Exception as e:
        return False, (jsonify({"error": str(e)}), 503)
    
@auth_bp.route("/api/database_health", methods = ['GET'])
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


### --- ACCOUNT CREATION --- ###
''' This will allow users to create a new account to use the system

    The following fields will need to be filled:
        1. firstName
        2. lastName
        3. username
        4. email
        5. password
        6. confirmPassword

    EXAMPLE URL: http://localhost:5000/api/register
'''
@auth_bp.route("/api/register", methods=['POST'])
def register():

    # check database health
    ok, err = mongo_required()
    if not ok:
        return err

    try: 
        username = request.form["username"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]
        email = request.form["email"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]

        # check if form data was entered correctly
        if not username or not password or not confirmPassword or not email or not firstName or not lastName:
            return make_response(jsonify({"error": "Missing form data, please check all required fields have been entered"}), 404)
        
        # check if passwords match
        if password != confirmPassword:

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Register new user",
                "Account" : "",
                "Message" : passwordsDontMatchMessage
            }
            result = controlLogs.insert_one(logsMessage)

            # Return Result
            return make_response(jsonify({"error": "Passwords do not match, please check the passwords entered"}), 409)
        
        # check if username already exists
        if users.find_one({'username' : username}):

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Register new user",
                "Account" : "",
                "Message" : usernameTakenMessage
            }
            result = controlLogs.insert_one(logsMessage)

            # Return Result
            return make_response(jsonify({"error" : "username already taken"}), 409)
        
        # check if email is in use
        if users.find_one({'email' : email}):

            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Register new user",
                "Account" : "",
                "Message" : emailInUseMessage
            }
            result = controlLogs.insert_one(logsMessage)

            # Return Result
            return make_response(jsonify({"error" : "Email already in use"}), 409)
        
        # hash the password
        hashed_password = bcrypt.hashpw(
            bytes(password, 'UTF-8'),
            bcrypt.gensalt()
        )

        # Create the new user document and add it to the users collection
        new_user = {
            "firstName" : firstName,
            "lastName" : lastName,
            "username" : username,
            "password" : hashed_password,
            "email" : email,
            "admin" : False,
            "memberOf" : [],
            "ownerOf" : []
        }

        result = users.insert_one(new_user)
        new_user_id = str(result.inserted_id)

        # Add to logs
        logsMessage = {
            "Date/Time" : datetime.datetime.now(datetime.UTC),
            "Action" : "Register new user",
            "Account" : username,
            "Message" : registrationSuccessMessage
        }
        result = controlLogs.insert_one(logsMessage)

        # output OK
        return make_response(jsonify({"message" : "User registered successfully", "user_id": new_user_id}), 201)

    except Exception as e:
        return (jsonify({"error": str(e)}), 503)


### --- USER LOGIN --- ###
''' This will be used to allow a user to login to their account

    EXAMPLE URL: http://localhost:5000/api/login
'''
@auth_bp.route("/api/login", methods=['GET'])
def login():

    # check database health
    ok, err = mongo_required()
    if not ok:
        return err

    try:

        auth = request.authorization

        if auth:
            user = users.find_one( {'username' : auth.username} )

            # create jwt joken, with a 30 minute session token
            if user is not None:
                if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user["password"]):
                    user_id = str(user['_id'])
                    token = jwt.encode( {
                        'user_db_id' : user_id,
                        'user' : auth.username,
                        'admin' : user['admin'],
                        'exp' : datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60)
                        },
                        globals.secret_key,
                        algorithm = "HS256"
                    )

                    # Add to logs
                    logsMessage = {
                        "Date/Time" : datetime.datetime.now(datetime.UTC),
                        "Action" : "Login",
                        "Account" : auth.username,
                        "Message" : loginSuccessMessage
                    }
                    result = controlLogs.insert_one(logsMessage)

                    # Return Result
                    return make_response( jsonify( {'token' : token, "user_id" : user_id}), 200)
                
                # invalid details
                else:

                    # Add to logs
                    logsMessage = {
                        "Date/Time" : datetime.datetime.now(datetime.UTC),
                        "Action" : "Login",
                        "Account" : auth.username,
                        "Message" : loginFailMessage
                    }
                    result = controlLogs.insert_one(logsMessage)

                    # Return Result
                    return make_response( jsonify ( {'message' : 'Invalid username or password'}), 401)
                
            # Add to logs
            logsMessage = {
                "Date/Time" : datetime.datetime.now(datetime.UTC),
                "Action" : "Login",
                "Account" : auth.username,
                "Message" : loginFailMessage
            }
            result = controlLogs.insert_one(logsMessage)

            # Return Result
            return make_response( jsonify( {'message' : 'Invalid username or Password'}), 401)
    
    except Exception as e:
        return (jsonify({"error": str(e)}), 503)
    

### --- LOGOUT --- ###
''' This route will allow users to log out of their accounts.
    This will add their session token to the blacklist collection

    EXAMPLE URL: http://localhost:5000/api/logout
'''
@auth_bp.route('/api/logout', methods=['GET'])
@jwt_required # only logged in users can access this
def logout(user_id):
        
    token = request.headers['x-access-token']
    blacklist.insert_one({"token" : token})

    # Add to logs
    logsMessage = {
        "Date/Time" : datetime.datetime.now(datetime.UTC),
        "Action" : "Login",
        "Account" : g.current_username,
        "Message" : logoutSuccessMessage
    }
    result = controlLogs.insert_one(logsMessage)

    # Return Result
    return make_response(jsonify( {'message' : 'Logout successful'} ), 200)
    
    
### --- DELETE ACCOUNT --- ###
''' 
    This will be used to allow a user to delete their account
    
    The user will need to be logged in to delete their account
    
    A user can not delete another users account
    
    EXAMPLE URL: http://localhost:5000/api/delete_account
'''
@auth_bp.route("/api/delete_account", methods = ['DELETE'])
@jwt_required
def delete_account(user_id):

    ok, err = mongo_required()
    if not ok:
        return err

    # TODO - LOG MESSAGES NEED ADDED, username needs passed from jwt token

    ### -- GET USER TOKEN -- ##
    try:
        user_object_id = ObjectId(user_id)
    except:
        return make_response( jsonify( { "error" : "Invalid token"}), 400)
    
    ## -- DELETE USER -- ##
    try:
        result = users.delete_one(
            {"_id" : ObjectId(user_object_id)},
        )

    except:
        logsMessage = {
                "Date/Time": datetime.datetime.now(datetime.UTC),
                "Action": "Delete Account - Unable to delete",
                "Account": g.current_username, 
                "Message": deleteAccountUnableToDelete
            }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"error" : "Invalid ID format"}), 400)
    
    if result.deleted_count == 1:

        logsMessage = {
                "Date/Time": datetime.datetime.now(datetime.UTC),
                "Action": "Delete Account",
                "Account": g.current_username, 
                "Message": deleteAccountMessage
            }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"message" : "User was deleted"}), 200)
    else:

        logsMessage = {
                "Date/Time": datetime.datetime.now(datetime.UTC),
                "Action": "Delete Account",
                "Account": g.current_username, 
                "Message": deleteAccountUnableToFindAccountMessage
            }
        controlLogs.insert_one(logsMessage)

        return make_response(jsonify({"message" : "Can not find the user"}), 404)