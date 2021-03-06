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
    duplicate_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else "" #retrieve delete_message from GET request
    remove_message = request.args.get("remove_message") if request.args.get("remove_message") else "" #retrieve remove_message from GET request
    update_message = request.args.get("update_message") if request.args.get("update_message") else "" #retrieve update_message from GET request

    # select all records from Courses table
    select_query = "SELECT * FROM Campuses ORDER BY campus_id ASC;"
    select_cursor = db.execute_query(db_connection=db_connection, query=select_query)
    select_results = select_cursor.fetchall()
    images = os.listdir(os.path.join(app.static_folder, "img/campus"))

    # find the number of students at each campus
    student_query = "SELECT campus_id, COUNT(*) AS count FROM Students GROUP BY campus_id ORDER BY campus_id ASC;"
    student_cursor = db.execute_query(db_connection=db_connection, query=student_query)
    student_results = student_cursor.fetchall()

    # join Campuses to Students table
    population_query = "SELECT std.*, cps.campus_name FROM Students std LEFT JOIN Campuses cps ON std.campus_id = cps.campus_id ORDER BY student_id ASC;"
    population_cursor = db.execute_query(db_connection=db_connection, query=population_query)
    population_results = population_cursor.fetchall()

    # select all records from Campuses table
    campus_query = "SELECT DISTINCT campus_id, campus_name FROM Campuses ORDER BY campus_id ASC;"
    campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query)
    campus_results = campus_cursor.fetchall()

    # select all records from Courses table
    course_query = "SELECT DISTINCT course_id, course_name FROM Courses ORDER BY course_id ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()

    # select all records from Courses_Campuses intersection table
    course_campus_query = "SELECT cps.campus_id, cps.campus_name, crs.course_id, crs.course_name FROM Courses_Campuses cmb \
                    JOIN Courses crs ON cmb.course_id = crs.course_id \
                    JOIN Campuses cps ON cmb.campus_id = cps.campus_id;"
    course_campus_cursor = db.execute_query(db_connection=db_connection, query=course_campus_query)
    course_campus_results = course_campus_cursor.fetchall()

    if request.method == "POST":
        campus_name = request.form['campus_name']
        course_name = request.form['course_name']

        course_flag = False
        for dict in course_results:
            course = dict.get('course_name')
            if course_name == course: #check if course exists in Courses table
                course_id = dict.get('course_id')
                course_flag = True
                break
            else:
                validate_message = "Course does not exist. Please try again."

        campus_flag = False
        for dict in campus_results:
            campus = dict.get('campus_name')
            if campus_name == campus: #check if campus exists in Campuses table
                campus_id = dict.get('campus_id')
                campus_flag = True
                break
            else:
                validate_message = "Campus does not exist. Please try again."

        duplicate_flag = False
        if course_flag and campus_flag:
            for dict in course_campus_results: #do not insert if record already exists in intersection table
                course_check = dict.get('course_id')
                campus_check = dict.get('campus_id')
                if course_id == course_check and campus_id == campus_check:
                    duplicate_flag = True
                    duplicate_message = "This entry already exists. Please try again."
                    print(duplicate_message)
                    break
            if not duplicate_flag:
                insert_query = "INSERT INTO Courses_Campuses(course_id, campus_id) VALUES (%s, %s);"
                data = (course_id, campus_id,)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "You have successfully added a new course called " + course_name + "to the " + campus_name + " campus."

                course_campus_query = "SELECT cps.campus_id, cps.campus_name, crs.course_id, crs.course_name FROM Courses_Campuses cmb \
                        JOIN Courses crs ON cmb.course_id = crs.course_id \
                        JOIN Campuses cps ON cmb.campus_id = cps.campus_id;"
                course_campus_cursor = db.execute_query(db_connection=db_connection, query=course_campus_query)
                course_campus_results = course_campus_cursor.fetchall()

    db_connection.close()
    return render_template("campuses.html", items=select_results, students=population_results, courses=course_results, campuses=campus_results, courses_campuses=course_campus_results, images=images, count=student_results, post_message=post_message, delete_message=delete_message, update_message=update_message, remove_message=remove_message, duplicate_message=duplicate_message)

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
            # update record in Campuses table
            update_query = "UPDATE Campuses SET campus_name = %s, campus_city = %s, campus_country = %s, campus_online = %s WHERE campus_id = %s;"
            data = (campus_name, campus_city, campus_country, campus_online, id)
            update_cursor = db.execute_query(db_connection=db_connection, query=update_query, query_params=data)
        
        update_message = "You have updated campus id #" + str(id) + "."
        db_connection.close()
        return redirect(url_for('campuses', update_message=update_message, **request.args))
            
    else:
        db_connection.close()
        return render_template("campus_update.html", items=campus_results, post_message=post_message)

