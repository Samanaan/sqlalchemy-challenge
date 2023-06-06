
# Import the dependencies.

# Import Flask
from flask import Flask, jsonify

#Import other dependancies
import pandas as pd
import datetime as dt
from pandas.api.types import is_datetime64_any_dtype
import numpy as np

# SQL Imports
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#______________________________________________________________________________________________________________________

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
measurement = Base.classes.measurement
station = Base.classes.station

#______________________________________________________________________________________________________________________

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

'''A homepage for users to land on and learn about the site.'''
@app.route("/")
def home():
    print("call for home page")
    return ("<h1>Hello, This is my climate app!!<h1/> <br/>"
            "Available routes on this app:<br/>"
            "<a href = 'http://127.0.0.1:5000/api/v1.0/precipitation'>To get to my precipitation page <a/> <br/>"
            "<a href = 'http://127.0.0.1:5000/api/v1.0/stations'> To get to my stations page <a/> <br/>"
            "<a href = 'http://127.0.0.1:5000/api/v1.0/tobs'> To get to my tobs page <a/> <br/>"
            "<br/>"
            "If you would like to know the min, max, and average of the recorded temperatures from the data use the below urls <br/>"
            "For specific start date fill in: http://127.0.0.1:5000/api/v1.0/[start_date] <br/>"
            "For a specific range of dates fill in: http://127.0.0.1:5000/api/v1.0/[start_date]/[end_date] <br/>"
            "Enter start and end dates in a yyyy-mm-dd format"
            )


'''A precipitation page that returns the precipitation for the last year as a JSON of a list of dictionaries.'''
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date one year from the last date in data set.
    First = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.prcp, measurement.date).filter(measurement.date > First).all()
    #Close the Session
    session.close()

    # Collect the precipation and dates from the results of the query
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = prcp
        prcp_dict["prcp"] = date
        all_prcp.append(prcp_dict)

    # Return the df as a JSON
    return jsonify(all_prcp)


'''A stations page that lists the names of the available stations'''
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    results = session.query(station.station).all()
    #Close the Session
    session.close()

    # convert the results to a list
    all_stations = list(np.ravel(results))

    # return the list of stations as a JSON
    return jsonify(all_stations)



'''Temperatures for one station over the course of one year.'''
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query for one station from '2017-08-23' to '2016-08-23'  (returns as tuples)
    results = session.execute("SELECT tobs FROM measurement WHERE station = 'USC00519281' AND date < '2017-08-23' AND date > '2016-08-23' ;")
    
    # convert to list of temperatures for the station
    one_station_one_year_list = []
    for temp in results:
        one_station_one_year_list.append(temp[0])
    
    # have to convert to a list for some reason
    one_station_one_year_list = list(one_station_one_year_list)
    
    # Close session
    session.close()
    # return the temperatures of the station as a JSON
    return jsonify(one_station_one_year_list)


'''Route for the user to imput a start date and get the min, max, and mean of precipetation from that date to the latest date'''
@app.route("/api/v1.0/<start>")
def start(start):
    """Fetch the date that matches the path variable supplied by the user, or a 404 if not."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query using the users input
    results = session.query(measurement.prcp, measurement.date).filter(measurement.date > start).all()
    
    # Run through the temp column and make sure there are no null values
    from_start_date = []
    for temp in results:
        if type(temp.prcp) == float:
            from_start_date.append(temp.prcp)  


    # Close session
    session.close()

    #Create a list of dictionaries to hold the min, max and mean of the requested data.
    from_start_date_stats = []
    temp_dict = {}
    temp_dict["min"] = np.min(from_start_date)
    temp_dict["max"] = np.max(from_start_date)
    temp_dict["mean"] = np.mean(from_start_date)
    from_start_date_stats.append(temp_dict)

    return jsonify(from_start_date_stats)


'''Route for the user to imput a start and end date and get the min, max, and mean of precipetation from that range of dates'''
@app.route("/api/v1.0/<start>/<end>")
def end(start,end):   
    """Fetch the date that matches the TWO path variable supplied by the user, or a 404 if not."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query using the users TWO inputs
    results = session.query(measurement.prcp, measurement.date).filter(measurement.date > start,measurement.date < end).all()
    
     # Run through the temp column and make sure there are no null values
    start_end_temps = []
    for temp in results:
        if type(temp.prcp) == float:
            start_end_temps.append(temp.prcp)  

    # Close session
    session.close()

    #Create a list of dictionaries to hold the min, max and mean of the requested data.
    start_end_stats = []
    temp_dict = {}
    temp_dict["min"] = np.min(start_end_temps)
    temp_dict["max"] = np.max(start_end_temps)
    temp_dict["mean"] = np.mean(start_end_temps)
    start_end_stats.append(temp_dict)
    return jsonify(start_end_stats)


#Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

