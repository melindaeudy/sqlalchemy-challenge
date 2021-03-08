import numpy as np
import sqlalchemy
import datetime as dt
import re
import pandas as pd

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

session=Session(engine)

# Find the most recent date in the database
most_recent_date = session.query(measurement.date).\
    order_by(measurement.date.desc()).first()

# Find date one year from most recent date
year_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')- dt.timedelta(days=365)

# Find the first date in the database
oldest_date = session.query(measurement.date).\
    order_by(measurement.date).first()

session.close

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii - Climate Page<br/>"
        f"<br/>"
        f"This site has data from 01-01-2010 to 08-23-2017<br/>"
        f"<br/>"
        f"Available Pages:<br/>"
        f"<br/>"
        f"<br/>"
        f"  Station Information<br/>"
        f"    /api/v1.0/stations<br/>"
        f"<br/>"
        f"  Percipitation Information<br/>"
        f"    /api/v1.0/percipitation<br/>"
        f"<br/>"
        f"  Temperature Observations<br/>"
        f"    /api/v1.0/tobs<br/>"
        f"<br/>"
        f"  Start Date information - complete url is '/api/v1.0//yyyy-mm-dd'<br/>"
        f"    /api/v1.0/start<br/>"
        f"<br/>"
        f"  Start and End Date information - complete url is  '/api/v1.0/yyyy-mm-dd/yyyy-mm-dd'<br/>"
        f"    /api/v1.0/start/end"
    )



@app.route("/api/v1.0/percipitation")
def percipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and percipitation
    results = session.query(measurement.date, measurement.prcp).\
        order_by(measurement.date).all()

    session.close()

     #Create a dictionary using 'date' as key and 'prcp' as the value
    percipitation = []
    for result in results:
        percipitation_dict = {}
        percipitation_dict["date"] = result[0]
        percipitation_dict["prcp"] = result[1]
        percipitation.append(percipitation_dict)

    return jsonify(percipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query list of stations
    results = session.query(measurement.id, measurement.station).all()

    session.close()

    #Create a dictionary of stations and statiob names
    station = []
    for result in results:
        station_dict = {}
        station_dict["station id"] = result.id
        station_dict["station name"] = result.station
        station.append(station_dict)

    return jsonify(station)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find most active statopm

    active_list = (session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all())
    
    # Query date and temperature temperature observations for most active station
    
    results = (session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.date >= year_date).\
        filter(measurement.station == active_list[0][0]).all())

    session.close()

     #Create a dictionary using the most active station, 'date' as key and 'tobs' as the value with last 12 months of data
    tobs = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result[1]
        tobs_dict["station"] = result[0]
        tobs_dict["temperature"] = result[2]      
        tobs.append(tobs_dict)

    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def start_only(start):
    #Create our session (link) from Python to DB
    session = Session(engine)

    # Query Maximum Temperature (TMAX), Minimum Temperature (TMIN), and Average Temperature (TAVG) based on start date
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()    

    session.close  

    start_list = []
    for result in results:
        start_list_dict = {}
        start_list_dict["Date"] = start
        start_list_dict["TMIN"] = result[0]
        start_list_dict["TMAX"] = result[1]
        start_list_dict["TAVG"] = result[2]
        start_list.append(start_list_dict)
    
    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #Create our session (link) from Python to DB
    session = Session(engine)

    # Query Maximum Temperature (TMAX), Minimum Temperature (TMIN), and Average Temperature (TAVG) between start and end date

    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
            filter(measurement.date <= end).all()

    session.close

    start_end_list = []
    for result in results:
        start_end_list_dict = {}
        start_end_list_dict["Start Date"] = start
        start_end_list_dict["End Date"] = end
        start_end_list_dict["TMIN"] = result[0]
        start_end_list_dict["TMAX"] = result[1]
        start_end_list_dict["TAVG"] = result[2]
        start_end_list.append(start_end_list_dict)


    return jsonify(start_end_list)



if __name__ == '__main__':
    app.run(debug=True)