@app.route("/delete-campus/<int:id>")
def delete_campus(id):
    """Delete a campus from the Campuses table"""
    db_connection = db.connect_to_database()

    # delete record from Campuses table
    delete_query = "DELETE FROM Campuses WHERE campus_id = %s;"
    data=(id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted campus id #" + str(id) + ". All associated courses, sections, instructors and students will be deleted as well."

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
                if campus_name == campus: #do not insert if campus name is used in an existing record
                    flag = True
                    post_message = "The campus name is already in use. Please enter another name."
                    break

            if not flag:
                insert_query = "INSERT INTO Campuses(campus_name, campus_city, campus_country, campus_online) VALUES (%s, %s, %s, %s);"
                data = (campus_name, campus_city, campus_country, campus_online)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "You have successfully created a new campus, " + campus_name + ". Please note that new records have been automatically added to the Courses_Campuses table based on the existing records from the Courses table."

                new_campus_query = "SELECT * FROM Campuses WHERE campus_name = %s;"
                data = (campus_name,)
                new_campus_cursor = db.execute_query(db_connection=db_connection, query=new_campus_query, query_params=data)
                new_campus_results = new_campus_cursor.fetchall()

                # add new records to M:M relationship
                intersect_insert_query = "INSERT INTO Courses_Campuses(course_id, campus_id) SELECT course_id, campus_id FROM Courses t1 CROSS JOIN Campuses t2 WHERE t2.campus_id = %s;"
                for dict in new_campus_results:
                    campus_id = dict.get('campus_id')
                data = (campus_id,)
                intersect_insert_cursor = db.execute_query(db_connection=db_connection, query=intersect_insert_query, query_params=data)

    db_connection.close()
    return render_template("add_campuses.html", post_message=post_message)

@app.route("/delete-course-campus/<int:id1><int:id2>")
def delete_course_campus(id1, id2):
    """Delete a row from the Courses_Campuses intersection table """
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM Courses_Campuses WHERE course_id = %s and campus_id = %s;"
    data = (id1, id2,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted course id #" + str(id1) + " for campus id #" + str(id2) + "."

    db_connection.close()
    return redirect(url_for('campuses', remove_message=delete_message, **request.args))

# Instructors
@app.route("/instructors.html", methods=["GET", "POST"])
def instructors():
    """Display records from the Instructors table"""
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else "" #retrieve delete_message from GET request
    update_message = request.args.get("update_message") if request.args.get("update_message") else "" #retrieve update_message from GET request
    
    # select all records from Instructors table joined with Campuses
    instructor_query = "SELECT ins.*, cps.campus_name FROM Instructors ins LEFT JOIN Campuses cps ON ins.campus_id = cps.campus_id ORDER BY instructor_id ASC;"
    instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query)
    instructor_results = instructor_cursor.fetchall()

    campuses_query = "SELECT DISTINCT campus_id, campus_name FROM Campuses ORDER BY campus_id ASC;"
    campuses_cursor = db.execute_query(db_connection=db_connection, query=campuses_query)
    campuses_results = campuses_cursor.fetchall()

    db_connection.close()    
    return render_template("instructors.html", items=instructor_results, campuses=campuses_results, post_message=post_message, delete_message=delete_message, update_message=update_message)

@app.route("/update-instructor/<int:id>", methods=["GET", "POST"])
def update_instructor(id):
    """Update a record in the Instructors table"""
    db_connection = db.connect_to_database()
    post_message = ""

    instructor_query = "SELECT * FROM Instructors WHERE instructor_id = %s;"
    data = (id,)
    instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query, query_params=data)
    instructor_results = instructor_cursor.fetchall()
    print(instructor_results)

    select_query = "SELECT * FROM Campuses ORDER BY campus_id ASC;"
    select_cursor = db.execute_query(db_connection=db_connection, query=select_query)
    select_results = select_cursor.fetchall()
    print(select_results)

    if request.method == "POST":
        instructor_first_name = request.form['instructor_first_name']
        instructor_last_name = request.form['instructor_last_name']
        campus_name = request.form['campus_name']

        if campus_name != "Unassigned": #if campus_name is not null
            campus_query = "SELECT DISTINCT * FROM Campuses WHERE campus_name = %s;"
            data = (campus_name,)
            campus_cursor = db.execute_query(db_connection=db_connection, query=campus_query, query_params=data)
            campus_results = campus_cursor.fetchall()

            for dict in campus_results:
                campus_id = dict.get('campus_id')

        else: #if campus_name is null
            campus_id = None
        
        update_query = "UPDATE Instructors SET instructor_first_name = %s, instructor_last_name = %s, campus_id = %s WHERE instructor_id = %s;"
        data = (instructor_first_name, instructor_last_name, campus_id, id)
        update_cursor = db.execute_query(db_connection=db_connection, query=update_query, query_params=data)
        
        update_message = "You have updated instructor id #" + str(id) + "."
        db_connection.close()
        return redirect(url_for('instructors', update_message=update_message, **request.args))
            
    else:
        db_connection.close()
        return render_template("instructor_update.html", items=instructor_results, campuses=select_results, post_message=post_message)
    
