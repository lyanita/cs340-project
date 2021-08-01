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
# Home
@app.route("/")
def root():
    """Render index.html as home page"""
    return render_template("index.html")

@app.route("/index.html")
def index():
    """Render index.html as home page"""
    return render_template("index.html")

# Campus
@app.route("/campuses.html", methods=["GET", "POST"])
def campuses():
    """Display records from the Campuses table"""
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else "" #retrieve delete_message from GET request

    select_query = "SELECT * FROM Campuses ORDER BY campus_id ASC;"
    select_cursor = db.execute_query(db_connection=db_connection, query=select_query)
    select_results = select_cursor.fetchall()
    images = os.listdir(os.path.join(app.static_folder, "img/campus"))

    student_query = "SELECT campus_id, COUNT(*) AS count FROM Students GROUP BY campus_id ORDER BY campus_id ASC;"
    student_cursor = db.execute_query(db_connection=db_connection, query=student_query)
    student_results = student_cursor.fetchall()

    population_query = "SELECT std.*, cps.campus_name FROM Students std LEFT JOIN Campuses cps ON std.campus_id = cps.campus_id ORDER BY student_id ASC;"
    population_cursor = db.execute_query(db_connection=db_connection, query=population_query)
    population_results = population_cursor.fetchall()

    campus_query = "SELECT DISTINCT campus_id, campus_name FROM Campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    course_query = "SELECT cps.campus_id, cps.campus_name, crs.course_id, crs.course_name FROM Courses_Campuses cmb \
                    JOIN Courses crs ON cmb.course_id = crs.course_id \
                    JOIN Campuses cps ON cmb.campus_id = cps.campus_id;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()

    db_connection.close()
    return render_template("campuses.html", items=select_results, students=population_results, campuses=campus_results, courses=course_results, images=images, count=student_results, post_message=post_message, delete_message=delete_message)

@app.route("/update-campus/<int:id>", methods=["GET", "POST"])
def update_campus(id):
    """Update a campus in the Campuses table"""
    db_connection = db.connect_to_database()
    post_message = ""

    campus_query = "SELECT * FROM Campuses WHERE campus_id = %s;"
    data = (id,)
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query, query_params=data)
    campus_results = campus_cursor.fetchall()

    if request.method == "POST":
        campus_name = request.form['campus_name']
        campus_city = request.form['campus_city']
        campus_country = request.form['campus_country']
        check = request.form['campus_online']
        campus_online = True if request.form['campus_online'] == 'TRUE' else False #adjust boolean values

        if campus_name == "":
            post_message = "Please enter a campus name."
        else:
            update_query = "UPDATE Campuses SET campus_name = %s, campus_city = %s, campus_country = %s, campus_online = %s WHERE campus_id = %s;"
            data = (campus_name, campus_city, campus_country, campus_online, id)
            update_cursor = db.execute_query(db_connection=db_connection, query=update_query, query_params=data)
        
        db_connection.close()
        return redirect("/campuses.html")
            
    else:
        db_connection.close()
        return render_template("campus_update.html", items=campus_results, post_message=post_message)

@app.route("/delete-campus/<int:id>")
def delete_campus(id):
    """Delete a campus from the Campuses table"""
    db_connection = db.connect_to_database()

    delete_query = "DELETE FROM Campuses WHERE campus_id = %s;"
    data=(id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted campus id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('campuses', delete_message=delete_message, **request.args))

@app.route("/add_campuses.html", methods=["GET", "POST"])
def add_campuses():
    """Add a campus to the Campuses table"""
    db_connection = db.connect_to_database()
    post_message = ""

    campus_query = "SELECT * FROM Campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    if request.method == "POST":
        campus_name = request.form['campus_name']
        campus_city = request.form['campus_city']
        campus_country = request.form['campus_country']
        campus_online = True if request.form['campus_online'] == 'TRUE' else False

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
                insert_query = "INSERT INTO Campuses(campus_name, campus_city, campus_country, campus_online) VALUES (%s, %s, %s, %s);"
                data = (campus_name, campus_city, campus_country, campus_online)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "You have successfully created a new campus."

                new_campus_query = "SELECT * FROM Campuses WHERE campus_name = %s;"
                data = (campus_name,)
                new_campus_cursor = db.execute_query(db_connection=db_connection, query=new_campus_query, query_params=data)
                new_campus_results = new_campus_cursor.fetchall()

                intersect_insert_query = "INSERT INTO Courses_Campuses(course_id, campus_id) SELECT course_id, campus_id FROM Courses t1 CROSS JOIN Campuses t2 WHERE t2.campus_id = %s;"
                for dict in new_campus_results:
                    campus_id = dict.get('campus_id')
                data = (campus_id,)
                intersect_insert_cursor = db.execute_query(db_connection=db_connection, query=intersect_insert_query, query_params=data)

    db_connection.close()
    return render_template("add_campuses.html", post_message=post_message)

