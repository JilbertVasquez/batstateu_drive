drop database batstateudrive;
CREATE DATABASE batstateudrive;
use batstateudrive;

CREATE TABLE users (
	userid int not null auto_increment,
    firstname varchar(255),
    lastname varchar(255),
    username varchar(255),
    email varchar(255),
    password varchar(255),
    primary key(userid),
    index(username)
);

CREATE TABLE file_details (
    file_id INT NOT NULL AUTO_INCREMENT,
    filename VARCHAR(255),
    size VARCHAR(50),
    extension VARCHAR(50),
    upload_date DATE,
    path VARCHAR(255),
    username VARCHAR(255),
    PRIMARY KEY (file_id),
    FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE share_files (
	share_id INT NOT NULL AUTO_INCREMENT,
    filename VARCHAR(255),
    extension VARCHAR(10),
    share_by VARCHAR(255),
    share_to VARCHAR(255),
    path VARCHAR(255),
    PRIMARY KEY (share_id)
);