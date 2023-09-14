from rise_class import Rise

# Variables of interest:
altitude = "Ownship/Flight/Altitude/AboveGroundLevel"
air_temp = "Ownship/Flight/OutsideAirTemperature"
speed_ground = "Ownship/Flight/GroundSpeed/U"
pitch = "Ownship/Flight/Pitch/Angle"
aog = "Ownship/Flight/AircraftOnGround"
dist = "StandardAircraft/DistanceToRunwayEnd"
speed_air = "Ownship/Flight/Airspeed/Calibrated"

# telemetry csv files:
telemetry_file1 = "Telemetry_R00000036_2020-01-08T11.43.21Z.csv"
telemetry_file2 = "Telemetry_R00000036_2020-01-08T11.47.38Z.csv"


def main():
    # Create an instance of Rise
    rise = Rise(telemetry_file2, altitude, air_temp, speed_ground, pitch, aog, dist, speed_air)

    # Save to disk by serializing in pickle format
    rise.frame.to_pickle("rise_dataframe.pkl")

    # Plot telemetry data
    rise.plot()

    # Metric computation
    print(f"Average airspeed while the aircraft was in the air: {round(rise.getAveSpeed(), 1)} knot")
    print(f"Pitch angle at touchdown: {round(rise.getPitchTd(), 1)} degree")
    print(f"Distance traveled on runway after touchdown: {round(rise.getDisGround(), 1)} ft")

    # Data sampling rate
    print(f"Min sampling rate: {round(rise.getRate()[0], 1)} Hz")
    print(f"Max sampling rate: {round(rise.getRate()[1], 1)} Hz")


if __name__ == "__main__":
    main()
