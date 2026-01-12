"""Suggestion list component - View and admin management of suggestions."""
import streamlit as st
from datetime import datetime

from config import pdict
from src.suggestion.domain.exceptions import InvalidSuggestionException


def render_suggestion_list(suggestion_service):
    """Render community suggestions with optional admin controls."""
    st.header("Community Suggestions")
    suggestions = suggestion_service.get_all_suggestions()
    st.write("See suggestions from the community for new charging locations.")

    # Admin password protection (from config)
    admin_password = st.text_input("Enter Admin Password to review", type="password")

    if admin_password == pdict.get("admin_password", ""):
        admin_mode = True
        st.success("Admin mode unlocked")
    else:
        admin_mode = False
        st.info("Enter the correct admin password to unlock review features.")

    if not suggestions:
        st.info("No suggestions yet. Be the first to suggest a new charging location!")
    else:
        st.write(f"**Total suggestions:** {len(suggestions)}")
        _render_suggestions_by_plz(suggestions, admin_mode, suggestion_service)


def _render_suggestions_by_plz(suggestions, admin_mode, suggestion_service):
    """Group and render suggestions by PLZ."""
    suggestions_by_plz = {}
    for s in suggestions:
        plz = s.get('plz', 'Unknown')
        if plz not in suggestions_by_plz:
            suggestions_by_plz[plz] = []
        suggestions_by_plz[plz].append(s)

    for plz in sorted(suggestions_by_plz.keys()):
        with st.expander(f"PLZ {plz} ({len(suggestions_by_plz[plz])} suggestions)"):
            for suggestion in suggestions_by_plz[plz]:
                _render_single_suggestion(suggestion, admin_mode, suggestion_service)


def _render_single_suggestion(suggestion, admin_mode, suggestion_service):
    """Render a single suggestion with optional admin controls."""
    status = suggestion.get('status', 'pending')
    status_emoji = {"pending": "...", "approved": "[OK]", "rejected": "[X]"}.get(status, "?")

    st.write(f"{status_emoji} **Location:** {suggestion.get('address', 'N/A')}")
    st.write(f"**Reason:** {suggestion.get('reason', 'N/A')}")
    st.write(f"**Status:** {status.title()}")

    timestamp = suggestion.get('timestamp', '')
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            st.caption(f"Suggested on {dt.strftime('%Y-%m-%d %H:%M')}")
        except:
            st.caption(f"Suggested: {timestamp}")

    # Show review info if available
    if suggestion.get('reviewed_by'):
        st.caption(f"Reviewed by {suggestion['reviewed_by']} on {suggestion.get('review_date', '')[:10]}")
        if suggestion.get('review_notes'):
            st.caption(f"Notes: {suggestion['review_notes']}")

    # Admin review buttons
    if admin_mode and status == 'pending':
        _render_admin_controls(suggestion, suggestion_service)

    st.divider()


def _render_admin_controls(suggestion, suggestion_service):
    """Render admin review controls for a suggestion."""
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"Approve #{suggestion['id']}", key=f"approve_{suggestion['id']}"):
            try:
                suggestion_service.review_suggestion(suggestion['id'], 'approved', 'Admin')
                st.success("Suggestion approved!")
                st.rerun()
            except InvalidSuggestionException as e:
                st.error(str(e))
    with col2:
        if st.button(f"Reject #{suggestion['id']}", key=f"reject_{suggestion['id']}"):
            try:
                suggestion_service.review_suggestion(suggestion['id'], 'rejected', 'Admin')
                st.success("Suggestion rejected!")
                st.rerun()
            except InvalidSuggestionException as e:
                st.error(str(e))
    with col3:
        notes = st.text_input(f"Notes for #{suggestion['id']}", key=f"notes_{suggestion['id']}")
        if st.button(f"Add Notes #{suggestion['id']}", key=f"add_notes_{suggestion['id']}"):
            try:
                suggestion_service.review_suggestion(suggestion['id'], suggestion.get('status', 'pending'), 'Admin', notes)
                st.success("Notes added!")
                st.rerun()
            except InvalidSuggestionException as e:
                st.error(str(e))
