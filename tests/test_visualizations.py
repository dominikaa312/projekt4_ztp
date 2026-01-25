from scripts.visualizations import *
import pytest
import pandas as pd
from scripts.compute_averages import count_days_over_treshold


# przykładowe dane
@pytest.fixture(scope="session")
def monthly_df():
   df = pd.DataFrame({"year": [2015, 2018, 2018, 2021],
                       "month": [1, 2, 3, 4],
                       "Warszawa": [1.3, 20, 30, 5],
                        "Katowice": [4.2, 15, 3.1, 10],
                        "Lublin": [3.4, 8.1, 1.2, 2]})
   return df


@pytest.fixture(scope="session")
def data():
    return pd.DataFrame({"Kod stacji": ["2015-01-01 12:00:00",
                                        "2015-01-01 13:00:00",
                                        "2015-01-02 12:00:00",
                                        "2015-01-03 12:00:00",
                                        "2018-01-03 13:00:00",
                                        "2018-01-03 13:00:00"],
                         "Rok": [2015, 2015, 2015, 2015, 2018, 2018],
                         ("Warszawa", "WAR"): [25, 1, 9, 10, 16, 24],
                         ("Kraków", "KRA"): [4, 16, 10, 15, 18, 19]})


def test_heatmap_run_without_err(monthly_df):
   fig = heatmaps(monthly_df)
   assert fig is not None


# czy wszystkie lokalizacje zostaly zawarte w heatmapie
def test_heatmap_contains_all_locations(monthly_df):
   locations = [c for c in monthly_df.columns if c not in ["year", "month"]]
   fig = heatmaps(monthly_df)
   assert len(fig.data) == len(locations)


def test_city_trends_run_without_err(monthly_df):
   df = monthly_df.set_index(["year", "month"])
   fig = plot_city_trends(df, cities=["Warszawa", "Katowice"], years=[2015, 2018], ylim=[0, 75])
   assert fig is not None


# czy legenda jest poprawna
def test_city_trends_legend_labels(monthly_df):
    df = monthly_df.set_index(["year", "month"])
    ax = plot_city_trends(df, cities=["Warszawa", "Katowice"], years=[2015, 2018], ylim=[0, 75])
    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert "Warszawa 2015" in labels
    assert "Katowice 2018" in labels


# czy liczba linii na wykresie jest poprawna
def test_city_trends_num_lines(monthly_df):
    df = monthly_df.set_index(["year", "month"])
    ax = plot_city_trends(df, cities=["Warszawa", "Katowice"], years=[2015, 2018], ylim=[0, 75])
    series = {f"{city} {year}" for city in ["Warszawa", "Katowice"] for year in [2015, 2018]}
    assert len(ax.get_legend().get_texts()) == len(series)


def test_pm25_exceedance_run_without_err(data):
    exceedance_counts = count_days_over_treshold(data, treshold=15)
    fig = plot_pm25_exceedance_bars(exceedance_counts, top_n=1, base_year=2015,threshold=15)
    assert fig is not None


# czy liczba słupków na wykresie jest równa temu ile powinno ich być
def test_pm25_exceedance_bar_count(data):
    exceedance_counts = count_days_over_treshold(data, treshold=15)
    ax = plot_pm25_exceedance_bars(exceedance_counts, top_n=1, base_year=2015, threshold=15)

    lista = exceedance_counts[exceedance_counts["year"] == 2015]
    sort_lista = lista.sort_values("days_exceeded")

    selected_stations = sort_lista.head(1)["station"].tolist() + sort_lista.tail(1)["station"].tolist()
    years = exceedance_counts["year"].unique()

    expected_bars = len(selected_stations) * len(years)
    out_bars = sum(len(container) for container in ax.containers)

    assert out_bars == expected_bars
   

# czy jest tyle stacji na wykresie ile powinno być
def test_pm25_exceedance_station_count(data):
    exceedance_counts = count_days_over_treshold(data, treshold=15)
    fig = plot_pm25_exceedance_bars(exceedance_counts, top_n=1, base_year=2015, threshold=15)
    x_labels = [t.get_text() for t in fig.get_xticklabels()]
    assert len(x_labels) == 2
