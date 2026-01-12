"""Suggestion form component - User submission of new locations."""
import streamlit as st


def render_suggestion_form(suggestion_service):
    """Render suggestion submission form with PLZ validation."""
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
    """Handle form submission with validation."""
    if not plz.strip():
        st.error("Please enter a postal code")
    elif not address.strip():
        st.error("Please enter an address or location description")
    elif not reason.strip():
        st.error("Please explain why this location needs charging stations")
    else:
        try:
            plz_int = int(plz.strip())
            if 10000 <= plz_int <= 14200:
                suggestion_service.create_suggestion(
                    plz=plz.strip(),
                    address=address.strip(),
                    reason=reason.strip()
                )
                st.success("Thank you! Your suggestion has been submitted and will be reviewed.")
                st.balloons()
            else:
                st.error("Please enter a valid Berlin postal code (10000-14200)")
        except ValueError:
            st.error("Please enter a valid 5-digit postal code")
