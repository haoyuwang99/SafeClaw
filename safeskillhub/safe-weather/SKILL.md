---
name: safe-weather
description: Safe wrapper for the weather skill. Use when querying weather data via wttr.in or Open-Meteo under rate-limiting, location privacy, and data-integrity constraints. Trigger when the user asks about weather, temperature, or forecasts.
---

# Safe Weather

This skill adds a safety layer on top of `weather`.

Use this skill whenever a task involves:
- weather queries
- temperature or forecast lookups
- `wttr.in` or Open-Meteo requests
- travel weather checks

For command syntax, refer to the original `weather` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. excessive request volume (rate limit abuse)
2. exposure of precise user location without consent
3. command injection via location string
4. misuse of curl for non-weather requests
5. treating weather data as authoritative for safety-critical decisions

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Use curl to access URLs other than wttr.in or Open-Meteo endpoints | BLOCK | WE-B01 | Restrict curl usage strictly to weather service URLs |
| Inject shell commands or special characters via location string | BLOCK | WE-B02 | Sanitize location input; refuse strings containing shell metacharacters |
| Rapid repeated requests (more than 5 queries in a single task) | BLOCK | WE-B03 | Refuse excessive queries to avoid rate limiting |
| Present weather data as authoritative for safety-critical decisions (aviation, marine, severe weather) | BLOCK | WE-B04 | Refuse and redirect to official sources (NWS, METAR, etc.) |
| Use any HTTP tool other than curl (e.g., wget, httpie, fetch) for weather queries (refined) | BLOCK | WE-B05 | Only curl is sanctioned for accessing weather endpoints |
| Query weather using precise user coordinates (lat/lng) | CONFIRM | WE-C01 | Confirm that user consents to sending coordinates to external service |
| Query weather for a user-specified city or location name | ALLOW | WE-A01 | Safe; location names are non-sensitive |
| Query weather using airport code | ALLOW | WE-A02 | Safe; public identifier |
| Choose output format (one-liner, JSON, detailed) | ALLOW | WE-A03 | Safe format selection |
| Query forecast (today, tomorrow, 3-day, week) | ALLOW | WE-A04 | Safe read-only query |

---

## Required Operating Constraints

1. Only use curl (no wget, httpie, or other HTTP tools) to access `wttr.in` or `api.open-meteo.com`.
2. Sanitize location strings before including in URLs.
3. Limit to a reasonable number of queries per task.
4. Confirm before sending precise coordinates externally.
5. Never present weather data as safety-critical guidance.
6. Summarize weather results rather than dumping raw output.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the query type (current / forecast)
2. State the location data being sent (coordinates)
3. State risk:
   - location privacy (coordinates sent to external service)
4. Ask for confirmation

Example:

> This query will send your coordinates (37.7749, -122.4194) to wttr.in to get local weather. This reveals your approximate location to an external service. Confirm?

---

## Output Policy

Allowed:
- summarized weather conditions
- temperature, wind, humidity readings
- forecast summaries

Disallowed:
- raw curl output dumps without summarization
- user coordinates echoed unnecessarily
- weather data framed as safety-critical advice

---

## Domain Notes

The `weather` skill is relatively low-risk compared to communication or credential tools. The primary concerns are location privacy (coordinates sent externally), rate limiting (wttr.in is a free service), and ensuring weather data is not misused for safety-critical decisions where official sources should be consulted instead.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests weather information, temperature lookups, or forecasts via `wttr.in` or Open-Meteo, including travel weather checks.

**Task:** Ensure curl usage is restricted to approved weather service endpoints and location inputs are sanitized. BLOCK requests to non-weather URLs, shell injection via location strings, excessive query volume (more than 5 per task), presentation of weather data as authoritative for safety-critical decisions (aviation, marine, severe weather), and use of non-curl HTTP tools (wget, httpie, etc.). CONFIRM queries that include precise user coordinates, since these reveal approximate location to an external service. ALLOW queries by city name, airport code, or format/forecast selection.

**Resources:** `references/risk-notes.md` — threat model and risk rationale for the weather skill. No auxiliary config or scripts required.

---

## References

- Original skill: `weather`
- `references/risk-notes.md`
