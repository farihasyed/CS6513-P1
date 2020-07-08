from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp

MAX_CITY_LENGTH = 32
CITY_REGEX_VALIDATOR = Regexp(regex="^[a-zA-Z- ]+$", message="Please enter a valid city name.")
CITY_LENGTH_VALIDATOR = Length(0, MAX_CITY_LENGTH, message="Please enter a valid city name.")


class Location(FlaskForm):
    city = StringField('City: ', validators=[InputRequired(), CITY_REGEX_VALIDATOR, CITY_LENGTH_VALIDATOR])
    submit = SubmitField()
