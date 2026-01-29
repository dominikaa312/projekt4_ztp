import pytest
import yaml
import os
import tempfile
from scripts.pubmed_functions import build_query, top_journals, papers_count_per_year, plot_per_year
import pandas as pd


@pytest.fixture(scope="session")
def configfile():
    config_data = {"years": [2015, 2024],
                "cities": ["Warsaw", "Katowice"],
                "city_aliases": {"Warsaw": ["Warsaw", "Warszawa"], "Katowice": ["Katowice"]},
                "pm25": {"norm_limit": 15},
                "pubmed": {"entrez_email": {"d.aniszewsk2 @ student.uw.edu.pl"}},
                "queries": {'"PM2.5"[TIAB]', '"fine particulate matter"[TIAB]'},
                "retmax": 10}

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    os.remove(temp_path)


def test_build_query_return_str(configfile):
    config = yaml.safe_load(open(configfile))
    query = build_query(config, config["years"][0])
    assert isinstance(query, str)
    assert f"{config["years"][0]}" in query


def test_top_journals_count_correct():
    df = pd.DataFrame({"journal": ["A", "B", "A", "C", "A", "B", "D", "E"],
                    "title": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]})
    top = top_journals(df)
    assert "A" in top["journal"].values
    assert top["total_count"].iloc[0] == 5


def test_papers_count_per_year_sum_correct():
    df = pd.DataFrame({"year": [2015, 2018, 2024, 2024, 2024, 2015, 2018, 2018],
                    "title": ["T1","T2","T3","T4","T5", "T6", "T7", "T8"]})
    summary = papers_count_per_year(df)
    assert summary.loc[summary.year == 2015, "count"].values[0] == 2
    assert summary.loc[summary.year == 2018, "count"].values[0] == 3
    assert summary.loc[summary.year == 2024, "count"].values[0] == 3


def test_plot_per_year_run_without_err():
    df = pd.DataFrame({"year": [2015, 2018, 2024, 2024, 2024, 2015, 2018, 2018],
                       "title": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]})
    summary = papers_count_per_year(df)
    fig = plot_per_year(summary)
    assert fig is not None