
''' This is the main part of the application, responsible for running the flask application and the blueprints.

'''
### --- IMPROTS --- ###
from flask import Flask
from blueprints.auth.auth import auth_bp
from blueprints.groups.groups import groups_bp
from blueprints.posts.posts import posts_bp
from blueprints.comments.comments import comments_bp
from blueprints.calendar.calendar import calendar_bp
from flask_cors import CORS

### --- FLASK APPLICATION AND BLUEPRINTS --- ###
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:4200", "https://alchemaxdemo.co.uk"]}},
          allow_headers=["Authorization", "Content-Type", "x-access-token"])
app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(calendar_bp)


if __name__ == "__main__":
    app.run(debug=True)