@app.route("/delete-instructor/<int:id>")
def delete_instructor(id):
    """Delete an instructor from the Instructors table"""
    db_connection = db.connect_to_database()
    
    delete_query = "DELETE FROM Instructors WHERE instructor_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted instructor id #" + str(id) + ". All sections lectured by the instructor were also deleted."

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

        if instructor_first_name == "" or instructor_last_name == "": #fields cannot be blank or null
            post_message = "Please complete all fields in the form."

        if campus_name != "Unassigned": #if campus_name is not null
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
        
        else: #if campus_name is null
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
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else "" #retrieve delete_message from GET request
    
    # select more columns to display corresponding name attributes instead of displaying only IDs
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

    sections_query = "SELECT DISTINCT section_id FROM Sections;"
    sections_cursor = db.execute_query(db_connection=db_connection, query=sections_query)
    sections_results = sections_cursor.fetchall()
    
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
                return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result, sections=sections_results)
                
        if request.form['search_radio'] == 'course_name':
            course_name = request.form['course_name']
            if course_name == "":
                err_message = "Please enter valid Course Name."          
                return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result, sections=sections_results)
            else:
                course_name = "%" + course_name + "%"

        if request.form['search_radio'] == 'campus_name':
            campus_name = request.form['campus_name']
            if campus_name == "":
                err_message = "Please enter valid Campus Name."
                return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, courses=course_result, campuses=campus_result, sections=sections_results)
            else:
                campus_name = "%" + campus_name + "%"              
        
        # select any records that matches the search inputs
        search_query = "SELECT section_id, c.course_id, course_name, i.instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name) AS instructor_name, ca.campus_id, campus_name \
            FROM Sections s \
            JOIN Courses c ON s.course_id = c.course_id \
            JOIN Instructors i ON s.instructor_id = i.instructor_id \
            JOIN Campuses ca ON s.campus_id = ca.campus_id \
            WHERE section_id = %s OR c.course_name LIKE %s OR ca.campus_name LIKE %s \
            ORDER BY section_id ASC;"
        data = (section_id, course_name, campus_name)        
        search_cursor = db.execute_query(db_connection=db_connection, query=search_query, query_params=data)
        search_results = search_cursor.fetchall()
        
        # if no search result, display all rows
        if len(search_results) == 0: 
            err_message = "No search results founds."
            cursor.execute(query)
            search_results = cursor.fetchall()            
        return render_template("sections.html", items=search_results, post_message=post_message, err_message=err_message, delete_message=delete_message, courses=course_result, campuses=campus_result, sections=sections_results)
    
    db_connection.close()
    return render_template("sections.html", items=results, post_message=post_message, err_message=err_message, delete_message=delete_message, courses=course_result, campuses=campus_result, sections=sections_results)

