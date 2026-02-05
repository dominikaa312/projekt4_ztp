import pandas as pd
import os



def monthly_average(data):
    """
    Function used to compute monthly averages of PM2.5 concentration.
    Averages over measurements in all stations for a given city in a given month (in a given year)
    Args:
        data (pandas.DataFrame): a dataframe of PM2.5 levels

    Returns:
        result (pandas.DataFrame): a dataframe of average monthly PM2.5 in each city with MultiIndex (year, month) and cities as columns.
    """
    # convert the incoherent date column to one unified format
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

    meta_cols = {"Kod stacji", "year", "month"}
    station_cols = [c for c in data.columns if c not in meta_cols]

    no_metadata_df = data.drop("Kod stacji", axis=1)

    long = no_metadata_df.melt(id_vars=["year", "month"],
                               value_vars=station_cols,
                               var_name="station",
                               value_name="pm2.5")

    long["city"] = long["station"].str.extract(r"'([^']+)'")
    long.drop("station", axis=1, inplace=True)

    # perform the actual aggregation
    long["pm2.5"] = pd.to_numeric(long["pm2.5"], errors="coerce")
    long_avg = long.groupby(["year", "month", "city"], as_index=False).mean(numeric_only=True)
    monthly = (long_avg
    .pivot(
        index=["year", "month"],
        columns="city",
        values="pm2.5"
    )
    .sort_index())

    monthly = monthly.reset_index()

    return monthly



def daily_average(data):
    """
        Function used to compute daily averages of PM2.5 concentration
        Averages over measurements in all stations for a given city in a given month (in a given year)

        Args:
             data (pandas.DataFrame): a dataframe of PM2.5 levels

        Returns:
            daily (pandas.DataFrame): a dataframe of average daily PM2.5 in each city with MultiIndex
    """
    # convert the incoherent date column to one unified format
    s = data["Kod stacji"].astype(str)

    # first attempt: with milliseconds
    dt = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")

    # second attempt: without milliseconds, only where first failed
    mask = dt.isna()
    dt[mask] = pd.to_datetime(s[mask], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    # assign back
    data["Kod stacji"] = dt

    # extract year, month and day
    data["year"] = dt.dt.year
    data["month"] = dt.dt.month
    data["day"] = dt.dt.day

    meta_cols = {"Kod stacji", "year", "month", "day"}
    station_cols = [c for c in data.columns if c not in meta_cols]

    no_metadata_df = data.drop("Kod stacji", axis=1)

    long = no_metadata_df.melt(id_vars=["year", "month", "day"],
                            value_vars=station_cols,
                            var_name="station",
                            value_name="pm2.5")

    long["city"] = long["station"].str.extract(r"'([^']+)'")
    long.drop("station", axis=1, inplace=True)

    # perform the actual aggregation
    long["pm2.5"] = pd.to_numeric(long["pm2.5"], errors="coerce")
    long_avg = long.groupby(["year", "month", "day", "city"], as_index=False).mean(numeric_only=True)

    daily = (long_avg.pivot(index=["year", "month", "day"],
                            columns="city",
                            values="pm2.5").sort_index())

    daily = daily.reset_index()

    return daily



def count_days_over_threshold(data, threshold, year, cities, city_aliases):
    """
     Function used to count days when PM2.5 concentration exceeds a given threshold for given cities in a given year.
     Args:
         data (pandas.DataFrame): a dataframe of PM2.5 levels
         threshold (int): maximum acceptable PM2.5
         year (int): year of interest
         cities (list[str]): list of cities of interest
         city_aliases (list[str]): list of aliases of cities

     Returns:
         exceedance_counts (pandas.DataFrame): a dataframe containing - for every station and given year - the number of days when the average PM2.5 exceeded the acceptable threshold.
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

    # extract year and date
    data["year"] = dt.dt.year
    data["date"] = dt.dt.date

    data = data[data["year"] == year]

    # prepare station columns
    meta_cols = {"Kod stacji", "year", "date"}
    station_cols = [c for c in data.columns if c not in meta_cols]

    no_metadata_df = data.drop("Kod stacji", axis=1)

    # prepare the long dataframe used for aggregation
    long = no_metadata_df.melt(
        id_vars=["year", "date"],
        value_vars=station_cols,
        var_name="station_tuple",
        value_name="pm25"
    )

    # extract city and station code into two new columns
    long[["city", "station"]] = long["station_tuple"].str.extract(
        r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)"
    )

    long = long.drop("station_tuple", axis=1)

    long["pm25"] = pd.to_numeric(long["pm25"], errors="coerce")

    city_cols = []
    for city in cities:
        if city in long["city"].values:
            city_cols.append(city)
        elif city_aliases and city in city_aliases:
            for alias in city_aliases[city]:
                if alias in long["city"].values:
                    long.loc[long["city"] == alias, "city"] = city
                    city_cols.append(city)
                    break

    # filter only selected cities
    long = long[long["city"].isin(city_cols)]

    # compute daily average PM2.5 by station
    daily = (
        long
        .groupby(["year", "date", "city", "station"], as_index=False)
        .agg(daily_pm25=("pm25", "mean"))
    )

    if isinstance(cities, str):
        daily = daily[daily["city"] == cities]
    elif isinstance(cities, (list, tuple, set)):
        daily = daily[daily["city"].isin(cities)]

    daily["exceeded"] = daily["daily_pm25"] > threshold

    exceedance_counts = (
        daily
        .groupby(["year", "city", "station"], as_index=False)
        .agg(days_exceeded=("exceeded", "sum"))
        .sort_values(["city", "station"])
    )

    return exceedance_counts



def main():
    print("compute_averages module. This is only to be used through an import.")

if __name__ == "__main__":
    main()