"""
ROADGUARD AI - Authentication & Role-Based Access Control
Session state helpers for Citizen and Municipal Authority roles.
"""

import streamlit as st
from typing import Optional, Dict, Any
from database.db import authenticate_user, create_user

def init_session_auth():
    """Initializes user session state if not already set."""
    if "user" not in st.session_state:
        # Default unauthenticated or default citizen guest
        st.session_state["user"] = {
            "id": 1,
            "username": "admin",
            "full_name": "Municipal Road Engineer (Admin)",
            "role": "authority"
        }

def get_current_user() -> Optional[Dict[str, Any]]:
    """Returns the currently active logged-in user dict."""
    return st.session_state.get("user")

def is_authority() -> bool:
    """Returns True if user has authority/admin privileges."""
    user = get_current_user()
    return user is not None and user.get("role") == "authority"

def is_citizen() -> bool:
    """Returns True if user is a citizen reporter."""
    user = get_current_user()
    return user is not None and user.get("role") == "citizen"

def switch_role(role: str):
    """Allows rapid role toggling between Municipal Authority and Citizen."""
    if role == "authority":
        st.session_state["user"] = {
            "id": 1,
            "username": "admin",
            "full_name": "Municipal Road Engineer",
            "role": "authority"
        }
    else:
        st.session_state["user"] = {
            "id": 2,
            "username": "citizen",
            "full_name": "Citizen Reporter",
            "role": "citizen"
        }
