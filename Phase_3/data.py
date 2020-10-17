def query_login(cursor, email, password):
	query = """
			SELECT
				* 
			FROM
				User 
			WHERE
				email = %s 
				and password = %s ;
			"""
	params = (email, password)
	cursor.execute(query, params)
	query_result = cursor.fetchone()
	return query_result

def query_max_dogid(cursor):
	query = """
			SELECT
				MAX(dogID) 
			FROM
				Dog;
			"""
	cursor.execute(query)
	query_result = cursor.fetchone()[0]
	return query_result

def query_add_dog(cursor, conn, name, sex, alteration_status, age, description, breed_names, microchipID, email,surrender_date,reason, ac):
	maxid = query_max_dogid(cursor)+1

	query2 = """
			INSERT 
			INTO
				Dog
			VALUES
				(%s,%s,%s,%s,%s,%s);
			"""
	params2 = (maxid,name, sex, alteration_status, age, description)
	cursor.execute(query2, params2)

	for breed in breed_names:
		query3 = """
				INSERT 
				INTO
					DogBreed
					
				VALUES
					(%s, %s)
				"""
		params3 = (maxid, breed)
		cursor.execute(query3, params3)

	if microchipID != '':
		query4 = """
				INSERT 
				INTO
					Microchip
				VALUES
					(%s,%s);
				"""
		params4 = (maxid, microchipID)
		cursor.execute(query4, params4)

	query5 = """
			INSERT 
			INTO
				Surrender
			VALUES
				(%s,%s,%s,%s,%s);
			"""
	params5 = (maxid,email,surrender_date,reason, ac)
	cursor.execute(query5, params5)

	conn.commit()

def query_view_dog_dashboard(cursor):
	query = """ SELECT
				Dog.dogID,
				name,
				age,
				sex,
				alteration_status,
				CASE 
					WHEN ((alteration_status = 'altered') AND (Microchip.microchipID IS NOT NULL)) THEN 'Yes' 
					ELSE 'No' 
				END AS adoptability_status,
				ConBreed.ConcatBreeds AS breed_name,
				Surrender.date
			FROM
				Dog 
			LEFT JOIN
				(
					SELECT
						dogID,
						GROUP_CONCAT(DISTINCT breed_name 
					ORDER BY
						breed_name SEPARATOR '/') AS ConcatBreeds 
					FROM
						DogBreed 
					GROUP BY
						dogID
				) AS ConBreed 
					ON Dog.dogID = ConBreed.dogID 
			LEFT JOIN
				Surrender 
					ON Dog.dogID = Surrender.dogID 
			LEFT JOIN
				Microchip	 
					ON Dog.dogID = Microchip.dogID	 
			WHERE
				Dog.dogID not in (
					SELECT
						dogID 
					FROM
						Adoption
				)  
			ORDER BY
				Surrender.date;
			"""
	cursor.execute(query)
	query_result = cursor.fetchall()
	return query_result

def query_available_space(cursor):
	query = """	SELECT
					15-((SELECT
						COUNT(*) 
					FROM
						Dog) - (SELECT
						COUNT(*) 
					FROM
						Adoption)) AS Difference
			"""
	cursor.execute(query)
	query_result = cursor.fetchone()
	return query_result[0]

def query_review_application(cursor, conn):
	query = """	SELECT
					Application.applicationID,
					Application.Date,
					Applicant.First_Name,
					Applicant.Last_Name,
					Applicant.Email,
					Application.Co_Applicant_First_Name,
					Application.Co_Applicant_Last_Name,
					Applicant.Street,
					Applicant.City,
					Applicant.State,
					Applicant.Zip_Code,
					Applicant.Phone_Number 
				FROM
					Application,
					Applicant 
				WHERE
					Application.Applicant_Email = Applicant.Email 
					AND Application.ApplicationID NOT IN (
						SELECT
							applicationID 
						FROM
							Approved
					) 
					AND Application.ApplicationID NOT IN (
						SELECT
							applicationID 
						FROM
							Rejected
					);
			"""
	cursor.execute(query)
	conn.commit()
	query_result = cursor.fetchall()
	return query_result

