# from flask import Flask, render_template, request, redirect, url_for, send_file, session
# from pymongo import MongoClient
# from bson import ObjectId
# import gridfs
# import bcrypt

# app = Flask(__name__)
# app.secret_key = 'secret_key' # session management

# client = MongoClient("mongodb://localhost:27017/")
# db = client['testLogin']
# users_collection = db['users']
# fs = gridfs.GridFS(db) # storing images

# @app.route("/")
# def home():
#     if 'username' in session:
#         images = db.fs.files.find()
#         return render_template('home.html', username = session['username'], images = images)

# # Login route
# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = users_collection.find_one({"users": {"$elemMatch": {"username": username}}})

#         if user:
#             for user_data in user['users']:
#                 if user_data['username'] == username:
#                     stored_hashed_password = user_data['password']

#                     if isinstance(stored_hashed_password, str):
#                         stored_hashed_password = stored_hashed_password.encode('utf-8')

#                     if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
#                         return redirect(url_for('home'))

#         return "Invalid credentials, please try again."
    
#     return render_template('login.html')

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # Hash the password
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#         # Insert new user or append to array
#         existing_doc = users_collection.find_one({})  # Assuming there's only one document to hold the array
#         if existing_doc:
#             users_collection.update_one(
#                 {},
#                 {"$push": {"users": {"username": username, "password": hashed_password}}}
#             )
#         else:
#             # Create the document with the array of users if it doesn't exist
#             users_collection.insert_one({
#                 "users": [{"username": username, "password": hashed_password}]
#             })

#         return render_template('register_success.html')

#     return render_template('register.html')

# # Route to upload images
# @app.route("/upload", methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         file = request.files['image']  # Get the uploaded image
#         if file:
#             # Save image to MongoDB using GridFS
#             fs.put(file, filename=file.filename)
#             return redirect(url_for('home'))

#     return render_template('upload.html')

# # Route to serve the uploaded images
# @app.route("/image/<image_id>")
# def image(image_id):
#     gridout = fs.get(ObjectId(image_id))  # Fetch the image from GridFS using its ID
#     return send_file(gridout, mimetype="image/jpeg")

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, send_file, session
from pymongo import MongoClient
import bcrypt
import gridfs
from bson import ObjectId

app = Flask(__name__)
app.secret_key = "secret_key"  # Required for session management

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['testLogin']
users_collection = db['users']  # Collection to store user data
fs = gridfs.GridFS(db)  # GridFS for storing images

@app.route("/")
def home():
    if 'username' in session:
        user = users_collection.find_one({"username": session['username']})
        if user:
            images = user.get('images', [])
        else:
            images = []
        return render_template('home.html', username=session['username'], images=images)
    return render_template('home.html')

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username  # Create session
            return redirect(url_for('home'))
        else:
            return "Invalid credentials. Please try again."
    
    return render_template('login.html')

# Register route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users_collection.insert_one({"username": username, "password": hashed_password, "images": []})
        session['username'] = username  # Create session
        return redirect(url_for('home'))
    
    return render_template('register.html')

# Logout route
@app.route("/logout")
def logout():
    session.pop('username', None)  # Clear session
    return redirect(url_for('home'))

# Upload images (only if logged in)
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        file = request.files['image']  # Get the uploaded image
        if file:
            # Save image to MongoDB using GridFS
            file_id = fs.put(file, filename=file.filename)
            users_collection.update_one({"username": session['username']}, {"$push": {"images": {"filename": file.filename, "file_id": file_id}}})
            return redirect(url_for('home'))

    return render_template('upload.html')

# Route to serve the uploaded images
@app.route("/image/<image_id>")
def image(image_id):
    gridout = fs.get(ObjectId(image_id))  # Fetch the image from GridFS using its ID
    return send_file(gridout, mimetype="image/jpeg")

if __name__ == '__main__':
    app.run(debug=True)
