# Game Analytics: Unlocking Tennis Data with SportRadar API

A Python + SQL + Streamlit project that extracts tennis data from the SportRadar Tennis API, stores it in relational tables, and provides an interactive analytics dashboard.

## 1. Project features

- Downloads the SportRadar **Competitions**, **Complexes**, and **Doubles Competitor Rankings** feeds.
- Transforms nested JSON into relational records.
- Stores categories, competitions, complexes, venues, competitors, and rankings.
- Provides search, filters, leaderboards, country analysis, charts, and SQL analysis.
- Handles API/network errors and retries temporary server/rate-limit responses.
- Keeps the API key outside source code using environment variables.

## 2. Technology stack

- Python
- SportRadar Tennis API v3
- SQLAlchemy
- SQLite by default; MySQL and PostgreSQL connection URLs are supported
- Streamlit
- Pandas and Plotly

## 3. Project structure

```text
tennis_sport_radar_project/
├── app.py
├── config.py
├── database.py
├── sportradar_client.py
├── data_loader.py
├── load_data.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── sql/
    ├── schema.sql
    └── analysis_queries.sql
```

## 4. Setup

Use Python 3.10 or newer.

### Windows

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set `SPORTRADAR_API_KEY` to the API key provided for your own SportRadar account. Do not share the key or commit `.env` to GitHub.

Set `SPORTRADAR_ACCESS_LEVEL` to `trial` or `production` to match the key/subscription assigned by SportRadar.

## 5. Database configuration

The project runs with SQLite out of the box:

```env
DATABASE_URL=sqlite:///tennis_analytics.db
```

For MySQL, create a database first, then set:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/tennis_analytics
```

For PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/tennis_analytics
```

The application creates the required tables automatically when it starts.

## 6. Fetch API data

Run this once after configuring `.env`:

```bash
python load_data.py
```

The importer calls these SportRadar Tennis API v3 feeds:

- `/competitions.json`
- `/complexes.json`
- `/double_competitors_rankings.json`

Authentication is sent through the `x-api-key` request header. The ranking table is refreshed as a current snapshot each time the importer runs. Other source tables are updated by their SportRadar IDs.

**Important:** Your SportRadar account must have access to the requested feeds. Trial keys may have different data coverage, quotas, or restrictions. A 403 response usually indicates a key/access-level/entitlement issue; a 429 response indicates the request quota/rate limit was reached.

## 7. Run the Streamlit dashboard

```bash
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

Dashboard sections:
1. Overview
2. Competitions
3. Complexes & Venues
4. Doubles Rankings
5. SQL Analysis

## 8. SQL documentation

All SQL queries corresponding to the project brief are provided in:

`sql/analysis_queries.sql`

The table definitions are provided in:

`sql/schema.sql`

## 9. Database tables

| Table | Purpose |
|---|---|
| `categories` | Competition categories |
| `competitions` | Competition details and parent-child hierarchy |
| `complexes` | Sports complex details |
| `venues` | Venues associated with complexes |
| `competitors` | Competitor identity and country information |
| `competitor_rankings` | Rank, movement, points, competitions played, and ranking period |

The project brief's core columns are retained. `level`, `capacity`, `tour`, `gender`, `year`, and `week` are additional useful fields exposed by the API or needed to preserve ranking context.

## 10. Troubleshooting

- **Missing API key:** check `SPORTRADAR_API_KEY` in `.env`.
- **403 Forbidden:** confirm the key, access level, product subscription, and endpoint entitlement.
- **429 Too Many Requests:** wait and retry later; avoid repeated manual imports.
- **Empty dashboard:** run `python load_data.py` and confirm that the API account returns data.
- **Database connection error:** verify the `DATABASE_URL`, database service, credentials, and installed driver.
- **Foreign-key errors:** use the provided importer so parent records are loaded before dependent records.

## 11. Academic project workflow

```text
SportRadar API
      |
      v
Python API Client
      |
      v
JSON Transformation
      |
      v
SQL Relational Database
      |
      v
SQL Analysis Queries
      |
      v
Streamlit Dashboard
```

## 12. GitHub checklist

- Upload Python source files, README, requirements, and SQL files.
- Upload `.env.example`, not `.env`.
- Never upload API keys, passwords, or a database containing private credentials.
- Include screenshots of the running dashboard in the project report.
