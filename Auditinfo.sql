USE project;
DROP TABLE IF EXISTS AuditInfo;
CREATE TABLE IF NOT EXISTS AuditInfo (
	id int NOT NULL AUTO_INCREMENT,
    username varchar(255) NOT NULL,
	login varchar(255) NOT NULL,
    logout varchar(255) NOT NULL,
    city varchar(100) NOT NULL,
    country varchar(100) NOT NULL,
    continent varchar(100) NOT NULL,
    is_vpn varchar(10) NOT NULL,
	PRIMARY KEY (id)
)ENGINE=InnoDB AUTO_INCREMENT=2;