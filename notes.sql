CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_of_birth DATE ,
    date_of_upload DATE NOT NULL,
    first_name VARCHAR(255) ,
    last_name VARCHAR(255) ,
    data JSON
);