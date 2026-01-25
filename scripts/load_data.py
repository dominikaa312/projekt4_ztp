import pandas as pd
import requests
import zipfile
import io

def load_data():
    """
        Returns:
                all_data (pd.DataFrame): DataFrame, który zawiera dzienne stężenia PM2.5 w latach
                2015, 2018, 2021 i 2024 dla wszystkich lokalizacji
    """
    # id archiwum dla poszczególnych lat
    gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
    gios_url_ids = {2015: '236', 2018: '603', 2021: '486', 2024: '582'}
    gios_pm25_file = {2015: '2015_PM25_1g.xlsx', 2018: '2018_PM25_1g.xlsx', 2021: '2021_PM25_1g.xlsx', 2024: '2024_PM25_1g.xlsx'}

    # funkcja do ściągania podanego archiwum
    def download_gios_archive(year, gios_id, filename):
        # Pobranie archiwum ZIP do pamięci
        url = f"{gios_archive_url}{gios_id}"
        response = requests.get(url)
        response.raise_for_status()  # jeśli błąd HTTP, zatrzymaj
    
        # Otwórz zip w pamięci
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # znajdź właściwy plik z PM2.5
            if not filename:
                print(f"Błąd: nie znaleziono {filename}.")
            else:
                # wczytaj plik do pandas
                with z.open(filename) as f:
                    try:
                        df = pd.read_excel(f, header=0)
                    except Exception as e:
                        print(f"Błąd przy wczytywaniu {year}: {e}")
        return df

    # pobranie danych z podanych lat: 2015, 2018, 2021 i 2024
    years = [2015, 2018, 2021, 2024]
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

    # pobranie metadanych
    metadata_url = 'https://powietrze.gios.gov.pl/pjp/archives/downloadFile/622'
    metadata_response = requests.get(metadata_url)
    metadata_response.raise_for_status()

    # wczytanie pliku do pandas
    dfmetadata = pd.read_excel(io.BytesIO(metadata_response.content), header=0)

    # Utworzenie słownika z starym i nowym kodem, który posłuży do aktualizowania starych kodów stacji
    try:
        new_codes_raw = dict(zip(dfmetadata['Stary Kod stacji \n(o ile inny od aktualnego)'], dfmetadata['Kod stacji']))
        new_codes = {}
        for old_codes, new_code in new_codes_raw.items():
        # jeśli więcej niż jeden stary kod to rozdziel po przecinku na wiele kluczy
            for code in [c.strip() for c in str(old_codes).split(',')]:
                new_codes[code] = new_code
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

    # ujednolicenie formatów dataframes z róźnych lat
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

    # aktualizacja starych kodów na nowe
    for year, df in dataframes.items():
        df.rename(columns=new_codes, inplace=True)

    # sprawdzenie czy nie brakuje któregoś kodu stacji w metadanych
    all_codes = set()
    for df in dataframes.values():
        all_codes.update(df.columns[1:])
  
    missing = all_codes - set(dfmetadata['Kod stacji'])
    if len(missing) > 0:
        print(f"W metadanych brakuje podanych kodów stacji: {missing}")

    # filtrowanie stacji na te, które pojawiają się w kaźdym roku z słownika
    non_station_cols = ['Kod stacji']
    first_df = next(iter(dataframes.values()))

    common_stations = [c for c in first_df.columns if c not in non_station_cols and all(c in df.columns for df in dataframes.values())]

    # dodanie miejscowości do kodu stacji/nazwy kolumny za pomocą metody MultiIndex
    code_city = dict(zip(dfmetadata['Kod stacji'], dfmetadata['Miejscowość']))

    multi_index = pd.MultiIndex.from_tuples([(code_city.get(code, None), code) for code in common_stations], names=["Miejscowość", "Kod stacji"])

    for key, df in dataframes.items():
        df_time = df[non_station_cols].copy()
        df_stations = df[common_stations].copy()
        df_stations.columns = multi_index
        df = pd.concat([df_time, df_stations], axis=1)
        df.iloc[:, 1:] = df.iloc[:, 1:].apply(lambda c: pd.to_numeric(c.astype(str).str.replace(",", "."), errors="coerce"))
        dataframes[key] = df

    # sprawdzenie czy w każdym df mamy tyle samo stacji
    num_stations = {key: len(df.columns) - 1 for key, df in dataframes.items()}
    if len(set(num_stations.values())) != 1:
        print("Są różne liczby stacji w danych")

    # zmiana dnia pomiaru o północy na poprzedni jako ostatni pomiar tego dnia
    def change_midnight(df):

        df = df.copy()
        df['Kod stacji'] = pd.to_datetime(df['Kod stacji']).dt.floor("s")
        time = df['Kod stacji'].dt.hour == 0
        df.loc[time, 'Kod stacji'] = df.loc[time, 'Kod stacji'] - pd.Timedelta(minutes=5)

        return df

    for key, df in dataframes.items():
        df = change_midnight(df)
        dataframes[key] = df

    # sprawdzenie czy w każdym df mamy odpowiednią liczbę dni w danym roku
    for year, df in dataframes.items():
        days = df['Kod stacji'].dt.normalize().nunique()
        expected_days = 366 if pd.Timestamp(year=year, month=1, day=1).is_leap_year else 365
        if days != expected_days:
            print(f" W roku {year} jest {days} dni, a powinno być {expected_days} dni")

    # dodanie kolumny 'Rok' aby następnie połączyć wszystkie dane w jeden plik .csv
    for key, df in dataframes.items():
        df.loc[:, 'Rok'] = key

    try:
        all_data = pd.concat([df for df in dataframes.values()], ignore_index=True)
        all_data.to_csv("all_data.csv", index=False)
        return all_data
    except Exception as e:
        return f"Wystąpił błąd przy zapisywaniu danych do pliku all_data.csv: {e}"

def main():
    print("Load data module. This is only to be used through an import.")

if __name__ == "__main__":
    main()
