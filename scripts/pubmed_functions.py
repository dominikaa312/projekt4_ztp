import pandas as pd
import re
import matplotlib.pyplot as plt



def build_query(config, year):
    topic_query = " OR ".join(config["pubmed"]["queries"])

    city_aliases = config["city_aliases"]
    city_query = " OR ".join(f'"{alias}"[TIAB]' for aliases in city_aliases.values() for alias in aliases)

    year_query = f'"{year}"[PDAT] : "{year}"[PDAT]'

    full_query = f"(({topic_query}) AND ({city_query})) AND ({year_query})"

    return full_query



def extract_month(dp):

    m = re.search(r"^\d{4}-(\d{2})", dp)
    if m:
        return m.group(1)

    m = re.search(r"^\d{4}\s+([A-Za-z]{3})", dp)
    if m:
        month_str = m.group(1).lower()
        months_map = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", "jul": "07",
                      "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
        return months_map.get(month_str)

    return None



def record_to_df(record):

    rows = []
    for rec in record:
        PMID = rec.get("PMID", "")
        title = rec.get("TI", "")
        year = rec.get("DP", "")[:4]
        journal = rec.get("JT", "")
        authors = ", ".join(rec.get("AU", []))
        month = extract_month(rec.get("DP", ""))
        rows.append({"PMID": PMID, "title": title, "year": year, "month": month, "journal": journal, "authors": authors})

    return pd.DataFrame(rows)



def month_count_per_month(df):

    month_counts = (df.groupby("month")
                    .size()
                    .reset_index(name="count")
                    .sort_values("month"))

    return month_counts



def plot_per_month(month_counts, year):

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(month_counts["month"], month_counts["count"])

    ax.set_title(f"Liczba artykułów na miesiąc w roku {year}")
    ax.set_xlabel("Miesiąc")
    ax.set_ylabel("Liczba artykułów")

    return fig



def top_journals(df):

    top = df["journal"].value_counts().head(10).reset_index.rename(columns={"index": "journal", "journal": "count"})

    return top



def main():
    print("Functions for pubmed literature module. This is only to be used through an import.")

if __name__ == "__main__":
    main()