def query_approve_application(cursor, conn, application_number):
	query = "INSERT INTO approved VALUES (%s);"
	params = (application_number)
	cursor.execute(query, params)
	conn.commit()

def query_reject_application(cursor, conn, application_number):
	query = "INSERT INTO rejected VALUES (%s);"
	params = (application_number)
	cursor.execute(query, params)
	conn.commit()
	
def query_report_animal_control_summary(cursor):
	query = """	
		WITH	 
			-- the count of dogs turned over by animal control   
			t1 AS (SELECT
				DATE_FORMAT(DATE_FORMAT(Surrender.date ,
				'%Y-%m-01'),
				"%b %Y") AS Month,
				Count(Surrender.dogID) AS NumberSurrenderedDogs	 
			FROM
				Surrender	 
			WHERE
				animal_control = true	 
				AND Surrender.date between DATE_SUB(DATE_FORMAT(NOW() ,'%Y-%m-01'), INTERVAL 6 MONTH) AND NOW()	 
			GROUP BY
				DATE_FORMAT(DATE_FORMAT(Surrender.date ,
				'%Y-%m-01'),
				"%b %Y"),
				DATE_FORMAT(Surrender.date ,
				'%Y-%m-01')	 
			ORDER BY
				DATE_FORMAT(Surrender.date ,
				'%Y-%m-01')),
			-- the count of any dogs adopted during that month who had spent in the rescue 60 days or more and total expense from them	   
			t2 AS (SELECT
				DATE_FORMAT(DATE_FORMAT(Adoption.Date ,
				'%Y-%m-01'),
				"%b %Y") AS Month,
				Count(Surrender.DogID) AS NumberAdoptedDogsInShelter60Days,
                SUM(TotalExpense) AS TotalExpenseFromAdoptedDogsInShelter60Days
			FROM
				Surrender 
			INNER JOIN
				Adoption	 
				ON Surrender.DogID = Adoption.DogID
			LEFT JOIN (SELECT DogID, SUM(amount) AS TotalExpense FROM Expense GROUP BY DogID) AS TotalExpense
				ON Surrender.DogID = TotalExpense.DogID
			WHERE DATEDIFF(Adoption.Date,
				Surrender.Date) >= 60	 
				AND Adoption.Date between DATE_SUB(DATE_FORMAT(NOW() ,
				'%Y-%m-01'),
				INTERVAL 6 MONTH) AND NOW()	 
			GROUP BY
				DATE_FORMAT(DATE_FORMAT(Adoption.Date ,
				'%Y-%m-01'),
				"%b %Y"),
				DATE_FORMAT(Adoption.Date ,
				'%Y-%m-01')	 
			ORDER BY
				DATE_FORMAT(Adoption.Date ,
				'%Y-%m-01'))
			SELECT
				Month,
				IFNULL(NumberSurrenderedDogs,
				0) AS `Number Animal Control Dogs`,
				IFNULL(NumberAdoptedDogsInShelter60Days,
				0) AS `Number Adopted Dogs In Shelter For 60 Days`,
				IFNULL(TotalExpenseFromAdoptedDogsInShelter60Days,
				0) AS `Total Expense By Adopted Dogs In Shelter For 60 Days`		 
			FROM
				(SELECT
						COALESCE(t1.Month,
						t2.Month) AS Month,
						NumberSurrenderedDogs,
						NumberAdoptedDogsInShelter60Days,
                        TotalExpenseFromAdoptedDogsInShelter60Days
					FROM
						t1	 
					LEFT OUTER JOIN
						t2 
							ON t1.Month = t2.Month	 
					UNION
					SELECT
						COALESCE(t1.Month,
						t2.Month) AS Month,
						NumberSurrenderedDogs,
						NumberAdoptedDogsInShelter60Days,
                        TotalExpenseFromAdoptedDogsInShelter60Days
					FROM
						t1	 
					RIGHT OUTER JOIN
						t2 
							ON t1.Month = t2.Month) j
		ORDER BY
		DATE(Month);
		"""
	cursor.execute(query)
	query_result = cursor.fetchall()
	return query_result

