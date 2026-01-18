import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
import requests
import os

# Função para garantir que temos uma fonte com suporte a acentos
def baixar_fonte():
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/reingart/pyfpdf/raw/master/font/DejaVuSans.ttf"
        response = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(response.content)
    return font_path

st.set_page_config(page_title="Extrator de Destaques", page_icon="📝")

st.title("📝 Extrator de Grifos em PDF")
st.write("Agora com suporte total a acentos e cedilha!")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Preparar fonte
    caminho_fonte = baixar_fonte()
    
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    highlights = []

    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8:
                text = page.get_textbox(annot.rect)
                highlights.append(f"Página {page_num + 1}: {text.strip()}")

    if highlights:
        st.success(f"Encontramos {len(highlights)} destaques!")

        # Gerando o PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Registrando e usando a fonte Unicode
        pdf.add_font("DejaVu", "", caminho_fonte)
        pdf.set_font("DejaVu", size=16)
        pdf.cell(0, 10, "Relatório de Destaques", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("DejaVu", size=11)
        for h in highlights:
            # multi_cell evita que o texto saia da folha
            pdf.multi_cell(0, 8, h)
            pdf.ln(2)
        
        pdf_output = pdf.output(dest='S')
        
        st.download_button(
            label="📥 Baixar Destaques em PDF",
            data=pdf_output,
            file_name="meus_destaques.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("Nenhum destaque encontrado.")
