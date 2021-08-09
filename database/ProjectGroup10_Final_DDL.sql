-- SQL Statements (Data Definition Queries)

-- Drop tables if they exist
DROP TABLE IF EXISTS Students_Sections;
DROP TABLE IF EXISTS Courses_Campuses;
DROP TABLE IF EXISTS Sections;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Instructors;
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Campuses;

-- a) Data Definition Queries
CREATE TABLE Campuses(
    campus_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    campus_name VARCHAR(255) NOT NULL UNIQUE,
    campus_city TEXT,
    campus_country TEXT,
    campus_online BOOLEAN
) ENGINE = InnoDB;

CREATE TABLE Instructors(
    instructor_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    instructor_first_name VARCHAR(255) NOT NULL,
    instructor_last_name VARCHAR(255) NOT NULL,
    campus_id INT,
    FOREIGN KEY (campus_id) REFERENCES Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE Students(
    student_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    student_first_name VARCHAR(255) NOT NULL,
    student_last_name VARCHAR(255) NOT NULL,
    campus_id INT NOT NULL,
    FOREIGN KEY (campus_id) references Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE Courses(
    course_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB;

CREATE TABLE Sections(
    section_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    campus_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id) ON DELETE CASCADE,
    FOREIGN KEY (campus_id) REFERENCES Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE Students_Sections(
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    PRIMARY KEY(student_id, section_id),
    FOREIGN KEY(student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES Sections(section_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE Courses_Campuses(
    course_id INT NOT NULL,
    campus_id INT NOT NULL,
    PRIMARY KEY(course_id, campus_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY(campus_id) REFERENCES Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- b) Sample Data:
INSERT INTO Campuses(campus_name, campus_city, campus_country, campus_online)
VALUES 
    ("Corvallis", "Corvallis", "United States of America", TRUE), 
    ("Davis", "Los Angeles", "United States of America", FALSE), 
    ("Washington", "Seattle", "United States of America", TRUE)
;

INSERT INTO Instructors(instructor_first_name, instructor_last_name, campus_id) 
VALUES
    ("Chuckie", "Finster", 1),
    ("Tommy", "Pickles", 1),
    ("Kimi", "Finster", 2),
    ("Matt", "Chung", 2),
    ("Edwin", "Deville", 3),
    ("Angel", "Carmin", 3)
;

INSERT INTO Students(student_first_name, student_last_name, campus_id) 
VALUES 
    ("Amal", "Chamlee", 1),
    ("Clair", "Hansel", 1),
    ("David", "Byer", 2),
    ("Drew", "Kenyon", 3),
    ("John", "Snow", 3)
;

INSERT INTO Courses(course_name)
VALUES 
    ("Introduction to Databases"), 
    ("Introduction to Computer Science"), 
    ("Software Engineering")
;

INSERT INTO Sections(course_id, instructor_id, campus_id) 
VALUES
    (
        (SELECT course_id FROM Courses WHERE course_id = 1),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 1),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 1)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 1),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 2),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 2)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 1),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 3),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 3)
    ),(        
        (SELECT course_id FROM Courses WHERE course_id = 1),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 4),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 4)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 1),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 5),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 5)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 2),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 1),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 1)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 2),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 2),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 2)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 2),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 3),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 3)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 2),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 4),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 4)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 2),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 5),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 5)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 3),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 1),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 1)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 3),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 2),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 2)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 3),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 3),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 3)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 3),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 4),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 4)
    ),(
        (SELECT course_id FROM Courses WHERE course_id = 3),
        (SELECT instructor_id FROM Instructors WHERE instructor_id = 5),
        (SELECT campus_id FROM Instructors WHERE instructor_id = 5)
    );

INSERT INTO Students_Sections(student_id, section_id)
VALUES 
    (1,1), 
    (2,1), 
    (3,2)
;

INSERT INTO Courses_Campuses(course_id, campus_id)
SELECT course_id, campus_id
FROM Courses AS t1
CROSS JOIN Campuses as t2
;
