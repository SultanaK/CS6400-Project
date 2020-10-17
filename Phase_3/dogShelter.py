from flask import Flask, render_template, url_for, flash, redirect, request, session
from forms import *
from data import *
from flaskext.mysql import MySQL
import yaml
import json
from collections import defaultdict
from functools import wraps

app = Flask(__name__)


app.config['SECRET_KEY'] = 'e9eb6ba543753822522bb404a2bbeade'

#config DB
db = yaml.load(open('db.yaml'))
app.config['MYSQL_DATABASE_USER'] = db['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DATABASE_HOST'] = db['mysql_host']
app.config['MYSQL_DATABASE_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
con = mysql.connect()
cur = con.cursor()
status = 'incomplete'

def login_required(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if session['logged_in']==True:
			return f(*args,**kwargs)
		else:
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
	session.clear()
	session['logged_in']=False

	return render_template('index.html')

@app.route("/login", methods=['GET','POST'])
def login():
	form = LoginForm(request.form)
	if request.method == "POST":
		email = request.form['email']
		password = request.form['password']
		data = query_login(cur, email, password)

		if data is not None:

			session['logged_in'] = True

			response = redirect(url_for('viewDogDashBoard'))
			response.set_cookie('email',email)
			return response
		else:
			msg = 'Login unsuccessfull. Please check username and password'
			return render_template('login.html', title = 'Login', msg = msg)

	return render_template('login.html', title = 'Login', form = form)


@app.route("/viewDogDashBoard", methods=['GET','POST'])
@login_required
def viewDogDashBoard():
	dogDetails = query_view_dog_dashboard(cur)
	diff = query_available_space(cur)
	email = request.cookies.get('email')
	return render_template('dashboard.html', diff = diff, dogDetails = dogDetails, email = email)

@app.route("/addDog", methods=['GET','POST'])
@login_required
def addDog():
	form = AddDogForm(request.form)
	breeds = query_breed(cur)
	count = len(breeds)
	breed = []
	for i in range (count):
		a = breeds[i]
		b = breeds[i][0]
		new = a + (b,)
		breed.append(new)
	form.breed_name.choices=breed

	if request.method =="POST":
		name = request.form['name']
		breed_names = [];
		for breed_name in form:
			if breed_name.type == 'SelectMultipleField':
				breed_names = breed_name.data
		for i in breed_names:
			if name.lower() =='uga' and i == "Bulldog":
				flash(f'Dog name UGA and breed Bulldog cannot be a combination.', 'danger')
				return redirect(url_for('addDog'))
		if len(breed_names)>1:
			for i in breed_names:
				#print(i)
				if i == "Mixed" or i == "Unknown":
					flash(f'Mixed or Unknown with other breed combination is not allowed.', 'danger')
					return redirect(url_for('addDog'))
		sex = request.form['sex']
		if request.form['alteration_status'] == 'Neutered/Spayed':
			alteration_status = 'altered'
		else:
			alteration_status = 'unaltered'
		age = request.form['age']
		description = request.form['description']
		microchipID = request.form['microchipID']
		microchipIDs = query_add_microchip_id(cur,microchipID)
		if microchipIDs is not None:
			flash(f'Duplicated microchipID, please use a different one.', 'danger')
			return redirect(url_for('addDog'))
		else:
			surrender_date = request.form['surrender_date']
			reason = request.form['reason']
			animal_control = request.form['animal_control']
			if(animal_control =='Yes'):
				ac = 1
			else:
				ac = 0
			email = request.cookies.get('email')
			query_add_dog(cur, con, name, sex, alteration_status, age, description, breed_names, microchipID, email,surrender_date,reason, ac)
			return redirect(url_for('choose'))
	return render_template('addDog.html',title='Add Dog', form = form)

@app.route("/choose")
@login_required
def choose():
	dogID = query_max_dogid(cur)
	return render_template('choose.html', title='Choose', dogID = dogID)

@app.route("/review_application", methods=['GET', 'POST'])
@login_required
def review_application():
	data = query_review_application(cur, con)
	if len(data)<1:
		msg = 'No pending adoption application.'
		return render_template('review_application.html', msg=msg, title='Adoption Application Review')
	else:
		if request.method == "POST":
			for i in range(len(data)):
				option = request.form['bt_' + str(data[i][0])]
				if option == 'approved':
					query_approve_application(cur, con, data[i][0])
				elif option == 'rejected':
					query_reject_application(cur, con, data[i][0])
			return redirect(url_for('review_application'))
	return render_template('review_application.html', output_data=data, title='Adoption Application Review')

@app.route("/reports")
@login_required
def reports():
	return render_template('reports.html', title='Reports')

@app.route("/report_animal_control")
@login_required
def report_animal_control():
	data = query_report_animal_control_summary(cur)
	# convert to dict -> then to json later
	summary = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in data]

	detail_data1 = query_report_animal_control_detail1(cur)
	# convert to dict -> then to json later
	detail1 = defaultdict(list)
	for i in [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in detail_data1]:
		detail1[i['Month']].append({'DogID':i['dogID'],'Bread Name':i['breed_name'], 'Sex':i['sex'],'Alteration Status':i['alteration_status'],'MicrochipID':i['microchipID'], 'Surrender Date':i['date']})

	detail_data2 = query_report_animal_control_detail2(cur)
	# convert to dict -> then to json later
	detail2 = defaultdict(list)
	for i in [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in detail_data2]:
		detail2[i['Month']].append({'DogID':i['dogID'],'Bread Name':i['breed_name'], 'Sex':i['sex'],'Alteration Status':i['alteration_status'],'MicrochipID':i['microchipID'], 'Surrender Date':i['surrenderDate'],'Adoption Date':i['adoptionDate'],'Days in Shelter':i['days_in_shelter'],'Total Expense':i['TotalExpense']})

	summary_data = {"summary": json.dumps(summary), "detail1": json.dumps(detail1),"detail2": json.dumps(detail2)}

	return render_template('report_animal_control.html', output_data=summary_data, title='Animal Control Report')


@app.route("/report_monthly_adoption")
@login_required
def report_monthly_adoption():
	data = query_report_monthly_adoption(cur, con)
	return render_template('report_monthly_adoption.html', data=data, title='Monthly Adoption Report')

@app.route("/report_expense_analysis")
@login_required
def report_expense_analysis():
	data = query_report_expense_analysis(cur, con)
	return render_template('report_expense_analysis.html', data=data, title='Expense Analysis Report')


@app.route("/report_volunteer_lookup", methods=['GET', 'POST'])
@login_required
def report_volunteer_lookup():
	cur = mysql.connect().cursor()
	if request.method == "POST":
		vName = request.form['VName']
		vName_like = '%'+vName+'%'
		data = query_report_volunteer_lookup(cur,con, vName_like)
		if len(data) < 1:
			msg = 'No matching name.'
			return render_template('report_volunteer_lookup.html', msg=msg, title='Volunteer Lookup')
		else:
			return render_template('report_volunteer_lookup.html', data=data, title='Volunteer Lookup')
	return render_template('report_volunteer_lookup.html', title='Volunteer Lookup')

@app.route("/addAdoption/<string:dogID>", methods=['GET', 'POST'])
@login_required
def addAdoption(dogID):
	if request.method == 'POST':
		if request.form['action'] == 'search_applicant':
			aName = request.form['ApplicantName']
			aName_like = '%'+aName+'%'
			data = query_add_adoption_search_from_lastname(cur, con, aName_like)
			if len(data) < 1:
				msg = 'No matching name.'
				return render_template('addAdoption.html', msg=msg, title='Add Adoption')
			else:
				return render_template('addAdoption.html', data=data, title='Add Adoption')

		if request.form['action'] == 'select_applicant':
			selection = request.form["bt_search"]
			info = query_add_adoption_most_recent_approved_application(cur, selection)
			fees = query_add_adoption_show_fee(cur, dogID)
			fees_formatted = 0 if fees is None else fees
			applicationID = info[0][0]
			data = query_add_adoption_view_application_by_applicationid(cur, applicationID)
			if len(info) < 1:
				msg2 = 'No adoption application found.'
				return render_template('addAdoption.html', msg2=msg2, title='Add Adoption', dogID=dogID, data=data)
			else:
				return render_template('addAdoption.html', info=info, fees_formatted=fees_formatted,
									   title='Add Adoption', dogID=dogID, data=data)

		if request.form['action'] == 'submit_adoption':
			input_date = request.form["enter_date"]
			if input_date is "":
				msg3 = 'Submission Failed - Date was not entered. Please search and select the adoption application. ' \
					   'And enter the adoption date.'
				return render_template('addAdoption.html', msg3=msg3, title='Add Adoption', dogID=dogID)
			applicationID = request.form['applicationID']
			fees_formatted = 0 if request.form['fee']=='None' else request.form['fee']
			user_email = request.cookies.get('email')
			query_add_adoption_submit(cur, con, dogID, applicationID, input_date, fees_formatted, user_email)
			return redirect(url_for('confirm_add_adoption'))
	return render_template('addAdoption.html', title='Add Adoption', dogID=dogID)


@app.route("/confirm_add_adoption")
@login_required
def confirm_add_adoption():
	return render_template('confirm_add_adoption.html')


@app.route("/viewDogDetails/<string:dogID>",methods=['GET', 'POST'])
@login_required
def viewDogDetails(dogID):
	user_emal = request.cookies.get('email')

	dog_details, dog_microchip, dog_breed_name, expenses_details,form,surrender_details = query_viewDogDetails(dogID)
	for item in dog_details:
		gender = item[4]
		alterationstatus=item[5]
		adoptionstatus =item [6]
	if request.method=="POST" :
		microchip_id_html=request.form.get('microchip_id')
		gender_html=request.form.get("gender")
		alterationstatus_html = request.form.get("alterationstatus")
		breed_list_html=request.form.getlist("breed_name")
		breed_list_html=sorted(breed_list_html)
		s="/"
		breed_html=s.join(breed_list_html)
		if dog_microchip != microchip_id_html and microchip_id_html is not None:
			microchipIDs = query_add_microchip_id(cur,microchip_id_html)
			if microchipIDs is not None:
				msg = 'Duplicated microchipID, please use a different one.'
				return render_template('viewDogDetails.html', title='View Dog Details', msg=msg,dog_breed_name=dog_breed_name,dog_details=dog_details,expenses_details=expenses_details,dogID=dogID,dog_microchip=dog_microchip,status = status,form=form, email = user_emal,surrender_details=surrender_details)
			else:
				query_add_microchip(cur, con, dogID, microchip_id_html)
				dog_details, dog_microchip, dog_breed_name, expenses_details,form ,surrender_details = query_viewDogDetails(dogID)
				return render_template('viewDogDetails.html', title='View Dog Details', dog_breed_name=dog_breed_name,dog_details=dog_details,expenses_details=expenses_details,dogID=dogID,dog_microchip=dog_microchip,status = status,form=form, email = user_emal,surrender_details=surrender_details)
		elif gender != gender_html and gender_html is not None:
			query_update_gender(cur, con, dogID, gender_html)
			dog_details, dog_microchip, dog_breed_name, expenses_details,form ,surrender_details = query_viewDogDetails(dogID)
			return render_template('viewDogDetails.html', title='View Dog Details', dog_breed_name=dog_breed_name,dog_details=dog_details,expenses_details=expenses_details,dogID=dogID,dog_microchip=dog_microchip,status = status,form=form, email = user_emal,surrender_details=surrender_details)
		elif alterationstatus != alterationstatus_html and alterationstatus_html is not None:
			query_update_alterationstatus(cur, con, dogID, alterationstatus_html)
			dog_details, dog_microchip, dog_breed_name, expenses_details,form ,surrender_details = query_viewDogDetails(dogID)
			return render_template('viewDogDetails.html', title='View Dog Details', dog_breed_name=dog_breed_name,dog_details=dog_details,expenses_details=expenses_details,dogID=dogID,dog_microchip=dog_microchip,status = status,form=form, email = user_emal,surrender_details=surrender_details)
		elif dog_breed_name != breed_html and breed_html is not None:
			query_update_dogbreed(cur, con, dogID, breed_list_html)
			dog_details, dog_microchip, dog_breed_name, expenses_details,form ,surrender_details = query_viewDogDetails(dogID)
			return render_template('viewDogDetails.html', title='View Dog Details', dog_breed_name=dog_breed_name,dog_details=dog_details,expenses_details=expenses_details,dogID=dogID,dog_microchip=dog_microchip,status = status,form=form, email = user_emal,surrender_details=surrender_details)

	return render_template('viewDogDetails.html', title='View Dog Details', dog_breed_name=dog_breed_name,dog_details=dog_details,expenses_details=expenses_details,dogID=dogID,dog_microchip=dog_microchip,status = status,form=form, email = user_emal,surrender_details=surrender_details)

def query_viewDogDetails(dogID):
	dog_details = query_view_dog_detail(cur, dogID)
	dog_microchip = query_view_dog_microchip(cur, dogID)
	if dog_microchip is None:
		dog_microchip = 'Not Present'
	else :
		dog_microchip=dog_microchip[0]
	dog_breed_name=query_view_dog_breedname(cur, dogID)[0]
	expenses_details = query_view_dog_expenses(cur, dogID)
	form = create_dog_bread_form()
	surrender_details = query_view_dog_surrender(cur, dogID)

	return dog_details, dog_microchip, dog_breed_name,  expenses_details, form, surrender_details

def create_dog_bread_form():
	form = EditDogDetailsForm_breed(request.form)
	dog_breeds = query_breed(cur, filter=True)
	dog_breed_count = len(dog_breeds)
	breed=[]
	for i in range (dog_breed_count):
		a=dog_breeds[i]
		b=dog_breeds[i][0]
		new = a + (b,)
		breed.append(new)
	form.breed_name.choices=breed
	return form

@app.route("/searchApplicant", methods=['GET','POST'])
@login_required
def searchApplicant():
	if request.method =="POST":
		applicant_email = request.form['email']
		application = query_search_applicant(cur, applicant_email)
		if len(application) < 1:
			msg = 'Email is not found.'
			return render_template('searchApplicant.html', msg=msg, title='Search Applicant')
		else:
			return render_template('searchApplicant.html', application=application, title='Search Applicant')
	return render_template('searchApplicant.html', title='Search Applicant')


@app.route("/addApplicant", methods=['GET','POST'])
@login_required
def addApplicant():
	form = AddApplicantForm(request.form)
	if request.method =="POST":
		last_name = request.form['last_name']
		first_name = request.form['first_name']
		phone_number = request.form['phone_number'].replace('-', '')
		applicant_email = request.form['email']
		street = request.form['street']
		city = request.form['city']
		zip_code = request.form['zip_code']
		state = request.form['state']
		email = request.cookies.get('email')

		phoneNo_List = query_search_phoneNo(cur,phone_number)
		if phoneNo_List is not None:
			flash(f'Duplicated phone number, please use a different one.','danger')
			return redirect(url_for('addApplicant'))
		application = query_search_applicant(cur, applicant_email)
		if len(application) < 1:
			query_add_applicant(cur, con, applicant_email,first_name,last_name,phone_number,street,city,zip_code,state)
			flash(f'Applicant saved success.','success')
			return redirect(url_for('addApplication',email = applicant_email))
	return render_template('addApplicant.html',title='Add Applicant', form = form)

@app.route("/addApplication/<string:email>", methods=['GET','POST'])
@login_required
def addApplication(email):
	form = AddApplicationForm(request.form)
	if request.method =="POST":
		date = request.form['date']
		co_applicant_first_name = request.form['co_applicant_first_name']
		co_applicant_last_name = request.form['co_applicant_last_name']
		user_emal = request.cookies.get('email')
		query_add_application(cur, con, email, date, co_applicant_first_name,co_applicant_last_name, user_emal)
		return redirect(url_for('viewAdoptionApplication',email = email))
	return render_template('addApplication.html',title='Add Applicantion', form = form, email = email)

@app.route("/addExpenses/<string:dogID>", methods=['GET','POST'])
@login_required
def addExpenses(dogID):
	form = AddExpenseForm(request.form)
	if request.method =="POST":
		expense_date = request.form['date']
		description = request.form['description']
		amount = request.form['amount']
		vendor_name = request.form['vendor_name']
		expense = query_check_expense_from_date(cur, con, expense_date, vendor_name, dogID)
		query_add_vendor(cur, con, vendor_name)
		if expense is None:
			query_add_expense(cur, con, dogID, vendor_name, expense_date, amount, description)
			flash(f'Expense is added.','success')
			return redirect(url_for('addExpenses',dogID = dogID))
		else:
			msg = 'Duplicated expense - a dog can incur only one expense associated with one vendor at a given date.'
			return render_template('addExpenses.html',title='Add Expenses', form = form, dogID = dogID, msg = msg)
	return render_template('addExpenses.html',title='Add Expenses', form = form, dogID = dogID)


@app.route("/viewAdoptionApplication/<string:email>")
@login_required
def viewAdoptionApplication(email):
	application = query_application_by_email(cur, email)
	return render_template('viewAdoptionApplication.html', title='View New Adoption Application',application = application)

if __name__=="__main__":
	app.run(debug=True)
