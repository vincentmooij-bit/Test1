#!/usr/bin/env python3
"""Simple CLI to fetch LinkedIn follower statistics for an organization."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

API_URL = "https://api.linkedin.com/v2/organizationalEntityFollowerStatistics"
ENV_ACCESS_TOKEN = "LINKEDIN_ACCESS_TOKEN"
ENV_ORG_ID = "LINKEDIN_ORGANIZATION_ID"
ENV_ORG_URN = "LINKEDIN_ORGANIZATION_URN"
DEFAULT_TIMEOUT = 10  # seconds


@dataclass
class FollowerCounts:
    """Container for follower counts returned by LinkedIn."""

    organic: int
    paid: int

    @property
    def total(self) -> int:
        return self.organic + self.paid


def build_org_urn(explicit_urn: Optional[str], org_id: Optional[str]) -> str:
    """Resolve the LinkedIn organization URN."""

    if explicit_urn:
        return explicit_urn

    if not org_id:
        raise ValueError(
            "Provide an organization ID via --organization-id or the "
            f"{ENV_ORG_ID} environment variable, or pass --organization-urn."
        )

    org_id = org_id.strip()
    if org_id.startswith("urn:li:organization:"):
        return org_id

    if not org_id.isdigit():
        raise ValueError("LinkedIn organization IDs must be numeric.")

    return f"urn:li:organization:{org_id}"


def fetch_follower_counts(access_token: str, org_urn: str, timeout: int = DEFAULT_TIMEOUT) -> FollowerCounts:
    """Call the LinkedIn API and return follower counts."""

    params = {
        "q": "organizationalEntity",
        "organizationalEntity": org_urn,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    response = requests.get(API_URL, headers=headers, params=params, timeout=timeout)
    if response.status_code == 401:
        raise RuntimeError("LinkedIn returned 401 Unauthorized. Double-check the access token.")
    if response.status_code == 403:
        raise RuntimeError(
            "LinkedIn returned 403 Forbidden. Ensure your application has access to the "
            "Marketing Developer Platform and the necessary permissions."
        )
    if not response.ok:
        raise RuntimeError(
            f"LinkedIn API request failed with status {response.status_code}: {response.text[:200]}"
        )

    data: Dict[str, Any] = response.json()
    elements = data.get("elements", [])
    if not elements:
        raise RuntimeError("LinkedIn response did not contain follower statistics.")

    follower_counts = elements[0].get("followerCounts") or {}
    organic = int(follower_counts.get("organicFollowerCount", 0))
    paid = int(follower_counts.get("paidFollowerCount", 0))

    return FollowerCounts(organic=organic, paid=paid)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch the current LinkedIn follower counts for an organization.",
    )
    parser.add_argument(
        "--organization-id",
        help=(
            "Numeric LinkedIn organization ID. Not required if --organization-urn is provided. "
            f"Defaults to ${ENV_ORG_ID} when set."
        ),
    )
    parser.add_argument(
        "--organization-urn",
        help=(
            "Full LinkedIn organization URN (e.g. urn:li:organization:12345). "
            f"Defaults to ${ENV_ORG_URN} when set."
        ),
    )
    parser.add_argument(
        "--access-token",
        help=(
            "LinkedIn REST API access token with r_organization_social + rw_organization_admin permissions. "
            f"Defaults to ${ENV_ACCESS_TOKEN} when set."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of a human-readable summary.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (implies --json).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    access_token = args.access_token or os.getenv(ENV_ACCESS_TOKEN)
    if not access_token:
        raise SystemExit(
            f"Missing LinkedIn access token. Set --access-token or the {ENV_ACCESS_TOKEN} environment variable."
        )

    org_urn = build_org_urn(
        explicit_urn=args.organization_urn or os.getenv(ENV_ORG_URN),
        org_id=args.organization_id or os.getenv(ENV_ORG_ID),
    )

    counts = fetch_follower_counts(access_token, org_urn, timeout=args.timeout)

    if args.json or args.pretty:
        payload = {
            "organizationUrn": org_urn,
            "organicFollowerCount": counts.organic,
            "paidFollowerCount": counts.paid,
            "totalFollowerCount": counts.total,
        }
        json_kwargs: Dict[str, Any] = {}
        if args.pretty:
            json_kwargs["indent"] = 2
        print(json.dumps(payload, **json_kwargs))
    else:
        print(f"Organization: {org_urn}")
        print(f"Organic followers: {counts.organic}")
        print(f"Paid followers: {counts.paid}")
        print(f"Total followers: {counts.total}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