# Instructors
@app.route("/instructors.html", methods=["GET", "POST"])
def instructors():
    """Display records from the Instructors table"""
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else "" #retrieve delete_message from GET request
    
    instructor_query = "SELECT ins.*, cps.campus_name FROM Instructors ins LEFT JOIN Campuses cps ON ins.campus_id = cps.campus_id ORDER BY instructor_id ASC;"
    instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query)
    instructor_results = instructor_cursor.fetchall()

    campuses_query = "SELECT DISTINCT campus_id, campus_name FROM Campuses ORDER BY campus_id ASC;"
    campuses_cursor = db.execute_query(db_connection=db_connection, query=campuses_query)
    campuses_results = campuses_cursor.fetchall()

    db_connection.close()    
    return render_template("instructors.html", items=instructor_results, campuses=campuses_results, post_message=post_message, delete_message=delete_message)

@app.route("/delete-instructor/<int:id>")
def delete_instructor(id):
    """Delete an instructor from the Instructors table"""
    db_connection = db.connect_to_database()
    
    delete_query = "DELETE FROM Instructors WHERE instructor_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted instructor id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('instructors', delete_message=delete_message, **request.args))

@app.route("/add_instructors.html", methods=["GET", "POST"])
def add_instructors():
    """Add an instructor to the Instructors table"""
    db_connection = db.connect_to_database()
    post_message = ""

    campuses_query = "SELECT DISTINCT campus_id, campus_name FROM Campuses ORDER BY campus_id ASC;"
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
            campus_query = "SELECT DISTINCT * FROM Campuses WHERE campus_name = %s;"
            data = (campus_name,)
            campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query, query_params=data)
            campus_results = campus_cursor.fetchall()

            for dict in campus_results:
                campus = dict.get('campus_name')
                if campus_name == campus:
                    campus_id = dict.get('campus_id')
        
            insert_query = "INSERT INTO Instructors(instructor_first_name, instructor_last_name, campus_id) VALUES (%s, %s, %s);"
            data = (instructor_first_name, instructor_last_name, campus_id)
        
        else:
            insert_query = "INSERT INTO Instructors(instructor_first_name, instructor_last_name) VALUES (%s, %s);"
            data = (instructor_first_name, instructor_last_name)
        
        insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
        post_message = "You have successfully added a new instructor."

    db_connection.close()
    return render_template("add_instructors.html", post_message=post_message, campuses=campuses_results)

# Sections
@app.route("/sections.html", methods=["GET", "POST"])
def sections():
    """Display records from the Sections table and search sections"""
    db_connection = db.connect_to_database()
    post_message = ""
    err_message = ""
    query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
        FROM Sections s \
        JOIN Courses c ON s.course_id = c.course_id \
        JOIN Instructors i ON s.instructor_id = i.instructor_id \
        JOIN Campuses ca ON s.campus_id = ca.campus_id \
        ORDER BY section_id ASC;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()    

    course_query = "SELECT DISTINCT course_name FROM Courses ORDER BY course_name ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_result = course_cursor.fetchall()

    campus_query = "SELECT DISTINCT campus_name FROM Campuses ORDER BY campus_name ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_result = campus_cursor.fetchall()
    
    # search from Sections table
    if request.method == "POST": 
        section_id = ""
        course_name = ""
        campus_name = ""
        
        # check for valid input
        if request.form['search_radio'] == 'section_id':
            section_id = request.form['section_id']
            if section_id == "":
                err_message = "Please enter valid Section ID."
                return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result)
                
        if request.form['search_radio'] == 'course_name':
            course_name = request.form['course_name']
            if course_name == "":
                err_message = "Please enter valid Course Name."          
                return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result)
            else:
                course_name = "%" + course_name + "%"

        if request.form['search_radio'] == 'campus_name':
            campus_name = request.form['campus_name']
            if campus_name == "":
                err_message = "Please enter valid Campus Name."
                return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result)
            else:
                campus_name = "%" + campus_name + "%"              
                        
        search_query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_id, campus_name \
            FROM Sections s \
            JOIN Courses c ON s.course_id = c.course_id \
            JOIN Instructors i ON s.instructor_id = i.instructor_id \
            JOIN Campuses ca ON s.campus_id = ca.campus_id \
            WHERE section_id = %s OR c.course_name like %s OR ca.campus_name like %s \
            ORDER BY section_id ASC;"
        data = (section_id, course_name, campus_name)        
        search_cursor = db.execute_query(db_connection=db_connection, query=search_query, query_params=data)
        search_results = search_cursor.fetchall()
        
        # if no search result, display all rows
        if len(search_results) == 0: 
            err_message = "No search results founds."
            cursor.execute(query)
            search_results = cursor.fetchall()            
        return render_template("sections.html", items=search_results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result)
    
    db_connection.close()
    return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result)