@app.route("/add_sections.html", methods=["GET", "POST"])
def add_sections():
    """Add a section to the Sections table"""
    db_connection = db.connect_to_database()
    post_message = ""
    section_query = "SELECT * FROM Sections ORDER BY section_id ASC;"
    section_cursor = db.execute_query(db_connection=db_connection, query=section_query)
    section_results = section_cursor.fetchall()

    course_query = "SELECT * FROM Courses ORDER BY course_name ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()

    # select instructor name along with registered campus name. 
    # if no campus is assigned, the instructor will not appear in the dropdown datalist
    instructor_query = "SELECT instructor_id, CONCAT(instructor_first_name, ' ', instructor_last_name, ' (', c.campus_name, ')') AS instructor_name, i.campus_id \
                        FROM Instructors i \
                        JOIN Campuses c ON i.campus_id = c.campus_id \
                        ORDER BY instructor_name ASC;"

    instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query)
    instructor_results = instructor_cursor.fetchall()

    if request.method == "POST":
        course_name = request.form['course_name']
        instructor_name = request.form['instructor_name']

        # validate if the course name exists
        course_flag = False
        for dict in course_results:
            course = dict.get('course_name')
            if course_name == course:
                course_id = dict.get('course_id')
                course_flag = True
                break
            else:
                post_message = "The course name doesn't exist in the database. Please try again."
               
        # validate if the instructor name exists 
        instructor_flag = False
        for dict in instructor_results:
            instructor = dict.get('instructor_name')
            campus_id = dict.get('campus_id')

            if instructor_name == instructor:
                instructor_id = dict.get('instructor_id')
                instructor_flag = True
                break
            else:
                post_message = "The instructor doesn't exist in the database or is not assigned to any campus. Please try again."
        
        # if both course and instructor inputs are valid
        if course_flag and instructor_flag:
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
    return render_template("/add_sections.html", post_message=post_message, courses=course_results, instructors=instructor_results)

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
    post_message = "You have deleted section id #" + str(id) + "."

    db_connection.close()
    return redirect(url_for('sections', post_message=post_message, **request.args))

