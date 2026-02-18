''' This is the decorator used for handling authentication'''

### --- IMPORTS --- ###
from flask import request, jsonify, make_response, g
import jwt
from functools import wraps
import globals

blacklist = globals.db.blacklist 

### --- JWT REQUIRED DECORATOR --- ###
def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        #token = request.args.get('token')
        token = None
        '''if not token:
            return make_response(jsonify(
                {'message' : 'Token is missing'}), 401)'''
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if blacklist.find_one({"token": token}):
            return make_response(jsonify({'message': 'Token has been revoked. Please log in again.'}), 401)
        
        try:
            data = jwt.decode(token,
                              globals.secret_key,
                              algorithms="HS256")
            
            # grab username for log reasons (possibly more who knows, early development, watch me forget to remove this)
            g.current_username = data['user']

        except:
            return make_response(jsonify (
                {'message' : 'Token is invalid' }), 401)
        
        user_id_str = data.get("user_db_id")

        if not user_id_str:
            return make_response(jsonify({"message" : "Token missing user ID"}), 401)
        kwargs["user_id"] = user_id_str

        return func(*args, **kwargs)
    
    return jwt_required_wrapper

### --- ADMIN REQUIRED --- ###
def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = jwt.decode( token, globals.secret_key, algorithms="HS256")
        if data["admin"]:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify ( { 'message' : 'Admin access required'}), 401)
    return admin_required_wrapper