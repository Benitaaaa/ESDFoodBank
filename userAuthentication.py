from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'zhongli'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/user"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CORS(app, supports_credentials=True, resources={r"/logout": {"origins": "*"}, r"*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    __tablename__ = 'users2'

    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.Enum('restaurant', 'foodbank', 'driver'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.user_id

@login_manager.user_loader
def load_user(user_id):
    print('Received user_id:', user_id)
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(user_email=user_email).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'message': 'Logged in successfully', 'user_id': user.user_id})
    else:
        abort(401)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    user_email = data.get('user_email')
    print(user_email)
    user_type = data.get('user_type')
    password = data.get('password')
    username = data.get('username')

    # Check if the user_email or username already exists
    existing_email = User.query.filter_by(user_email=user_email).first()
    existing_username = User.query.filter_by(username=username).first()

    if existing_email or existing_username:
        return jsonify({'message': 'Email or username already exists'}), 409

    # Create a new user
    new_user = User(user_email=user_email, user_type=user_type, username=username)
    new_user.set_password(password)

    # Save the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Log the user in
    login_user(new_user, remember=True)

    return jsonify({'message': 'User created successfully', 'user_id': new_user.user_id}), 201

@app.route('/logout')
@login_required
def logout():
    print('masuk sini')
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/protected')
@login_required
def protected():
    return jsonify({'message': 'Welcome, user!', 'user_id': current_user.id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
