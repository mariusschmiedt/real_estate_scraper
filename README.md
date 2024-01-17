# real_estate_scraper

Real Estate Scraper is based on the implementation of the real estate scraper: https://github.com/orangecoding/fredy
It is scraping different real estate platforms to retreive real estates.
- immoscout
- immoswp
- immowelt
- kleinanzeigen

The Python scraping library is BeautifulSoup4. With the found results the geo information of the real estate is determined with geopy and Nominatim with OpenStreetMap data.

The real estate listings and the found addresses are stored in two different tables of one sql database.

# Jobs
To determine which real estate platform/s should be scraped a job has to be set up with the search link.

```json
{
  "kleinanzeigen": {
    "apartement_buy": {
      "url": "https://www.kleinanzeigen.de/s-stuttgart/eigentumswohnung/k0l9280",
      "country": "Germany"
    }
  }
}
```

or for multiple jobs

```json
{
  "immoscout": {
    "apartement_rent": {
      "url": "https://www.immobilienscout24.de/Suche/de/wohnung-mieten",
      "country": "Germany"
    }
  },
  "kleinanzeigen": {
    "apartement_buy": {
      "url": "https://www.kleinanzeigen.de/s-stuttgart/eigentumswohnung/k0l9280",
      "country": "Germany"
    }
  }
}
```
