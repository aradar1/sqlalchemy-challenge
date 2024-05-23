# Import the dependencies.

from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Available routes:<br/>"
        f"<a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<br/>"
        f"<a href=\"/api/v1.0/stations\">/api/v1.0/stations<br/>"
        f"<a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Return a list of all daily precipitation totals for the last year""" 
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        func.sum(Measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
   
    session.close()
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of all the active Weather stations"""
    sel = [Measurement.station]
    active_stations = session.query(*sel).\
        group_by(Measurement.station).all()
    session.close()

    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """ Query the last 12 months of temperature observation data for the most active station"""
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
    station_temps = session.query(*sel).\
            filter(Measurement.date >= start_date, Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    session.close()

    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/<start>")
def calc_temp(start):
    """Given a start date, calculate tmin, tavg, tmax"""
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    """Return JSON list of tmin, tavg, tmax"""
    query = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date >= start_date).all()

    result = list(np.ravel(query))

    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_2(start,end):
    """Given start and end date calculate tmin, tavg, tmax"""
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")

    """Return JSON list of tmin, tavg, tmax"""
    query = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date.between(start_date,end_date)).all()

    result = list(np.ravel(query))
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=False)