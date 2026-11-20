"""Database engine and relational schema."""
from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Integer, ForeignKey,
    Index, UniqueConstraint
)
from sqlalchemy.engine import Engine

metadata = MetaData()

categories = Table(
    "categories", metadata,
    Column("category_id", String(50), primary_key=True),
    Column("category_name", String(100), nullable=False),
)

competitions = Table(
    "competitions", metadata,
    Column("competition_id", String(50), primary_key=True),
    Column("competition_name", String(100), nullable=False),
    Column("parent_id", String(50), nullable=True),
    Column("type", String(20), nullable=False, default="unknown"),
    Column("gender", String(20), nullable=False, default="unknown"),
    Column("category_id", String(50), ForeignKey("categories.category_id")),
    # Extra metadata from SportRadar, useful for the requested level filters.
    Column("level", String(40), nullable=True),
)
Index("ix_competitions_category", competitions.c.category_id)
Index("ix_competitions_type_gender", competitions.c.type, competitions.c.gender)

complexes = Table(
    "complexes", metadata,
    Column("complex_id", String(50), primary_key=True),
    Column("complex_name", String(100), nullable=False),
)

venues = Table(
    "venues", metadata,
    Column("venue_id", String(50), primary_key=True),
    Column("venue_name", String(100), nullable=False),
    Column("city_name", String(100), nullable=False, default="Unknown"),
    Column("country_name", String(100), nullable=False, default="Unknown"),
    Column("country_code", String(3), nullable=False, default="UNK"),
    Column("timezone", String(100), nullable=False, default="Unknown"),
    Column("complex_id", String(50), ForeignKey("complexes.complex_id")),
    Column("capacity", Integer, nullable=True),
)
Index("ix_venues_country", venues.c.country_name)
Index("ix_venues_complex", venues.c.complex_id)

competitors = Table(
    "competitors", metadata,
    Column("competitor_id", String(50), primary_key=True),
    Column("name", String(100), nullable=False),
    Column("country", String(100), nullable=False, default="Unknown"),
    Column("country_code", String(3), nullable=False, default="UNK"),
    Column("abbreviation", String(10), nullable=False, default=""),
)

competitor_rankings = Table(
    "competitor_rankings", metadata,
    Column("rank_id", Integer, primary_key=True, autoincrement=True),
    Column("rank", Integer, nullable=False),
    Column("movement", Integer, nullable=False, default=0),
    Column("points", Integer, nullable=False, default=0),
    Column("competitions_played", Integer, nullable=False, default=0),
    Column("competitor_id", String(50), ForeignKey("competitors.competitor_id"), nullable=False),
    # Additional API metadata, preserving the tour/week context of a ranking.
    Column("tour", String(20), nullable=False, default="Unknown"),
    Column("gender", String(20), nullable=False, default="unknown"),
    Column("year", Integer, nullable=True),
    Column("week", Integer, nullable=True),
)
Index("ix_rankings_rank", competitor_rankings.c.rank)
Index("ix_rankings_points", competitor_rankings.c.points)
Index("ix_rankings_country", competitors.c.country)

def get_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)

def init_db(engine: Engine) -> None:
    metadata.create_all(engine)
