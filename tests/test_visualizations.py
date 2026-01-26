from scripts.visualizations import *
import pytest
import pandas as pd



# przykładowe dane
@pytest.fixture(scope="session")
def monthly_df():
   df = pd.DataFrame({"year": [2015],
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
   fig = plot_city_trends(df, cities=["Warszawa", "Katowice"], year=2015, ylim=[0, 75])
   assert fig is not None


# czy legenda jest poprawna
def test_city_trends_legend_labels(monthly_df):
    df = monthly_df.set_index(["year", "month"])
    ax = plot_city_trends(df, cities=["Warszawa", "Katowice"], year=2015, ylim=[0, 75])
    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert "Warszawa 2015" in labels


# czy liczba linii na wykresie jest poprawna
def test_city_trends_num_lines(monthly_df):
    df = monthly_df.set_index(["year", "month"])
    ax = plot_city_trends(df, cities=["Warszawa", "Katowice"], year=2015, ylim=[0, 75])
    series = {f"{city} {year}" for city in ["Warszawa", "Katowice"] for year in [2015]}
    assert len(ax.get_legend().get_texts()) == len(series)