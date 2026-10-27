"""External data: current weather at campus from Open-Meteo (no API key needed).

Shows the three habits for any external service: timeout, limited retries, graceful fallback.
"""

from __future__ import annotations

import logging
import time

import httpx

from assistant_api.schemas import Weather

log = logging.getLogger("assistant_api.weather")

WMO = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    51: "light drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    80: "rain showers",
    81: "heavy showers",
    95: "thunderstorm",
}


class ExternalServiceError(Exception):
    """The upstream service failed and no cached value is available."""


class WeatherClient:
    def __init__(
        self,
        url: str,
        lat: float,
        lon: float,
        timeout_s: float = 3.0,
        retries: int = 1,
        cache_ttl_s: float = 600,
        transport: httpx.BaseTransport | None = None,
    ):
        self.url, self.lat, self.lon = url, lat, lon
        self.retries, self.cache_ttl_s = retries, cache_ttl_s
        self._client = httpx.Client(timeout=timeout_s, transport=transport)
        self._cache: tuple[float, Weather] | None = None

    def current(self) -> Weather:
        if self._cache and time.monotonic() - self._cache[0] < self.cache_ttl_s:
            return self._cache[1]
        params = {"latitude": self.lat, "longitude": self.lon, "current": "temperature_2m,weather_code,wind_speed_10m"}
        last_exc: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = self._client.get(self.url, params=params)
                r.raise_for_status()
                cur = r.json()["current"]
                w = Weather(
                    temperature_c=cur["temperature_2m"],
                    wind_kmh=cur["wind_speed_10m"],
                    description=WMO.get(cur["weather_code"], f"code {cur['weather_code']}"),
                    observed_at=cur["time"],
                )
                self._cache = (time.monotonic(), w)
                return w
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                last_exc = exc
                log.warning("weather attempt %d failed: %s", attempt + 1, type(exc).__name__)
                time.sleep(0.2 * (attempt + 1))
        if self._cache:  # graceful: stale but useful
            return self._cache[1].model_copy(update={"stale": True})
        raise ExternalServiceError("weather service unavailable") from last_exc
