from flask import Flask, render_template, request, url_for, redirect
from tables import EventsTable
from database import get_events
from forms import Location, Results
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
        city = bleach.clean(form.city.data)
        state = form.state.data
        genre = form.genre.data
        events_after = form.events_after.data
        events_before = form.events_before.data
        return results(city, state, genre, events_after, events_before)
    return render_template("location.html", form=form)


@app.route('/results.html', methods=['GET'])
def results(city, state, genre, events_after, events_before):
    form = Results()
    events = get_events(city, state, genre, events_after, events_before)
    return render_template("results.html", city=city, state=state, table=EventsTable(events), form=form)
