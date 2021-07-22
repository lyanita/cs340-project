DROP TABLE IF EXISTS students_sections;

CREATE TABLE students_sections(
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    PRIMARY KEY(student_id, section_id),
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES sections(section_id) ON DELETE CASCADE
) ENGINE = InnoDB;

INSERT INTO students_sections(student_id, section_id)
SELECT student_id, section_id
FROM students AS t1
CROSS JOIN sections AS t2
;
