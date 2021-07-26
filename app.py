# Dependencies
from flask import Flask, render_template, json, url_for, request, session, redirect, flash
import os
import database.db_connector as db
from markupsafe import escape
import geopy as gp
import json
import datetime

# Configuration
app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)

# Routes
@app.route("/")
def root():
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/campuses.html", methods=["GET", "POST"])
def campuses():
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else ""
    campus_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    if request.method == "POST":
        campus_name = request.form['campus_name']
        campus_city = request.form['campus_city']
        campus_country = request.form['campus_country']
        campus_online = True if request.form['campus_online'] == 'TRUE' else False
        print(campus_online)

        if campus_name == "":
            post_message = "Please enter a campus name."
        else:

            flag = False
            for dict in campus_results:
                campus = dict.get('campus_name')
                if campus_name == campus:
                    flag = True
                    post_message = "The campus name is already in use. Please enter another name."
                    break
            if not flag:
                insert_query = "INSERT INTO campuses(campus_name, campus_city, campus_country, campus_online) VALUES (%s, %s, %s, %s);"
                data = (campus_name, campus_city, campus_country, campus_online)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "You have successfully created a new campus."

                new_campus_query = "SELECT * FROM campuses WHERE campus_name = %s;"
                data = (campus_name,)
                new_campus_cursor = db.execute_query(db_connection=db_connection, query=new_campus_query, query_params=data)
                new_campus_results = new_campus_cursor.fetchall()
                print(new_campus_results)

                intersect_insert_query = "INSERT INTO courses_campuses(course_id, campus_id) SELECT course_id, campus_id FROM courses t1 CROSS JOIN campuses t2 WHERE t2.campus_id = %s;"
                for dict in new_campus_results:
                    campus_id = dict.get('campus_id')
                data = (campus_id,)
                intersect_insert_cursor = db.execute_query(db_connection=db_connection, query=intersect_insert_query, query_params=data)

            campus_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
            campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
            campus_results = campus_cursor.fetchall()
    
    db_connection.close()
    return render_template("campuses.html", items=campus_results, post_message=post_message, delete_message=delete_message)

@app.route("/update-campus/<int:id>", methods=["GET", "POST"])
def update_campus(id):
    post_message = ""
    db_connection = db.connect_to_database()
    campus_query = "SELECT * FROM campuses WHERE campus_id = %s;"
    data = (id,)
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query, query_params=data)
    campus_results = campus_cursor.fetchall()
    print(campus_results)

    if request.method == "POST":
        campus_name = request.form['campus_name']
        campus_city = request.form['campus_city']
        campus_country = request.form['campus_country']
        check = request.form['campus_online']
        campus_online = True if request.form['campus_online'] == 'TRUE' else False
        print(check)
        print(campus_online)

        if campus_name == "":
            post_message = "Please enter a campus name."
        else:
            update_query = "UPDATE campuses SET campus_name = %s, campus_city = %s, campus_country = %s, campus_online = %s WHERE campus_id = %s;"
            data = (campus_name, campus_city, campus_country, campus_online, id)
            update_cursor = db.execute_query(db_connection=db_connection, query=update_query, query_params=data)
        
        db_connection.close()
        return redirect("/campuses.html")
            
    else:
        db_connection.close()
        return render_template("campus_update.html", items=campus_results, post_message=post_message)

@app.route("/delete-campus/<int:id>")
def delete_campus(id):
    db_connection = db.connect_to_database()
    data=(id,)
    #intersect_delete_query = "DELETE FROM courses_campuses WHERE campus_id = %s;"
    #intersect_delete_cursor = db.execute_query(db_connection=db_connection, query=intersect_delete_query, query_params=data)
    delete_query = "DELETE FROM campuses WHERE campus_id = %s;"
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted campus id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('campuses', delete_message=delete_message, **request.args))
    #return redirect("/campuses.html")

