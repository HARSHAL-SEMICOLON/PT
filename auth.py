import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt

from database import supabase
from model import TokenData, UserCreate

load_dotenv()

SECRET_KEY: str = os.getenv("JWT_SECRET", "changeme")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Password helpers ──────────────────────────────────────────────────────────

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── Supabase user helpers ─────────────────────────────────────────────────────

def get_user_by_email(email: str) -> Optional[dict]:
    resp = supabase.table("users").select("*").eq("email", email).execute()
    return resp.data[0] if resp.data else None


def get_user_by_id(user_id: str) -> Optional[dict]:
    # 1. Fetch from users table
    resp = supabase.table("users").select("*").eq("id", user_id).execute()
    if not resp.data:
        return None
    user = resp.data[0]

    # 2. Depending on role, fetch profile details
    if user["role"] == "patient":
        p_resp = supabase.table("patients").select("id, phone").eq("user_id", user_id).execute()
        if p_resp.data:
            user["patient_id"] = p_resp.data[0]["id"]
            user["phone"] = p_resp.data[0]["phone"]
    elif user["role"] == "doctor":
        d_resp = supabase.table("doctors").select("id, specialization").eq("user_id", user_id).execute()
        if d_resp.data:
            user["doctor_id"] = d_resp.data[0]["id"]
            user["specialization"] = d_resp.data[0]["specialization"]

    return user


def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    if not user or not verify_password(password, user.get("password", "")):
        return None
    return user


def register_user(payload: UserCreate) -> dict:
    if get_user_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 1. Insert into users table
    user_resp = (
        supabase.table("users")
        .insert(
            {
                "name": payload.name,
                "email": payload.email,
                "password": hash_password(payload.password),
                "role": payload.role,
            }
        )
        .execute()
    )
    if not user_resp.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user record",
        )
    user = user_resp.data[0]

    # 2. Insert into profile table based on role
    if payload.role == "doctor":
        doc_resp = (
            supabase.table("doctors")
            .insert({
                "user_id": user["id"],
                "specialization": payload.specialization
            })
            .execute()
        )
        if not doc_resp.data:
            # Rollback user creation
            supabase.table("users").delete().eq("id", user["id"]).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create doctor profile",
            )
        user["doctor_id"] = doc_resp.data[0]["id"]
        user["specialization"] = doc_resp.data[0]["specialization"]

    elif payload.role == "patient":
        pat_resp = (
            supabase.table("patients")
            .insert({
                "user_id": user["id"],
                "phone": payload.phone
            })
            .execute()
        )
        if not pat_resp.data:
            # Rollback user creation
            supabase.table("users").delete().eq("id", user["id"]).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create patient profile",
            )
        user["patient_id"] = pat_resp.data[0]["id"]
        user["phone"] = pat_resp.data[0]["phone"]

    return user


# ── FastAPI dependencies ──────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise exc
        token_data = TokenData(id=user_id)
    except JWTError:
        raise exc

    user = get_user_by_id(token_data.id)
    if user is None:
        raise exc
    return user


def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user
