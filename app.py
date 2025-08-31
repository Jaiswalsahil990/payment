from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import os

app = Flask(__name__)

# Get MongoDB connection string from environment variable
MONGO_URI = os.environ.get("mongodb+srv://jaiswalsahil283_db_user:Gmail%4012@cluster0.wu7p4hk.mongodb.net/student_payments?retryWrites=true&w=majority")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["payment_db"]   # Your database name
collection = db["students"] # Your collection name

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    reg_id = request.form.get("reg_id")
    phone = request.form.get("phone")
    email = request.form.get("email")
    utr = request.form.get("utr")

    # Insert data into MongoDB
    collection.insert_one({
        "name": name,
        "reg_id": reg_id,
        "phone": phone,
        "email": email,
        "utr": utr
    })

    return redirect("/success")

@app.route("/success")
def success():
    return "Payment data submitted successfully 🎉"

if __name__ == "__main__":
    app.run(debug=True)
