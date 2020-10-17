-- CREATE USER 'DBO'@'localhost' IDENTIFIED BY 'password';

#################################################
## Create User		#
#################################################

CREATE USER IF NOT EXISTS dbo@localhost IDENTIFIED BY 'password';

#################################################
## Drop Database If Exists			#
## Create Database				#
#################################################


DROP DATABASE IF EXISTS cs6400_su20_team08;
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS cs6400_su20_team08
        	DEFAULT CHARACTER SET utf8mb4
        	DEFAULT COLLATE utf8mb4_unicode_ci;

#################################################
## Grant All Privileges		#
#################################################

GRANT SELECT, INSERT, UPDATE, DELETE, FILE ON *.* TO 'dbo'@'localhost';
GRANT ALL PRIVILEGES ON *.*TO 'dbo'@'localhost';
GRANT ALL PRIVILEGES ON cs6400_su20_team08.* TO 'dbo'@'localhost';

#################################################
## Flush Privileges To Ensure They Take Affect	#
#################################################

FLUSH PRIVILEGES;
