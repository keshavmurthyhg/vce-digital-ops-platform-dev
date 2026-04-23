import streamlit as st


def render_main(df):

    st.title("Incident Report Generator")

    # ---------------- SINGLE INCIDENT ---------------- #
    col1, col2 = st.columns([3, 1])

    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique()
        )

    with col2:
        st.write("")  # spacing
        fetch = st.button("Fetch", use_container_width=True)

    # ---------------- BULK INPUT ---------------- #
    st.markdown("### Bulk Incident Numbers")

    bulk_input = st.text_area(
        "Enter comma-separated incident numbers",
        placeholder="INC123, INC456, INC789"
    )

    # ---------------- ACTION BUTTONS ---------------- #
    colA, colB, colC, colD = st.columns(4)

    with colA:
        generate_pdf = st.button("Generate PDF", use_container_width=True)

    with colB:
        generate_word = st.button("Generate Word", use_container_width=True)

    with colC:
        bulk_btn = st.button("Bulk Generate", use_container_width=True)

    with colD:
        clear_btn = st.button("Clear", use_container_width=True)

    # ---------------- LOGIC HOOKS ---------------- #

    if fetch:
        st.session_state["selected_incident"] = incident
        st.success(f"Loaded {incident}")

    if generate_pdf:
        st.info("PDF generation triggered")

    if generate_word:
        st.info("Word generation triggered")

    if bulk_btn:
        if bulk_input.strip():
            incidents = [x.strip() for x in bulk_input.split(",") if x.strip()]
            st.session_state["bulk_list"] = incidents
            st.success(f"{len(incidents)} incidents ready for bulk")
        else:
            st.warning("Enter incident numbers")

    if clear_btn:
        st.session_state.clear()
        st.rerun()
