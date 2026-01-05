import pg8000.dbapi as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import os
from config import settings

def get_db_config():
    """Get DB config from settings"""
    return {
        "user": settings.db_user,
        "password": settings.db_password,
        "database": settings.db_name,
        "host": settings.db_host,
        "port": settings.db_port
    }

COLORS = {
    "bg": "#121212",
    "text": "#E5E5E5",
    "orange": "#FF5E00",
    "purple": "#7000FF",
    "dark_purple": "#3700b3"
}

def set_seaborn_style():
    """Configure Seaborn for dark theme"""
    sns.set_theme(context="poster", style="dark", rc={
        "axes.facecolor": COLORS["bg"],
        "figure.facecolor": COLORS["bg"],
        "grid.color": "#333333",
        "text.color": COLORS["text"],
        "axes.labelcolor": COLORS["text"],
        "xtick.color": COLORS["text"],
        "ytick.color": COLORS["text"],
        "axes.edgecolor": COLORS["bg"]
    })

def get_data(query):
    conn = db.connect(**get_db_config())
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def plot_heatmap_activity(pdf):
    print("1. [Seaborn] Drawing Heatmap...")
    query = """
        SELECT EXTRACT(YEAR FROM concert_date)::INT as year, 
               EXTRACT(MONTH FROM concert_date)::INT as month, 
               COUNT(*) as count
        FROM Concerts
        WHERE EXTRACT(YEAR FROM concert_date) >= 2010
        GROUP BY year, month
        ORDER BY year DESC, month ASC;
    """
    df = get_data(query)
    pivot_table = df.pivot(index="year", columns="month", values="count").fillna(0)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(data=pivot_table,
                cmap="inferno",
                annot=True,
                fmt=".0f",
                linewidths=.5,
                linecolor=COLORS["bg"],
                cbar_kws={'label': 'Concert count'},
                ax=ax)

    ax.set_title("ACTIVITY HEATMAP (2010-2024)", color=COLORS["orange"], pad=20, fontweight="bold")
    ax.set_xlabel("Month", color=COLORS["text"])
    ax.set_ylabel("Year", color=COLORS["text"])

    pdf.savefig(fig, facecolor=COLORS["bg"])
    plt.close()

def plot_artist_barplot(pdf):
    print("2. [Seaborn] Drawing Top Artists (Barplot)...")
    query = """
        SELECT T2.artist_name, COUNT(T1.concert_id) as count
        FROM Concerts AS T1 
        JOIN Artists AS T2 ON T1.artist_mbid = T2.artist_mbid
        GROUP BY T2.artist_name
        ORDER BY count DESC 
        LIMIT 10;
    """
    df = get_data(query)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x="count", y="artist_name", data=df,
                palette="blend:#7000FF,#FF5E00",
                ax=ax)

    ax.set_title("TOP-10 ARTISTS (BAR PLOT)", color=COLORS["text"], pad=20, fontweight="bold")
    ax.set_xlabel("Show count", color=COLORS["text"])
    ax.set_ylabel("", color=COLORS["text"])
    ax.bar_label(ax.containers[0], color=COLORS["text"], padding=5)

    pdf.savefig(fig, facecolor=COLORS["bg"])
    plt.close()

def plot_country_boxplot(pdf):
    print("3. [Seaborn] Drawing Country Distribution (Boxplot)...")
    query = """
        SELECT T2.country_name, EXTRACT(YEAR FROM concert_date) as year, COUNT(*) as count
        FROM Concerts AS T1
        JOIN Venues AS V ON T1.venue_id = V.venue_id
        JOIN Cities AS C ON V.city_id = C.city_id
        JOIN Countries AS T2 ON C.country_code = T2.country_code
        WHERE T2.country_code IN ('DE', 'GB', 'FR', 'IT', 'ES')
        GROUP BY T2.country_name, year;
    """
    df = get_data(query)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.boxplot(x="country_name", y="count", data=df,
                palette="dark:violet",
                boxprops=dict(alpha=.7),
                ax=ax)
    sns.stripplot(x="country_name", y="count", data=df,
                  color=COLORS["orange"], alpha=0.6, jitter=True, ax=ax)

    ax.set_title("CONCERT TOUR DENSITY (DISTRIBUTION)", color=COLORS["purple"], pad=20, fontweight="bold")
    ax.set_ylabel("Concerts per year", color=COLORS["text"])
    ax.set_xlabel("Country", color=COLORS["text"])

    pdf.savefig(fig, facecolor=COLORS["bg"])
    plt.close()

def plot_trend_regplot(pdf):
    print("4. [Seaborn] Drawing Trend with Regression...")
    query = """
        SELECT EXTRACT(YEAR FROM concert_date)::INT as year, COUNT(*) as count
        FROM Concerts
        GROUP BY year
        ORDER BY year ASC;
    """
    df = get_data(query)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.regplot(x="year", y="count", data=df,
                scatter_kws={"color": COLORS["orange"], "s": 100},
                line_kws={"color": COLORS["purple"]},
                ax=ax)

    ax.set_title("INDUSTRY GROWTH TREND (WITH REGRESSION LINE)", color=COLORS["text"], pad=20, fontweight="bold")

    pdf.savefig(fig, facecolor=COLORS["bg"])
    plt.close()

def create_seaborn_report():
    set_seaborn_style()
    filename = 'rock_analytics_seaborn.pdf'

    print(f"Generating advanced report: {filename}...")

    try:
        with PdfPages(filename) as pdf:
            fig = plt.figure(figsize=(11, 8))
            fig.text(0.5, 0.6, "ROCK DATA SCENE", ha='center', va='center', fontsize=50, fontweight='bold',
                     color=COLORS["orange"])
            fig.text(0.5, 0.5, "ADVANCED SEABORN ANALYTICS", ha='center', va='center', fontsize=20,
                     color=COLORS["purple"])
            pdf.savefig(fig, facecolor=COLORS["bg"])
            plt.close()

            plot_heatmap_activity(pdf)
            plot_artist_barplot(pdf)
            plot_country_boxplot(pdf)
            plot_trend_regplot(pdf)

        print(f"\n✅ DONE! Check file: {os.path.abspath(filename)}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    create_seaborn_report()
