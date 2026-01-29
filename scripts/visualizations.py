import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def plot_city_trends(monthly_df, cities, year, city_aliases, ylim=[0, 75]):
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

    # preparing data
    if "year" not in monthly_df.columns:
        monthly_df = monthly_df.reset_index()

    # filtering data to have only one year and cities of interest
    selected_cols = ["year", "month"]

    for city in cities:
        if city in monthly_df.columns:
            selected_cols.append(city)
        elif city_aliases and city in city_aliases:
            for alias in city_aliases[city]:
                if alias in monthly_df.columns:
                    selected_cols.append(alias)
                    break

    df = monthly_df[monthly_df["year"] == year][selected_cols]

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
    plt.close(fig)
    return fig



def heatmaps(monthly_df, year, cities, city_aliases):
    """
        Function that creates heatmaps for selected cities and years.
        Args:
            monthly_df (pd.DataFrame): dataframe with monthly average levels of PM2.5
            year (int): year to include in the plot
            cities (list[str]): cities to include in the plot
        Returns:
            fig (plotly.graph_objects.Figure): heatmaps for selected cities and year
    """

    if "year" not in monthly_df.columns:
        monthly_df = monthly_df.reset_index()

    if isinstance(cities, str):
        cities = [cities]

    # filtering data to have only one year and cities of interest
    selected_cols = ["year", "month"]

    for city in cities:
        if city in monthly_df.columns:
            selected_cols.append(city)
        elif city_aliases and city in city_aliases:
            for alias in city_aliases[city]:
                if alias in monthly_df.columns:
                    selected_cols.append(alias)
                    break

    df = monthly_df[monthly_df["year"] == year][selected_cols]
    city_cols = [col for col in selected_cols if col not in ["year", "month"]]

    # creating subplots and heatmap
    zmin = df[city_cols].min().min()
    zmax = df[city_cols].max().max()

    n = len(city_cols)
    cols = 2 if n > 1 else 1
    rows = int(np.ceil(n / cols))

    fig = make_subplots(rows=rows, cols=cols, subplot_titles=city_cols)

    for i, loc in enumerate(city_cols):
        row = i // cols + 1
        col = i % cols + 1

        heatmap_data = df.set_index("month")[loc].reindex(range(1, 13))
        z = heatmap_data.values[::-1].reshape(12, 1)

        fig.add_trace(
            go.Heatmap(z=z, x=[""], y=list(range(1, 13)),
                    colorscale="RdBu_r",
                    zmin=zmin, zmax=zmax,
                    showscale=(i == 0),
                    hovertemplate = ("Stężenie: %{z:.2f} µg/m³"),
                    colorbar=dict(title=dict(text="PM2.5 µg/m³"),
                                tickmode="array",
                                tickvals=np.linspace(zmin, zmax, 5),
                                ticktext=[f"{v:.0f}" for v in np.linspace(zmin, zmax, 5)])),
                    row=row, col=col)

    # each month is labeled on y-ax
    for i in range(1, rows * cols + 1):
        fig.update_yaxes(tickmode="array",
                        tickvals=list(range(1, 13)),
                        ticktext=[str(m) for m in range(1, 13)][::-1],
                        title_text="Miesiąc",
                        title_standoff=7,
                        row=(i - 1) // cols + 1,
                        col=(i - 1) % cols + 1)

    fig.update_layout(height=400 * rows, width=700,
                    title=dict(text=f"Średnie miesięczne stężenia PM2.5 w roku {year}", x=0.5), font=dict(size=11))

    return fig



def main():
    print("visualizations module. This is only to be used through an import.")

if __name__ == "__main__":
    main()