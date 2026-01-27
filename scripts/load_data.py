import pandas as pd
import requests
import zipfile
import io
import os



def load_data(years):
    """
        Function that downloads dataframes with levels of PM2.5 from various locations in Poland in given years
        and then combine them into one dataframe
        Args:
            years (list[int]): list of years of interest
        Returns:
            all_data (pd.DataFrame): dataframe, that contain daily levels of PM2.5 from various locations in given years
    """
    # id archives for all years that have a file with levels of PM2.5 for every hour
    gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
    gios_url_ids = {2006: '227', 2007: '228', 2008: '229', 2009: '230', 2010: '231', 2011: '232', 2012: '233', 2013: '234',
                    2014: '302', 2015: '236', 2016: '602', 2017: '262', 2018: '603', 2019: '322', 2020: '424', 2021: '486',
                    2022: '524', 2023: '564', 2024: '582'}
    gios_pm25_file = {2006: '2006_PM2.5_1g.xlsx', 2007: '2007_PM2.5_1g.xlsx', 2008: '2008_PM2.5_1g.xlsx', 2009: '2009_PM2.5_1g.xlsx',
                      2010: '2010_PM2.5_1g.xlsx', 2011: '2011_PM2.5_1g.xlsx', 2012: '2012_PM2.5_1g.xlsx', 2013: '2013_PM2.5_1g.xlsx',
                      2014: '2014_PM2.5_1g.xlsx', 2015: '2015_PM25_1g.xlsx', 2016: '2016_PM2.5_1g.xlsx', 2017: '2017_PM25_1g.xlsx',
                      2018: '2018_PM25_1g.xlsx', 2019: '2019_PM25_1g.xlsx', 2020: '2020_PM25_1g.xlsx', 2021: '2021_PM25_1g.xlsx',
                      2022: '2022_PM25_1g.xlsx', 2023: '2023_PM25_1g.xlsx', 2024: '2024_PM25_1g.xlsx'}

    # function for downloading files
    def download_gios_archive(year, gios_id, filename):
        # download ZIP archive to local storage
        url = f"{gios_archive_url}{gios_id}"
        response = requests.get(url)
        response.raise_for_status()  # if HTTP error, stop
    
        # unzip in-memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # find an appropriate file
            if not filename:
                print(f"Błąd: nie znaleziono {filename}.")
            else:
                # load the file to pandas
                with z.open(filename) as f:
                    try:
                        df = pd.read_excel(f, header=0)
                    except Exception as e:
                        print(f"Błąd przy wczytywaniu {year}: {e}")
        return df

    # if int convert to list
    if isinstance(years, int):
        years = [years]

    # creating a dictionary with files for given years
    dataframes = {}
    for year in years:
        try:
            df = download_gios_archive(year, gios_url_ids[year], gios_pm25_file[year])
            if df.empty:
                print(f"Pobrany plik dla roku {year} jest pusty")
            else:
                dataframes[year] = df
        except Exception as e:
            print(f"Błąd przy pobieraniu danych dla {year}: {e}")

    # downloading metadata
    metadata_url = 'https://powietrze.gios.gov.pl/pjp/archives/downloadFile/622'
    metadata_response = requests.get(metadata_url)
    metadata_response.raise_for_status()

    # loading metadata into pandas
    metadata = pd.read_excel(io.BytesIO(metadata_response.content), header=0)

    # creating a dictionary with an old code as key and a new code as value
    try:
        new_codes_raw = dict(zip(metadata['Stary Kod stacji \n(o ile inny od aktualnego)'], metadata['Kod stacji']))
        new_codes = {}
        for old_codes, new_code in new_codes_raw.items():
        # if there is more than one old code, split them into several keys
            for code in [c.strip() for c in str(old_codes).split(',')]:
                new_codes[code] = new_code
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

    # standardizing dataframes
    for key, df in dataframes.items():
        if key < 2016:
            df = df[2:]
            df = df.reset_index(drop=True)
        else:
            df.columns = df.iloc[0]
            df = df[5:]
            df = df.reset_index(drop=True)
        df = df.drop(df[df['Kod stacji'].isin(["Wskaźnik", "Czas uśredniania"])].index)
        dataframes[key] = df

    # updating old codes
    for year, df in dataframes.items():
        df.rename(columns=new_codes, inplace=True)

    # checking if there is any missing code in metadata
    all_codes = set()
    for df in dataframes.values():
        all_codes.update(df.columns[1:])
  
    missing = all_codes - set(metadata['Kod stacji'])
    if len(missing) > 0:
        print(f"W metadanych brakuje podanych kodów stacji: {missing}")

    # leaving stations that appear in every given years
    non_station_cols = ['Kod stacji']
    first_df = next(iter(dataframes.values()))

    common_stations = [c for c in first_df.columns if c not in non_station_cols and all(c in df.columns for df in dataframes.values())]

    # creating a MultiIndex for columns
    code_city = dict(zip(metadata['Kod stacji'], metadata['Miejscowość']))

    multi_index = pd.MultiIndex.from_tuples([(code_city.get(code, None), code) for code in common_stations], names=["Miejscowość", "Kod stacji"])

    for key, df in dataframes.items():
        df_time = df[non_station_cols].copy()
        df_stations = df[common_stations].copy()
        df_stations = df_stations.replace(",", ".", regex=True)
        df_stations = df_stations.astype(float)
        df = pd.concat([df_time, df_stations], axis=1)
        dataframes[key] = df

    # checking if every dataframe has the same number of stations
    num_stations = {key: len(df.columns) - 1 for key, df in dataframes.items()}
    if len(set(num_stations.values())) != 1:
        print("Są różne liczby stacji w danych")

    # shifting midnight timestamps to the previous day as the last one that day
    def change_midnight(df):
        df = df.copy()
        df['Kod stacji'] = pd.to_datetime(df['Kod stacji']).dt.floor("s")
        time = df['Kod stacji'].dt.hour == 0
        df.loc[time, 'Kod stacji'] = df.loc[time, 'Kod stacji'] - pd.Timedelta(minutes=5)
        return df

    for key, df in dataframes.items():
        dataframes[key] = change_midnight(df)

    # checking if there is a correct number of days in a year in every dataframe
    for year, df in dataframes.items():
        days = df['Kod stacji'].dt.normalize().nunique()
        expected_days = 366 if pd.Timestamp(year=year, month=1, day=1).is_leap_year else 365
        if days != expected_days:
            print(f" W roku {year} jest {days} dni, a powinno być {expected_days} dni")

    all_data = pd.concat([df for df in dataframes.values()], ignore_index=True)
    all_data.columns = ["Kod stacji"] + list(multi_index)

    # creating a file path to save combined dataframe
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(scripts_dir)
    data_path = os.path.join(base_dir, "data", "all_data.csv")

    try:
        all_data.to_csv(data_path, index=False)
        return all_data
    except Exception as e:
        return f"Wystąpił błąd przy zapisywaniu danych do pliku all_data.csv: {e}"

def main():
    print("Load data module. This is only to be used through an import.")

if __name__ == "__main__":
    main()
