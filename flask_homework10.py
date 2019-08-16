#import 
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

app = Flask(__name__)

#recreate the setup of the climate_starter
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#home page
@app.route("/")
def home():
    return(
    f"/api/v1.0/precipitation"
    f"<br>"
    f"/api/v1.0/stations"
    f"<br>"
    f"/api/v1.0/tobs"
    f"<br>"
    f"/api/v1.0/<start> <----Place a date on the end in YYYY-MM-DD format"
    f"<br>"
    f"/api/v1.0/<start>/<end> <-------- Place 2 dates for start and stop dates in YYYY-MM-DD/YYYY-MM-DD format (start/stop)"
    )

#create a fucntion to convert to dictionary
def dict_convert(results, second_var):
    #hmmmmm.... not sure how to get this to work with list comp
    #dictionary = [({'date': record[0], second_var: record[1]}(x)) for x in results]

    dictionary = []
    for x in results:
        dictionary.append({'date': x[0], second_var: x[1]})

    return dictionary

#need a get last date fucntion so I don't have to look at the data to get the most recent date
def recent_date():
    #r_date = session.query(Measurement).\
        #order_by(Measurement.date.desc()).limit(1)
    r_date = engine.execute('SELECT * FROM Measurement AS m ORDER BY m.date DESC LIMIT 1')
    for date in r_date:
        most_recent_date = date.date

    return dt.datetime.strptime(most_recent_date, "%Y-%m-%d")


#precipitation page
#Convert the query results to a Dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route('/api/v1.0/precipitation')
def return_precipitation():
    most_recent_date = recent_date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    recent_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()
    #prefer engine.exectute but cant seem to get it to work
    #recent_prcp = engine.execute('SELECT m.date, m.prcp FROM Measurement AS m WHERE m.date >= one_year_ago ORDER BY m.date DESC')
    return jsonify(dict_convert(recent_prcp, second_var='prcp'))


#Stations page
#Convert the query results to a Dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route('/api/v1.0/stations')
def return_station_list():
    station_list = engine.execute('SELECT DISTINCT m.station FROM Measurement AS m')

    return jsonify([x[0] for x in station_list])


#temperature observed (tobs)
#Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/tobs')
def return_tobs():
    most_recent_date = recent_date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    recent_tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    return jsonify(dict_convert(recent_tobs_data, second_var='tobs'))

#start date
#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route('/api/v1.0/<start>/')
def given_date(start):
    
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == start).all()


    data_list = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Average Temperature'] = result[1]
        row['High Temperature'] = result[2]
        row['Low Temperature'] = result[3]
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = result[0]
        row["High Temperature"] = result[1]
        row["Low Temperature"] = result[2]
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)