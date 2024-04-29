drop database batstateudrive;
CREATE DATABASE batstateudrive;
-- use batstateudrive;

-- CREATE TABLE users (
-- 	userid int not null auto_increment,
--     firstname varchar(255),
--     lastname varchar(255),
--     username varchar(255),
--     email varchar(255),
--     password varchar(255),
--     primary key(userid)
-- );

-- CREATE TABLE file_details (
--     file_id INT NOT NULL AUTO_INCREMENT,
--     filename VARCHAR(255),
--     size VARCHAR(50),
--     extension VARCHAR(50),
--     upload_date DATE,
--     path VARCHAR(1000),
--     user_id INT,
--     PRIMARY KEY (file_id),
--     FOREIGN KEY (user_id) REFERENCES users(userid)
-- );

-- CREATE TABLE share_files (
-- 	share_id INT NOT NULL AUTO_INCREMENT,
--     file_id INT,
--     filename VARCHAR(255),
--     extension VARCHAR(10),
--     share_by VARCHAR(255),
--     share_to VARCHAR(255),
--     path VARCHAR(1000),
--     PRIMARY KEY (share_id),
--     FOREIGN KEY (file_id) REFERENCES file_details(file_id)
-- );