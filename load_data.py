"""Fetch all three required SportRadar feeds and load the SQL database."""
import logging
from config import get_settings
from database import get_engine, init_db
from sportradar_client import SportRadarClient, SportRadarError
from data_loader import load_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def main():
    settings = get_settings()
    engine = get_engine(settings.database_url)
    init_db(engine)

    client = SportRadarClient(
        api_key=settings.sportradar_api_key,
        access_level=settings.access_level,
        language_code=settings.language_code,
        timeout=settings.request_timeout,
    )

    try:
        logging.info("Downloading competitions...")
        competitions_payload = client.get_competitions()
        logging.info("Downloading complexes and venues...")
        complexes_payload = client.get_complexes()
        logging.info("Downloading doubles competitor rankings...")
        rankings_payload = client.get_doubles_rankings()

        counts = load_all(
            engine, competitions_payload, complexes_payload, rankings_payload
        )
        logging.info("Import completed successfully.")
        for table, count in counts.items():
            logging.info("%s: %s rows", table, count)
    except SportRadarError as exc:
        logging.error("SportRadar import failed: %s", exc)
        raise
    except Exception:
        logging.exception("Unexpected import/database error.")
        raise

if __name__ == "__main__":
    main()
