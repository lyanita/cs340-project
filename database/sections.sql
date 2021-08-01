DROP TABLE IF EXISTS Sections;

CREATE TABLE Sections(
    section_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    campus_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id) ON DELETE CASCADE,
    FOREIGN KEY (campus_id) REFERENCES Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

INSERT INTO Sections(course_id, instructor_id, campus_id) 
VALUES
    (
        (SELECT course_id FROM Courses WHERE course_name = "Introduction to Databases"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Chuckie" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Corvallis")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Introduction to Databases"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Kimi" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Davis")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Introduction to Databases"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Edwin" and instructor_last_name = "Deville"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Washington")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Introduction to Computer Science"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Chuckie" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Corvallis")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Introduction to Computer Science"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Kimi" and instructor_last_name = "Finster"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Davis")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Introduction to Computer Science"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Edwin" and instructor_last_name = "Deville"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Washington")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Software Engineering"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Tommy" and instructor_last_name = "Pickles"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Corvallis")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Software Engineering"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Matt" and instructor_last_name = "Chung"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Davis")
    ),(
        (SELECT course_id FROM Courses WHERE course_name = "Software Engineering"),
        (SELECT instructor_id FROM Instructors WHERE instructor_first_name = "Angel" and instructor_last_name = "Carmin"),
        (SELECT campus_id FROM Campuses WHERE campus_name = "Washington")
    );

