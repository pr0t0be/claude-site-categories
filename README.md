# Site category registry for Claude in Chrome

[Русская версия](README.ru.md) · [Registry page with the one-minute check](https://pr0t0be.github.io/claude-site-categories/) · [Report a site](#how-to-send-a-result)

A public list of which site is in which category for Claude in Chrome (Anthropic's Chrome extension). The category decides how Claude behaves on a site: a normal site with an "Always allow" button, a prompt on every action with no way to allow the site permanently, or a full block. Anthropic does not publish this list. Here users collect it from their own observations, every row with a date and a method.

The registry works like a ping: you open a site, the extension asks the Anthropic server, the server answers with a category, the answer gets recorded.

## Why

Before acting on a site the extension sends the page URL to an Anthropic server and gets a category back. On category3 sites Claude asks for confirmation on every click, the "Always allow" button is disabled, and the side panel modes ("Automatically approve", "Skip all approvals") do not change that. You only find out when you hit the wall. The list lets you know in advance what to expect on your work site or on a site you build for a client.

## How the check works on Anthropic's side

From the code of the Claude in Chrome extension version 1.0.102 (files `assets/mcpPermissions-*.js` and `assets/sidepanel-*.js`, reviewed 2026-10-25):

- Request: `POST https://api.anthropic.com/api/web/url_hash_check/browser_extension`, header `Authorization: Bearer <login token>`, body `{"url": "<page url>", "max_supported_category": 4}`.
- Response: `{"url": ..., "domain": ..., "category": ..., "org_policy": ..., "policy_source": ...}`. The `domain` field shows the category is assigned per domain, not per page.
- Cache: 5 minutes per URL (`CACHE_TTL_MS = 3e5`). The request is sent from the extension service worker, not from the page.
- There is no site list inside the extension. The category comes from the server. Anthropic does not publish the criteria; the help center only says there are some websites on which Claude requires approval for every action, and that Claude asks for permission before accessing financial sites.

| Category | What the extension does |
|---|---|
| category0 | normal site, "Always allow" works |
| category4 | third-party content site: once per domain a dialog "By continuing, you confirm you have the right to access content on this site", then it behaves as normal |
| category3 | prompt on every action: hint "You must approve any Claude action on this site", the permission dialog says "Site-level permissions are disabled for this site", the "Always allow" button is disabled |
| category2 | blocked without the blocked.html page; purpose not described in the code |
| category1 | fully blocked, the tab is redirected to blocked.html |

Internal values the server does not send and the extension sets itself: `category_unknown_error` (the category could not be fetched, the extension blocks "as a precaution") and `category_org_blocked` (the server returned `org_policy: "block"` or a Chrome enterprise policy applies). They are not recorded in the registry.

Severity order in the code: category0 < category4 < category3 < category_unknown_error < category2 = category_org_blocked < category1.

## Registry

<!-- registry:start -->
_8 entries (category0: 2, category3: 6). Generated from registry.csv by validate.py, do not edit by hand._

| domain | category | checked_at | method | reporter | source | notes |
|---|---|---|---|---|---|---|
| fl.ru | category0 | 2026-10-22 | dialog_observed | pr0t0be | self-report (registry author; observed 2026-10-21..22) | Always allow button present and it worked on later actions |
| freelance.ru | category0 | 2026-10-22 | dialog_observed | pr0t0be | self-report (registry author; observed 2026-10-21..22) | Always allow button present and it worked on later actions |
| dev.vk.com | category3 | 2026-09-16 | third_party_report | anthropics/claude-code#94880 | [github.com/anthropics/claude-code/issues/94880](https://github.com/anthropics/claude-code/issues/94880) | Issue author: site-level permissions unavailable, no way to grant them; category inferred from the dialog, not from a server response |
| docs.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| facebook.com | category3 | 2026-06-20 | third_party_report | abrahamjeyaraj.com | [www.abrahamjeyaraj.com/articles/claude-chrome-facebook-pe...](https://www.abrahamjeyaraj.com/articles/claude-chrome-facebook-permission-wall) | Blog post: permission prompt on every action, site-level permissions disabled; category inferred from the dialog |
| redash.k.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| stash.msk.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| www.avito.ru | category3 | 2026-10-25 | devtools_response | pr0t0be | [www.avito.ru_category3_2026-10-25.webp](evidence/www.avito.ru_category3_2026-10-25.webp) | Response tab of url_hash_check in the extension service worker DevTools; org_policy null, policy_source null; extension 1.0.102 |
<!-- registry:end -->

Source of truth: [registry.csv](registry.csv). The table above and the [registry page](https://pr0t0be.github.io/claude-site-categories/) are generated from it by `python validate.py`.

Columns:

- `domain`: the `domain` field of the server response, or the host from the address bar. Lowercase, no `https://`, no path.
- `category`: category0, category1, category2, category3 or category4.
- `checked_at`: date of the observation, YYYY-MM-DD. Required: categories can change.
- `method`: how it was checked. `devtools_response`: the server response was seen in DevTools. `dialog_observed`: judged by the permission dialog ("Always allow" present or not, blocked page or not). `third_party_report`: a public report by someone else (issue, article), category inferred from their description.
- `reporter`: who observed it (GitHub login, `form` for form reports) or where the report comes from.
- `source`: link to an issue, an article, or a file in `evidence/` (screenshot of the Response tab or of the dialog only).
- `notes`: anything else that matters: dialog text, extension version, Claude product (extension or Desktop built-in browser), caveats.

Reliability, highest first: `devtools_response` > `dialog_observed` > `third_party_report`. A `third_party_report` row is not an observation by registry contributors, it is a pointer to someone else's public report; Anthropic has not confirmed such reports.

## How to check your site

### In a minute, by the dialog

You need Chrome with the Claude extension. Open the site and tell Claude in the side panel: "Open this page and click any safe link in the menu. Do not type or submit anything." Look at the first dialog:

| What you see | Category |
|---|---|
| A blocked page, the site did not open | category1 (or a block by your organization's policy) |
| A dialog with an "Always allow" button | category0 |
| A dialog without that button, with "Site-level permissions are disabled for this site" at the bottom | category3 |
| Once, a dialog "By continuing, you confirm you have the right to access content on this site", then normal | category4 |

**Caveat: read the dialog in a clean setup.** From the extension code (version 1.0.102, not tested in every setup): in the side panel the dialog depends on the page you are on. In the small pop-up window that appears when Claude is driven from Claude Code or Claude Desktop, "Always allow" is disabled when *any tab in the Claude tab group* is category3, when the category check failed, and also while the pop-up has not got an answer yet. So a neighbouring tab of a category3 site turns every dialog in that group into a category3-looking dialog, whatever site you are visiting. Test with one tab in the Claude tab group and nothing else, or use the DevTools method below, which shows the category of the exact address.

Method in the registry: `dialog_observed` (only if the Claude tab group held no other site).

### Exactly, through DevTools, five steps

1. In Chrome open `chrome://extensions` and turn on "Developer mode" in the top right.
2. On the Claude extension card click the "service worker" link (small, under the extension description). DevTools opens.
3. Go to the Network tab and type `url_hash` into the filter field.
4. In the Claude side panel ask it to open the site you want to check.
5. A `browser_extension` row appears. Click it and open the Response tab: the `category` field is there.

If there is no row, the response is cached for 5 minutes: ask Claude to open another page of the same site.

**Warning.** The Headers tab next to it shows your Claude login token. Look at Response only. Never send anyone a screenshot of Headers; the registry deletes them unread.

Method in the registry: `devtools_response`.

## How to send a result

Three doors, pick the easiest:

1. **The form** ([open it directly](https://docs.google.com/forms/d/e/1FAIpQLSfi7jWeiR1db45H7FNWV712p4t1Nm3f9PebTDT6ppyLhOnq_Q/viewform) or on the [registry page](https://pr0t0be.github.io/claude-site-categories/#send)): no sign-in, no email. Domain, what you saw, date, which Claude product, optional screenshot link, comment. (Field texts and setup: [FORM_setup.md](FORM_setup.md).)
2. **A GitHub issue** with the "Report a site category" template: for people who already have a GitHub account.
3. **A pull request**: a row in `registry.csv`, a screenshot in `evidence/` (named `domain_category_YYYY-MM-DD.webp` or `.png`), then `python validate.py` and commit together with the regenerated README files and `docs/registry.csv`.

Every report is reviewed by a person before it lands in `registry.csv`. Details in [CONTRIBUTING.md](CONTRIBUTING.md).

## How the registry grows

Three streams, none of them touches the Anthropic endpoint by script:

- **Reports from people** (form, issues, pull requests): the main stream. Form responses are pulled into `candidates_form.csv` by `python import_form.py --url <published CSV link>` and reviewed by hand.
- **GitHub radar**: `python radar_github.py` searches public issues in `anthropics/claude-code` for the phrases that accompany this behaviour ("Site-level permissions are disabled", "category3", "url_hash_check", "per-action approval"), pulls out the domains mentioned near them with a 200-character quote, and writes `candidates_github.csv` plus the list of matched issues in `candidates_github_issues.csv`. Only GitHub is queried; the `gh` CLI is used when present, otherwise plain unauthenticated REST. Candidates are reviewed by a person and, when the source really states the observation, added as `third_party_report`. Run it by hand or once a day from a scheduler; no secrets are involved.
- **Manual check sessions**: a person works with Claude in Chrome as usual with the service worker DevTools open and records the exact server response for a list of sites. The first list of 20 sites and the step-by-step routine are in [CHECKLIST_manual.md](CHECKLIST_manual.md) (in Russian, the list is for the Russian-speaking audience the registry started with). Repeat monthly: categories can change.

**What we do not do:** mass automated querying of `url_hash_check`. It is an undocumented endpoint behind a personal login token; scanning a domain list through it risks the account and the terms of use, and rows produced that way are not accepted.

## Registry rules

1. Own observations only: a server response, or a permission dialog read in a clean setup (one site in the Claude tab group), with a date. Guesses by site type ("a bank is probably category3") are not accepted.
2. No mass automated scanning through the Anthropic endpoint, and we do not ask anyone to do it.
3. Categories can change. That is why the date is required, and a new observation of the same domain is added as a new row; the old one stays.
4. Screenshots of the Headers tab are deleted unread: they contain the token. Response tab or the dialog only.
5. The domain is recorded as the server returns it (`www.avito.ru`, not `avito.ru`); subdomains get their own rows.
6. Public reports by others may be added as `third_party_report` with a link, without adding details: only what the source says.

## Files

| File | What it is |
|---|---|
| `registry.csv` | the registry, source of truth |
| `validate.py` | checks the CSV, rebuilds the README tables, copies the CSV into `docs/`; `--check` in CI |
| `docs/index.html` | the registry page for GitHub Pages (enable Pages from the `docs/` folder on `main`) |
| `radar_github.py` | GitHub issues radar, writes `candidates_github.csv` and `candidates_github_issues.csv` |
| `import_form.py` | pulls form responses into `candidates_form.csv` |
| `FORM_setup.md` | form fields and a 5-minute setup guide |
| `CHECKLIST_manual.md` | manual check session routine and the first 20 sites |
| `CONTRIBUTING.md` | how to add a row |
| `evidence/` | screenshots of the Response tab or dialogs, never Headers |
| `POST_reddit_draft.md` | announcement draft |

## What the registry does not know

- The criteria Anthropic uses to assign categories. Not published.
- The full list. Only what someone has checked is here.
- Whether the built-in browser of the Claude Desktop app checks categories with the same request. Anthropic's documentation says it consults the same site safety list, but no contributor has seen its server response.
- Whether a category review can be requested. Not described in the documentation.

## Licenses

Data (`registry.csv`, `candidates_*.csv`, `evidence/`): [CC BY 4.0](LICENSE-DATA.md). Code: [MIT](LICENSE).

## Links

- Claude in Chrome permissions guide: https://support.claude.com/en/articles/12902446-claude-in-chrome-permissions-guide
- Use Claude in Chrome safely: https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely
- Browser in Claude Desktop for organizations, Site safety check: https://claude.com/docs/third-party/claude-desktop/browser.md
- Claude Code with Chrome: https://code.claude.com/docs/en/chrome.md
- User reports in the Claude Code repository: [99007](https://github.com/anthropics/claude-code/issues/99007), [94880](https://github.com/anthropics/claude-code/issues/94880), [91495](https://github.com/anthropics/claude-code/issues/91495), [93201](https://github.com/anthropics/claude-code/issues/93201), [101684](https://github.com/anthropics/claude-code/issues/101684), [104074](https://github.com/anthropics/claude-code/issues/104074)

This registry is not affiliated with Anthropic. Claude and Anthropic are trademarks of their owner.
