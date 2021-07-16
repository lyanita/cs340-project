DROP TABLE sections;

CREATE TABLE sections(
    section_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    instructor_id INT,
    campus_id INT,
    max_occupancy INT NOT NULL,
    current_occupancy INT NOT NULL,
    CHECK (current_occupancy <= max_occupancy),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id),
    FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
);

INSERT INTO sections(course_id, instructor_id, campus_id, max_occupancy, current_occupancy) 
VALUES
    (SELECT course_id FROM courses WHERE course_name = "Introduction to Databases"),
    (SELECT instructor_id FROM instructors WHERE instructor_first_name = "Tommy" and instructor_last_name = "Pickles"),
    (SELECT campus_id FROM campuses WHERE campus_id = "1"), 30
    -- need to insert query for current_occupancy)
)