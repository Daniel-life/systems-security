DROP DATABASE IF EXISTS project;
CREATE DATABASE IF NOT EXISTS project;
USE project;
DROP TABLE IF EXISTS Accounts;
CREATE TABLE IF NOT EXISTS Accounts (
	id int NOT NULL AUTO_INCREMENT,
	username varchar(50) NOT NULL,
    firstname varchar(50) NOT NULL,
    lastname varchar(50) NOT NULL,
	password varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
    gender varchar(10) NOT NULL,
    address varchar(255) NOT NULL,
    symmetrickey varchar(255) NULL,
	PRIMARY KEY (id)
)ENGINE=InnoDB AUTO_INCREMENT=2;


INSERT INTO `project`.`accounts`
(`username`,`firstname`, `lastname`,`password`,`email`,`gender`,`address`, `symmetrickey`)
VALUES
('user', 'Jim', 'Tan','password','email@email.com', 'Male', '123 Tampines Ave', 'testsymmetrickey');