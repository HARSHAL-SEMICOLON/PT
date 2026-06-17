import os
import re

# Naye Supabase keys (sb_publishable_*) ko support karne ke liye regex validation bypass pattern lagaya hai.
orig_match = re.match
re.match = lambda pat, s, f=0: True if pat == r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$" else orig_match(pat, s, f)

from dotenv import load_dotenv
from supabase import Client, create_client

# Local .env variables load ho rahe hain
load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Agar credentials missing hain toh error generate hoga
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL ya key .env file me missing hai!")

# DB connection client create ho raha hai
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
