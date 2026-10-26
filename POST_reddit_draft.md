# Reddit post draft (r/ClaudeAI, r/ClaudeCode)

Draft only. Not posted. Replace `<registry page link>` with the GitHub Pages address after publishing. The classifieds site is not named, on purpose.

---

**Title options** (pick one):

- Claude in Chrome has a hidden site list: on some sites it asks "Allow" on every click and you can't turn it off. We're building a public registry of those sites, check yours in a minute
- Found out why Claude in Chrome asks permission for every click on some sites (server-side category list). Started a public registry, help fill it
- "Site-level permissions are disabled for this site": what it means, how to check any site in one minute, and a public list we're building together

**Body:**

If you've used Claude in Chrome and hit the dialog that says "Site-level permissions are disabled for this site", with the "Always allow" button greyed out, you've met a server-side site list. I spent a few evenings figuring out where it comes from, and the short version is: before Claude acts on a page, the extension sends the page URL to an Anthropic endpoint and gets back a category for the domain. category0 is a normal site. category3 means "approve every single action", and no side panel mode ("Automatically approve", "Skip all approvals") changes that. category1 is blocked outright. The list itself is not published, and there's no documented way to ask for a review.

I ran into it on a large classifieds site where I manage my own listings: every click, every scroll, "Allow". I looked through the extension code (version 1.0.102), then opened DevTools on the extension's service worker and saw the response with my own eyes: `"category": "category3"`. Others have hit the same wall on dev.vk.com, on Facebook, and on internal corporate subdomains; the Claude Code repo has several open issues about it with no answer so far.

So we started a public registry: which domain got which category, on which date, and how it was observed. It's a plain CSV on GitHub with a page that renders it, and a one-minute way to check any site without touching DevTools: open the site with Claude, ask it to click a safe link, and look at the first dialog. "Always allow" present means category0. No "Always allow" and the "Site-level permissions are disabled" line means category3. A "you confirm you have the right to access content" dialog means category4. A blocked page means category1. If you want the exact answer, there's a five-step DevTools method on the page too (one warning: look at the Response tab only, the Headers tab shows your login token).

Rules are simple. Only your own observation, with a date, because categories can change. No automated scanning of the Anthropic endpoint: it's undocumented, it runs under your personal login token, and nobody should risk their account for a list. No screenshots of the Headers tab, ever. Reports go through a short form (no sign-in) or a GitHub issue if you prefer.

Why bother: if your work site, or a site you're building for a client, is on that list, you want to know before you plan an agent workflow around it, not after an afternoon of clicking "Allow". And a list that many people contribute to, with dates, is the only way to see whether categories ever change.

Registry and the one-minute check: https://pr0t0be.github.io/claude-site-categories/

If you check a site, please send the result, even if it's category0. "Normal" sites are data too. Everything is CC BY 4.0, take it and build on it.

---

Notes for posting: no link to the Habr article (it's in Russian, different audience). If asked which classifieds site: "a large Russian classifieds site, I don't name it publicly". The registry itself lists domains openly; that's a known trade-off.
