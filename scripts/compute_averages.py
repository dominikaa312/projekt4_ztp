import pandas as pd



def monthly_average(data):
    """
    Function used to compute monthly averages of PM2.5 concentration in Zad2.
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

    data.drop("Rok", axis=1, inplace=True)

    meta_cols = {"Kod stacji", "year", "month"}
    station_cols = [c for c in data.columns if c not in meta_cols]

    no_metadata_df = data.drop("Kod stacji", axis=1)

    long = no_metadata_df.melt(id_vars=["year", "month"], value_vars=station_cols, var_name="station", value_name="pm2.5")

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

    monthly.to_csv("monthly_average.csv", index=False)

    return monthly



def monthly_average_filter(data, year, cities, city_aliases):
    """
    Function used filter the data based on a certain year and cities
    Args:
        data (pandas.DataFrame): a dataframe of PM2.5 levels
        year (int): year of interest
        cities (list): list of cities of interest
    Returns:
        data_filtered (pandas.DataFrame): filtered dataframe
    """

    # convert str to list
    if isinstance(cities, str):
        cities = [cities]

    # filter based on a certain year
    data = data[data["year"] == year]

    alias_to_city = {alias: city_name for city_name, aliases in city_aliases.items() for alias in aliases}

    columns_to_select = [alias for city_name in cities for alias in city_aliases.get(city_name, []) if alias in data.columns]

    data_filtered = data[['year', 'month'] + columns_to_select]
    data_filtered = data_filtered.rename(columns=alias_to_city)

    return data_filtered



def count_days_over_threshold(data, threshold, year, cities):
    """
     Function used to count days when PM2.5 concentration exceeds a given threshold for given cities in a given year.
     Args:
         data (pandas.DataFrame): a dataframe of PM2.5 levels
         threshold (int): maximum acceptable PM2.5
         year (int): year of interest
         cities (list): list of cities of interest

     Returns:
         exceedance_counts (pandas.DataFrame): a dataframe containing - for every station and given year - the number days where the average PM2.5 exceeded the acceptable threshold.
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

    if "Rok" in data.columns:
        data = data.drop("Rok", axis=1)

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