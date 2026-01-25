import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_city_trends(monthly_df, cities=["Warszawa", "Katowice"], years=[2015, 2024], ylim=[0, 75]):
    """(Zad2)
    Plot monthly PM2.5 trends for selected cities and years.

    Args:
        monthly_df (pd.DataFrame): DataFrame with MultiIndex (year, month) and cities as columns.
        cities (list[str]): Cities to include in the plot.
        years (list[int]): Years to include in the plot.
        ylim (list[int]): Y-axis limits.

    Returns:
        ax (matplotlib.axes.Axes): the desired lineplot to be shown in Zad2
    """

    # data preparation
    df = monthly_df.loc[years, cities].reset_index()

    df_long = df.melt(
        id_vars=["year", "month"],
        var_name="city",
        value_name="pm25"
    )

    df_long["series"] = (
        df_long["city"] + " " + df_long["year"].astype(str)
    )

    # coloring
    palette = sns.color_palette("coolwarm", 4)

    city_colors = {
        cities[0]: palette[:2][::-1], # reverse the pallete here for more consistent coloring (darker lines for later years)
        cities[1]: palette[2:],
    }

    year_order = sorted(years)
    color_map = {
        f"{city} {year}": city_colors[city][i]
        for city in cities
        for i, year in enumerate(year_order)
    }

    # plotting
    fig, ax = plt.subplots(figsize=(12, 6))

    sns.lineplot(
        data=df_long,
        x="month",
        y="pm25",
        hue="series",
        palette=color_map,
        marker="o",
        alpha=0.85,
        ax=ax,
    )

    ax.set_title(f"Wykres stężenia PM2.5 (µg/m³) w {cities[0]} i {cities[-1]} w latach {years[0]} oraz {years[-1]}", fontsize=13)
    ax.set_xlabel("Miesiąc")
    ax.set_ylabel("PM2.5 (µg/m³)")
    ax.set_xlim(1, 12)
    ax.set_ylim(*ylim)

    ax.set_xticks(range(1,13))
    ax.grid(alpha=0.4)

    ax.legend(title="", frameon=False)
    fig.tight_layout()

    return ax

def heatmaps(monthly_df):
    """
        Args:
            monthly_df (pd.DataFrame): DataFrame z śrędnią miesięczna stężenia PM2.5 dla wszystkich lokalizacji i lat.

        Returns:
            fig (plotly.graph_objects.Figure): Wykres heatmap z stężeniem PM2.5 dla wszystkich lokalizacji i lat.
    """

    # przygotowanie danych i parametrów wykresu
    locations = [c for c in monthly_df.columns if c not in ["year", "month"]]

    zmin = monthly_df[locations].min().min()
    zmax = monthly_df[locations].max().max()

    years = [2015, 2018, 2021, 2024]

    n = len(locations)
    rows = int(np.ceil(n / 2))
    cols = 2

    # tworzenie subplotów
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=locations)

    colorscale = "Viridis"

    for i, loc in enumerate(locations):
        row = i // 2 + 1
        col = i % 2 + 1


        heatmap_data = monthly_df.pivot(index="year", columns="month", values=loc)

        heatmap_data = heatmap_data.reindex(index=years, columns=range(1, 13))

        y = heatmap_data.index.astype(str)
        x = heatmap_data.columns

        showscale = i == 0

        # tworzenie heatmapy i dodanie jej do odpowiedniego subplotu
        hm = go.Heatmap(z=heatmap_data.values, x=x, y=y,
                        colorscale=colorscale,
                        zmin=zmin, zmax=zmax,
                        colorbar=dict(title=dict(text="PM2.5 µg/m³"),
                                      tickmode="array",
                                      tickvals=np.linspace(zmin, zmax, 5),
                                      ticktext=[f"{v:.0f}" for v in np.linspace(zmin, zmax, 5)],
                                      len=0.2, y=0.7, x=1.05),
                        hovertemplate="PM2.5: %{z} µg/m³",
                        showscale=showscale)

        fig.add_trace(hm, row=row, col=col)

    # aktualizacja osi dla wszystkich subplotów
    for i in range(1, rows * cols + 1):
        fig.update_yaxes(categoryorder='array', categoryarray=y,
                         row=(i - 1) // 2 + 1, col=(i - 1) % 2 + 1,
                         title_text="Rok", title_standoff=1)

        fig.update_xaxes(tickmode="array", tickvals=list(range(1, 13)), ticktext=list(range(1, 13)),
                         row=(i - 1) // 2 + 1, col=(i - 1) % 2 + 1,
                         title_text="Miesiąc", title_standoff=5)

    # dodatkowe ustawienia ogólnego wykresu
    fig.update_layout(height=250 * rows, width=750,
                      title=dict(text='Średnie PM2.5 w latach 2015, 2018, 2021 i 2024', x=0.5, y=0.99),
                      font=dict(size=11))

    return fig


