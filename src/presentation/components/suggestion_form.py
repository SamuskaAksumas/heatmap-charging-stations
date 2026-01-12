"""Suggestion form component - User submission of new locations."""
import streamlit as st

from src.suggestion.domain.exceptions import InvalidSuggestionException


def render_suggestion_form(suggestion_service):
    """Render suggestion submission form. Validation happens in Domain layer."""
    st.header("Suggest New Charging Location")
    st.write("Help improve Berlin's charging infrastructure by suggesting new locations where charging stations are needed.")

    with st.form("suggestion_form"):
        col1, col2 = st.columns(2)
        with col1:
            plz = st.text_input("Postal Code (PLZ)", placeholder="e.g., 10115")
        with col2:
            address = st.text_input("Address/Location Description", placeholder="Street name, building, or area")

        reason = st.text_area("Why is this location needed?", placeholder="Describe the need for charging stations here...")

        submitted = st.form_submit_button("Submit Suggestion")

        if submitted:
            _handle_submission(plz, address, reason, suggestion_service)


def _handle_submission(plz, address, reason, suggestion_service):
    """Handle form submission. Domain layer handles all validation."""
    try:
        suggestion_service.create_suggestion(
            plz=plz.strip(),
            address=address.strip(),
            reason=reason.strip()
        )
        st.success("Thank you! Your suggestion has been submitted and will be reviewed.")
        st.balloons()
    except InvalidSuggestionException as e:
        st.error(str(e))
