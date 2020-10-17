-- CREATE USER 'DBO'@'localhost' IDENTIFIED BY 'password';

CREATE USER IF NOT EXISTS dbo@localhost IDENTIFIED BY 'password';

DROP DATABASE IF EXISTS cs6400_su20_team08;
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS cs6400_su20_team08
        	DEFAULT CHARACTER SET utf8mb4
        	DEFAULT COLLATE utf8mb4_unicode_ci;
USE cs6400_su20_team08;

GRANT SELECT, INSERT, UPDATE, DELETE, FILE ON *.* TO 'dbo'@'localhost';
GRANT ALL PRIVILEGES ON *.*TO 'dbo'@'localhost';
GRANT ALL PRIVILEGES ON cs6400_su20_team08.* TO 'dbo'@'localhost';
FLUSH PRIVILEGES;

-- Tables

CREATE TABLE User(
        	email varchar(250) NOT NULL,
        	password varchar(50) NOT NULL,
        	first_name varchar(50) NOT NULL,
        	last_name varchar(50) NOT NULL,
        	phone_number varchar (20) NOT NULL,
        	start_date date NOT NULL,
        	PRIMARY KEY (email),
        	UNIQUE KEY phone_number (phone_number)
);

CREATE TABLE Admin(
        	email varchar(250) NOT NULL,
        	PRIMARY KEY (email)
);

CREATE TABLE Dog(
        	dogID int(16) unsigned NOT NULL AUTO_INCREMENT,
        	name varchar(50) NOT NULL,
        	sex varchar(10) NOT NULL,
        	alteration_status varchar(10) NOT NULL,
        	age int(3) NOT NULL,
        	description varchar(100) NOT NULL,
        	PRIMARY KEY(dogID)
);

CREATE TABLE Microchip(
        	dogID int(16) unsigned NOT NULL,
        	microchipID varchar(100) NOT NULL,
        	PRIMARY KEY (microchipID), 
        	UNIQUE (dogID)
);

CREATE TABLE Surrender(
        	dogID int(16) unsigned NOT NULL,
        	email varchar(250) NOT NULL,
        	date date NOT NULL,
        	reason varchar(100) NOT NULL,
        	animal_control boolean,
        	PRIMARY KEY(dogID, email)
);

CREATE TABLE Breed(
        	breed_name varchar(50) NOT NULL,
        	PRIMARY KEY(breed_name)
);

CREATE TABLE DogBreed(
        	dogID int(16) unsigned NOT NULL,
        	breed_name varchar(50) NOT NULL,
		UNIQUE (dogID, breed_name)
);

CREATE TABLE Vendor(
        	name varchar(50) NOT NULL,
        	PRIMARY KEY(name),
		UNIQUE KEY name(name)
);

CREATE TABLE Expense(
        	dogID int(16) unsigned NOT NULL,
        	vendor_name varchar(50) NOT NULL,
        	date date NOT NULL,
        	amount float(6,2) NOT NULL,
        	description varchar(100) NULL,
        	UNIQUE (dogID, vendor_name, date),
        	PRIMARY KEY(dogID, vendor_name, date)
);

CREATE TABLE Applicant(
        	email varchar(250) NOT NULL,
        	first_name varchar(50) NOT NULL,
        	last_name varchar(50) NOT NULL,
        	phone_number varchar (20) NOT NULL,
        	street varchar(100) NOT NULL,
        	city varchar (50) NOT NULL,
        	zip_code int(5) NOT NULL,
        	state varchar(2) NOT NULL,
        	PRIMARY KEY (email),
		UNIQUE KEY phone_number (phone_number)
);

CREATE TABLE Application(
        	applicationID int(16) unsigned NOT NULL AUTO_INCREMENT,
        	applicant_email varchar(250) NOT NULL,
        	date date NOT NULL,
        	co_applicant_first_name varchar(50) NULL,
        	co_applicant_last_name varchar(50) NULL,
        	user_email varchar(250) NOT NULL,
        	PRIMARY KEY(applicationID)
);

CREATE TABLE Approved(
        	applicationID int(16) unsigned NOT NULL,
        	PRIMARY KEY(applicationID)
);

CREATE TABLE Rejected(
        	applicationID int(16) unsigned NOT NULL,
        	PRIMARY KEY(applicationID)
);



CREATE TABLE Adoption(
        	dogID int(16) unsigned NOT NULL,
        	applicationID int(16) unsigned NOT NULL,
        	date date NOT NULL,
        	fee float(8,2) NOT NULL,
        	admin_email varchar(250) not null,
        	PRIMARY KEY(dogID,applicationID)
        	);


-- Constraints

ALTER TABLE Admin
ADD CONSTRAINT fk_Admin_email_User_email FOREIGN KEY (email) REFERENCES User(email);

ALTER TABLE Approved
ADD CONSTRAINT fk_Approved_applicationID_Application_applicationID FOREIGN KEY (applicationID) REFERENCES Application(applicationID);

ALTER TABLE Rejected
ADD CONSTRAINT fk_Rejected_applicationID_Application_applicationID FOREIGN KEY (applicationID) REFERENCES Application(applicationID);

ALTER TABLE Microchip
ADD CONSTRAINT fk_Microchip_dogID_Dog_dogID FOREIGN KEY(dogID) REFERENCES  Dog(dogID) ON UPDATE CASCADE;

ALTER TABLE DogBreed
ADD CONSTRAINT fk_DogBreed_dogID_Dog_dogID FOREIGN KEY(dogID) REFERENCES  Dog(dogID) ON UPDATE CASCADE,
ADD CONSTRAINT fk_DogBreed_breed_name_DogBreed_breed_name FOREIGN KEY(breed_name) REFERENCES Breed(breed_name) ON UPDATE CASCADE;

ALTER TABLE Adoption
ADD CONSTRAINT fk_Adoption_dogID_Dog_dogID FOREIGN KEY(dogID) REFERENCES  Dog(dogID),
ADD CONSTRAINT fk_Adoption_applicationID_Application_applicationID FOREIGN KEY(applicationID) REFERENCES Application(applicationID),
ADD CONSTRAINT fk_Adoption_admin_email_Admin_email FOREIGN KEY (admin_email) REFERENCES Admin(email);

ALTER TABLE Surrender
ADD CONSTRAINT fk_Surrender_dogID_Dog_dogID FOREIGN KEY(dogID) REFERENCES  Dog(dogID),
ADD CONSTRAINT fk_Surrender_email_User_email FOREIGN KEY(email) REFERENCES User(email);

ALTER TABLE Application
ADD CONSTRAINT fk_Application_user_email_User_email FOREIGN KEY (user_email) REFERENCES User(email),
ADD CONSTRAINT fk_Application_applicant_email_Applicant_email FOREIGN KEY (applicant_email) REFERENCES Applicant(email);

ALTER TABLE Expense
ADD CONSTRAINT fk_Expense_dogID_Dog_dogID FOREIGN KEY (dogID) REFERENCES Dog(dogID),
ADD CONSTRAINT fk_Expense_vendor_namel_Vendor_name FOREIGN KEY (vendor_name) REFERENCES Vendor(name);



