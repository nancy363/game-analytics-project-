"""Small, defensive client for the official SportRadar Tennis API v3."""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class SportRadarError(RuntimeError):
    pass

class SportRadarClient:
    BASE_URL = "https://api.sportradar.com/tennis"

    def __init__(self, api_key: str, access_level: str = "trial",
                 language_code: str = "en", timeout: int = 30):
        if not api_key:
            raise SportRadarError(
                "SPORTRADAR_API_KEY is missing. Add your key to the .env file."
            )
        if access_level not in {"trial", "production"}:
            raise SportRadarError("SPORTRADAR_ACCESS_LEVEL must be trial or production.")
        self.base = f"{self.BASE_URL}/{access_level}/v3/{language_code}"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Accept": "application/json",
            "User-Agent": "TennisAnalyticsStudentProject/1.0",
        })
        retry = Retry(
            total=3, connect=3, read=3, backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def get_json(self, feed: str) -> dict:
        url = f"{self.base}/{feed}.json"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 403:
                raise SportRadarError(
                    "SportRadar returned 403. Check the API key, access level and feed entitlement."
                )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            body = (response.text or "")[:500]
            raise SportRadarError(f"HTTP error for {feed}: {exc}. Response: {body}") from exc
        except requests.RequestException as exc:
            raise SportRadarError(f"Network error for {feed}: {exc}") from exc
        except ValueError as exc:
            raise SportRadarError(f"SportRadar returned invalid JSON for {feed}.") from exc

    def get_competitions(self) -> dict:
        return self.get_json("competitions")

    def get_complexes(self) -> dict:
        return self.get_json("complexes")

    def get_doubles_rankings(self) -> dict:
        return self.get_json("double_competitors_rankings")