def query_report_animal_control_detail1(cursor):
	query = """
			SELECT
				DATE_FORMAT(DATE_FORMAT(Surrender.date ,
				'%Y-%m-01'),
				"%b %Y") AS Month,
				Dog.dogID,
				ConBreed.ConcatBreeds AS breed_name,
				Dog.sex,
				Dog.alteration_status,
				Microchip.microchipID,
				DATE_FORMAT(Surrender.date ,
				'%Y-%m-%d') as `date`	 
			FROM
				Dog 
			INNER JOIN
				(
					SELECT
						dogID,
						GROUP_CONCAT(DISTINCT breed_name 
					ORDER BY
						breed_name SEPARATOR '/') AS ConcatBreeds	 
					FROM
						DogBreed 
					GROUP BY
						dogID
				) AS ConBreed	 
					ON Dog.dogID = ConBreed.dogID	 
			INNER JOIN
				Surrender	 
					ON Dog.dogID = Surrender.dogID	 
			LEFT JOIN
				Microchip	 
					ON Dog.dogID = Microchip.dogID	 
			WHERE
				animal_control = true	 
				AND Surrender.date between DATE_SUB(DATE_FORMAT(NOW() ,'%Y-%m-01'), INTERVAL 6 MONTH) AND NOW()	 
			ORDER BY
				Dog.dogID;
			"""
	cursor.execute(query)
	query_result = cursor.fetchall()
	return query_result

def query_report_animal_control_detail2(cursor):
	query = """
			SELECT
			DATE_FORMAT(DATE_FORMAT(Adoption.Date ,
			'%Y-%m-01'),
			"%b %Y") AS Month,
			Dog.dogID,
			ConBreed.ConcatBreeds AS breed_name,
			Dog.sex,
			Dog.alteration_status,
			Microchip.microchipID,
			DATE_FORMAT(Surrender.date ,
			'%Y-%m-%d') as surrenderDate,
			DATE_FORMAT(Adoption.date ,
			'%Y-%m-%d') as adoptionDate,
			DATEDIFF(Adoption.date,
				Surrender.date)
				AS days_in_shelter,
			IFNULL(TotalExpense, 0) AS TotalExpense 	 
		FROM
			Dog 
		INNER JOIN
			(
				SELECT
					dogID,
					GROUP_CONCAT(DISTINCT breed_name 
				ORDER BY
					breed_name SEPARATOR '/') AS ConcatBreeds	 
				FROM
					DogBreed 
				GROUP BY
					dogID
			) AS ConBreed	 
				ON Dog.dogID = ConBreed.dogID	 
		INNER JOIN
			Surrender	 
				ON Dog.dogID = Surrender.dogID	 
		INNER JOIN
			Adoption	 
				ON Dog.dogID = Adoption.dogID	 
		LEFT JOIN
			Microchip	 
				ON Dog.dogID = Microchip.dogID
		LEFT JOIN
			(SELECT dogID, SUM(amount) AS TotalExpense FROM cs6400_su20_team08.Expense GROUP BY dogID) as TotalExpense
				ON Dog.dogID = TotalExpense.dogID	 
		WHERE
			Adoption.Date between DATE_SUB(DATE_FORMAT(NOW() ,'%Y-%m-01'), INTERVAL 6 MONTH) AND NOW()
		AND 
			DATEDIFF(Adoption.date,Surrender.date) >= 60	 
		ORDER BY
			DATEDIFF(Adoption.date,
			Surrender.date) DESC,
			Dog.dogID;
		"""
	cursor.execute(query)
	query_result = cursor.fetchall()
	return query_result

