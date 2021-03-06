DROP TABLE IF EXISTS Instructors;

CREATE TABLE Instructors(
    instructor_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    instructor_first_name VARCHAR(255) NOT NULL,
    instructor_last_name VARCHAR(255) NOT NULL,
    campus_id INT,
    FOREIGN KEY (campus_id) REFERENCES Campuses(campus_id) ON DELETE CASCADE
) ENGINE = InnoDB;

INSERT INTO Instructors(instructor_first_name, instructor_last_name, campus_id) 
VALUES
    ("Chuckie", "Finster", 1),
    ("Tommy", "Pickles", 1),
    ("Kimi", "Finster", 2),
    ("Matt", "Chung", 2),
    ("Edwin", "Deville", 3),
    ("Angel", "Carmin", 3)
;
