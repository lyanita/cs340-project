# Dependencies
from flask import Flask, render_template, json, url_for, request, session, redirect
import os
import database.db_connector as db
from markupsafe import escape
import geopy as gp
import json
import datetime

# Configuration
app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)
db_connection = db.connect_to_database()

# Routes
@app.route("/")
def root():
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/campuses.html", methods=["GET", "POST", "DELETE"])
def campuses():
    post_message = ""
    delete_message = ""
    campus_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    if request.method == "POST":
        campus_name = request.form['campus_name']
        campus_city = request.form['campus_city']
        campus_country = request.form['campus_country']
        campus_online = request.form['campus_online']
        print(campus_online)

        flag = False
        for dict in campus_results:
            campus = dict.get('campus_name')
            if campus_name == campus:
                flag = True
                post_message = "The campus name is already in use. Please enter another name."
        if not flag:
            insert_query = "INSERT INTO campuses(campus_name, campus_city, campus_country, campus_online) VALUES (%s, %s, %s, %s);"
            data = (campus_name, campus_city, campus_country, campus_online)
            insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
            post_message = "You have successfully created a new campus."

        campus_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
        campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
        campus_results = campus_cursor.fetchall()

    return render_template("campuses.html", items=campus_results, post_message=post_message, delete_message=delete_message)

@app.route("/delete-campus/<int:id>")
def delete_campus(id):
    delete_query = "DELETE FROM campuses WHERE campus_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted campus id #" + str(id) + "."

    return redirect("/campuses.html")

@app.route("/sections.html")
def sections():
    return render_template("sections.html")

@app.route("/instructors.html")
def instructors():
    return render_template("instructors.html")

@app.route("/courses.html")
def courses():
    query = "SELECT * FROM courses;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
    return render_template("courses.html", items=results)

@app.route("/students.html", methods=["GET", "POST"])
def students():
    error = None
    message = ""
    select_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
    select_cursor = db.execute_query(db_connection=db_connection, query=select_query)
    select_results = select_cursor.fetchall()
    images = os.listdir(os.path.join(app.static_folder, "img"))

    student_query = "SELECT campus_id, COUNT(*) AS count FROM students GROUP BY campus_id ORDER BY campus_id ASC;"
    student_cursor = db.execute_query(db_connection=db_connection, query=student_query)
    student_result = student_cursor.fetchall()
    
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        campus = request.form['campus']
        
        campus_query = "SELECT DISTINCT campus_id, campus_name FROM campuses ORDER BY campus_id ASC;"
        campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
        campus_results = campus_cursor.fetchall()
        for dict in campus_results:
            campus_name = dict.get('campus_name')
            if campus_name == campus:
                campus_id = dict.get('campus_id')
                print(campus_id)
        
        insert_query = "INSERT INTO students(student_first_name, student_last_name, campus_id) VALUES (%s, %s, %s);"
        data = (first_name, last_name, campus_id)
        insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)

        register_query = "SELECT MAX(student_id) AS student_id FROM students;"
        register_cursor = db.execute_query(db_connection=db_connection, query=register_query)
        register_results = register_cursor.fetchall()
        print(register_results)
        student_id = str(register_results[0].get('student_id') + 1)
        message = "Thanks for registering, " + first_name + "! Your student ID is " + student_id + "."

    return render_template("students.html", items=select_results, images=images, count=student_result, message=message)

@app.route("/contact.html")
def contact():
    query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()

    coordinates_list = []
    locator = gp.Nominatim(user_agent="Geocoder")
    for dict in results:
        campus_city = dict.get("campus_city")
        campus_name = dict.get("campus_name")
        location = locator.geocode(campus_city)
        if location:
            print(location)
            lat = location.latitude
            long = location.longitude
            email = campus_name.lower() + "@ah.edu"
            coordinates = [campus_name, lat, long, campus_city, email]
            print(coordinates)
            coordinates_list.append(coordinates)

    return render_template("contact.html", items=results, markers=json.dumps(coordinates_list))

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7676))
    app.run(port=port, debug=True) # Use 'python app.py' or 'flask run' to run in terminal