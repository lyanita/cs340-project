DROP TABLE IF EXISTS instructors;

CREATE TABLE instructors(
    instructor_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    instructor_first_name VARCHAR(255) NOT NULL,
    instructor_last_name VARCHAR(255) NOT NULL,
    campus_id INT,
    FOREIGN KEY (campus_id) REFERENCES campuses(campus_id) ON DELETE CASCADE
);

INSERT INTO instructors(instructor_first_name, instructor_last_name, campus_id) 
VALUES
    ("Chuckie", "Finster", 1),
    ("Tommy", "Pickles", 1),
    ("Kimi", "Finster", 2),
    ("Matt", "Chung", 2),
    ("Edwin", "Deville", 3),
    ("Angel", "Carmin", 3)
;