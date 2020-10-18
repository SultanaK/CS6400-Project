## CS6400 Mo's Mutt House Project

## Getting Started

These instructions the Mo's Mutt House project up and running on your local machine for development and testing purposes. 

## Installation
Install Sublime: [https://www.sublimetext.com/3](https://www.sublimetext.com/3) 
Install MySQL Community Server 8.0.20: [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)

Unzip the Phase_3 to your desktop and open with Sublime.

## Configuring the application

Install required python modules before running the application:
	pip install Flask
	pip install Flask-WTF
	pip install Flask-Bcrypt
	pip install Flask-MySQL

Consider you are using Windows sytem, do the following steps to start MySQL server:
	1. Starting server
		a. Open Command Prompt as Administration
		b. cd to the location of \mysql-8.0.20-winx64\bin
		c. run mysqld --initialize --console command to initialize. A key will be created to login to MySQL server later.
		d. run mysqld command to start the server
	2. Starting client
		a. Open Command Prompt
		b. cd to the location of \mysql-8.0.20-winx64\bin
		c. run mysql -u root -p command and will ask you to enter the password. Please use the key that was generated in step 1.c
		d. Now you are in MySQL server
	
To create the user and database in MySQL:
	1. Open database_setup.sql file under setup folder
	2. Copy and paste sql statement in the command prompt
	3. A new user: "dbo" with password “password” is created if "dbo@localhost" is not exists
	4. All required privileges are given to the dbo user
	5. A new database named cs6400_su20_team08 is added

![ScreenShot](https://github.gatech.edu/CS6400-OMSA-2020-02-Summer/CS6400-2020-02-Team08/blob/master/Phase_3/image/db_setup.png)

```
define('MYSQL_DATABASE_HOST', "localhost");
define('MYSQL_DATABASE_USER', "dbo");
define('MYSQL_DATABASE_PASSWORD', "password");
define('MYSQL_DATABASE_DB', "cs6400_su20_team08");
```

Starting the application:
	1. Open Command Prompt
	2. cd to the location of Phase_3 project
	3. run python dogShelter.py command
	
Now launch the URL: 
[http://localhost:5000/Phase_3/](http://localhost:5000/Phase_3/)
 
Lastly, login as Admin with username and password below: 
```
username: mo@burdell.com
password: mo
```
You can also login as a Volunteer with username and password below:
```
username: walbares@conecom.com
password: pwd
```

### Congratulations!
You've successfully set up the Mo's Mutt House project on your local development machine!




