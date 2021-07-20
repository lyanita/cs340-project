DROP TABLE IF EXISTS courses_campuses;

CREATE TABLE courses_campuses(
    course_id INT NOT NULL,
    campus_id INT NOT NULL,
    PRIMARY KEY(course_id, campus_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id),
    FOREIGN KEY(campus_id) REFERENCES campuses(campus_id)
);