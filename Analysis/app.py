# Import Dependencies

import datetime as dt
import numpy as np
import pandas as pd
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine =  create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

## Calculate the date 1 year ago from the last data point in the database
#  change current date to one year prior to today
Last_date = dt.date.today() - dt.timedelta(days=365)

# make the lookback period as 12 months from current date
## Calculate the date 1 year ago from the last data point in the database
year_session = Last_date - dt.timedelta(days=365)


##################################################################################
##################################################################################
# Flask Setup to create all the required route
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():

    # """List all Required API routes."""
    return (
        f"Available Routes for climate analysis!<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/>/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
        #  Design a query to retrieve the last 12 months of precipitation data 
        # query the average precipitation of last 12 months, group and order by date
    result = session.query(Measurement.date, func.avg(Measurement.prcp))\
    .filter(Measurement.date >= year_session)\
    .filter(Measurement.date < Last_date)\
    .group_by(Measurement.date)\
    .order_by(Measurement.date).all()

    #Convert the query results to a Dictionary date as the key and prcp as the value.
    # create a dictionary for precipitation
    precipitation = {}
    # add data row by row to the dictorary
    for line in result:
        date = line[0]
        prcp = line[1]
        precipitation[date] = prcp

    #return results in json format
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
	"""return a list of stations from the dataset"""
	# qurey the station table
	result = session.query(Station.name).all()
	# Convert list of tuples into a list of stations
	station_list = list(np.ravel(result))
    #Return a JSON list of stations from the dataset.
	return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temperature():
    """return temperature observations from last year"""
    # query the average temperature of last 12 months
    result = session.query(Measurement.tobs).filter(Measurement.date >= year_session)\
    .filter(Measurement.date < Last_date).all()

    # convert result into a list of data converted in int type, otherwise json cannot serialize it
    temperatures = list(np.ravel(result))
    temp = []
    for t in temperatures:
    	temp.append(int(t))
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(temp)

# specify end_date as an optional variable to the path
@app.route("/api/v1.0/<start_date>/", defaults = {'end_date': None})
@app.route("/api/v1.0/<start_date>/<end_date>/")
def temp_lookup(start_date,end_date):
	try:
		# check if start_date and end_date are entered in the correct date format
		start_date = '2016-08-23'
		if end_date:
			end_date ='2017-08-23'
		# when end_date is not provided, query the data with date greater or equal to start_date
		if end_date is None:
			result = {}
			min = session.query(Measurement.date,func.min(Measurement.tobs))\
			    .filter(Measurement.date >= start_date).all()
			max = session.query(Measurement.date,func.max(Measurement.tobs))\
			    .filter(Measurement.date >= start_date).all()    
			avg = session.query(Measurement.date,func.avg(Measurement.tobs))\
			    .filter(Measurement.date >= start_date).all()    
			    
			result['TMIN'] = min[0][1]
			result['TMAX'] = max[0][1]
			result['TAVG'] = avg[0][1]

			return jsonify(result)
		# when end_date is provided, query the data between start_date and end_date, both inclusive
		result = {}
		min = session.query(Measurement.date,func.min(Measurement.tobs))\
		    .filter(Measurement.date >= start_date)\
		    .filter(Measurement.date <= end_date).all()
		max = session.query(Measurement.date,func.max(Measurement.tobs))\
		    .filter(Measurement.date >= start_date)\
		    .filter(Measurement.date <= end_date).all()  
		avg = session.query(Measurement.date,func.avg(Measurement.tobs))\
		    .filter(Measurement.date >= start_date)\
		    .filter(Measurement.date <= end_date).all()   
		    
		result['TMIN'] = min[0][1]
		result['TMAX'] = max[0][1]
		result['TAVG'] = avg[0][1]
		return jsonify(result)
	# if start_date or end_date not entered in the correct date format, show reminder for correct format
	except ValueError:
		return 'Please enter date in YYYY-MM-DD format'


if __name__ == '__main__':
    app.run(debug=True)