def query_report_monthly_adoption(cursor, conn):
	query = """
			WITH   S AS (	   SELECT
				DATE_FORMAT(Surrender.date ,
				'%Y-%m-01') AS Month,
				ConBreed.ConcatBreeds AS BreedName,
				Count(Surrender.dogID) AS NumDogsSurrendered	 
			FROM
				Surrender 
			INNER JOIN
				(SELECT
					dogID,
					GROUP_CONCAT(DISTINCT breed_name 
				ORDER BY
					breed_name SEPARATOR '/') AS ConcatBreeds	 
				FROM
					DogBreed	 
				GROUP BY
					DogID) AS ConBreed	 
					ON Surrender.dogID = ConBreed.dogID	 
			WHERE
				Surrender.Date between DATE_SUB(DATE_FORMAT(NOW() ,'%Y-%m-01'), INTERVAL 12 MONTH) AND LAST_DAY(NOW() - INTERVAL 1 MONTH)	 
			GROUP BY
				DATE_FORMAT(Surrender.date ,
				'%Y-%m-01'),
				ConBreed.ConcatBreeds),
				A AS (SELECT
					DATE_FORMAT(Adoption.date ,
					'%Y-%m-01') AS Month,
					ConBreed.ConcatBreeds AS BreedName,
					Count(DISTINCT Adoption.dogID) AS NumDogsAdopted,
					AVG(Adoption.fee) AS TotalAdoptionFee,
					SUM(Expense.amount) AS TotalExpense,
					SUM(Expense.amount) * 0.15 AS Profit -- piazza post 672 
				FROM
					Adoption 
				INNER JOIN
					(SELECT
						dogID,
						GROUP_CONCAT(DISTINCT breed_name 
					ORDER BY
						breed_name SEPARATOR '/') AS ConcatBreeds	 
					FROM
						DogBreed	 
					GROUP BY
						dogID) AS ConBreed	 
						ON Adoption.dogID = ConBreed.dogID	 
				LEFT OUTER JOIN
					Expense	 
						ON Adoption.dogID = Expense.dogID	 
				WHERE
					Adoption.date between DATE_SUB(DATE_FORMAT(NOW() ,'%Y-%m-01'), INTERVAL 12 MONTH) AND LAST_DAY(NOW() - INTERVAL 1 MONTH)	 
				GROUP BY
					DATE_FORMAT(Adoption.date ,
					'%Y-%m-01'),
					ConBreed.ConcatBreeds) SELECT
						DATE_FORMAT(Month,
						"%b %Y") as month,
						BreedName as breed_name,
						IFNULL(NumDogsSurrendered,
						0) AS num_dogs_surrendered,
						IFNULL(NumDogsAdopted,
						0) AS num_dogs_adopted,
						IFNULL(TotalAdoptionFee,
						0) AS total_adoption_fee,
						IFNULL(TotalExpense,
						0) AS total_expense,
						IFNULL(Profit,
						0) AS profit 
					FROM
						( SELECT
							COALESCE(S.Month,
							A.Month) AS Month,
							COALESCE(S.BreedName,
							A.BreedName) AS BreedName,
							NumDogsSurrendered,
							NumDogsAdopted,
							TotalAdoptionFee,
							TotalExpense,
							Profit 
						FROM
							S 
						LEFT OUTER JOIN
							A 
								ON S.Month = A.Month 
								AND S.BreedName = A.BreedName 
						UNION
						SELECT
							COALESCE(S.Month,
							A.Month) AS Month,
							COALESCE(S.BreedName,
							A.BreedName) AS BreedName,
							NumDogsSurrendered,
							NumDogsAdopted,
							TotalAdoptionFee,
							TotalExpense,
							Profit 
						FROM
							S 
						RIGHT OUTER JOIN
							A 
								ON S.Month = A.Month 
								AND S.BreedName = A.BreedName 
						) AS t 
				ORDER BY
					DATE(Month),
					BreedName;
			"""
	cursor.execute(query)
	conn.commit()
	query_result = cursor.fetchall()
	return query_result

