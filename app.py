from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, ADMIN_USER, ADMIN_PASS


app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folders
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FILE_NAME = "payments.xlsx"


# Create Excel if not exists
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=[
        "Name", "RegID", "Course", "Email", "Phone",
        "Branch", "Semester", "TransactionID", "Screenshot", "Status"
    ])
    df.to_excel(FILE_NAME, index=False)

# -------------------- Email Function --------------------
def send_email(to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# -------------------- Student Routes --------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    regid = request.form['regid']
    course = request.form['course']
    email = request.form['email']
    phone = request.form['phone']
    branch = request.form['branch']
    semester = request.form['semester']
    txnid = request.form['txnid']

    # Save screenshot
    screenshot = request.files['screenshot']
    filename = None
    if screenshot:
        filename = secure_filename(f"{regid}_{txnid}_{screenshot.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        screenshot.save(filepath)

    # Save to Excel
    # df = pd.read_excel(FILE_NAME, engine="openpyxl")
    df = pd.read_csv(FILE_NAME)


    df.loc[len(df)] = [name, regid, course, email, phone, branch, semester, txnid, filename, "Pending"]
    df.to_excel(FILE_NAME, index=False)

    # Send Confirmation Email
    subject = "📩 Payment Submission Received"
    body = f"""
    Hello {name},<br><br>
    We have received your payment details (Txn ID: <b>{txnid}</b>).<br>
    Your registration is <b style='color:orange;'>Pending Verification ⏳</b>.<br><br>
    Once verified, you will get another email.<br><br>
    Regards,<br>CSI Club
    """
    send_email(email, subject, body)

    return render_template("success.html", name=name)

# -------------------- Admin Routes --------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template("admin_login.html")

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    df = pd.read_excel(FILE_NAME)
    return render_template("admin_dashboard.html", tables=df.to_dict(orient="records"))

@app.route('/update/<int:row>/<status>')
def update(row, status):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    df = pd.read_excel(FILE_NAME)
    df.loc[row, "Status"] = status
    email = df.loc[row, "Email"]
    name = df.loc[row, "Name"]

    # Send decision email
    subject = f"🎉 Payment {status}"
    if status == "Approved":
        body = f"Hello {name},<br><br>Your payment has been <b style='color:green;'>Approved ✅</b>.<br>Welcome to CSI Club!"
    else:
        body = f"Hello {name},<br><br>Your payment has been <b style='color:red;'>Rejected ❌</b>. Please contact us."
    send_email(email, subject, body)

    df.to_excel(FILE_NAME, index=False)
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
