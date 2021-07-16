# Dependencies
from flask import Flask, render_template, json, url_for, request
import os
import database.db_connector as db
from markupsafe import escape

# Configuration
app = Flask(__name__)
db_connection = db.connect_to_database()

# Routes
@app.route("/")
def root():
    return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/courses")
def courses():
    query = "SELECT * FROM courses;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
    return render_template("courses.html", items=results)

@app.route("/campuses", methods=["GET", "POST"])
def campuses():
    error = None
    query = "SELECT * FROM campuses;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
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

    return render_template("campuses.html", items=results, images=images, count=student_result)

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=True) # Use 'python app.py' or 'flask run' to run in terminal