def plot_pm25_exceedance_bars(
    exceedance_counts: pd.DataFrame,
    top_n: int = 3,
    base_year: int = 2024,
    threshold: float = 15,
    figsize=(12, 6),
):
    """(Zad4)
    Create a grouped barplot of the number of days with average PM2.5 above who_threshold.
    Include top_n best and worst stations in terms of days over treshold in year base_year.

    Args:
        exceedance_counts (pd.DataFrame): 
        top_n (int): Number of highest and lowest exceedence stations to be displayed.
        base_year (int): year that constitues the criterion for selecting the highest and lowest exceedence stations.  
        who_threshold (int): information to be displayed on the plot

    Returns:
        ax (matplotlib.axes.Axes): the desired barplot to be shown in Zad4
    """
    # select top & bottom stations based on base_year
    exceedance_base = (
        exceedance_counts
        .loc[exceedance_counts["year"] == base_year]
        .sort_values("days_exceeded", ascending=True)
    )

    top_stations = exceedance_base["station"].tail(top_n).tolist()
    bottom_stations = exceedance_base["station"].head(top_n).tolist()
    # keep selected stations in a list for plot ordering
    selected_stations = bottom_stations + top_stations

    plot_df = (
        exceedance_counts
        .loc[exceedance_counts["station"].isin(selected_stations)]
        .copy()
    )

    # create labels for the barplot
    plot_df["label"] = (
        plot_df["city"].astype(str) + ": " + plot_df["station"].astype(str)
    )

    # build station to label mapping to make labels ordered correctly
    label_map = (
        plot_df
        .drop_duplicates("station")
        .set_index("station")["label"]
        .to_dict()
    )

    # try to make a colormap that always looks good...
    years = sorted(plot_df["year"].unique())
    palette = sns.color_palette("magma", n_colors=len(years) + 2)[2:]
    year_palette = dict(zip(years, palette))

    fig, ax = plt.subplots(figsize=figsize)

    sns.barplot(
        data=plot_df,
        x="station",
        y="days_exceeded",
        hue="year",
        order=selected_stations,
        palette=year_palette,
        ax=ax,
    )

    ax.set_xticks(range(len(selected_stations)))
    # replace x-axis labels with "city: station"
    ax.set_xticklabels(
        [label_map[s] for s in selected_stations],
        rotation=45,
        ha="right"
    )

    # styling
    ax.set_title(
        "Liczba dni z przekroczeniem normy dobowej PM2.5\n"
        f"(PM2.5 > {threshold} µg/m³, WHO)\n"
        f"{top_n} stacje z najmniejszą i {top_n} z największą liczbą dni w {base_year}",
        fontsize=13,
    )

    ax.set_xlabel("Stacja pomiarowa (miasto: kod stacji)")
    ax.set_ylabel("Liczba dni z przekroczeniem normy dobowej")
    ax.grid(axis="y", alpha=0.4)
    ax.legend(title="Rok", frameon=False)

    fig.tight_layout()
    return ax

def main():
    print("visualizations module. This is only to be used through an import.")

if __name__ == "__main__":
    main()