@app.route("/section_register.html", methods=["GET", "POST"])
def section_register():
    """"Display records from the Students & Sections intersection table and handles Students & Sections registration"""
    db_connection = db.connect_to_database()
    post_message = ""
    student_id = ""
    section_id = ""
    # query to select any records from Students_Sections table
    # more columns are added to display name attributes for the particular section_id and student_id
    query = "SELECT ss.student_id, CONCAT(student_first_name, ' ', student_last_name) as student_name, se.section_id, c.course_name, CONCAT(instructor_first_name, ' ', instructor_last_name) AS instructor_name, ca.campus_name \
        FROM Students_Sections ss \
        JOIN Students s ON ss.student_id = s.student_id \
        JOIN Sections se ON se.section_id = ss.section_id \
        JOIN Courses c ON c.course_id = se.course_id \
        JOIN Instructors i ON i.instructor_id = se.instructor_id\
        JOIN Campuses ca ON ca.campus_id = i.campus_id \
        ORDER BY student_id,section_id ASC;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()

    # select student names with each registered campus info, course names, instructor names with each registered campus for dropdown datalist
    students_query = "SELECT CONCAT(student_first_name, ' ', student_last_name, ' (', c.campus_name, ')') AS student_name \
        FROM Students s \
        JOIN Campuses c ON s.campus_id = c.campus_id \
        ORDER BY student_name ASC;"
    students_cursor = db.execute_query(db_connection=db_connection, query=students_query)
    students_results = students_cursor.fetchall()

    courses_query = "SELECT course_name FROM Courses ORDER BY course_name ASC;"
    courses_cursor = db.execute_query(db_connection=db_connection, query=courses_query)
    courses_results = courses_cursor.fetchall()

    # select instructor name as one string with registered campus
    # if no campus is assigned, the instructor will not appear in the dropdown datalist
    instructors_query = "SELECT CONCAT(instructor_first_name, ' ', instructor_last_name, ' (', c.campus_name, ')') AS instructor_name \
        FROM Instructors i \
        JOIN Campuses c ON i.campus_id = c.campus_id \
        ORDER BY instructor_name ASC;"
    instructors_cursor = db.execute_query(db_connection=db_connection, query=instructors_query)
    instructors_results = instructors_cursor.fetchall()
    
    # handle students & sections registration
    flag = False
    if request.method == "POST":
        student_name_split = str.split(request.form['student_name'])
        student_name = request.form['student_name']
        course_name = request.form['course_name']        
        instructor_name_split = str.split(request.form['instructor_name'])
        instructor_name = request.form['instructor_name']
        
        # if there is no input
        if student_name == "" or course_name == "" or instructor_name == "":
            flag = True
            post_message = "Please complete all fields in the form."            

        # check if the student name is valid
        student_flag = False
        for dict in students_results:
            student_full_name = dict.get('student_name')
            if student_name == student_full_name:
                student_flag = True
                break
            else:
                post_message = "The student does not exist in the database. Please try again."
        
        # check if the course name is valid
        course_flag = False
        for dict in courses_results:
            course_name1 = dict.get('course_name')
            if course_name1 == course_name:
                course_flag = True
                break
            else:
                post_message = "The course name does not exist in the database. Please try again."
                
        # check if the instructor name is valid
        instructor_flag = False
        for dict in instructors_results:
            instructor_full_name = dict.get('instructor_name')
            if instructor_full_name == instructor_name:
                instructor_flag = True
                break
            else:
                post_message = "The instructor does not exist in the database. Please try again."
                    
        # if all inputs are valid
        if student_flag and course_flag and instructor_flag:
            student_first_name = student_name_split[0]
            print(student_first_name)
            student_last_name = student_name_split[1]
            print(student_last_name)
            instructor_first_name = instructor_name_split[0]
            print(instructor_first_name)
            instructor_last_name = instructor_name_split[1]
            print(instructor_last_name)
                    
            # get student_id and campus_id for the given student name
            student_query = "SELECT student_id, campus_id FROM Students WHERE student_first_name = %s AND student_last_name = %s"
            data = (student_first_name, student_last_name)
            student_cursor = db.execute_query(db_connection=db_connection, query=student_query, query_params=data)
            student_results = student_cursor.fetchall()

            campus_id_student = ""
            for dict in student_results:
                student_id = dict.get('student_id')
                campus_id_student = dict.get('campus_id')

            # get campus_id for the given instructor name
            instructor_query = "SELECT campus_id FROM Instructors WHERE instructor_first_name = %s AND instructor_last_name = %s"
            data = (instructor_first_name, instructor_last_name)
            instructor_cursor = db.execute_query(db_connection=db_connection, query=instructor_query, query_params=data)
            instructor_results = instructor_cursor.fetchall()
            campus_id_instructor = ""
            for dict in instructor_results:
                campus_id_instructor = dict.get('campus_id')
            
            # validate if the student's campus and instructor's campus match
            if campus_id_student != campus_id_instructor:
                flag = True
                post_message = "The instructor does not teach at the student's campus."
    
            # get section_id for the given course_name and instructor name
            sections_query = "SELECT * FROM Sections se \
                JOIN Courses c ON c.course_id = se.course_id \
                JOIN Campuses ca ON ca.campus_id = se.campus_id \
                JOIN Instructors i ON i.instructor_id = se.instructor_id \
                WHERE course_name = %s and instructor_first_name = %s and instructor_last_name = %s;"
            data = (course_name, instructor_first_name, instructor_last_name)
            sections_cursor = db.execute_query(db_connection=db_connection, query=sections_query, query_params=data)
            sections_results = sections_cursor.fetchall()
            for dict in sections_results:
                section_id = dict.get('section_id')    
                
            for dict in results:
                student_id1 = dict.get('student_id')
                section_id1 = dict.get('section_id')
                print("Student ID1 is " + str(student_id1) + " and Section ID1 is " + str(section_id1))
                
                # if the student or section does not exist
                if student_id =="":
                    flag = True
                    post_message = "The student doesn't exist. Please enter a different value."    
                elif section_id == "":
                    flag = True
                    post_message = "The section doesn't exist. Please enter a different value."
                    
                # check for duplicate values    
                elif int(student_id1) == int(student_id) and int(section_id1) == int(section_id):
                    flag = True
                    post_message = "The section is already registered for the student. Please enter different values."
                    print("Duplicate")    
            
            # if inputs are valid, INSERT a new row to Students_Sections table
            if not flag:
                register_query = "INSERT INTO Students_Sections(student_id, section_id) VALUES (%s, %s);"
                data = (student_id, section_id,)
                register_cursor = db.execute_query(db_connection=db_connection, query=register_query, query_params=data)
                post_message = "You have successfully enrolled " + student_first_name + " " + student_last_name + " in section #" + str(section_id) + "."
    
    # disply updated table once a new record is created           
    query = "SELECT ss.student_id, CONCAT(student_first_name, ' ', student_last_name) AS student_name, se.section_id, c.course_name, CONCAT(instructor_first_name, ' ', instructor_last_name) as instructor_name, ca.campus_name \
        FROM Students_Sections ss \
        JOIN Students s ON ss.student_id = s.student_id \
        JOIN Sections se ON se.section_id = ss.section_id \
        JOIN Courses c ON c.course_id = se.course_id \
        JOIN Instructors i ON i.instructor_id = se.instructor_id\
        JOIN Campuses ca ON ca.campus_id = i.campus_id \
        ORDER BY student_id,section_id ASC;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
                
    db_connection.close()
    return render_template("section_register.html", items=results, students=students_results, courses=courses_results, instructors=instructors_results, post_message=post_message)

