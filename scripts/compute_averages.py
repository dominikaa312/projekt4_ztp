# liczenie średnich i wskazywanie dni z przekroczeniem normy
import pandas as pd

def monthly_average(data):
    """(Zad2)
    Function used to compute monthly averages of PM2.5 concentration in Zad2.
    Averages over measurements in all stations for a given city in a given month (in a given year)
    Args:
        data (pandas.DataFrame): a dataframe of PM2.5 levels

    Returns:
        result (pandas.DataFrame): a dataframe of average monthly PM2.5 in each city with MultiIndex (year, month) and cities as columns.
    """
    ## convert the incoherent date column to one unified format
    s = data["Kod stacji"].astype(str)

    # first attempt: with milliseconds
    dt = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")

    # second attempt: without milliseconds, only where first failed
    mask = dt.isna()
    dt[mask] = pd.to_datetime(s[mask], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    # assign back
    data["Kod stacji"] = dt

    # extract year and month
    data["year"] = dt.dt.year
    data["month"] = dt.dt.month

    data.drop("Rok", axis=1, inplace=True)

    meta_cols = {"Kod stacji", "year", "month"}
    station_cols = [c for c in data.columns if c not in meta_cols]

    no_metadata_df = data.drop("Kod stacji", axis=1)

    long = no_metadata_df.melt(id_vars=["year", "month"], value_vars=station_cols, var_name="station", value_name="pm2.5")
    #long["station"].iloc[3]

    long["city"] = long["station"].str.extract(r"'([^']+)'")
    long.drop("station", axis=1, inplace=True)

    ## perform the actual aggregation
    long["pm2.5"] = pd.to_numeric(long["pm2.5"], errors="coerce")
    long_avg = long.groupby(["year", "month", "city"], as_index=False).mean(numeric_only=True)
    monthly = (long_avg
    .pivot(
        index=["year", "month"],
        columns="city",
        values="pm2.5"
    )
    .sort_index())

    return monthly
    
def count_days_over_treshold(data, treshold=15):
    """ (Zad4)
    Function used to count days when PM2.5 concentration exceeds a given thershold for all stations in a given year.
    Args:
        data (pandas.DataFrame): a dataframe of PM2.5 levels
        treshold (int): maximum acceptable PM2.5 according to WHO 
      
    Returns:
        exceedance_counts (pandas.DataFrame): a dataframe containing - for every station and every year - the number days where the average PM2.5 exceeded the acceptable thershold.
    """
    ## convert the incoherent date column to one unified format
    s = data["Kod stacji"].astype(str)

    # first attempt: with milliseconds
    dt = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")

    # second attempt: without milliseconds, only where first failed
    mask = dt.isna()
    dt[mask] = pd.to_datetime(s[mask], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    # assign back
    data["Kod stacji"] = dt

    # extract year and month
    data["year"] = dt.dt.year
    data["date"] = dt.dt.date

    data = data.drop("Rok", axis=1)

    meta_cols = {"Kod stacji", "year", "month"}
    station_cols = [c for c in data.columns if c not in meta_cols]

    no_metadata_df = data.drop("Kod stacji", axis=1)

    # prepare the long dataframe used for aggregation
    long = no_metadata_df.melt(
        id_vars=["year", "date"],
        value_vars=station_cols,
        var_name="station_tuple",
        value_name='pm25'
    )

    # decouple city name and station code

    long["station_tuple"] = long["station_tuple"].astype(str)

    # extract city and station code into two new columns
    long[["city", "station"]] = long["station_tuple"].str.extract(
        r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)"
    )

    long.drop("station_tuple", axis=1)

    long["pm25"] = pd.to_numeric(long["pm25"], errors="coerce")

    # compute daily average PM2.5 by station
    daily  = (
        long
        .groupby(["year", "date", "city", "station"], as_index=False)
        .agg(daily_pm25=("pm25", "mean"))
    )

    daily["exceeded"] = daily["daily_pm25"] > treshold

    exceedance_counts = (
        daily
        .groupby(["year", "city", "station"], as_index=False)
        .agg(days_exceeded=("exceeded", "sum"))
    )

    return exceedance_counts

def main():
    print("compute_averages module. This is only to be used through an import.")

if __name__ == "__main__":
    main()