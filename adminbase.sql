DROP DATABASE IF EXISTS adminbase;
CREATE DATABASE IF NOT EXISTS adminbase;
USE adminbase;
DROP TABLE IF EXISTS admin_account;
CREATE TABLE IF NOT EXISTS admin_account (
	id int NOT NULL AUTO_INCREMENT,
	username varchar(50) NOT NULL,
    firstname varchar(50) NOT NULL,
    lastname varchar(50) NOT NULL,
	password varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
    gender varchar(10) NOT NULL,
    address varchar(255) NOT NULL,
    number varchar(20) NOT NULL,
    symmetrickey varchar(255) NULL,
	PRIMARY KEY (id)
)ENGINE=InnoDB AUTO_INCREMENT=2;
