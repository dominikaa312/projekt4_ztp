from scripts.visualizations import *
import pytest
import pandas as pd
import yaml
import tempfile
import os



# przykładowe dane
@pytest.fixture(scope="session")
def monthly_df():
   df = pd.DataFrame({"year": [2015, 2015, 2015, 2015],
                       "month": [1, 2, 3, 4],
                       "Warszawa": [1.3, 20, 30, 5],
                        "Katowice": [4.2, 15, 3.1, 10],
                        "Lublin": [3.4, 8.1, 1.2, 2]})
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
    locations = [c for c in monthly_df.columns if c not in ["year", "month"]]
    fig = heatmaps(monthly_df, config['years'][0], config['cities'], config['city_aliases'])
    assert len(fig.data) == len(locations)


def test_city_trends_run_without_err(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    df = monthly_df.set_index(["year", "month"])
    fig = plot_city_trends(df, config['cities'], config['years'][0], config['city_aliases'], ylim=[0, 75])
    assert fig is not None


# czy legenda jest poprawna
def test_city_trends_legend_labels(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    df = monthly_df.set_index(["year", "month"])
    ax = plot_city_trends(df, config['cities'], config['years'][0], config['city_aliases'], ylim=[0, 75])
    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert "Warszawa 2015" in labels


# czy liczba linii na wykresie jest poprawna
def test_city_trends_num_lines(monthly_df, configfile):
    with open(configfile) as f:
        config = yaml.safe_load(f)
    df = monthly_df.set_index(["year", "month"])
    ax = plot_city_trends(df, config['cities'], config['years'][0], config['city_aliases'], ylim=[0, 75])
    series = {f"{city} {year}" for city in ["Warszawa", "Katowice"] for year in [2015]}
    assert len(ax.get_legend().get_texts()) == len(series)