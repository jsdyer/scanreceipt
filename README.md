# Scan Receipt

A dated receipt for what a website loaded. Open https://coolcode.ca/scanreceipt/.

<!-- coolcode:guide -->
Open an existing public urlscan result, copy its full Result API JSON into the local workbench, then save a sanitized receipt. Import two receipts to compare destination hosts, requests and statuses. Scan time is distinct from collection time; a changed request does not prove tracking or removal.
<!-- /coolcode:guide -->

## Useful without a key

1. Paste an existing urlscan UUID or result link into the link helper. It builds report and Result API links locally; opening them contacts urlscan.io.
2. Paste a **full public Result API response** (`task`, `page`, `data.requests`) or open its JSON file. Search API summaries are not full evidence and are rejected with a clear message.
3. Inspect dated submitted/final URLs, redirect responses, hosting ASN/country, resource types, status codes and destination hosts. Search within network requests. URLs are defanged; they are never visited by the app.
4. Save a sanitized receipt JSON to retain it, or export network rows as CSV. Import that JSON later to reopen it. Add a second dated scan and compare domains, request URLs/statuses and redirect counts.

Public visibility is required explicitly; unlisted/private results are rejected. Maximum 15 MB per import, 20,000 requests per scan and 100 receipts in the desk. Repeated scan IDs replace the existing local copy. Source screenshots and reports are source-linked, never embedded or loaded automatically. The screenshot itself is not retained by this application and may become unavailable upstream. Request displays show the first 200 filtered rows; exports include all imported rows. No browser scan or remote page execution occurs. **This app never calls the scan-submission API.**

## Scheduled coverage and provider permission

The collector only searches existing public scans for the explicit `config.json` owned-domain allowlist (`coolcode.ca`, `jsdyer.github.io` initially). It makes two daily searches, each limited to the last 30 days and five results. A `URLSCAN_API_KEY` repository secret is sent only through the `API-Key` header. Anonymous searches can work at lower quotas; adding a key is separate from republication permission. API rate limits depend on the account and operation, with minute/hour/day windows; bounded backoff honors Retry-After and X-Rate-Limit-Reset-After. A zero response means no observations returned in that selected window, not no historical scans.

urlscan's terms restrict systematic database compilation and public republication; its API guidance prohibits wholesale mirroring. Therefore **public receipt republication is disabled by default** (`publish_receipts: false`). The initial scheduled archive contains real search coverage/status observations, not copied scan datasets. Local receipt imports and explicit downloads remain fully usable. To enable a narrow owned-site public archive, first document provider permission in `permission_note`, then change the setting. Merely adding an API key does not enable republication. Configured `existing_public_scan_ids` are validated UUIDs and still require public visibility and owned submitted hostname; the collector never retrieves arbitrary targets. At most 12 permitted receipts are fetched in one run. No screenshots, raw HTML, DOM, scripts or response bodies are downloaded.

Primary documentation and policy verified 2026-11-22:

- https://docs.urlscan.io/apis/urlscan-openapi/search/searchdatasource
- https://docs.urlscan.io/apis/urlscan-openapi/scanning/getresult
- https://docs.urlscan.io/pages/api-rate-limits
- https://docs.urlscan.io/pages/api-best-practices
- https://docs.urlscan.io/pages/faq
- https://urlscan.io/terms/

## Privacy and interpretation

Imports, searching, sanitizing and comparison run locally, in tab memory; no pasted JSON is uploaded or saved automatically. Reload/Clear discards it unless you have chosen Save receipts JSON. Queries, fragments, URL credentials, headers, cookies and request bodies are excluded. Paths and page titles can still contain sensitive content; review before sharing. Source links contact urlscan.io only when opened. The site loads its own saved metadata and the aggregate CoolCode open counter; inputs/filter values are excluded from metrics. Keys never enter client code, logs or retained artifacts.

A scan measures a particular browser, time and location. Consent defaults, timing, network conditions and dynamic content can change results. A destination host does not establish separate ownership, tracking, illegality or a relationship between organizations. Hosting country is not data residency. Redirect evidence reflects redirect responses actually supplied; a differing submitted/final URL alone is not reconstructed into an invented chain. Related tools: Tracker X-Ray and PhishIntel.

## Archive and checks

Schedule: **daily at 14:47 UTC** (`47 14 * * *`), best effort. Scheduled/manual runs refresh, validate, test, retain and deploy. Pushes build saved data offline except an absent baseline or pending-credential manifest. `data/index.json` is small hub metadata. `data/current.json` holds permitted normalized receipts (none by default) and actual coverage checks. `data/history.json` indexes immutable SHA-256-validated snapshots in `archive/YYYY-MM/`. Identical observations do not manufacture changes; the first is explicitly a baseline. Snapshot links download these metadata observations. Provider scan time, capture time and most recent check time remain distinct. Failed responses or validation preserve the previous good deployment.

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py        # offline
python3 scripts/collect.py      # explicit existing-result lookup only
```

Standard-library Python; no runtime dependencies. CI Playwright checks full JSON import, comparison, source-link safety, export, invalid/private input rejection and mobile layout. Browser automation is a CI-only test dependency. Code is MIT licensed; upstream data is subject to urlscan's terms, not relicensed.
