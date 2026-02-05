import pandas as pd
import numpy as np
import pytest
from scripts.compute_averages import monthly_average, count_days_over_threshold


@pytest.fixture
def raw_pm25():
    return pd.DataFrame(
        {
            "Rok": [2015, 2015],
            "Kod stacji": [
                "2015-01-01 01:00:00.000",
                "2015-01-01 02:00:00"
            ],
            "('Jelenia Góra', 'DsJelGorOgin')": [151.112, 262.566],
            "('Wrocław', 'DsWrocAlWisn')": [78.0, 42.0],
            "('Wrocław', 'DsWrocWybCon')": [50.0, 33.8244],
        }
    )

def test_monthly_average_structure(raw_pm25):
    out = monthly_average(raw_pm25.copy())

    assert "year" in out.columns
    assert "month" in out.columns
    assert "Wrocław" in out.columns
    assert "Jelenia Góra" in out.columns

def test_monthly_average_values(raw_pm25):
    out = monthly_average(raw_pm25.copy())

    jel_gora = (151.112 + 262.566) / 2
    wroc_al = (78.0 + 42.0) / 2
    wroc_wyb = (50.0 + 33.8244) / 2
    wroc_avg = (wroc_al + wroc_wyb) / 2

    assert out.loc[2015, 1, "Jelenia Góra"] == pytest.approx(jel_gora)
    assert out.loc[2015, 1, "Wrocław"] == pytest.approx(wroc_avg)


@pytest.fixture
def raw_pm25_daily():
    return pd.DataFrame(
        {
            "Rok": [2015, 2015],
            "Kod stacji": [
                "2015-01-01 00:00:00",
                "2015-01-02 00:00:00"
            ],
            "('Jelenia Góra', 'DsJelGorOgin')": [20.0, 10.0],
            "('Wrocław', 'DsWrocAlWisn')": [16.0, 14.0],
        }
    )

def test_count_days_over_threshold(raw_pm25_daily):
    out = count_days_over_threshold(raw_pm25_daily.copy(), threshold=15, year=2015, cities=['Wrocław', 'Jelenia Góra'],
                                    city_aliases={"Jelenia Góra": ["Jelenia Góra"], "Wrocław": ["Wrocław"]})

    out = out.sort_values(["city", "station"]).reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "year": [2015, 2015],
            "city": ["Jelenia Góra", "Wrocław"],
            "station": ["DsJelGorOgin", "DsWrocAlWisn"],
            "days_exceeded": [1, 1],
        }
    )

    out["year"] = out["year"].astype(np.int32)
    expected["year"] = expected["year"].astype(np.int32)

    pd.testing.assert_frame_equal(out, expected)

def test_count_days_over_threshold_none_exceeded(raw_pm25_daily):
    out = count_days_over_threshold(raw_pm25_daily.copy(), threshold=250, year=2015, cities=['Wrocław', 'Jelenia Góra'],
                                    city_aliases={"Jelenia Góra": ["Jelenia Góra"], "Wrocław": ["Wrocław"]})

    assert (out["days_exceeded"] == 0).all()
