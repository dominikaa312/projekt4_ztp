import pandas as pd
import ast


def monthly_average_filter(data, year, cities):
    if isinstance(cities, str):
        cities = [cities]
    data["year"] = data["year"].astype(int)
    data = data[data["year"] == year]
    cities_filter = [c for c in data.columns.tolist() if c in cities]

    return data[['year', 'month'] + cities_filter]



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