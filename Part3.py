import argparse
import json
import typing as T
import statistics
import pandas
import numpy as np
from pathlib import Path
from datetime import datetime

def load_data(file: Path) -> T.Dict[str, pandas.DataFrame]:
    temperature = {}

    with open(file, "r") as f:
        for line in f:
            r = json.loads(line)
            room = list(r.keys())[0]
            time = datetime.fromisoformat(r[room]["time"])
            temperature[time] = {room: r[room]["temperature"][0]}

    data = {"temperature": pandas.DataFrame.from_dict(temperature, "index").sort_index(),}
    return data

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="load and analyze IoT JSON data")
    p.add_argument("file", help="path to JSON data file")
    P = p.parse_args()

    file = Path(P.file).expanduser()

    #Get data
    data = load_data(file)

    rooms = ["lab1", "class1","office"]

    stds = 1.5

    for room in rooms:
        print("Finding anomalies: " + room)
        temps = data["temperature"][room].dropna()
        rmean = statistics.mean(temps)
        rstdev = statistics.stdev(temps)
        badsize=0
        size=temps.size
        print("Number of Data Points "+str(size))
        to_drop = []
        for x in range(0, temps.size):
          
            limit = rstdev *stds
            temp = temps.iloc[x]
            dev = abs(temp - rmean)
            
            if dev > limit:
                badsize=badsize +1
                print("Error: outlier")
                print("Time: " + str(temps.index[x]) + " Temperature: " + str(temps[x]))
                to_drop += [temps.index[x]]
        temps = temps.drop(to_drop)

        percent = (badsize/size)*100
        print("Percent of Bad Data Points is " + str(percent))
        median = statistics.median(temps)
        variance = statistics.variance (temps)
        print("The median temperature is "+ str(median))
        print("The variance of the temperature is "+ str(variance))

                
                #mean and variance
               
        print("\n")

# Does a persistent change in temperature always indicate a failed sensor?
#         No. Our algorithm detects anomalies by comparing the data points to the other 
#         data points through standard deviation to the mean. If a persistent change occurs 
#         This will affect the variance and our algorithm will not flag it as outliers.
#         Whether a persistent change indicates a failing sensor that is not flagged as 
#         an outlier is a possible false negative. 
        
# What are the possible bounds for each room?
#         In all three rooms, we use 1.5 standard deviations to get rid of outlier data. 
#         In the office, that is 2.22% of data points. 13 degrees from the median. 
#         In the lab, this gets rid of 6.25% of data points. 0.5 degrees from the median. 
#         In the class, this gets rid of 2% of data points. 6 degrees from the median. 
