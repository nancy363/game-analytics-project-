"""Streamlit dashboard for Game Analytics: Unlocking Tennis Data with SportRadar API."""
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

from database import get_engine, init_db
from config import get_settings

st.set_page_config(
    page_title="Tennis Analytics Explorer",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main {background-color: #f7f9fc;}
    [data-testid="stMetric"] {
        background: white; padding: 16px; border-radius: 12px;
        border: 1px solid #e7ebf2;
    }
    .block-container {padding-top: 1.5rem;}
</style>
""", unsafe_allow_html=True)

settings = get_settings()
engine = get_engine(settings.database_url)
init_db(engine)

@st.cache_data(ttl=60)
def load_df(query: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})

def safe_df(query: str, params: dict | None = None) -> pd.DataFrame:
    try:
        return load_df(query, params)
    except Exception as exc:
        st.error(f"Database query failed: {exc}")
        return pd.DataFrame()

def refresh_data():
    load_df.clear()

st.title("🎾 Tennis Analytics Explorer")
st.caption("Game Analytics: Unlocking Tennis Data with SportRadar API")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select a section",
        ["Overview", "Competitions", "Complexes & Venues", "Doubles Rankings", "SQL Analysis"],
    )
    st.divider()
    st.caption("Data source: SportRadar Tennis API")
    if st.button("↻ Refresh dashboard data", use_container_width=True):
        refresh_data()
        st.rerun()
    st.caption("To import the latest API data, run `python load_data.py` from the project folder.")

if page == "Overview":
    st.subheader("Project Overview")
    stats = safe_df("""
        SELECT
          (SELECT COUNT(*) FROM competitors) AS total_competitors,
          (SELECT COUNT(DISTINCT country) FROM competitors WHERE country <> '') AS countries,
          (SELECT MAX(points) FROM competitor_rankings) AS highest_points,
          (SELECT COUNT(*) FROM competitions) AS total_competitions,
          (SELECT COUNT(*) FROM venues) AS total_venues
    """)
    if not stats.empty:
        row = stats.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Competitors", f"{int(row.total_competitors):,}")
        c2.metric("Countries", f"{int(row.countries):,}")
        c3.metric("Highest points", f"{int(row.highest_points or 0):,}")
        c4.metric("Competitions", f"{int(row.total_competitions):,}")
        c5.metric("Venues", f"{int(row.total_venues):,}")

    left, right = st.columns(2)
    with left:
        country_df = safe_df("""
            SELECT country, COUNT(*) AS competitors, ROUND(AVG(points), 1) AS average_points
            FROM competitors c
            LEFT JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
            WHERE country IS NOT NULL AND country <> ''
            GROUP BY country ORDER BY competitors DESC LIMIT 15
        """)
        st.markdown("#### Competitors by country")
        if not country_df.empty:
            fig = px.bar(country_df, x="country", y="competitors",
                         title="Top 15 countries by competitor count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No country data yet. Configure your API key and run the data importer.")

    with right:
        type_df = safe_df("""
            SELECT type, COUNT(*) AS total
            FROM competitions GROUP BY type ORDER BY total DESC
        """)
        st.markdown("#### Competition types")
        if not type_df.empty:
            fig = px.pie(type_df, names="type", values="total", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No competition data available yet.")

    st.markdown("#### Latest top-ranked doubles competitors")
    leaders = safe_df("""
        SELECT r.rank, c.name, c.country, r.points, r.movement, r.competitions_played,
               r.tour, r.gender, r.week, r.year
        FROM competitor_rankings r
        JOIN competitors c ON c.competitor_id = r.competitor_id
        ORDER BY r.rank ASC LIMIT 10
    """)
    st.dataframe(leaders, use_container_width=True, hide_index=True)

elif page == "Competitions":
    st.subheader("Competition Explorer")
    df = safe_df("""
        SELECT cp.competition_id, cp.competition_name, cp.parent_id, cp.type,
               cp.gender, cp.level, ca.category_name
        FROM competitions cp
        LEFT JOIN categories ca ON ca.category_id = cp.category_id
        ORDER BY ca.category_name, cp.competition_name
    """)
    if not df.empty:
        f1, f2, f3 = st.columns(3)
        types = ["All"] + sorted(df["type"].dropna().astype(str).unique().tolist())
        genders = ["All"] + sorted(df["gender"].dropna().astype(str).unique().tolist())
        categories = ["All"] + sorted(df["category_name"].dropna().astype(str).unique().tolist())
        selected_type = f1.selectbox("Competition type", types)
        selected_gender = f2.selectbox("Gender", genders)
        selected_category = f3.selectbox("Category", categories)
        filtered = df.copy()
        if selected_type != "All":
            filtered = filtered[filtered.type == selected_type]
        if selected_gender != "All":
            filtered = filtered[filtered.gender == selected_gender]
        if selected_category != "All":
            filtered = filtered[filtered.category_name == selected_category]
        st.caption(f"{len(filtered):,} competitions")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.markdown("#### Competition distribution by category")
        chart = (filtered.groupby("category_name", dropna=False).size()
                 .reset_index(name="competitions"))
        if not chart.empty:
            st.plotly_chart(px.bar(chart, x="category_name", y="competitions"),
                            use_container_width=True)
        top_level = filtered[filtered.parent_id.isna() | (filtered.parent_id == "")]
        with st.expander("Top-level competitions (no parent)"):
            st.dataframe(top_level, use_container_width=True, hide_index=True)
    else:
        st.info("No competition records found. Run the API importer first.")

elif page == "Complexes & Venues":
    st.subheader("Sports Complexes & Venues")
    df = safe_df("""
        SELECT v.venue_id, v.venue_name, v.city_name, v.country_name,
               v.country_code, v.timezone, v.capacity, c.complex_name
        FROM venues v
        LEFT JOIN complexes c ON c.complex_id = v.complex_id
        ORDER BY c.complex_name, v.venue_name
    """)
    if not df.empty:
        a, b = st.columns(2)
        countries = ["All"] + sorted(df.country_name.dropna().unique().tolist())
        complexes = ["All"] + sorted(df.complex_name.dropna().unique().tolist())
        country = a.selectbox("Country", countries)
        complex_name = b.selectbox("Complex", complexes)
        filtered = df.copy()
        if country != "All":
            filtered = filtered[filtered.country_name == country]
        if complex_name != "All":
            filtered = filtered[filtered.complex_name == complex_name]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        counts = (df.groupby("complex_name", dropna=False).size()
                  .reset_index(name="venue_count")
                  .sort_values("venue_count", ascending=False).head(15))
        st.markdown("#### Complexes with the most venues")
        st.plotly_chart(px.bar(counts, x="complex_name", y="venue_count"),
                        use_container_width=True)
    else:
        st.info("No venue records found. Run the API importer first.")

elif page == "Doubles Rankings":
    st.subheader("Doubles Competitor Rankings")
    df = safe_df("""
        SELECT r.rank, c.name, c.country, c.country_code, c.abbreviation,
               r.points, r.movement, r.competitions_played, r.tour,
               r.gender, r.year, r.week
        FROM competitor_rankings r
        JOIN competitors c ON c.competitor_id = r.competitor_id
        ORDER BY r.rank ASC
    """)
    if not df.empty:
        a, b, c = st.columns(3)
        tours = ["All"] + sorted(df.tour.dropna().unique().tolist())
        countries = ["All"] + sorted(df.country.dropna().unique().tolist())
        genders = ["All"] + sorted(df.gender.dropna().unique().tolist())
        tour = a.selectbox("Tour", tours)
        country = b.selectbox("Country", countries)
        gender = c.selectbox("Gender", genders)
        search = st.text_input("Search competitor")
        min_rank, max_rank = int(df["rank"].min()), int(df["rank"].max())
        rank_range = st.slider("Rank range", min_rank, max_rank, (min_rank, max_rank))
        min_points = st.number_input("Minimum points", min_value=0, value=0, step=100)
        filtered = df.copy()
        if tour != "All": filtered = filtered[filtered.tour == tour]
        if country != "All": filtered = filtered[filtered.country == country]
        if gender != "All": filtered = filtered[filtered.gender == gender]
        if search: filtered = filtered[filtered.name.str.contains(search, case=False, na=False)]
        filtered = filtered[
            filtered["rank"].between(rank_range[0], rank_range[1]) &
            (filtered["points"] >= min_points)
        ]
        st.caption(f"{len(filtered):,} ranking records match your filters")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.markdown("#### Points leaderboard")
        chart_data = filtered.nsmallest(10, "rank").sort_values("points", ascending=False)
        if not chart_data.empty:
            st.plotly_chart(px.bar(chart_data, x="name", y="points",
                                   hover_data=["rank", "country"]),
                            use_container_width=True)
        st.markdown("#### Country-wise performance")
        country_data = (filtered.groupby("country")
                        .agg(competitors=("name", "count"),
                             average_points=("points", "mean"),
                             total_points=("points", "sum"))
                        .reset_index().sort_values("competitors", ascending=False))
        st.dataframe(country_data, use_container_width=True, hide_index=True)
    else:
        st.info("No rankings found. Check your SportRadar subscription and run the importer.")

else:
    st.subheader("SQL Analysis")
    queries = {
        "Competitions with category": """
            SELECT cp.competition_name, ca.category_name, cp.type, cp.gender
            FROM competitions cp LEFT JOIN categories ca ON ca.category_id=cp.category_id
            ORDER BY ca.category_name, cp.competition_name
        """,
        "Competition count by category": """
            SELECT ca.category_name, COUNT(cp.competition_id) AS competition_count
            FROM categories ca LEFT JOIN competitions cp ON cp.category_id=ca.category_id
            GROUP BY ca.category_id, ca.category_name ORDER BY competition_count DESC
        """,
        "Doubles competitions": "SELECT * FROM competitions WHERE LOWER(type) LIKE '%doubles%'",
        "Top-level competitions": "SELECT * FROM competitions WHERE parent_id IS NULL OR parent_id=''",
        "Venues with complex": """
            SELECT v.*, c.complex_name FROM venues v
            LEFT JOIN complexes c ON c.complex_id=v.complex_id
        """,
        "Venue count by complex": """
            SELECT c.complex_name, COUNT(v.venue_id) AS venue_count
            FROM complexes c LEFT JOIN venues v ON v.complex_id=c.complex_id
            GROUP BY c.complex_id, c.complex_name ORDER BY venue_count DESC
        """,
        "Competitors with rank and points": """
            SELECT c.name, c.country, r.rank, r.points, r.movement
            FROM competitors c JOIN competitor_rankings r
            ON c.competitor_id=r.competitor_id ORDER BY r.rank
        """,
        "Top 5 competitors": """
            SELECT c.name, c.country, r.rank, r.points
            FROM competitors c JOIN competitor_rankings r
            ON c.competitor_id=r.competitor_id ORDER BY r.rank LIMIT 5
        """,
        "Stable rank competitors": """
            SELECT c.name, c.country, r.rank, r.points
            FROM competitors c JOIN competitor_rankings r
            ON c.competitor_id=r.competitor_id WHERE r.movement=0 ORDER BY r.rank
        """,
        "Competitor count by country": """
            SELECT country, COUNT(*) AS competitor_count FROM competitors
            GROUP BY country ORDER BY competitor_count DESC
        """,
    }
    choice = st.selectbox("Choose an analysis query", list(queries))
    result = safe_df(queries[choice])
    st.dataframe(result, use_container_width=True, hide_index=True)
    st.download_button(
        "Download result as CSV",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="tennis_analysis.csv",
        mime="text/csv",
        disabled=result.empty,
    )

st.divider()
st.caption("Academic project | Python · SportRadar API · SQL · Streamlit")
