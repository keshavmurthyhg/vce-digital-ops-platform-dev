import streamlit as st
from modules.doc_word import generate_word_doc
from modules.doc_pdf import generate_pdf


def render_doc_generator():

    import streamlit as st

    st.set_page_config(layout="wide")

    # ================= SIDEBAR =================
    st.sidebar.title("Module")
    st.sidebar.selectbox("Select Module", ["Word Report Generator"])

    st.sidebar.title("Filters")
    priority = st.sidebar.multiselect(
        "Priority",
        ["Priority 1", "Priority 2", "Priority 3", "Priority 4"]
    )

    if st.sidebar.button("Clear"):
        st.session_state.clear()
        st.rerun()

    # ================= MAIN =================
    st.title("SNOW Incident Report Generator")

    incident = st.text_input("Enter Incident Number", key="incident")

    # ================= BUTTON ROW =================
    col1, col2, col3, col4 = st.columns(4)

    # FETCH
    with col1:
        if st.button("Fetch"):
            st.session_state["doc_data"] = {
                "number": incident,
                "azure_bug": "695698",
                "ptc_case": "18007559",
                "priority": "Priority 4",
                "created_by": "Jordan Bingaman",
                "created_date": "2026-01-29",
                "assigned_to": "Keshavamurthy Hg",
                "resolved_date": "2026-02-16",
                t2 = doc.add_table(rows=2, cols=2)
                t2.style = "Table Grid"
                
                t2.rows[0].cells[0].text = "SHORT DESCRIPTION"
                t2.rows[0].cells[1].text = "DESCRIPTION"
                
                t2.rows[1].cells[0].text = clean_text(data.get("short_description"))
                t2.rows[1].cells[1].text = clean_text(data.get("description"))
            }
            
            st.success("Incident loaded")

    # WORD (SAFE — WON'T BREAK UI)
    with col2:
        if st.button("Word"):
            if "doc_data" not in st.session_state:
                st.warning("Fetch incident first")
            else:
                try:
                    from modules.doc_word import generate_word_doc

                    st.session_state["word_file"] = generate_word_doc(
                        st.session_state["doc_data"],
                        "",
                        "",
                        "",
                        None
                    )
                    st.success("Word generated")
                except Exception as e:
                    st.error(f"Word error: {e}")

        if "word_file" in st.session_state:
            st.download_button(
                "⬇",
                st.session_state["word_file"],
                file_name=f"{st.session_state['doc_data']['number']}.docx"
            )

    # PDF (SAFE)
    with col3:
        if st.button("PDF"):
            if "doc_data" not in st.session_state:
                st.warning("Fetch incident first")
            else:
                try:
                    from modules.doc_pdf import generate_pdf

                    st.session_state["pdf_file"] = generate_pdf(
                        st.session_state["doc_data"],
                        "",
                        "",
                        ""
                    )
                    st.success("PDF generated")
                except Exception as e:
                    st.error(f"PDF error: {e}")

        if "pdf_file" in st.session_state:
            st.download_button(
                "⬇",
                st.session_state["pdf_file"],
                file_name=f"{st.session_state['doc_data']['number']}.pdf"
            )

    # PREVIEW
    with col4:
        if st.button("Preview"):
            if "doc_data" in st.session_state:
                d = st.session_state["doc_data"]

                st.markdown("### Preview")
                st.write("Incident:", d["number"])
                st.write("Description:", d["description"])
            else:
                st.warning("Fetch first")
