from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key

# MongoDB Connection
# client = MongoClient("mongodb+srv://jaiswalsahil283_db_user:Gmail@12@cluster0.wu7p4hk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Change if using MongoDB Atlas
# db = client["student_payments"]
# collection = db["payments"]
client = MongoClient("mongodb+srv://jaiswalsahil283_db_user:Gmail%4012@cluster0.wu7p4hk.mongodb.net/student_payments?retryWrites=true&w=majority")
db = client["student_payments"]
collection = db["payments"]
collection.create_index("utr", unique=True)

# Routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/details", methods=["GET", "POST"])
def details():
    if request.method == "POST":
        name = request.form.get("name")
        regid = request.form.get("regid")
        phone = request.form.get("phone")
        email = 'kumardeepanshu85047@gmail.com'
        sem = request.form.get("sem")
        branch = request.form.get("branch")
        course = request.form.get("course")
        utr = request.form.get("utr")

        if not utr:
            return render_template("details.html", error="Please enter UTR number")

        # Check if UTR already exists
        if collection.find_one({"utr": utr}):
            return render_template("details.html", error="UTR number already used. Please use a different UTR.")

        data = {
            "name": name,
            "regid": regid,
            "phone": phone,
            "email": email,
            "semester": sem,
            "branch": branch,
            "course": course,
            "utr": utr
        }

        try:
            collection.insert_one(data)
            return redirect(url_for('success', final='1'))
        except DuplicateKeyError:
            return render_template("details.html", error='UTR already used. Please use a different UTR.')

    return render_template("details.html")

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         name = request.form.get("name")
#         regid = request.form.get("regid")
#         phone = request.form.get("phone")
#         email = request.form.get("email")
#         sem = request.form.get("sem")
#         branch = request.form.get("branch")
#         course = request.form.get("course")
#         utr = request.form.get("utr")

#         screenshot_file = request.files["screenshot"]
#         screenshot_filename = secure_filename(screenshot_file.filename)
#         screenshot_path = os.path.join(app.config['UPLOAD_FOLDER'], screenshot_filename)
#         screenshot_file.save(screenshot_path)

#         # Save in MongoDB
#         data = {
#             "name": name,
#             "regid": regid,
#             "phone": phone,
#             "email": email,
#             "semester": sem,
#             "branch": branch,
#             "course": course,
#             "utr": utr,
#             "screenshot": screenshot_filename
#         }
#         collection.insert_one(data)

#         return redirect(url_for("success"))

#     return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