@app.route("/instructors.html", methods=["GET", "POST"])
def instructors():
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else ""
    instructor_query = "SELECT ins.*, cps.campus_name FROM instructors ins LEFT JOIN campuses cps ON ins.campus_id = cps.campus_id ORDER BY instructor_id ASC;"
    instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query)
    instructor_results = instructor_cursor.fetchall()

    campuses_query = "SELECT DISTINCT campus_id, campus_name FROM campuses ORDER BY campus_id ASC;"
    campuses_cursor = db.execute_query(db_connection=db_connection, query=campuses_query)
    campuses_results = campuses_cursor.fetchall()

    if request.method == "POST":
        instructor_first_name = request.form['instructor_first_name']
        instructor_last_name = request.form['instructor_last_name']
        campus_name = request.form['campus_name']
        print(campus_name)

        if instructor_first_name == "" or instructor_last_name == "":
            post_message = "Please complete all fields in the form."

        if campus_name != "Unassigned":
            campus_query = "SELECT DISTINCT * FROM campuses WHERE campus_name = %s;"
            data = (campus_name,)
            campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query, query_params=data)
            campus_results = campus_cursor.fetchall()

            for dict in campus_results:
                campus = dict.get('campus_name')
                if campus_name == campus:
                    campus_id = dict.get('campus_id')
        
            insert_query = "INSERT INTO instructors(instructor_first_name, instructor_last_name, campus_id) VALUES (%s, %s, %s);"
            data = (instructor_first_name, instructor_last_name, campus_id)
        
        else:
            insert_query = "INSERT INTO instructors(instructor_first_name, instructor_last_name) VALUES (%s, %s);"
            data = (instructor_first_name, instructor_last_name)
        
        insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
        post_message = "You have successfully added a new instructor."

        instructor_query = "SELECT ins.*, cps.campus_name FROM instructors ins LEFT JOIN campuses cps ON ins.campus_id = cps.campus_id ORDER BY instructor_id ASC;"
        instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query)
        instructor_results = instructor_cursor.fetchall()

    db_connection.close()    
    return render_template("instructors.html", items=instructor_results, campuses=campuses_results, post_message=post_message, delete_message=delete_message)

@app.route("/delete-instructor/<int:id>")
def delete_instructor(id):
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM instructors WHERE instructor_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted instructor id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('instructors', delete_message=delete_message, **request.args))
    #return redirect("/instructors.html")

@app.route("/sections.html", methods=["GET", "POST"])
def sections():
    db_connection = db.connect_to_database()
    query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
        FROM sections s \
        JOIN courses c ON s.course_id = c.course_id \
        JOIN instructors i ON s.instructor_id = i.instructor_id \
        JOIN campuses ca ON s.campus_id = ca.campus_id \
        ORDER BY section_id ASC;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()    
    
    if request.method == "POST":        
        section_id = request.form['section_id']
        course_id = request.form['course_id']
        instructor_id = request.form['instructor_id']
        campus_id = request.form['campus_id']
        
        search_query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
            FROM sections s \
            JOIN courses c ON s.course_id = c.course_id \
            JOIN instructors i ON s.instructor_id = i.instructor_id \
            JOIN campuses ca ON s.campus_id = ca.campus_id \
            WHERE section_id LIKE %s OR c.course_id LIKE %s OR i.instructor_id LIKE %s OR ca.campus_id LIKE %s \
            ORDER BY section_id ASC;"
        data = (section_id, course_id, instructor_id, campus_id)        
        search_cursor = db.execute_query(db_connection=db_connection, query=search_query, query_params=data)
        search_results = search_cursor.fetchall()
        
        # if no result, display all rows
        if len(search_results) == 0: 
            cursor.execute(query)
            search_results = cursor.fetchall()            
        return render_template("sections.html", items=search_results)
    
    db_connection.close()
    return render_template("sections.html", items=results)

