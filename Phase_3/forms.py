from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, SelectField, IntegerField
from wtforms import *
from wtforms.validators import DataRequired, Email, NumberRange
from wtforms.fields.html5 import DateField

class LoginForm (FlaskForm):
    email = StringField ('Email', validators=[DataRequired(), Email()])
    password = PasswordField ('Password',validators=[DataRequired()])
    submit = SubmitField('Login')
    
class AddDogForm(FlaskForm):
	sex_type = [('male','male'),('female','female'),('unknown','unknown')]
	alteration_status_type = [('Neutered/Spayed','Neutered/Spayed'),('Unaltered','Unaltered')]
	animal_control_type = [('Yes','Yes'),('No','No')]
	name = StringField('Name',validators=[DataRequired()])
	breed_name = SelectMultipleField('Breed', choices=[], coerce = str, validators=[DataRequired()])
	sex = SelectField('Sex', choices = sex_type)
	alteration_status = SelectField('Alteration Status', choices = alteration_status_type)
	age = IntegerField('Age',validators=[DataRequired()])
	description = StringField('Description',validators=[DataRequired()])
	microchipID = StringField('Microchip Id')
	surrender_date = DateField('Surrender Date',format = '%Y-%m-%d')
	reason = StringField('Surrender Reason',validators=[DataRequired()])
	animal_control = SelectField('Animal Control', choices = animal_control_type)
	submit = SubmitField('Submit')

class EditDogDetailsForm_breed(FlaskForm):
    breed_name = SelectMultipleField('Select Breed(s)', choices=[], coerce=str,
                        validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddExpenseForm(FlaskForm):
	date = DateField('Date',validators=[DataRequired()])
	description = StringField('Description')
	amount = FloatField('Amount',validators=[DataRequired()])
	vendor_name = StringField('Vendor Name',validators=[DataRequired()])
	submit = SubmitField('Submit')
	
class AddApplicantForm(FlaskForm):
	state_type = [('AL','AL'),('AK','AK'),('AZ','AZ'),('AR','AR'),('CA','CA'),('CO','CO'),('CT','CT'),('DE','DE'),('FL','FL'),('GA','GA'),
	('HI','HI'),('ID','ID'),('IL','IL'),('IN','IN'),('IA','IA'),('KS','KS'),('KY','KY'),('LA','LA'),('ME','ME'),('MD','MD'),('MA','MA'),
	('MI','MI'),('AK','MN'),('MS','MS'),('MO','MO'),('MT','MT'),('NE','NE'),('NV','NV'),('NH','NH'),('NJ','NJ'),('MO','MO'),('MT','MT'),
	('NE','NE'),('NV','NV'),('NH','NH'),('NJ','NJ'),('NM','NM'),('NY','NY'),('NC','NC'),('ND','ND'),('OH','OH'),('OK','OK'),('OR','OR'),
	('PA','PA'),('RI','RI'),('SC','SC'),('NM','SD'),('TN','TN'),('TX','TX'),('UT','UT'),('VT','VT'),('VA','VA'),('WA','WA'),('WV','WV'),
	('WI','WI'),('WY','WY')]
	last_name = StringField('Last Name',validators=[DataRequired()])
	first_name = StringField('First Name',validators=[DataRequired()])
	phone_number = StringField('Phone Number',validators=[DataRequired()])
	email = StringField('Email',validators=[DataRequired()])
	street = StringField('Street',validators=[DataRequired()])
	city = StringField('City',validators=[DataRequired()])
	zip_code = StringField('Zip Code',validators=[DataRequired()])
	state = SelectField('State',choices = state_type)
	submit = SubmitField('Submit')

class AddApplicationForm(FlaskForm):
	date = DateField('Date',validators=[DataRequired()])
	co_applicant_last_name = StringField('Co-Applicant Last Name')
	co_applicant_first_name = StringField('Co-Applicant First Name')
	submit = SubmitField('Submit')
