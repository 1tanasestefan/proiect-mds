"""
=======================================================
PHASE 1 — Supabase Diagnostic Script
Run: python test_db.py
=======================================================
This script tests each layer of the Supabase stack
individually so we can pinpoint the exact failure point.
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

# ── STEP 0: ENV VAR CHECK ──────────────────────────────────────────
print("\n========================================")
print("STEP 0 — Environment Variable Check")
print("========================================")
print(f"  SUPABASE_URL        : {'✅ Set → ' + SUPABASE_URL if SUPABASE_URL else '❌ MISSING'}")
print(f"  SUPABASE_KEY        : {'✅ Set → ' + SUPABASE_KEY[:20] + '...' if SUPABASE_KEY else '❌ MISSING'}")
print(f"  SUPABASE_JWT_SECRET : {'✅ Set → ' + SUPABASE_JWT_SECRET[:16] + '...' if SUPABASE_JWT_SECRET else '❌ MISSING'}")

# Warn if key looks like a publishable key (wrong for server use)
if SUPABASE_KEY.startswith("sb_publishable_") or SUPABASE_KEY.startswith("sb_"):
    print()
    print("  ⚠️  WARNING: SUPABASE_KEY looks like a Publishable/Anon key.")
    print("  The Python backend needs the 'service_role' secret key (starts with 'eyJ...').")
    print("  Find it in: Supabase Dashboard → Project Settings → API → service_role key")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ Cannot continue — required env vars are missing.")
    sys.exit(1)

# ── STEP 1: SUPABASE CLIENT INIT ──────────────────────────────────
print("\n========================================")
print("STEP 1 — Supabase Client Initialisation")
print("========================================")
try:
    from supabase import create_client, Client
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("  ✅ Supabase client created successfully.")
except Exception as e:
    print(f"  ❌ Failed to create Supabase client: {type(e).__name__}: {e}")
    sys.exit(1)

# ── STEP 2: BASIC NETWORK / DNS CHECK ─────────────────────────────
print("\n========================================")
print("STEP 2 — Network / DNS Check")
print("========================================")
try:
    import urllib.request
    with urllib.request.urlopen(SUPABASE_URL, timeout=8) as resp:
        print(f"  ✅ Supabase URL reachable. HTTP status: {resp.status}")
except Exception as e:
    print(f"  ❌ Cannot reach Supabase URL: {type(e).__name__}: {e}")
    print("      → This is a network/DNS issue. Check your internet connection or Supabase project status.")

# ── STEP 3: READ FROM 'profiles' TABLE ────────────────────────────
print("\n========================================")
print("STEP 3 — Read from 'profiles' table")
print("========================================")
try:
    result = sb.table("profiles").select("*").limit(1).execute()
    if result.data is not None:
        print(f"  ✅ Query succeeded. Returned {len(result.data)} row(s).")
        if result.data:
            print(f"     Sample row keys: {list(result.data[0].keys())}")
        else:
            print("     (Table is empty — that is fine.)")
    else:
        print(f"  ⚠️  Query returned None data. Full response: {result}")
except Exception as e:
    print(f"  ❌ Read failed: {type(e).__name__}: {e}")
    err = str(e).lower()
    if "relation" in err and "does not exist" in err:
        print("      → The 'profiles' table does not exist in your Supabase database.")
        print("        Run the SQL in backend-python/schema.sql in the Supabase SQL Editor.")
    elif "permission denied" in err or "rls" in err or "42501" in err:
        print("      → Row Level Security (RLS) is blocking the query.")
        print("        You must use the 'service_role' key for server-side access.")
    elif "invalid api key" in err or "401" in err:
        print("      → Invalid or expired API key.")
    else:
        print(f"      → Raw error: {e}")

# ── STEP 4: READ FROM 'itineraries' TABLE ─────────────────────────
print("\n========================================")
print("STEP 4 — Read from 'itineraries' table")
print("========================================")
try:
    result = sb.table("itineraries").select("id, title, destination").limit(1).execute()
    if result.data is not None:
        print(f"  ✅ Query succeeded. Returned {len(result.data)} row(s).")
    else:
        print(f"  ⚠️  Query returned None. Full response: {result}")
except Exception as e:
    print(f"  ❌ Read failed: {type(e).__name__}: {e}")

# ── STEP 5: SUPABASE AUTH HEALTH CHECK ────────────────────────────
print("\n========================================")
print("STEP 5 — Supabase Auth API Health")
print("========================================")
try:
    import urllib.request, urllib.error
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/health",
        headers={"apikey": SUPABASE_KEY}
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        body = resp.read().decode()
        print(f"  ✅ Auth API healthy. Response: {body[:120]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ Auth API returned HTTP {e.code}: {e.reason}")
except Exception as e:
    print(f"  ❌ Auth API check failed: {type(e).__name__}: {e}")

# ── STEP 6: JWT SECRET CHECK ───────────────────────────────────────
print("\n========================================")
print("STEP 6 — JWT Secret / Library Check")
print("========================================")
if not SUPABASE_JWT_SECRET:
    print("  ❌ SUPABASE_JWT_SECRET is not set. Auth middleware will reject all requests.")
elif len(SUPABASE_JWT_SECRET) < 20:
    print(f"  ⚠️  JWT secret looks too short ({len(SUPABASE_JWT_SECRET)} chars): '{SUPABASE_JWT_SECRET}'")
    print("      → For HS256, the secret should be the 'JWT Secret' from Supabase Dashboard → API.")
    print("      → For ES256, you need the full JWK, not just the kid UUID.")
else:
    print(f"  ✅ SUPABASE_JWT_SECRET appears set ({len(SUPABASE_JWT_SECRET)} chars).")

try:
    from jose import jwt
    print("  ✅ python-jose library is installed.")
except ImportError:
    print("  ❌ python-jose is not installed. Run: pip install python-jose[cryptography]")

print("\n========================================")
print("DIAGNOSTIC COMPLETE — Paste output above")
print("========================================\n")
