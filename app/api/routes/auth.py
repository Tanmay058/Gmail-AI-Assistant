
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.services.gmail_client import save_credentials
import os
import secrets

router = APIRouter()

SERVICES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".."
)
CREDENTIALS_FILE = os.path.abspath(
    os.path.join(SERVICES_DIR, "credentials.json")
)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

REDIRECT_URI = "http://localhost:8000/auth/callback"
FRONTEND_URL = "http://localhost:5173"

# Local development: keep PKCE verifiers until callback.
# For production, use secure server-side session storage.
pending_verifiers = {}


def create_flow():
    if not os.path.exists(CREDENTIALS_FILE):
        raise HTTPException(
            status_code=500,
            detail="credentials.json not found in project root"
        )

    return Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        autogenerate_code_verifier=True,
    )


def create_auth_url():
    flow = create_flow()

    # Generate a unique state for this authorization attempt.
    state = secrets.token_urlsafe(32)

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )

    verifier = flow.code_verifier
    if not verifier:
        raise HTTPException(
            status_code=500,
            detail="PKCE code verifier was not generated"
        )

    pending_verifiers[state] = verifier
    return auth_url


@router.get("/url")
def get_auth_url():
    return {"auth_url": create_auth_url()}


@router.get("/login")
def login():
    return RedirectResponse(create_auth_url())


@router.get("/callback")
def auth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth error: {error}"
        )

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code"
        )

    if not state:
        raise HTTPException(
            status_code=400,
            detail="Missing OAuth state"
        )

    verifier = pending_verifiers.pop(state, None)
    if not verifier:
        raise HTTPException(
            status_code=400,
            detail=(
                "OAuth session expired or verifier not found. "
                "Start login again from /auth/login."
            )
        )

    flow = create_flow()
    flow.code_verifier = verifier

    try:
        flow.fetch_token(code=code)
        save_credentials(flow.credentials)
    except Exception as exc:
        print(f"[AUTH CALLBACK ERROR] {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=(
                "Google token exchange failed. "
                "Check backend terminal for the error."
            )
        )

    return RedirectResponse(
        url=f"{FRONTEND_URL}/?auth=success"
    )