def query_report_expense_analysis(cursor, conn):
	query = """
			SELECT 	Vendor.name,
				IFNULL(CAST(SUM(Expense.amount) AS DECIMAL(10,2)),0) AS total_expense 
			FROM Vendor 
			LEFT JOIN Expense 
			ON Vendor.name = Expense.vendor_name 
			GROUP BY Vendor.name 
			ORDER BY SUM(Expense.amount) DESC;
			"""
	cursor.execute(query)
	conn.commit()
	query_result = cursor.fetchall()
	return query_result

def query_report_volunteer_lookup(cursor, conn, name_like):
	query = """	
			SELECT
				first_name,
				last_name,
				USER.email,
				phone_number,
				start_date 
			FROM
				USER 
			WHERE
				USER.email not in (
					SELECT
						email 
					FROM
						admin
				) 
				AND (
					USER.first_name LIKE %s 
					OR USER.last_name LIKE %s
				) 
			ORDER BY
				last_name,
				first_name;
			"""
	params = (name_like, name_like)
	cursor.execute(query, params)
	conn.commit()
	query_result = cursor.fetchall()
	return query_result

def query_add_adoption_search_from_lastname(cursor, conn, name_like):
	query = """	
			SELECT
				distinct Applicant.last_name,
				Applicant.first_name,
				Applicant.phone_number,
				Applicant.email,
				Applicant.street,
				Applicant.city,
				Applicant.zip_code,
				Applicant.state,
				Application.co_applicant_last_name,	 
				Application.co_applicant_first_name
			FROM
				Applicant,
				Application	 
			WHERE
				Application.applicant_email = Applicant.email	  
				AND (
					(Applicant.last_name like %s)	   
					OR (Application.co_applicant_last_name like %s)	 
				)	  
				AND Application.applicationID in (
					SELECT
						applicationID	   
					FROM
						Approved	 
				)								 
				AND Application.applicationID NOT in (
					SELECT
						applicationID 
					FROM
						Adoption
				);
			"""
	params = (name_like, name_like)
	cursor.execute(query, params)
	conn.commit()
	query_result = cursor.fetchall()
	return query_result


def query_add_adoption_most_recent_approved_application(cursor, email):
	query = """
			SELECT
				Application.applicationID,
				Application.applicant_email,
				date,
				co_applicant_first_name,
				co_applicant_last_name,
				'Approved' AS status 
			FROM
				Application,
				Applicant,
				Approved 
			WHERE
				Application.applicant_email = Applicant.email 
				AND Approved.applicationID = Application.applicationID 
				AND Application.applicant_email = %s						  
				AND Application.applicationID not in (
					SELECT
						applicationID 
					FROM
						Adoption
				)
			ORDER BY
				date DESC LIMIT 1;
			"""
	params = (email)
	cursor.execute(query, params)
	query_result = cursor.fetchall()
	return query_result


def query_add_adoption_show_fee(cursor, dog_id):
	query = """
			SELECT
				animal_control,
				CASE	 
					WHEN animal_control = true THEN (SELECT
						SUM(Amount)*0.15 
					FROM
						Expense 
					WHERE
						dogID = %s)	 
					ELSE (SELECT
						SUM(Amount)*1.15 
					FROM
						Expense 
					WHERE
						dogID = %s) 
				END AS Fees 
			FROM
				Surrender 
			WHERE
				dogID = %s;
			"""
	params = (dog_id, dog_id, dog_id)
	cursor.execute(query, params)
	query_result = cursor.fetchone()
	return query_result[1]

def query_add_adoption_view_application_by_applicationid(cursor, applicationID):
	query = """
			SELECT
				Applicant.last_name,
				Applicant.first_name,
				Applicant.phone_number,
				Applicant.email,
				Applicant.street,
				Applicant.city,
				Applicant.zip_code,
				Applicant.state,
				Application.co_applicant_last_name,
				Application.co_applicant_first_name 
			FROM
				Applicant,
				Application 
			WHERE
				Application.applicant_email = Applicant.email 
				AND Application.applicationID = %s;
			"""
	params = (applicationID)
	cursor.execute(query, params)
	query_result = cursor.fetchall()
	return query_result

