import numpy as np
import sqlalchemy
from matplotlib import style

import matplotlib.pyplot as plt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
from flask import Flask, jsonify


# Database

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
#################################################
app = Flask(__name__)

# Flask Routes
#################################################
@app.route("/")
def welcome():
    ## List all available routes
    return(
        "Welcome"
    f"Routes Available:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"Enter start or end date with format: '%Y-%m-%d'<br/>"
    f"/api/v1.0/&lt;start&gt;<br/>"
    f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# * Query for the dates and precipitation observations from the last year.
#   * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#   * Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation/<input_date>")
def prcp(input_date):
    prcp_dict = {}
    sel = session.query(Measurement.prcp).filter(func.strftime("%Y-%m-%d", input_date)== Measurement.date).all()    
    sel_list = list(np.ravel(sel))
    prcp_dict["Date"] = input_date
    prcp_dict["Precipitation"] = sel_list
    return jsonify(prcp_dict)

# * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    sta = session.query(Station.station).all()
    sta_list = list(np.ravel(sta))
    return jsonify(sta_list)


# * Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs/<start_date>")
def temp(start_date):
    query = session.query(Measurement.tobs).\
            filter(Measurement.date >= func.strftime("%Y-%m-%d",start_date)).all()
    # converting the list of tuples into a  normal list
    query_unraveled = list(np.ravel(query))
    return jsonify(query_unraveled)


# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date1>")
def temp_stats(start_date1):
    temp_dict = {}
    Temp = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                 filter(Measurement.date >= func.strftime("%Y-%m-%d",start_date1)).all()
    temp_query_unraveled = list(np.ravel(Temp))
    temp_dict["Min_temp"] = temp_query_unraveled[1]
    temp_dict["Avg_temp"] = temp_query_unraveled[2]
    temp_dict["Max_temp"] = temp_query_unraveled[0]
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start_date2>/<end_date2>")
def temp_stats_2(start_date2,end_date2):
    temp_dict_2 = {}
    temp_query_2 = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                   filter(Measurement.date >= func.strftime("%Y-%m-%d",start_date2)).\
                   filter(Measurement.date <= func.strftime("%Y-%m-%d",end_date2)).all()
    temp_query_2_unraveled = list(np.ravel(temp_query_2))
    temp_dict_2["Temp_min"] = temp_query_2_unraveled[0]
    temp_dict_2["Temp_avg"] = temp_query_2_unraveled[1]
    temp_dict_2["Temp_max"] = temp_query_2_unraveled[2]
    return jsonify(temp_dict_2)

if __name__ == '__main__':
    app.run(debug=True)