import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class Rise:
    def __init__(self, csv_name, *vars):
        self.df = pd.read_csv(csv_name, usecols=["Uri", "OriginTime", "Value"])
        self.df = self.df.loc[self.df["Uri"].isin(vars)]
        self.vars = vars
        # process the 'OriginTime' column
        self.df["OriginTime"] = pd.to_datetime(self.df["OriginTime"], format="%Y-%m-%dT%H:%M:%S.%fZ")
        self.df["OriginTime"] = (self.df["OriginTime"] - self.df["OriginTime"].min()).dt.total_seconds()
        self.df["Value"] = pd.to_numeric(self.df["Value"], errors="coerce")

    @property
    def frame(self):
        return self.df

    @property
    def var(self):
        return self.vars

    def saveDf(self):
        self.df.to_pickle("rise_dataframe.pkl")

    def loadDf(self):
        self.df = pd.read_pickle("rise_dataframe.pkl")

    def getTimeTd(self):
        # This method computes the time at touchdown based on AOG flag
        var = "Ownship/Flight/AircraftOnGround"
        time_td = self.df.loc[(self.df["Uri"] == var) & (self.df["Value"] == 1), "OriginTime"]
        return time_td.values[0]

    def getTimeStop(self):
        # This method computes the time when aircraft stops moving after landing.
        # Calculated based on ground speed
        var = "Ownship/Flight/GroundSpeed/U"
        time_stop = self.df.loc[(self.df["Uri"] == var) & (self.df["Value"] < 0.1), "OriginTime"]
        return time_stop.values[0]

    def getPitchTd(self):
        # This method computes the pitch angle at touch down
        var = "Ownship/Flight/Pitch/Angle"
        time_td = self.getTimeTd()
        pitch_td = self.df.loc[(self.df["Uri"] == var) & (self.df["OriginTime"] == time_td), "Value"]
        return pitch_td.values[0]

    def getAveSpeed(self):
        # This method computes the average airspeed while aircraft in the air
        var = "Ownship/Flight/Airspeed/Calibrated"
        time_td = self.getTimeTd()
        aveSpeed = self.df.loc[(self.df["Uri"] == var) & (self.df["OriginTime"] < time_td), "Value"].mean()
        return aveSpeed

    def getDisGround(self):
        # This method computes the distance traveled on runway after touchdown
        var = "StandardAircraft/DistanceToRunwayEnd"
        time_td = self.getTimeTd()
        time_stop = self.getTimeStop()
        distance_td = self.df.loc[(self.df["Uri"] == var) & (self.df["OriginTime"] == time_td), "Value"]
        distance_stop = self.df.loc[(self.df["Uri"] == var) & (self.df["OriginTime"] - time_stop > 0), "Value"]
        dist_travel = distance_td.values[0] - distance_stop.values[0]
        return dist_travel

    def getRate(self):
        # This method returns the max and min sampling rate (in Hz) as a tuple
        rate_list = []
        for var in self.df["Uri"].unique():
            column = self.df.loc[self.df["Uri"] == var, "OriginTime"]
            sample_rate = [column.iloc[i + 1] - column.iloc[i] for i in range(len(column) - 1)]
            rate_list.append(max(sample_rate))
            rate_list.append(min(sample_rate))
        return (np.reciprocal(min(rate_list)), np.reciprocal(max(rate_list)))

    def porcessLabel(self, var):
        # This method processed variable name for plot title
        if var == "Ownship/Flight/Altitude/AboveGroundLevel":
            pvar = "Altitude (ft)"
        elif var == "Ownship/Flight/OutsideAirTemperature":
            pvar = "Air temperature (deg C)"
        elif var == "Ownship/Flight/GroundSpeed/U":
            pvar = "Ground speed (ft/sec)"
        elif var == "Ownship/Flight/Pitch/Angle":
            pvar = "Pitch angle (degree)"
        elif var == "Ownship/Flight/AircraftOnGround":
            pvar = "Aircraft on ground flag"
        elif var == "StandardAircraft/DistanceToRunwayEnd":
            pvar = "Distance to runway end (ft)"
        elif var == "Ownship/Flight/Airspeed/Calibrated":
            pvar = "calibrated airspeed (knot)"
        return pvar

    def plot(self):
        fig = plt.figure()

        for index, var in enumerate(self.vars):
            ax = fig.add_subplot(3, 3, index + 1)
            x = self.df.loc[(self.df["Uri"] == var), ["OriginTime"]]
            y = self.df.loc[(self.df["Uri"] == var), ["Value"]]
            ax.plot(x, y)
            ax.set_xlabel("Time (second)")
            ax.set_ylabel(self.porcessLabel(var))
            ax.set_title(self.porcessLabel(var))
            # Increase the number of y-axis ticks
            num_ticks_x = 5
            ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks_x))

        fig.tight_layout()
        plt.show()