def query_add_adoption_submit(cursor, conn, dogID, applicationID, input_date, fees_formatted, user_email):
	query = """
			INSERT 
			INTO 
				Adoption 
			VALUES 
				(%s,%s,%s,%s,%s);
	"""
	params = (dogID, applicationID, input_date, fees_formatted, user_email)
	cursor.execute(query, params)
	conn.commit()

def query_view_dog_detail(cursor, dog_id):
	query = """
			SELECT
				Dog.dogID,
				description,
				name,
				age,
				sex,
				alteration_status,
				CASE 
					WHEN ((alteration_status = 'altered') AND (Microchip.microchipID IS NOT NULL)) THEN 'Yes' 
					ELSE 'No' 
				END AS adoptability_status 
			FROM
				Dog
			LEFT JOIN
				Microchip	 
					ON Dog.dogID = Microchip.dogID	  
			WHERE
				Dog.dogID = %s;
			"""
	params = (dog_id)
	cursor.execute(query, params)
	query_result = cursor.fetchall()
	return query_result

def query_view_dog_microchip(cursor, dog_id):
	query = """
			SELECT
				microchipID 
			FROM
				microchip 
			WHERE
				dogID = %s;
			"""
	params = (dog_id)
	cursor.execute(query, params)
	query_result = cursor.fetchone()
	return query_result

def query_view_dog_breedname(cursor, dog_id):
	query = """
			SELECT
				GROUP_CONCAT(DISTINCT breed_name 
			ORDER BY
				breed_name SEPARATOR '/')
			FROM
				DogBreed 
			WHERE
				dogID=%s;
			"""
	params = (dog_id)
	cursor.execute(query, params)
	query_result = cursor.fetchone()
	return query_result


def query_view_dog_expenses(cursor, dog_id):
	query = """
			SELECT
				date,
				description,
				amount,
				vendor_name 
			FROM
				Expense 
			WHERE
				dogID = %s
				ORDER BY date;
			"""
	params = (dog_id)
	cursor.execute(query, params)
	query_result = cursor.fetchall()
	return query_result


def query_add_microchip(cursor, conn, dog_id, microchip_id):
	query = """
			INSERT 
			INTO
				microchip
				
			VALUES
				(%s,%s);
			"""
	params = (dog_id, microchip_id)
	cursor.execute(query, params)
	conn.commit()

def query_update_gender(cursor, conn, dog_id, gender):
	query = """
			UPDATE
				Dog 
			SET
				sex = %s 
			WHERE
				dogID = %s;
			"""
	params = (gender, dog_id)
	cursor.execute(query, params)
	conn.commit()

def query_update_alterationstatus(cursor, conn, dog_id, alterationstatus):
	query = """
			UPDATE
				Dog 
			SET
				alteration_status = %s 
			WHERE
				dogID = %s;
			"""
	params = (alterationstatus, dog_id)
	cursor.execute(query, params)
	conn.commit()

def query_update_dogbreed(cursor, conn, dog_id, breed_list):
	query1 = """
			DELETE 
			FROM
				dogbreed 
			WHERE
				dogID = %s;
			"""
	params1 = (dog_id)
	cursor.execute(query1, params1)

	for breed in breed_list:
		query2 = """
				INSERT 
				INTO
					dogbreed
					
				VALUES
					(%s,%s);
				"""
		params2 = (dog_id, breed)
		cursor.execute(query2, params2)
	conn.commit()

def query_breed(cursor, filter=False):
	query = """
			SELECT
				* 
			FROM
				breed 
			"""
	if filter == True:
		query += """			
				WHERE
				breed_name not IN (
					'Mixed','Unknown'
				)"""
	cursor.execute(query)
	query_result = cursor.fetchall()
	return query_result

