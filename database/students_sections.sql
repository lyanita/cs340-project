DROP TABLE IF EXISTS Students_Sections;

CREATE TABLE Students_Sections(
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    PRIMARY KEY(student_id, section_id),
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES sections(section_id) ON DELETE CASCADE
) ENGINE = InnoDB;

INSERT INTO Students_Sections(student_id, section_id)
VALUES 
    (1,1), 
    (2,1), 
    (3,2)
;
