DROP TABLE sections;

CREATE TABLE sections(
    section_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    instructor_id INT,
    campus_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id),
    FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
);

INSERT INTO sections(course_id, instructor_id, campus_id) 
VALUES
    (
        (SELECT course_id FROM courses WHERE course_name = "Introduction to Databases"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Chuckie" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Corvallis")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Introduction to Databases"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Kimi" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Davis")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Introduction to Databases"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Edwin" and instructor_last_name = "Deville"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Washington")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Introduction to Computer Science"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Chuckie" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Corvallis")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Introduction to Computer Science"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Kimi" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Davis")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Introduction to Computer Science"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Edwin" and instructor_last_name = "Deville"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Washington")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Software Engineering"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Tommy" and instructor_last_name = "Pickles"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Corvallis")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Software Engineering"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Matt" and instructor_last_name = "Chung"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Davis")
    ),(
        (SELECT course_id FROM courses WHERE course_name = "Software Engineering"),
        (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Angel" and instructor_last_name = "Carmin"),
        (SELECT campus_id FROM campuses WHERE campus_name = "Washington")
    );
