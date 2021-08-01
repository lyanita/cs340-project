DROP TABLE IF EXISTS Courses;

CREATE TABLE Courses(
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB;

INSERT INTO Courses(course_name)
VALUES 
    ("Introduction to Databases"), 
    ("Introduction to Computer Science"), 
    ("Software Engineering")
;
