CREATE TABLE courses(
    course_id INT(10) PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(255) NOT NULL UNIQUE
);

INSERT INTO courses(course_name)
VALUES ("Introduction to Databases"), ("Introduction to Computer Science"), ("Software Engineering");