@app.route("/section-register/<int:id>", methods=["GET", "POST"])
def section_register(id):
    db_connection = db.connect_to_database()
    post_message = ""
    post_message2 = ""
    register_query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
        FROM sections s \
        JOIN courses c ON s.course_id = c.course_id \
        JOIN instructors i ON s.instructor_id = i.instructor_id \
        JOIN campuses ca ON s.campus_id = ca.campus_id \
        WHERE section_id = %s \
        ORDER BY section_id ASC;"
    data = (id,)
    register_cursor = db.execute_query(db_connection=db_connection, query=register_query, query_params=data)
    register_results = register_cursor.fetchall()
    
    query = "SELECT * FROM students_sections WHERE section_id = %s;"
    data = (id,)
    cursor = db.execute_query(db_connection=db_connection, query=query, query_params=data)
    results = cursor.fetchall()
    print(results)
    
    if request.method == "POST":
        student_id = request.form['student_id']
        section_id = request.form['section_id']
        print("Student ID is " + str(student_id) + " and Section ID is " + str(section_id))

        if student_id == "" or section_id == "":
            post_message = "Please complete all fields in the form."
        else:
            flag = False
            for dict in results:
                student_id1 = dict.get('student_id')
                section_id1 = dict.get('section_id')
                print("Student ID1 is " + str(student_id1) + " and Section ID1 is " + str(section_id1))
                
                if int(student_id1) == int(student_id) and int(section_id1) == int(section_id):
                    flag = True
                    post_message = "The section is already registered for the student. Please enter different values."
                    print("Duplicate")
                    break
            if not flag:
                register_query = "INSERT INTO students_sections(student_id, section_id) VALUES (%s, %s);"
                data = (student_id, section_id,)
                register_cursor = db.execute_query(db_connection=db_connection, query=register_query, query_params=data)
                post_message = "You have successfully registered for the section."
                post_message2 = "*List of Sections registered for student_id #" + str(student_id)
            
        query = "SELECT * FROM students_sections WHERE student_id = %s;"
        data = (student_id,)
        cursor = db.execute_query(db_connection=db_connection, query=query, query_params=data)
        results = cursor.fetchall()
        
    db_connection.close()
    return render_template("section_register.html", items=register_results, items2=results, post_message=post_message, post_message2=post_message2)

