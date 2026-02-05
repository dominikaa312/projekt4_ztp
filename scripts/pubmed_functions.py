import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator



def build_query(config, year):
    """
        Function that combines topic keywords, city aliases, and a publication year into a single PubMed-compatible query.

        Args:
            config (dict): dictionary of configuration parameters
            year (int): PubMed-compatible year

        Returns:
            full_query (str): PubMed-compatible query

    """
    topic_query = " OR ".join(config["pubmed"]["queries"])

    city_aliases = config["city_aliases"]
    city_query = " OR ".join(f'"{alias}"[TIAB]'for aliases_list in city_aliases.values() for alias in aliases_list)

    year_query = f'"{year}"[PDAT] : "{year}"[PDAT]'

    full_query = f"(({topic_query}) AND ({city_query})) AND ({year_query})"

    return full_query



def record_to_df(record):
    """
        Function that converts a PubMed-compatible record into a Pandas DataFrame.

        Args:
             record (dict): PubMed-compatible record

        Returns:
            pandas.DataFrame: PubMed-compatible DataFrame
    """

    rows = []
    for rec in record:
        PMID = rec.get("PMID", "")
        title = rec.get("TI", "")
        year = rec.get("DP", "")[:4]
        journal = rec.get("JT", "")
        authors = ", ".join(rec.get("AU", []))
        rows.append({"PMID": PMID, "title": title, "year": year, "journal": journal, "authors": authors})

    return pd.DataFrame(rows)



def papers_count_per_year(df):
    """
        Function that counts the number of papers per year.

        Args:
            df (pandas.DataFrame): PubMed-compatible DataFrame

        Returns:
            year_count (pandas.DataFrame): Number of papers per year

    """

    year_count = (df.groupby("year")
                    .size()
                    .reset_index(name="count")
                    .sort_values("year"))

    return year_count



def plot_per_year(year_count):
    """
        Function that plots the number of papers per year.

        Args:
            year_count (pandas.DataFrame): Number of papers per year

        Returns:
            fig (matplotlib.figure.Figure): Figure containing the number of papers per year
    """

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(year_count["year"], year_count["count"])

    ax.set_title(f"Liczba artykułów w danym roku")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Liczba artykułów")

    ax.set_xticks(year_count["year"])

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.grid(axis='y', linestyle='--', alpha=0.5)

    return fig



def top_journals(df):
    """
        Function that returns the top journals from the PubMed-compatible DataFrame.

        Args:
            df (pandas.DataFrame): PubMed-compatible DataFrame

        Returns:
            top (pandas.DataFrame): dataframe containing top journals
    """

    top = (df["journal"].value_counts().head(10).reset_index())
    top.columns = ["journal", "total_count"]

    return top



def main():
    print("Functions for pubmed literature module. This is only to be used through an import.")

if __name__ == "__main__":
    main()