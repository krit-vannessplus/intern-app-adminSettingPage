import os
import pandas as pd
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
API = os.getenv("API")

# External API endpoints
FETCH_USERS_URL = f"{API}/api/users/getAllAdmins"
CREATE_USER_URL = f"{API}/api/users/registerAdmin"
BULK_CREATE_USER_URL = f"{API}/api/users/registerAdmins"
DELETE_ALL_ADMINS_URL = f"{API}/api/users/deleteAllAdmins"

def fetch_admins():
    try:
        response = requests.get(FETCH_USERS_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        flash(f"Error fetching admins: {str(e)}")
        return []

@app.route("/", methods=["GET"])
def index():
    admins = fetch_admins()
    return render_template("index.html", admins=admins)

@app.route("/delete_user", methods=["POST"])
def delete_user():
    email = request.form.get("email")
    if not email:
        flash("No email provided for deletion.")
        return redirect(url_for("index"))
    try:
        delete_url = f"{API}/api/users/deleteByEmail/{email}"
        response = requests.delete(delete_url)
        response.raise_for_status()
        flash(f"Deleted admin with email: {email}")
    except Exception as e:
        flash(f"Error deleting admin {email}: {str(e)}")
    return redirect(url_for("index"))

@app.route("/delete_all_admins", methods=["POST"])
def delete_all_admins():
    try:
        response = requests.delete(DELETE_ALL_ADMINS_URL)
        response.raise_for_status()
        flash("All admins deleted successfully.")
    except Exception as e:
        flash("Error deleting all admins: " + str(e))
    return redirect(url_for("index"))

@app.route("/create_user", methods=["POST"])
def create_user():
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password:
        flash("Email and password are required.")
        return redirect(url_for("index"))
    try:
        response = requests.post(CREATE_USER_URL, json={"email": email, "password": password})
        response.raise_for_status()
        flash(f"Admin {email} created successfully!")
    except Exception as e:
        flash(f"Error creating admin: {str(e)}")
    return redirect(url_for("index"))

def process_text_file(file_storage):
    try:
        content = file_storage.read().decode("utf-8")
        admins = []
        for line in content.splitlines():
            parts = line.strip().split(',')
            if len(parts) == 2:
                email = parts[0].strip()
                password = parts[1].strip()
                admins.append({"email": email, "password": password})
        return admins
    except Exception as e:
        flash("Error processing text file: " + str(e))
        return []

def process_excel_file(file_storage):
    try:
        df = pd.read_excel(file_storage)
        admins = []
        if "email" in df.columns and "password" in df.columns:
            for _, row in df.iterrows():
                admins.append({"email": row["email"], "password": row["password"]})
        else:
            flash("Excel file must contain 'email' and 'password' columns.")
        return admins
    except Exception as e:
        flash("Error processing excel file: " + str(e))
        return []

@app.route("/upload_text", methods=["POST"])
def upload_text():
    if "textfile" not in request.files:
        flash("No text file uploaded.")
        return redirect(url_for("index"))
    file = request.files["textfile"]
    if file.filename == "":
        flash("No text file selected.")
        return redirect(url_for("index"))
    admins = process_text_file(file)
    if not admins:
        flash("No valid admin data found in the text file.")
        return redirect(url_for("index"))
    try:
        response = requests.post(BULK_CREATE_USER_URL, json={"users": admins})
        response.raise_for_status()
        flash(f"Successfully processed and created {len(admins)} admins from text file!")
    except Exception as e:
        flash("Error uploading admins from text file: " + str(e))
    return redirect(url_for("index"))

@app.route("/upload_excel", methods=["POST"])
def upload_excel():
    if "excelfile" not in request.files:
        flash("No excel file uploaded.")
        return redirect(url_for("index"))
    file = request.files["excelfile"]
    if file.filename == "":
        flash("No excel file selected.")
        return redirect(url_for("index"))
    admins = process_excel_file(file)
    if not admins:
        flash("No valid admin data found in the excel file.")
        return redirect(url_for("index"))
    try:
        response = requests.post(BULK_CREATE_USER_URL, json={"users": admins})
        response.raise_for_status()
        flash(f"Successfully processed and created {len(admins)} admins from excel file!")
    except Exception as e:
        flash("Error uploading admins from excel file: " + str(e))
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)