@app.route("/delete-student-section/<int:id1><int:id2>")
def delete_student_section(id1, id2):
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM students_sections WHERE student_id = %s and section_id = %s;"
    data = (id1, id2,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted section id #" + str(id2) + "registerd for student_id #" + str(id1) + "."

    db_connection.close()
    return redirect("/sections.html")

@app.route("/courses.html", methods=["GET", "POST"])
def courses():
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = ""
    course_query = "SELECT * FROM courses ORDER BY course_id ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()

    if request.method == "POST":
        course_name = request.form['course_name']
        print(course_name)

        if course_name == "":
            post_message = "Please enter a course name."
        else:
            flag = False
            for dict in course_results:
                course = dict.get('course_name')
                if course_name == course:
                    flag = True
                    post_message = "The course name is already in use. Please enter another name."
                    break
            if not flag:
                insert_query = "INSERT INTO courses(course_name) VALUES (%s);"
                data = (course_name,)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "You have successfully created a new course."

            course_query = "SELECT * FROM courses ORDER BY course_id ASC;"
            course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
            course_results = course_cursor.fetchall()
    
    db_connection.close()
    return render_template("courses.html", items=course_results, post_message=post_message, delete_message=delete_message)

@app.route("/delete-course/<int:id>")
def delete_course(id):
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM courses WHERE course_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted course id #" + str(id) + "."

    db_connection.close()
    return redirect("../courses.html")

@app.route("/manage-section/<int:id>", methods=["GET", "POST"])
def manage_section(id):
    db_connection = db.connect_to_database()
    post_message = ""
    add_query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
        FROM sections s \
        JOIN courses c ON s.course_id = c.course_id \
        JOIN instructors i ON s.instructor_id = i.instructor_id \
        JOIN campuses ca ON s.campus_id = ca.campus_id \
        WHERE c.course_id = %s \
        ORDER BY section_id ASC;"
    data = (id,)
    add_cursor = db.execute_query(db_connection=db_connection, query=add_query, query_params=data)
    add_results = add_cursor.fetchall()
    
    if request.method == "POST":
        course_id = request.form['course_id']
        instructor_id = request.form['instructor_id']
        campus_id = request.form['campus_id']

        if course_id == "" or instructor_id == "" or campus_id == "":
            post_message = "Please complete all fields in the form."
        else:
            flag = False
            for dict in add_results:
                course_id1 = dict.get('course_id')
                instructor_id1 = dict.get('instructor_id')
                campus_id1 = dict.get('campus_id')
                
                if course_id1 == course_id and instructor_id1 == instructor_id and campus_id1 == campus_id:
                    flag = True
                    post_message = "The section already exists. Please enter different values."
            if not flag:
                add_query = "INSERT INTO sections(course_id, instructor_id, campus_id) VALUES (%s, %s, %s);"
                data = (course_id, instructor_id, campus_id,)
                add_cursor = db.execute_query(db_connection=db_connection, query=add_query, query_params=data)
                post_message = "You have successfully created a new section."
                
            add_query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
                        FROM sections s \
                        JOIN courses c ON s.course_id = c.course_id \
                        JOIN instructors i ON s.instructor_id = i.instructor_id \
                        JOIN campuses ca ON s.campus_id = ca.campus_id \
                        WHERE c.course_id = %s \
                        ORDER BY section_id ASC;"
            data = (id,)
            add_cursor = db.execute_query(db_connection=db_connection, query=add_query, query_params=data)
            add_results = add_cursor.fetchall()
            
    db_connection.close()
    return render_template("manage_section.html", items=add_results, post_message=post_message)

@app.route("/delete-section/<int:id>")
def delete_section(id):
    db_connection = db.connect_to_database()
    data = (id,)
    course_query = "SELECT * FROM sections WHERE section_id = %s;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query, query_params=data)
    course_results = course_cursor.fetchall()
    for dict in course_results:
        course_id = dict.get("course_id")
    delete_query = "DELETE FROM sections WHERE section_id = %s;"
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted section id #" + str(id) + "."

    db_connection.close()
    #return redirect("/courses.html")
    return redirect("/manage-section/"+str(course_id))

@app.route("/students.html", methods=["GET", "POST"])
def students():
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else ""
    select_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
    select_cursor = db.execute_query(db_connection=db_connection, query=select_query)
    select_results = select_cursor.fetchall()
    images = os.listdir(os.path.join(app.static_folder, "img/campus"))

    student_query = "SELECT campus_id, COUNT(*) AS count FROM students GROUP BY campus_id ORDER BY campus_id ASC;"
    student_cursor = db.execute_query(db_connection=db_connection, query=student_query)
    student_results = student_cursor.fetchall()

    population_query = "SELECT std.*, cps.campus_name FROM students std LEFT JOIN campuses cps ON std.campus_id = cps.campus_id ORDER BY student_id ASC;"
    population_cursor = db.execute_query(db_connection=db_connection, query=population_query)
    population_results = population_cursor.fetchall()

    campus_query = "SELECT DISTINCT campus_id, campus_name FROM campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    course_query = "SELECT cps.campus_id, cps.campus_name, crs.course_id, crs.course_name FROM courses_campuses cmb JOIN courses crs ON cmb.course_id = crs.course_id JOIN campuses cps ON cmb.campus_id = cps.campus_id;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        campus = request.form['campus']
        print(first_name)
        print(campus)

        if first_name == "" or last_name == "":
            post_message = "Please complete all fields in the form."
        else:
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
            student_id = str(register_results[0].get('student_id'))
            post_message = "Thanks for registering, " + first_name + "! Your student ID is " + student_id + "."

            population_query = "SELECT std.*, cps.campus_name FROM students std LEFT JOIN campuses cps ON std.campus_id = cps.campus_id ORDER BY student_id ASC;"
            population_cursor = db.execute_query(db_connection=db_connection, query=population_query)
            population_results = population_cursor.fetchall()

    db_connection.close()
    return render_template("students.html", items=select_results, students=population_results, campuses=campus_results, courses=course_results, images=images, count=student_results, post_message=post_message, delete_message=delete_message)

@app.route("/delete-student/<int:id>")
def delete_student(id):
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM students WHERE student_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted student id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('students', delete_message=delete_message, **request.args))
    #return redirect("/students.html")

@app.route("/contact.html")
def contact():
    db_connection = db.connect_to_database()
    campus_query = "SELECT * FROM campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    coordinates_list = []
    locator = gp.Nominatim(user_agent="Geocoder")
    for dict in campus_results:
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
    
    db_connection.close()
    return render_template("contact.html", items=campus_results, markers=json.dumps(coordinates_list))

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7676))
    app.run(port=port, debug=True) # Use 'python app.py' or 'flask run' to run in terminal
