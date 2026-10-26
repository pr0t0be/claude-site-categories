# Google Form for reports: fields and a 5-minute setup

The form is the main door for people who are not developers: no GitHub account, no sign-in, one link. Responses land in a Google Sheet; `import_form.py` pulls them into `candidates_form.csv`, and a person moves confirmed ones into `registry.csv`.

The owner creates the form in their own Google account. Nothing in this repository holds a Google credential.

## Fields (copy the text as is)

Form title: **Claude in Chrome: what did Claude show on your site?**

Form description:

> Help build a public list of which sites Claude in Chrome treats as "prompt on every action", "blocked" or "normal". Anthropic does not publish this list. Only report what you saw yourself, today or on a known date. No sign-in needed. Registry: <registry page link>.
> Never upload the DevTools Headers tab: it contains your Claude login token.

1. **Domain** (Short answer, required)
   Help text: `As in the address bar or in the "domain" field of the server response. Example: www.example.com. No https://, no path.`
   Validation: Regular expression, Matches, `^[a-z0-9.-]+\.[a-z]{2,}$`, error text `Lowercase domain only, like www.example.com`.

2. **What did you see?** (Multiple choice, required)
   - `A dialog with an "Always allow" button (normal site, category0)`
   - `A dialog without "Always allow", with "Site-level permissions are disabled for this site" (prompt on every action, category3)`
   - `A dialog "By continuing, you confirm you have the right to access content on this site" (category4)`
   - `A blocked page, the site did not open (category1 or organization block)`
   - `I saw the server response in DevTools (write the category in the comment)`

3. **Date** (Date, required)
   Help text: `When you saw it. Categories can change, so the date matters.`

4. **Claude product** (Multiple choice, required)
   - `Claude in Chrome extension`
   - `Claude Desktop built-in browser`
   - `Not sure`

5. **Screenshot link** (Short answer, optional)
   Help text: `Optional. A link to a screenshot of the dialog or of the DevTools Response tab (imgur, Google Drive, anything public). NEVER the Headers tab: it shows your login token. Screenshots of Headers are deleted unread.`
   Why a link and not a file upload: a "File upload" question in Google Forms forces respondents to sign in to Google. A link keeps the form open to everyone.

6. **Comment** (Paragraph, optional)
   Help text: `Anything else: extension version, side panel mode, the exact dialog text, the category from DevTools.`

Settings: "Collect email addresses" off, "Limit to 1 response" off (it requires sign-in), "Show link to submit another response" on. Confirmation message: `Thanks. Reports are reviewed by a person before they appear in the registry.`

## Setup in 5 minutes

1. Open https://forms.google.com, "Blank form". Paste the title and description.
2. Add the six questions above. Set "Required" where marked.
3. Settings (gear or "Settings" tab): Responses, turn off "Collect email addresses"; Presentation, set the confirmation message.
4. Responses tab, the Sheets icon: "Create a new spreadsheet". This is where answers go.
5. In that spreadsheet: File, Share, "Publish to web", choose the responses sheet, format "Comma-separated values (.csv)", Publish. Copy the link; it looks like `https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid=0&single=true&output=csv`. This is the `--url` for `import_form.py`. The link exposes only this sheet, read-only.
6. "Send" button, link icon, "Shorten URL", copy. This is the public form link.
7. For the registry page: "Send", the `<>` icon, copy the HTML embed code. Put the `src` value into `docs/index.html` where `FORM_EMBED_URL` is set.

## Current form (created 2026-10-26, account of the registry owner)

- Public link: https://docs.google.com/forms/d/e/1FAIpQLSfi7jWeiR1db45H7FNWV712p4t1Nm3f9PebTDT6ppyLhOnq_Q/viewform
- Embed `src`: https://docs.google.com/forms/d/e/1FAIpQLSfi7jWeiR1db45H7FNWV712p4t1Nm3f9PebTDT6ppyLhOnq_Q/viewform?embedded=true (already set in `docs/index.html`)
- Responses sheet: linked, published to the web as CSV; the CSV link is kept by the owner, not in the repository.

## Pulling responses

```bash
python import_form.py --url "https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?output=csv"
```

Writes `candidates_form.csv`. Rows already there keep their `reviewed` mark. Review each candidate; if the description matches a real observation, add it to `registry.csv` as `dialog_observed` or `devtools_response` with `reporter` set to `form` and `source` set to the screenshot link or `form response <date>`.
