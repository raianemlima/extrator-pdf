import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF

st.set_page_config(page_title="Extrator de Destaques", page_icon="📝")

st.title("📝 Extrator de Grifos em PDF")
st.write("Seus destaques serão organizados em um novo arquivo PDF.")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    highlights = []

    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8: # Tipo Highlight
                text = page.get_textbox(annot.rect)
                highlights.append(f"Página {page_num + 1}: {text.strip()}")

    if highlights:
        st.success(f"Encontramos {len(highlights)} destaques!")

        # --- GERAÇÃO DO PDF DE SAÍDA ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(40, 10, "Relatório de Destaques")
        pdf.ln(15) # Quebra de linha
        
        pdf.set_font("Arial", size=12)
        for h in highlights:
            # Multi_cell é melhor para textos longos que precisam quebrar linha
            pdf.multi_cell(0, 10, h)
            pdf.ln(2)
        
        # Converter PDF para bytes para o download
        pdf_output = pdf.output(dest='S')
        
        st.download_button(
            label="📥 Baixar Destaques em PDF",
            data=pdf_output,
            file_name="meus_destaques.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("Nenhum destaque encontrado.")
