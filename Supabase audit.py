"""
-------------------------------
USAGE
-------------------------------
1. Create a Supabase service role or read-only API key (recommended).
2. Set the following environment variables:

   SUPABASE_URL
   SUPABASE_SERVICE_KEY

3. Run:

   python wellspace_audit.py

------------------------------------------------------
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    sys.exit("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}


def fetch(table: str, limit: int = 5) -> List[Dict]:
    """Fetch a small sample of rows from a table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?limit={limit}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


# -----------------------------
# AUDIT CHECKS
# -----------------------------

def audit_concerns():
    rows = fetch("concerns")
    failures = []

    for r in rows:
        if "user_id" in r and r.get("user_id"):
            failures.append("Concern contains user_id")

    return failures


def audit_incidents():
    rows = fetch("incidents")
    failures = []

    for r in rows:
        if not r.get("user_id"):
            failures.append("Incident missing user_id")
        if r.get("status") not in {"Open", "Reviewed", "Resolved"}:
            failures.append("Invalid incident status")

    return failures


def audit_notifications():
    rows = fetch("notifications")
    failures = []

    for r in rows:
        if r.get("type") not in {"concern", "incident"}:
            failures.append("Invalid notification type")

    return failures


# -----------------------------
# REPORTING
# -----------------------------

def main():
    print("WellSpace Privacy & Integrity Audit")
    print("====================================")
    print(f"Run at: {datetime.utcnow().isoformat()}Z")
    print()

    results = {
        "Concerns": audit_concerns(),
        "Incidents": audit_incidents(),
        "Notifications": audit_notifications(),
    }

    ok = True

    for section, failures in results.items():
        print(f"[{section}]")
        if not failures:
            print("  ✅ Passed")
        else:
            ok = False
            for f in failures:
                print(f"  ❌ {f}")
        print()

    if not ok:
        print("AUDIT RESULT: ❌ FAIL")
        sys.exit(1)
    else:
        print("AUDIT RESULT: ✅ PASS")


if __name__ == "__main__":
    main()
