DROP TABLE IF EXISTS Courses_Campuses;

CREATE TABLE Courses_Campuses(
    course_id INT NOT NULL,
    campus_id INT NOT NULL,
    PRIMARY KEY(course_id, campus_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY(campus_id) REFERENCES Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

INSERT INTO Courses_Campuses(course_id, campus_id)
SELECT course_id, campus_id
FROM Courses AS t1
CROSS JOIN Campuses as t2
;
