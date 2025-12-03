# CIRCPACK LinkedIn follower dashboard (HTML/CSS/JS)

This repository is a single-page web app—written only with vanilla HTML, CSS,
and JavaScript—that queries LinkedIn's
`organizationalEntityFollowerStatistics` endpoint to show real follower totals
for the CIRCPACK company page. No backend services or Python scripts are
involved.

> ⚠️ LinkedIn's API requires OAuth access tokens with the `r_organization_social`
scope and Marketing Developer Platform approval. Browser-based requests may be
blocked by CORS unless your LinkedIn application explicitly allows it.

## Getting started

1. Clone or download this repository.
2. Open `index.html` in any modern browser (double-click or serve with a static
   file host).
3. Paste a valid LinkedIn access token, the CIRCPACK organization ID (or URN),
   and click **Fetch follower count**.

Everything runs locally in the browser: tokens are never transmitted anywhere
other than directly to LinkedIn's API.

## Finding the CIRCPACK organization ID

1. Log in to LinkedIn with an account that can manage the CIRCPACK company page.
2. Visit `https://www.linkedin.com/company/circpack/`.
3. View the page source (right click → View Source) and search for
   `urn:li:organization:`.
4. Copy the numeric portion and paste it into the Organization ID field. You can
   also paste the full URN (e.g. `urn:li:organization:1234567`).

## Project structure

```
index.html  # markup + form
styles.css  # layout and visual styling
script.js   # fetch logic and DOM updates
```

## How it works

- Form submission calls a small `fetch` helper that hits
  `https://api.linkedin.com/v2/organizationalEntityFollowerStatistics` with the
  access token you provide.
- The script normalizes either a numeric organization ID or a full URN before
  querying.
- Organic, paid, and total follower counts are displayed in a card. Errors
  (missing scopes, expired tokens, CORS blocks, etc.) are surfaced inline so you
  can fix them quickly.

## Deployment ideas

Because the project is fully static, you can host it via any static-site option:

- GitHub Pages
- Netlify / Vercel static deployments
- S3 + CloudFront or Azure Static Web Apps
- A basic Nginx/Apache directory on your own server

Just ensure the domain you host from is permitted by your LinkedIn app, otherwise
LinkedIn will reject the browser requests.
