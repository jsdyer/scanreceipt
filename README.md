# Scan Receipt

Open [Scan Receipt](https://coolcode.ca/scanreceipt/) to inspect real, dated screenshots and network evidence immediately.

<!-- coolcode:guide -->
Start with a saved CoolCode receipt, choose Inspect receipt to see its screenshot and network responses, then compare two captures of the same page. Daily first-party captures establish a baseline and build history. The owner-only urlscan workflow accepts configured owned pages and returns provider links; its output is separate from the public browser-capture archive. Use Receipts · Capture and publish with capture_url to add a permanent public browser receipt. Visitors can also import public urlscan Result JSON locally; download receipts to keep local imports.
<!-- /coolcode:guide -->

## Use the public tool

1. Choose **Inspect receipt** beside Rack Expiry, Radar Scope or Hotspot Ledger. See the original capture time, page URL, requests/statuses, redirect responses and a retained screenshot.
2. Choose earlier/later captures of the same page and **Compare receipts**. The app compares destination hosts, request URLs/statuses and screenshot images. Different pages/methods are explicitly flagged; a first capture is a baseline, not an invented historical comparison.
3. Use **Find urlscan reports** for another public domain, or **Create a scan on urlscan.io** using your own account. Provider links contact urlscan only when opened.
4. Open a public scan's Result API JSON, paste it into **Bring your evidence**, and choose **Import JSON**. You can save a sanitized receipt and compare it with another scan. Imports stay in this tab; they are not uploaded or automatically stored.

## Use your saved urlscan key now

Open [Personal urlscan · Scan an owned page](https://github.com/jsdyer/scanreceipt/actions/workflows/urlscan-check.yml), select **Run workflow**, choose one of the fifteen URLs or enter `custom_url` for another public page on a configured owned site, and run it. When complete, open the run's **Summary** for report, Result API JSON and screenshot links. Import that JSON into the public workbench for local comparison. Only repository users with workflow permissions can run this client; anonymous visitors cannot spend the owner's quota.

`URLSCAN_API_KEY` remains a repository Actions secret. One public scan is submitted per run, followed by bounded result polling. The urlscan workflow runs only when manually dispatched; configuration edits do not submit scans. Failed/uncertain submissions are never automatically retried. A scan becomes public on urlscan; this workflow records links only and does not commit report data or screenshots from the provider.

For local personal use, clone this MIT-licensed repository, set `URLSCAN_API_KEY` in your environment and run `python3 scripts/urlscan_check.py --target https://coolcode.ca/`. Do not put a key in a command argument or public file. Scope changes require owner authorization and compliance with the provider's [terms](https://urlscan.io/terms/) and [API guidance](https://docs.urlscan.io/guides/quickstart).

## Daily first-party evidence

The public archive uses **our own Chromium browser**, independent of the urlscan API. At **14:47 UTC daily**, GitHub Actions visits the three URLs in `config.json` in fresh unsigned-in contexts, 1280×900 viewport, en-CA, UTC. It waits for network idle plus two seconds. It blocks POST and other non-read requests, service workers and the CoolCode metrics script. No consent banners are clicked. Browser version and capture context are recorded.

Completed network responses are sanitized: query values, fragments, URL credentials, headers, cookies and bodies are not retained. Failed/blocked requests are not represented as successful responses. Paths and titles can still contain information, so only operator-owned public pages are allowlisted. Screenshot height is capped at 20,000 CSS pixels; `screenshot_clipped` identifies any cap. The JPEG screenshot is retained in `evidence/`, not hosted by a provider.

The desk shows the newest 30 receipts. Earlier receipts remain in immutable `archive/YYYY-MM/` JSON captures, with SHA-256 checksums in `data/history.json`; screenshots remain available. Download an older archive JSON and import it into the workbench when needed. Source capture time and collection/check time remain separate. Failures preserve the last deployed version. GitHub schedules are best effort; **Receipts · Capture and publish → Run workflow** also captures fresh evidence.

## Privacy and interpretation

This is a record of one browser visit, not proof of tracking or a security audit. Consent, geography, timing and dynamic content affect results. Screenshot differences are visual evidence; the app does not invent a numerical pixel-diff score. Provider screenshots are linked only; our own screenshots are embedded when inspecting/comparing first-party receipts. Local imports have unverified provenance and should be reviewed before sharing. Public urlscan visibility is required; private/unlisted imports are rejected.

The public site has no shared API proxy or API key. It loads saved evidence and the aggregate CoolCode counter; input values never enter metrics. Its own capture browser blocks that counter. Code is MIT; imported provider evidence remains subject to its source terms. Requests are defanged; evidence URLs are not visited automatically.

## Checks

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

The offline build verifies archived hashes and fingerprints browser assets. CI installs Playwright for the scheduled capture and browser acceptance checks, including real evidence, local imports, comparisons, downloads, sanitization and mobile layout. Publication copies only the built `dist/` directory. Never commit secrets or `dist/`.

## Add a site or receipt

There are three different paths:

| Goal | Action | Result |
| --- | --- | --- |
| Permanently save a screenshot and network receipt here | Run **Receipts · Capture and publish**, set `capture_url` to a public HTTPS page on a configured owned site | Committed screenshot and JSON, deployed to the public evidence desk |
| Submit a scan using your urlscan API key | Run **Personal urlscan · Scan an owned page**, choose a URL or enter `custom_url` | Public provider report; links in Summary, no automatic public mirror |
| Inspect a provider report locally | Paste its full public Result API JSON into **Bring your evidence** | Tab-only receipt; use Save receipts JSON to retain it yourself |

The configured owner scope contains CoolCode, jsdyer.github.io, Liminal Hacker, Slash Access, JSD Technologies, jsd.technology, Jeffrey Dyer, NetHush, Interweb International, FunApps, HackMe and SuperApp. The urlscan chooser also includes the three existing CoolCode tool pages. `custom_url` accepts other public HTTPS paths on these hosts and their `www` aliases. Credentials, query strings, fragments, other ports and unrelated hosts are rejected.

To add a future domain, edit `config.json`: add its hostname to `owned_hosts`. Add a URL to `capture_urls` only if it should be captured every day. `urlscan_targets` lists suggested URLs; a new target can always be entered in `custom_url` after its host is allowed. To add it to the visual dropdown too, append the URL under `.github/workflows/urlscan-check.yml` → `inputs.target.options`. No new API key is needed.

The daily set remains Rack Expiry, Radar Scope and Hotspot Ledger. Blank `capture_url` runs that set now. A manual capture adds to the newest 30 retained receipts without changing the daily set. The archive retains older receipts and images. Only capture pages intended for public sharing; paths and screenshots are public.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

The separate schedule guard remains a mitigation, not a scheduling guarantee. The independent [CoolCode refresh watchdog](https://github.com/jsdyer/jsdyer.github.io/blob/main/services/refresh-watchdog/README.md) is maintained in GitHub and uses the generated workflow and freshness registry; do not maintain another target list here. Using it requires installation on a Linux server and GitHub credentials with access to this repository. A generated target does not prove that a private server has adopted it; verify the installed service's report. The guard does not collect data, create dummy commits or change source/check timestamps. Successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
