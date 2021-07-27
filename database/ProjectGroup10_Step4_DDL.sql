-- SQL Statements (Data Definition Queries)

-- Drop tables if they exist
DROP TABLE IF EXISTS students_sections;
DROP TABLE IF EXISTS courses_campuses;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS instructors;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS campuses;

-- a) Data Definition Queries
CREATE TABLE campuses(
    campus_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    campus_name VARCHAR(255) NOT NULL UNIQUE,
    campus_city TEXT,
    campus_country TEXT,
    campus_online BOOLEAN
) ENGINE = InnoDB;

CREATE TABLE instructors(
    instructor_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    instructor_first_name VARCHAR(255) NOT NULL,
    instructor_last_name VARCHAR(255) NOT NULL,
    campus_id INT,
    FOREIGN KEY (campus_id) REFERENCES campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE students(
    student_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    student_first_name VARCHAR(255) NOT NULL,
    student_last_name VARCHAR(255) NOT NULL,
    campus_id INT NOT NULL,
    FOREIGN KEY (campus_id) references campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE courses(
    course_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB;

CREATE TABLE sections(
    section_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    campus_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE CASCADE,
    FOREIGN KEY (campus_id) REFERENCES campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE students_sections(
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    PRIMARY KEY(student_id, section_id),
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES sections(section_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE courses_campuses(
    course_id INT NOT NULL,
    campus_id INT NOT NULL,
    PRIMARY KEY(course_id, campus_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY(campus_id) REFERENCES campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- b) Sample Data:
INSERT INTO campuses(campus_name, campus_city, campus_country, campus_online)
VALUES 
    ("Corvallis", "Corvallis", "United States of America", TRUE), 
    ("Davis", "Los Angeles", "United States of America", FALSE), 
    ("Washington", "Seattle", "United States of America", TRUE)
;

INSERT INTO instructors(instructor_first_name, instructor_last_name, campus_id) 
VALUES
    ("Chuckie", "Finster", 1),
    ("Tommy", "Pickles", 1),
    ("Kimi", "Finster", 2),
    ("Matt", "Chung", 2),
    ("Edwin", "Deville", 3),
    ("Angel", "Carmin", 3)
;

INSERT INTO students(student_first_name, student_last_name, campus_id) 
VALUES 
    ("Amal", "Chamlee", 1),
    ("Clair", "Hansel", 1),
    ("David", "Byer", 2),
    ("Drew", "Kenyon", 3),
    ("John", "Snow", 3)
;

INSERT INTO courses(course_name)
VALUES 
    ("Introduction to Databases"), 
    ("Introduction to Computer Science"), 
    ("Software Engineering")
;

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

INSERT INTO students_sections(student_id, section_id)
VALUES 
    (1,1), 
    (1,2), 
    (2,2)
;

INSERT INTO courses_campuses(course_id, campus_id)
SELECT course_id, campus_id
FROM courses AS t1
CROSS JOIN campuses as t2
;
