"""Transform SportRadar nested JSON feeds and load them into SQL tables."""
import logging
from sqlalchemy import delete
from sqlalchemy.engine import Engine
from database import (
    categories, competitions, complexes, venues, competitors, competitor_rankings
)

logger = logging.getLogger(__name__)

def _items(value):
    """Normalize a possibly missing API list."""
    return value if isinstance(value, list) else []

def _text(value, default="Unknown"):
    return str(value).strip() if value not in (None, "") else default

def transform_competitions(payload: dict):
    category_rows, competition_rows = {}, []
    for item in _items(payload.get("competitions")):
        if not isinstance(item, dict):
            continue
        cat = item.get("category") or {}
        cat_id = cat.get("id")
        if cat_id:
            category_rows[cat_id] = {
                "category_id": cat_id,
                "category_name": _text(cat.get("name")),
            }
        competition_rows.append({
            "competition_id": item.get("id"),
            "competition_name": _text(item.get("name")),
            "parent_id": item.get("parent_id"),
            "type": _text(item.get("type"), "unknown"),
            "gender": _text(item.get("gender"), "unknown"),
            "category_id": cat_id,
            "level": item.get("level"),
        })
    competition_rows = [r for r in competition_rows if r["competition_id"]]
    return list(category_rows.values()), competition_rows

def transform_complexes(payload: dict):
    complex_rows, venue_rows = [], []
    for item in _items(payload.get("complexes")):
        if not isinstance(item, dict) or not item.get("id"):
            continue
        complex_id = item["id"]
        complex_rows.append({
            "complex_id": complex_id,
            "complex_name": _text(item.get("name")),
        })
        for venue in _items(item.get("venues")):
            if not isinstance(venue, dict) or not venue.get("id"):
                continue
            venue_rows.append({
                "venue_id": venue["id"],
                "venue_name": _text(venue.get("name")),
                "city_name": _text(venue.get("city_name")),
                "country_name": _text(venue.get("country_name")),
                "country_code": _text(venue.get("country_code"), "UNK")[:3],
                "timezone": _text(venue.get("timezone")),
                "complex_id": complex_id,
                "capacity": venue.get("capacity"),
            })
    return complex_rows, venue_rows

def transform_rankings(payload: dict):
    competitor_rows, ranking_rows = {}, []
    for ranking_group in _items(payload.get("rankings")):
        if not isinstance(ranking_group, dict):
            continue
        tour = _text(ranking_group.get("name"))
        gender = _text(ranking_group.get("gender"), "unknown")
        year, week = ranking_group.get("year"), ranking_group.get("week")
        for item in _items(ranking_group.get("competitor_rankings")):
            if not isinstance(item, dict):
                continue
            competitor = item.get("competitor") or {}
            competitor_id = competitor.get("id")
            if not competitor_id:
                continue
            competitor_rows[competitor_id] = {
                "competitor_id": competitor_id,
                "name": _text(competitor.get("name")),
                "country": _text(competitor.get("country")),
                "country_code": _text(competitor.get("country_code"), "UNK")[:3],
                "abbreviation": _text(competitor.get("abbreviation"), "")[:10],
            }
            ranking_rows.append({
                "rank": int(item.get("rank") or 0),
                "movement": int(item.get("movement") or 0),
                "points": int(item.get("points") or 0),
                "competitions_played": int(item.get("competitions_played") or 0),
                "competitor_id": competitor_id,
                "tour": tour,
                "gender": gender,
                "year": int(year) if year is not None else None,
                "week": int(week) if week is not None else None,
            })
    return list(competitor_rows.values()), ranking_rows

def _upsert(conn, table, rows, key):
    """Portable update-then-insert upsert for SQLite/MySQL/PostgreSQL."""
    for row in rows:
        existing = conn.execute(
            table.select().where(table.c[key] == row[key])
        ).first()
        if existing:
            conn.execute(table.update().where(table.c[key] == row[key]).values(**row))
        else:
            conn.execute(table.insert().values(**row))

def load_all(engine: Engine, competitions_payload: dict,
             complexes_payload: dict, rankings_payload: dict) -> dict:
    cats, comps = transform_competitions(competitions_payload)
    complex_rows, venue_rows = transform_complexes(complexes_payload)
    competitor_rows, ranking_rows = transform_rankings(rankings_payload)

    # One transaction: do not leave partially refreshed tables on a failed import.
    with engine.begin() as conn:
        _upsert(conn, categories, cats, "category_id")
        _upsert(conn, competitions, comps, "competition_id")
        _upsert(conn, complexes, complex_rows, "complex_id")
        _upsert(conn, venues, venue_rows, "venue_id")
        _upsert(conn, competitors, competitor_rows, "competitor_id")

        # Ranking feed represents a current snapshot; replace old snapshot.
        conn.execute(delete(competitor_rankings))
        if ranking_rows:
            conn.execute(competitor_rankings.insert(), ranking_rows)

    return {
        "categories": len(cats), "competitions": len(comps),
        "complexes": len(complex_rows), "venues": len(venue_rows),
        "competitors": len(competitor_rows), "rankings": len(ranking_rows),
    }
