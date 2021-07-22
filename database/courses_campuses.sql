DROP TABLE IF EXISTS courses_campuses;

CREATE TABLE courses_campuses(
    course_id INT NOT NULL,
    campus_id INT NOT NULL,
    PRIMARY KEY(course_id, campus_id),
    CONSTRAINT course_id_ref FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    CONSTRAINT campus_id_ref FOREIGN KEY(campus_id) REFERENCES campuses(campus_id) ON DELETE CASCADE
);

INSERT INTO courses_campuses(course_id, campus_id)
SELECT course_id, campus_id
FROM courses AS t1
CROSS JOIN campuses as t2
;