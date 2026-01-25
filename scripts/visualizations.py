import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_city_trends(monthly_df, cities, year, ylim=[0, 75]):
    """
    Plot monthly PM2.5 trends for selected cities and years.

    Args:
        monthly_df (pd.DataFrame): DataFrame with MultiIndex (year, month) and cities as columns.
        cities (list[str]): Cities to include in the plot.
        year (list[int]): Year to include in the plot.
        ylim (list[int]): Y-axis limits.

    Returns:
        ax (matplotlib.axes.Axes): the desired lineplot to be shown in Zad2
    """

    df = monthly_df[monthly_df["year"] == year][["year", "month"] + cities]

    df_long = df.melt(
        id_vars=["year", "month"],
        var_name="city",
        value_name="pm25"
    )

    df_long["series"] = (
        df_long["city"] + " " + df_long["year"].astype(str)
    )

    # plotting
    fig, ax = plt.subplots(figsize=(12, 6))

    sns.lineplot(
        data=df_long,
        x="month",
        y="pm25",
        hue="series",
        marker="o",
        alpha=0.85,
        ax=ax,
    )

    ax.set_title(f"Wykres stężenia PM2.5 (µg/m³) w roku {year}", fontsize=13)
    ax.set_xlabel("Miesiąc")
    ax.set_ylabel("PM2.5 (µg/m³)")
    ax.set_xlim(1, 12)
    ax.set_ylim(*ylim)

    ax.set_xticks(range(1,13))
    ax.grid(alpha=0.4)

    ax.legend(title="", frameon=False)
    fig.tight_layout()

    return fig


def heatmaps(monthly_df, year, cities):
    """
        Args:
            monthly_df (pd.DataFrame): DataFrame z śrędnią miesięczna stężenia PM2.5 dla wszystkich lokalizacji i lat.
            year (int): Rok, który ma być uwzględniony w wykresie.

        Returns:
            fig (plotly.graph_objects.Figure): Wykres heatmap z stężeniem PM2.5 dla wszystkich lokalizacji i podanego roku.
    """

    if isinstance(cities, str):
        cities = [cities]

    locations = [c for c in monthly_df.columns if c not in ["year", "month"]]
    locations = [c for c in locations if c in cities]


    zmin = monthly_df[locations].min().min()
    zmax = monthly_df[locations].max().max()

    n = len(locations)
    cols = 2 if n > 1 else 1
    rows = int(np.ceil(n / cols))

    fig = make_subplots(rows=rows, cols=cols, subplot_titles=locations)

    for i, loc in enumerate(locations):
        row = i // cols + 1
        col = i % cols + 1

        heatmap_data = monthly_df.set_index("month")[loc].reindex(range(1, 13))
        z = heatmap_data.values.reshape(12, 1)

        fig.add_trace(
            go.Heatmap(z=z, x=[""], y=list(range(1, 13)),
                    colorscale="Viridis",
                    zmin=zmin, zmax=zmax,
                    showscale=(i == 0),
                    hovertemplate = ("Miesiąc: %{y}<br>"
                                    "Stężenie: %{z:.2f} µg/m³"
                                    "<extra></extra>"),
                    colorbar=dict(title=dict(text="PM2.5 µg/m³"),
                                tickmode="array",
                                tickvals=np.linspace(zmin, zmax, 5),
                                ticktext=[f"{v:.0f}" for v in np.linspace(zmin, zmax, 5)])),
                    row=row, col=col)

    for i in range(1, rows * cols + 1):
        fig.update_yaxes(tickmode="array",
                        tickvals=list(range(1, 13)),
                        ticktext=[str(m) for m in range(1, 13)],
                        title_text="Miesiąc",
                        row=(i - 1) // cols + 1,
                        col=(i - 1) % cols + 1)

    fig.update_layout(height=400 * rows, width=700,
        title=dict(text=f"Średnie miesięczne stężenia PM2.5 w roku {year}", x=0.5), font=dict(size=11))

    return fig


def plot_pm25_exceedance_bars(exceedance_counts, top_n, base_year, threshold, figsize=(12, 6),):
    """
    Create a grouped barplot of the number of days with average PM2.5 above who_threshold.
    Include top_n best and worst stations in terms of days over threshold in year base_year.

    Args:
        exceedance_counts (pd.DataFrame): 
        top_n (int): Number of highest and lowest exceedence stations to be displayed.
        base_year (int): year that constitues the criterion for selecting the highest and lowest exceedence stations.  
        threshold (int): information to be displayed on the plot

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
    return fig, ax

def main():
    print("visualizations module. This is only to be used through an import.")

if __name__ == "__main__":
    main()