@app.route("/add_sections.html", methods=["GET", "POST"])
def add_sections():
    """Add a section to the Sections table"""
    db_connection = db.connect_to_database()
    post_message = ""
    section_query = "SELECT * FROM Sections ORDER BY section_id ASC;"
    section_cursor = db.execute_query(db_connection=db_connection, query=section_query)
    section_results = section_cursor.fetchall()
    
    if request.method == "POST":
        course_id = request.form['course_id']
        instructor_id = request.form['instructor_id']
        campus_id = ""
        add_query = "INSERT INTO Sections(course_id, instructor_id, campus_id) VALUES (%s, %s, %s);"
        data = (course_id, instructor_id, campus_id)

        if course_id == "" or instructor_id == "":
            post_message = "Please complete all fields in the form."
        else:
            flag = False
            for dict in section_results:
                course_id1 = dict.get('course_id')
                instructor_id1 = dict.get('instructor_id')                
                if int(course_id1) == int(course_id) and int(instructor_id1) == int(instructor_id):
                    flag = True
                    post_message = "The section already exists. Please enter different values."
                    
            if not flag:
                # get campus_id based on instructor_id
                get_campus_query = "SELECT * FROM Instructors WHERE instructor_id = %s;"
                data = (instructor_id,)
                get_campus_cursor = db.execute_query(db_connection=db_connection, query=get_campus_query, query_params=data)
                get_campus_results = get_campus_cursor.fetchall()
                for dict in get_campus_results:
                    campus_id = dict.get('campus_id')
                    
                add_query = "INSERT INTO Sections(course_id, instructor_id, campus_id) VALUES (%s, %s, %s);"
                data = (course_id, instructor_id, campus_id)
                add_cursor = db.execute_query(db_connection=db_connection, query=add_query, query_params=data)
                post_message = "You have successfully created a new section."
            
    db_connection.close()
    return render_template("/add_sections.html", post_message=post_message)

@app.route("/delete-section/<int:id>")
def delete_section(id):
    """Delete a section from the Sections table"""
    db_connection = db.connect_to_database()
    data = (id,)
    course_query = "SELECT * FROM Sections WHERE section_id = %s;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query, query_params=data)
    course_results = course_cursor.fetchall()
    for dict in course_results:
        course_id = dict.get("course_id")
    delete_query = "DELETE FROM Sections WHERE section_id = %s;"
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted section id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('sections', delete_message=delete_message, **request.args))

@app.route("/section_register.html", methods=["GET", "POST"])
def section_register():
    """"Display records from the Students & Sections intersection table and handles Students & Sections registration"""
    db_connection = db.connect_to_database()
    post_message = ""
    query = "SELECT ss.student_id, CONCAT(student_first_name, ' ', student_last_name) as student_name, se.section_id, c.course_name, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_name \
        FROM Students_Sections ss \
        JOIN Students s ON ss.student_id = s.student_id \
        JOIN Sections se ON se.section_id = ss.section_id \
        JOIN Courses c ON c.course_id = se.course_id \
        JOIN Instructors i ON i.instructor_id = se.instructor_id\
        JOIN Campuses ca ON ca.campus_id = i.campus_id \
        ORDER BY student_id,section_id ASC;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()

    # handle students & sections registration
    if request.method == "POST":
        student_first_name = request.form['student_first_name']
        student_last_name = request.form['student_last_name']
        section_id = request.form['section_id']
        
        # get student_id for the given first name and last name
        student_id_query = "SELECT student_id FROM Students WHERE student_first_name = %s and student_last_name = %s"
        data = (student_first_name, student_last_name)
        student_id_cursor = db.execute_query(db_connection=db_connection, query=student_id_query, query_params=data)
        student_id_results = student_id_cursor.fetchall()
        student_id = ""
        for dict in student_id_results:
            student_id = dict.get('student_id')
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
                
                # verify if student's registered campus and the section's campus match
                student_campus_query = "SELECT campus_id FROM Students WHERE student_id = %s"
                data = (student_id,)
                student_campus_cursor = db.execute_query(db_connection=db_connection, query=student_campus_query, query_params=data)
                student_campus_results = student_campus_cursor.fetchall()
                
                section_campus_query = "SELECT campus_id FROM Sections WHERE section_id = %s"
                data = (section_id,)
                section_campus_cursor = db.execute_query(db_connection=db_connection, query=section_campus_query, query_params=data)
                section_campus_results = section_campus_cursor.fetchall()
                
                if student_campus_results != section_campus_results:
                    flag = True
                    post_message = "The section is not available in the student's registered campus. Please enter different values."
                    break
                
            if not flag:
                register_query = "INSERT INTO Students_Sections(student_id, section_id) VALUES (%s, %s);"
                data = (student_id, section_id,)
                register_cursor = db.execute_query(db_connection=db_connection, query=register_query, query_params=data)
                post_message = "You have successfully enrolled " + student_first_name + " " + student_last_name + " in section #" + section_id + "."
                #post_message2 = "*List of Sections registered for student_id #" + str(student_id)
        cursor = db.execute_query(db_connection=db_connection, query=query)
        results = cursor.fetchall()
    db_connection.close()
    return render_template("section_register.html", items=results, post_message=post_message)

