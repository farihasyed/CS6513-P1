from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FormField
from wtforms.validators import InputRequired, Length, Regexp

MAX_CITY_LENGTH = 32
CITY_REGEX_VALIDATOR = Regexp(regex="^[a-zA-Z ]+$", message="Please enter a valid city name.")
CITY_LENGTH_VALIDATOR = Length(0, MAX_CITY_LENGTH, message="Please enter a valid city name.")

STATES = [('', 'Select a State'), ('AL', 'AL'), ('AK', 'AK'), ('AR', 'AR'), ('AZ', 'AZ'), ('CA', 'CA'), ('CO', 'CO'),
          ('CT', 'CT'), ('DC', 'DC'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('IA', 'IA'),
          ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('MA', 'MA'),
          ('MD', 'MD'), ('ME', 'ME'), ('MI', 'MI'), ('MN', 'MN'), ('MO', 'MO'), ('MS', 'MS'), ('MT', 'MT'),
          ('NC', 'NC'), ('NE', 'NE'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NV', 'NV'), ('NY', 'NY'),
          ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'),
          ('SD', 'SD'),  ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'),
          ('WI', 'WI'), ('WV', 'WV'), ('WY', 'WY')]

GENRES = [('', 'Select a Genre'), ('Alternative', 'Alternative'), ('Blues', 'Blues'),
          ("Children's Music", "Children's Music"), ('Classical', 'Classical'), ('Country', 'Country'),
          ('Dance/Electronic', 'Dance/Electronic'), ('Folk', 'Folk'), ('Hip-Hop/Rap', 'Hip-Hop/Rap'), ('Jazz', 'Jazz'),
          ('Latin', 'Latin'), ('Metal', 'Metal'), ('Multimedia', 'Multimedia'), ('New Age', 'New Age'),
          ('Other', 'Other'), ('Pop', 'Pop'), ('R&B', 'R&B'), ('Reggae', 'Reggae'), ('Religious', 'Religious'),
          ('Rock', 'Rock'), ('Variety', 'Variety'), ('World', 'World')]

MONTHS = [("0", 'Month'), ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'), ('07', '7'),
          ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12')]

DAYS = MONTHS[1:]
DAYS.insert(0, ("0", 'Day'))
DAYS.extend([('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'),
         ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'),
         ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31')])

YEARS = [("0", 'Year'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022')]

DISTANCES = [(0, "Distance (Miles)"), (1, 1), (5, 5), (10, 10), (25, 25), (50, 50), (100, 100), (250, 250)]


class Results(FlaskForm):
    back = SubmitField()


class DateForm(FlaskForm):
    day = SelectField('Day', choices=DAYS)
    month = SelectField('Month', choices=MONTHS)
    year = SelectField('Year', choices=YEARS)


class Location(FlaskForm):
    city = StringField('City: ', validators=[InputRequired(), CITY_REGEX_VALIDATOR, CITY_LENGTH_VALIDATOR])
    state = SelectField('State', choices=STATES, validators=[InputRequired()])
    genre = SelectField('Genre', choices=GENRES)
    submit = SubmitField()
    events_after = FormField(DateForm)
    events_before = FormField(DateForm)
    distance = SelectField('Distance (Miles)', choices=DISTANCES, coerce=int)




