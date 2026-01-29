from scripts.visualizations import *
import pytest
import pandas as pd
import yaml
import tempfile
import os



# przykładowe dane
@pytest.fixture(scope="session")
def monthly_df():
   df = pd.DataFrame({"year": [2015]*12,
                      "month": list(range(1, 13)),
                      "Warszawa": [1.3, 20, 30, 5, 4.2, 5.1, 6, 7.1, 8, 7, 8, 1.9],
                      "Katowice": [4.2, 15, 3.1, 10, 11.1, 12, 13, 14, 15, 15.1, 6.2, 10],
                      "Lublin": [3.4, 8.1, 1.2, 2, 3.4, 2.1, 1.2, 2, 9, 2.3, 10, 7]})
   return df


@pytest.fixture(scope="session")
def configfile():
    config_data = {"years": [2015, 2024],
                "cities": ["Warsaw", "Katowice"],
                "city_aliases": {"Warsaw": ["Warsaw", "Warszawa"], "Katowice": ["Katowice"]},
                "pm25": {"norm_limit": 15}}

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    os.remove(temp_path)



def test_heatmap_run_without_err(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    fig = heatmaps(monthly_df, config['years'][0], config['cities'], config['city_aliases'])
    assert fig is not None


# czy wszystkie lokalizacje zostaly zawarte w heatmapie
def test_heatmap_contains_all_locations(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    fig = heatmaps(monthly_df, config['years'][0], config['cities'], config['city_aliases'])
    expected_locs = [city for city in config['cities']
                     if city in monthly_df.columns or any(alias in monthly_df.columns for alias in config['city_aliases'][city])]
    assert len(fig.data) == len(expected_locs)


def test_city_trends_run_without_err(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    df = monthly_df.set_index(["year", "month"])
    fig = plot_city_trends(df, config['cities'], config['years'][0], config['city_aliases'], ylim=[0, 75])
    assert fig is not None


# czy liczba linii na wykresie jest poprawna
def test_city_trends_num_lines(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    df = monthly_df.set_index(["year", "month"])
    fig = plot_city_trends(df, config['cities'], config['years'][0], config['city_aliases'], ylim=[0, 75])
    assert len(fig.data) == len(config['cities'])