DROP TABLE IF EXISTS Campuses;

CREATE TABLE Campuses(
    campus_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    campus_name VARCHAR(255) NOT NULL UNIQUE,
    campus_city TEXT,
    campus_country TEXT,
    campus_online BOOLEAN
) ENGINE = InnoDB;

INSERT INTO Campuses(campus_name, campus_city, campus_country, campus_online)
VALUES 
    ("Corvallis", "Corvallis", "United States of America", TRUE), 
    ("Davis", "Los Angeles", "United States of America", FALSE), 
    ("Washington", "Seattle", "United States of America", TRUE)
;
