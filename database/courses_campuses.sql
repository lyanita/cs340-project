DROP TABLE IF EXISTS Courses_Campuses;

CREATE TABLE Courses_Campuses(
    course_id INT NOT NULL,
    campus_id INT NOT NULL,
    PRIMARY KEY(course_id, campus_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY(campus_id) REFERENCES campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

INSERT INTO Courses_Campuses(course_id, campus_id)
SELECT course_id, campus_id
FROM courses AS t1
CROSS JOIN campuses as t2
;