@app.route("/delete-student-section/<int:id1><int:id2>")
def delete_student_section(id1, id2):
    """Delete a row from the Students_Sections intersection table """
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM Students_Sections WHERE student_id = %s and section_id = %s;"
    data = (id1, id2,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    post_message = "You have deleted section id #" + str(id2) + " for student id #" + str(id1) + "."

    db_connection.close()
    return redirect(url_for('section_register', post_message=post_message, **request.args))

# Courses
@app.route("/courses.html", methods=["GET", "POST"])
def courses():
    """Display records from the Courses table"""
    db_connection = db.connect_to_database()
    post_message = ""
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else "" #retrieve delete_message from GET request

    course_query = "SELECT * FROM Courses ORDER BY course_id ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()
    
    db_connection.close()
    return render_template("courses.html", items=course_results, delete_message=delete_message)

@app.route("/delete-course/<int:id>")
def delete_course(id):
    """Delete a course from the Courses table"""
    db_connection = db.connect_to_database()
    delete_query = "DELETE FROM Courses WHERE course_id = %s;"
    data = (id,)
    delete_cursor = db.execute_query(db_connection=db_connection, query=delete_query, query_params=data)
    delete_message = "You have deleted course id #" + str(id) + ". All sections for the course were also deleted."

    db_connection.close()
    return redirect(url_for('courses', delete_message=delete_message, **request.args))

@app.route("/add_courses.html", methods=["GET", "POST"])
def add_courses():
    """Add a course to the Courses table"""
    db_connection = db.connect_to_database()
    post_message = ""

    course_query = "SELECT * FROM Courses ORDER BY course_id ASC;"
    course_cursor = db.execute_query(db_connection=db_connection, query=course_query)
    course_results = course_cursor.fetchall()

    # Handling POST form
    if request.method == "POST":
        course_name = request.form['course_name']
        print(course_name)

        if course_name == "":
            post_message = "Please enter a course name."
        else:
            flag = False
            # check for duplicate values
            for dict in course_results:
                course = dict.get('course_name')
                if course_name == course:
                    flag = True
                    post_message = "The course name is already in use. Please enter another name."
                    break
                
            # if input is valid, INSERT a new course
            if not flag:
                insert_query = "INSERT INTO Courses(course_name) VALUES (%s);"
                data = (course_name,)
                insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)
                post_message = "A new course, " + course_name + ", has been created. Please note that new records have been automatically added to the Courses_Campuses table based on the existing records from the Campuses table."

                new_course_query = "SELECT * FROM Courses WHERE course_name = %s;"
                data = (course_name,)
                new_course_cursor = db.execute_query(db_connection=db_connection, query=new_course_query, query_params=data)
                new_course_results = new_course_cursor.fetchall()

                # auto insert the corresponding FK attributes in the Courses_Campuses intersection table
                intersect_insert_query = "INSERT INTO Courses_Campuses(course_id, campus_id) SELECT course_id, campus_id FROM Courses t1 CROSS JOIN Campuses t2 WHERE t1.course_id = %s;"
                for dict in new_course_results:
                    course_id = dict.get('course_id')
                data = (course_id,)
                intersect_insert_cursor = db.execute_query(db_connection=db_connection, query=intersect_insert_query, query_params=data)

    db_connection.close()
    return render_template("add_courses.html", post_message=post_message)

# Students
@app.route("/students.html", methods=["GET", "POST"])
def students():
    """Display records from the Students table"""
    db_connection = db.connect_to_database()
    delete_message = request.args.get("delete_message") if request.args.get("delete_message") else ""

    # select all records from Students joined to Campuses
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
    delete_message = "You have deleted student id #" + str(id) + ". The student's section registration info was also deleted."

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

        if first_name == "" or last_name == "": #fields must not be blank or null
            post_message = "Please complete all fields in the form."
        else:
            for dict in campus_results:
                campus_name = dict.get('campus_name')
                if campus_name == campus: #get campus_id for campus_name chosen
                    campus_id = dict.get('campus_id')
                    print(campus_id)
        
            # insert new record into Students section
            insert_query = "INSERT INTO Students(student_first_name, student_last_name, campus_id) VALUES (%s, %s, %s);"
            data = (first_name, last_name, campus_id)
            insert_cursor = db.execute_query(db_connection=db_connection, query=insert_query, query_params=data)

            # get the student_id of the newly created record
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