def query_search_applicant(cursor, applicant_email):
	query = """
			SELECT
				FIRST_NAME,
				LAST_NAME,
				PHONE_NUMBER,
				EMAIL,
				STREET,
				CITY,
				ZIP_CODE,
				STATE 
			FROM
				APPLICANT 
			WHERE
				EMAIL = %s ;
			"""
	params = (applicant_email)
	cursor.execute(query, params)
	query_result = cursor.fetchall()
	return query_result

def query_add_applicant(cursor, conn, applicant_email,first_name,last_name,phone_number,street,city,zip_code,state):
	query = """
			INSERT 
			INTO
				Applicant
				
			VALUES
				(%s,%s,%s,%s,%s,%s,%s,%s);
			"""
	params = (applicant_email,first_name,last_name,phone_number,street,city,zip_code,state)
	cursor.execute(query, params)
	conn.commit()


def query_add_application(cursor, conn, email, date, co_applicant_first_name,co_applicant_last_name, user_emal):
	query1 = """
			SELECT
				MAX(applicationID) 
			FROM
				Application;
			"""
	cursor.execute(query1)
	applicationID = cursor.fetchone()[0]+1

	query2 = """
			INSERT 
			INTO
				Application
				
			VALUES
				(%s,%s,%s,%s,%s,%s);
			"""
	params2 = (applicationID, email, date, co_applicant_first_name,co_applicant_last_name, user_emal)
	cursor.execute(query2, params2)
	conn.commit()

def query_check_expense_from_date(cursor, conn, expense_date, vendor_name, dogID):
	query = """
			SELECT
				date,
				dogID,
				vendor_name 
			FROM
				Expense 
			WHERE
				date = %s 
				AND vendor_name=%s 
				AND dogID = %s;
			"""
	params = (expense_date, vendor_name, dogID)
	cursor.execute(query, params)
	query_result = cursor.fetchone()
	return query_result

def query_add_vendor(cursor, conn, vendor_name):
	# INSERT IF NOT EXISTS
	query = """
			INSERT IGNORE
			INTO
				Vendor
			SET 
				name = %s;
			"""
	params = (vendor_name)
	cursor.execute(query, params)
	conn.commit()

def query_add_expense(cursor, conn, dogID, vendor_name, expense_date, amount, description):
	# INSERT IF NOT EXISTS
	query = """
			INSERT
			INTO
				Expense
			VALUES 
				(%s,%s,%s,%s,%s);
			"""
	params = (dogID, vendor_name, expense_date, amount, description)
	cursor.execute(query, params)
	conn.commit()

def query_application_by_email(cursor, applicant_email):
	query = """
			SELECT
			Application.applicationID,
			last_name,
			first_name,
			phone_number,
			email,
			street,
			city,
			zip_code,
			state,
			date,
			co_applicant_first_name,
			co_applicant_last_name 
		FROM
			Applicant,
			Application 
		WHERE
			Applicant.email = Application.applicant_email 
			and Applicant.email = %s
		ORDER BY Application.applicationID DESC
		Limit 1;
			"""
	params = (applicant_email)
	cursor.execute(query, params)
	query_result = cursor.fetchall()
	return query_result

def query_view_dog_surrender(cursor,dogID):
		query = """
		select
			date,
			reason,
			animal_control
		FROM
			Surrender
		where
			dogID = %s;
				"""
		params = (dogID)
		cursor.execute(query, params)
		query_result = cursor.fetchall()
		return query_result

def query_add_microchip_id(cursor,microchipID):
		query = """
		select
			microchipID
		FROM
			Microchip
		where
			microchipID = %s;
				"""
		params = (microchipID)
		cursor.execute(query, params)
		query_result = cursor.fetchone()
		return query_result

def query_search_phoneNo(cursor,phone_number):
		query = """
		select
			phone_number
		FROM
			Applicant
		where
			phone_number = %s;
				"""
		params = (phone_number)
		cursor.execute(query, params)
		query_result = cursor.fetchone()
		return query_result