@app.route("/delete-student-section/<int:id1><int:id2>")
def delete_student_section(id1, id2):
    """Delete a row from the Students_Sections intersection table """
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM Students_Sections WHERE student_id = %s and section_id = %s;"
    data = (id1, id2,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted section id #" + str(id2) + "for student_id #" + str(id1) + "."

    db_connection.close()
    return redirect("/section_register.html")

# Courses
@app.route("/courses.html", methods=["GET", "POST"])
def courses():
    """Display records from the Courses table"""
    db_connection = db.connect_to_database()
    post_message = ""

    course_query = "SELECT * FROM Courses ORDER BY course_id ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()
    
    db_connection.close()
    return render_template("courses.html", items=course_results, post_message=post_message)

@app.route("/delete-course/<int:id>")
def delete_course(id):
    """Delete a course from the Courses table"""
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM Courses WHERE course_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted course id #" + str(id) + "."

    db_connection.close()
    return redirect("../courses.html")

@app.route("/add_courses.html", methods=["GET", "POST"])
def add_courses():
    """Add a course to the Courses table"""
    db_connection = db.connect_to_database()
    post_message = ""

    course_query = "SELECT * FROM Courses ORDER BY course_id ASC;"
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
                insert_query = "INSERT INTO Courses(course_name) VALUES (%s);"
                data = (course_name,)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "A new course, " + course_name + ", has been created."

    db_connection.close()
    return render_template("add_courses.html", post_message=post_message)

# Students
@app.route("/students.html", methods=["GET", "POST"])
def students():
    """Display records from the Students table"""
    db_connection = db.connect_to_database()
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else ""

    population_query = "SELECT std.*, cps.campus_name FROM Students std LEFT JOIN Campuses cps ON std.campus_id = cps.campus_id ORDER BY student_id ASC;"
    population_cursor = db.execute_query(db_connection=db_connection, query=population_query)
    population_results = population_cursor.fetchall()

    db_connection.close()
    return render_template("students.html", students=population_results, delete_message=delete_message)

@app.route("/delete-student/<int:id>")
def delete_student(id):
    """Delete a student from the Students table"""
    db_connection = db.connect_to_database()

    delete_query = "DELETE FROM Students WHERE student_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted student id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('students', delete_message=delete_message, **request.args))

@app.route("/add_students.html", methods=["GET", "POST"])
def add_students():
    """Add a student to the Students table"""
    db_connection = db.connect_to_database()
    post_message = ""
    campus_query = "SELECT DISTINCT campus_id, campus_name FROM Campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

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
        
            insert_query = "INSERT INTO Students(student_first_name, student_last_name, campus_id) VALUES (%s, %s, %s);"
            data = (first_name, last_name, campus_id)
            insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)

            register_query = "SELECT MAX(student_id) AS student_id FROM Students;"
            register_cursor = db.execute_query(db_connection=db_connection, query=register_query)
            register_results = register_cursor.fetchall()
            student_id = str(register_results[0].get('student_id'))
            post_message = "A new student, " + first_name + " " + last_name + ", has been added to the database with student id #" + student_id + "."

    db_connection.close()
    return render_template("add_students.html", campuses=campus_results, post_message=post_message)

# Contact
@app.route("/contact.html")
def contact():
    """Renders a contact us page with map coordinates of campus locations"""
    db_connection = db.connect_to_database()
    campus_query = "SELECT * FROM Campuses ORDER BY campus_id ASC;"
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
