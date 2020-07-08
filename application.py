from flask import Flask, render_template, request, url_for, redirect
from tables import EventsTable
from database import get_events
from forms import Location
import bleach


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY='dev')
    return app


app = create_app()
if __name__ == "__main__":
    app.run()


@app.route('/')
def start():
    return redirect(url_for("location"))


@app.route('/location', methods=['GET', 'POST'])
def location():
    form = Location()
    if request.method == 'POST':
        city = bleach.clean(request.values['city'])
        state = request.values['state']
        return results(city, state)
    return render_template("location.html", form=form)


@app.route('/results.html', methods=['GET'])
def results(city, state):
    events = get_events(city, state)
    return render_template("results.html", city=city, state=state, table=EventsTable(events))
