
import fitz  # PyMuPDF
import re
import streamlit as st

@st.cache_data(ttl=300)
def extract_text_from_pdf(file_hash: str, uploaded_file, max_pages: int = 15) -> str:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = ""
        progress_bar = st.progress(0)
        total_pages = min(len(doc), max_pages)

        for i in range(total_pages):
            page_text = doc.load_page(i).get_text()
            if page_text.strip():
                full_text += f"\n--- Page {i + 1} ---\n{page_text}"
            progress_bar.progress((i + 1) / total_pages)

        progress_bar.empty()
        doc.close()

        full_text = re.sub(r'\n\s*\n', '\n\n', full_text)
        full_text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'/]', '', full_text)

        return full_text
    except Exception as e:
        st.error(f"PDF processing error: {str(e)}")
        return None
