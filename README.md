# CIRCPACK LinkedIn follower tool

This repository contains a small Python CLI that calls LinkedIn's official
`organizationalEntityFollowerStatistics` endpoint to display the real follower
count for the CIRCPACK organization (or any other LinkedIn company page, if you
supply a different ID).

Because LinkedIn gates the data behind OAuth, you must supply an access token
and CIRCPACK's organization ID/URN that you retrieve from your own Developer
account. The script handles the API call, parses the response, and prints the
organic, paid, and total follower counts on demand.

## Prerequisites

- Python 3.10+
- A LinkedIn Developer application that has been approved for the Marketing
  Developer Platform and granted `r_organization_social` (read) access. The
  application must also be authorized by the admins of the CIRCPACK company
  page so it can query follower statistics.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Required environment variables

| Variable | Description |
| --- | --- |
| `LINKEDIN_ACCESS_TOKEN` | A valid OAuth access token generated for your LinkedIn app. |
| `LINKEDIN_ORGANIZATION_ID` | Numeric organization ID for CIRCPACK. Optional if you set `LINKEDIN_ORGANIZATION_URN`. |
| `LINKEDIN_ORGANIZATION_URN` | Full URN in the form `urn:li:organization:<id>`. Optional if you provide the numeric ID. |

You can find the CIRCPACK organization ID by:

1. Visiting `https://www.linkedin.com/company/circpack/` while logged in as an
   admin.
2. Opening the page source and searching for `urn:li:organization:`.
3. Copying the numeric portion of the URN.
4. Exporting it as `LINKEDIN_ORGANIZATION_ID` (or storing the entire URN in
   `LINKEDIN_ORGANIZATION_URN`).

## Usage

```bash
python linkedin_followers.py \
  --organization-id "$LINKEDIN_ORGANIZATION_ID" \
  --access-token "$LINKEDIN_ACCESS_TOKEN"
```

Flags:

- `--organization-id` – Numeric LinkedIn organization ID. Defaults to the
  `LINKEDIN_ORGANIZATION_ID` env var when omitted.
- `--organization-urn` – Pass the full URN instead of the numeric ID.
- `--access-token` – Provide a token explicitly. Defaults to
  `LINKEDIN_ACCESS_TOKEN` when omitted.
- `--json` – Emit machine-readable JSON.
- `--pretty` – Pretty-print the JSON payload (implies `--json`).

### Example human-readable output

```text
Organization: urn:li:organization:1234567
Organic followers: 4821
Paid followers: 0
Total followers: 4821
```

### Example JSON output

```bash
python linkedin_followers.py --json --pretty
```

```json
{
  "organizationUrn": "urn:li:organization:1234567",
  "organicFollowerCount": 4821,
  "paidFollowerCount": 0,
  "totalFollowerCount": 4821
}
```

## Notes

- The script intentionally fails fast with clear messaging if the token is
  missing, expired, or lacks the proper permissions.
- LinkedIn throttles API usage; consider caching the value if you query it
  frequently.
- The tool defaults to CIRCPACK via the environment variables, but you can use
  it for other organizations by supplying their IDs.
