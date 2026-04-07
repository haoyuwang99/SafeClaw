# Risk Notes for safe-weather

## Threat Model Summary

The `weather` skill uses `curl` to query `wttr.in` or Open-Meteo for weather data. It is a low-risk, read-only skill, but still has concerns around location privacy, rate limiting, and potential misuse of curl as a general HTTP client.

## Key Risks

### 1. Location Privacy
Risk:
- Queries with precise lat/lng coordinates reveal user location to an external service.
- Location data in URL parameters may be logged by the service.

Mitigation:
- Confirm before sending precise coordinates.
- Prefer city names or airport codes over raw coordinates.

### 2. Rate Limit Abuse
Risk:
- wttr.in is a free service with rate limits.
- Excessive queries could get the user's IP temporarily blocked.

Mitigation:
- Limit queries per task.
- Block rapid repeated requests.

### 3. Command Injection via Location String
Risk:
- Location strings are interpolated into curl URLs.
- Malicious location input could inject shell commands or URL parameters.

Mitigation:
- Sanitize location input.
- Block shell metacharacters in location strings.

### 4. Curl Misuse
Risk:
- The skill uses curl, which could theoretically be redirected to non-weather URLs.
- This could be exploited for SSRF or data exfiltration.

Mitigation:
- Restrict curl to wttr.in and Open-Meteo domains only.

### 5. Safety-Critical Misuse
Risk:
- Users might rely on casual weather data for aviation, marine, or severe weather decisions.
- wttr.in is not an authoritative source for safety-critical weather.

Mitigation:
- Block presentation of data as safety-critical.
- Redirect to official sources (NWS, METAR) for such use cases.

## Safe vs Unsafe

Safe:
- Weather by city name
- Weather by airport code
- Format selection
- Forecast queries

Confirm:
- Precise coordinate queries

Block:
- Non-weather curl requests
- Shell injection via location
- Excessive queries
- Safety-critical framing
