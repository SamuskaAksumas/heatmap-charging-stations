"""Suggestion list component - View and admin management of suggestions."""
from datetime import datetime

import streamlit as st

from config import pdict
from src.suggestion.domain.exceptions import InvalidSuggestionException


def render_suggestion_list(suggestion_service):
    """Render community suggestions with optional admin controls."""
    st.header("Community Suggestions")
    st.write("See suggestions from the community for new charging locations.")

    # Admin password protection (from config)
    admin_password = st.text_input("Enter Admin Password to review", type="password")

    if admin_password == pdict.get("admin_password", ""):
        admin_mode = True
        st.success("Admin mode unlocked")
        # Admin sees all suggestions (except deleted)
        suggestions = suggestion_service.get_all_suggestions()
    else:
        admin_mode = False
        st.info("Enter the correct admin password to unlock review features.")
        # Users see only pending + approved
        suggestions = suggestion_service.get_suggestions_for_users()

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
        except ValueError:
            st.caption(f"Suggested: {timestamp}")

    # Show review info if available
    if suggestion.get('reviewed_by'):
        review_date = suggestion.get('review_date', '')[:10]
        st.caption(f"Reviewed by {suggestion['reviewed_by']} on {review_date}")
        if suggestion.get('review_notes'):
            st.caption(f"Notes: {suggestion['review_notes']}")

    # Admin controls
    if admin_mode:
        _render_admin_controls(suggestion, suggestion_service, status)

    st.divider()


def _render_admin_controls(suggestion, suggestion_service, status):
    """Render admin review controls for a suggestion."""
    suggestion_id = suggestion['id']

    # Notes input field for admin
    notes = st.text_input(
        "Review notes (optional)",
        key=f"notes_{suggestion_id}",
        placeholder="Add notes for this review..."
    )

    # Approve/Reject only for pending
    if status == 'pending':
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✓ Approve", key=f"approve_{suggestion_id}"):
                try:
                    suggestion_service.review_suggestion(suggestion_id, 'approved', 'Admin', notes)
                    st.success("Suggestion approved!")
                    st.rerun()
                except InvalidSuggestionException as e:
                    st.error(str(e))
        with col2:
            if st.button("✗ Reject", key=f"reject_{suggestion_id}"):
                try:
                    suggestion_service.review_suggestion(suggestion_id, 'rejected', 'Admin', notes)
                    st.success("Suggestion rejected!")
                    st.rerun()
                except InvalidSuggestionException as e:
                    st.error(str(e))
        with col3:
            if st.button("🗑 Delete", key=f"delete_{suggestion_id}"):
                try:
                    suggestion_service.review_suggestion(suggestion_id, 'deleted', 'Admin', notes)
                    st.success("Suggestion deleted!")
                    st.rerun()
                except InvalidSuggestionException as e:
                    st.error(str(e))
    else:
        # For approved/rejected: only delete button
        if st.button("🗑 Delete", key=f"delete_{suggestion_id}"):
            try:
                suggestion_service.review_suggestion(suggestion_id, 'deleted', 'Admin', notes)
                st.success("Suggestion deleted!")
                st.rerun()
            except InvalidSuggestionException as e:
                st.error(str(e))
