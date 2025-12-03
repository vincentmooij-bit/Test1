const API_URL = "https://api.linkedin.com/v2/organizationalEntityFollowerStatistics";

const formEl = document.getElementById("follower-form");
const messageEl = document.getElementById("message");
const resultsCard = document.getElementById("results-card");
const orgLabel = document.getElementById("organization-label");
const organicEl = document.getElementById("organic-count");
const paidEl = document.getElementById("paid-count");
const totalEl = document.getElementById("total-count");
const updatedEl = document.getElementById("updated-timestamp");
const fetchBtn = document.getElementById("fetch-btn");

const numberFormatter = new Intl.NumberFormat("en-US");

function buildOrgUrn(providedUrn, orgId) {
  if (providedUrn) {
    return providedUrn.trim();
  }

  if (!orgId) {
    throw new Error("Enter either the organization ID or URN.");
  }

  const trimmed = orgId.trim();
  if (trimmed.startsWith("urn:li:organization:")) {
    return trimmed;
  }

  if (!/^\d+$/.test(trimmed)) {
    throw new Error("Organization IDs must be numeric.");
  }

  return `urn:li:organization:${trimmed}`;
}

function setMessage(text, type = "") {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`.trim();
}

function renderCounts(urn, followerCounts) {
  const organic = followerCounts.organicFollowerCount ?? 0;
  const paid = followerCounts.paidFollowerCount ?? 0;
  const total = organic + paid;

  orgLabel.textContent = urn;
  organicEl.textContent = numberFormatter.format(organic);
  paidEl.textContent = numberFormatter.format(paid);
  totalEl.textContent = numberFormatter.format(total);
  updatedEl.textContent = `Fetched at ${new Date().toLocaleString()}`;
  resultsCard.classList.remove("hidden");
}

async function fetchFollowers(accessToken, orgUrn) {
  const params = new URLSearchParams({
    q: "organizationalEntity",
    organizationalEntity: orgUrn,
  });

  const response = await fetch(`${API_URL}?${params.toString()}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "X-Restli-Protocol-Version": "2.0.0",
    },
  });

  if (response.status === 401) {
    throw new Error("LinkedIn rejected the token (401 Unauthorized).");
  }
  if (response.status === 403) {
    throw new Error("LinkedIn denied access (403). Ensure your app has Marketing Developer Platform approval.");
  }
  if (!response.ok) {
    const snippet = await response.text();
    throw new Error(`LinkedIn request failed (${response.status}). ${snippet.slice(0, 160)}`);
  }

  const payload = await response.json();
  if (!payload.elements?.length) {
    throw new Error("LinkedIn did not return follower statistics for that organization.");
  }

  return payload.elements[0];
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage("", "");
  resultsCard.classList.add("hidden");

  const accessToken = document.getElementById("access-token").value.trim();
  const orgId = document.getElementById("organization-id").value.trim();
  const orgUrnField = document.getElementById("organization-urn").value.trim();

  if (!accessToken) {
    setMessage("Please provide an access token.", "error");
    return;
  }

  let resolvedUrn;
  try {
    resolvedUrn = buildOrgUrn(orgUrnField, orgId);
  } catch (err) {
    setMessage(err.message, "error");
    return;
  }

  fetchBtn.disabled = true;
  fetchBtn.textContent = "Fetching...";

  try {
    const element = await fetchFollowers(accessToken, resolvedUrn);
    renderCounts(resolvedUrn, element.followerCounts ?? {});
    setMessage("Follower counts updated.", "success");
  } catch (err) {
    if (err instanceof TypeError && err.message === "Failed to fetch") {
      setMessage("Network or CORS error. LinkedIn may be blocking browser calls.", "error");
    } else {
      setMessage(err.message || "Something went wrong.", "error");
    }
  } finally {
    fetchBtn.disabled = false;
    fetchBtn.textContent = "Fetch follower count";
  }
});
