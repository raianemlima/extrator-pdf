import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
import requests
import os

# Função para garantir suporte a acentos
def baixar_fonte():
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/reingart/pyfpdf/raw/master/font/DejaVuSans.ttf"
        response = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(response.content)
    return font_path

# Configuração da Identidade Visual Duo
COR_VERDE_DUO = (166, 201, 138)  # Tom de verde extraído do material 

st.set_page_config(page_title="Extrator de Destaques - Duo", page_icon="📝")

# Estilo da Interface (Mimicando o cabeçalho do PDF) [cite: 1, 3]
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 10px; border-radius: 5px; text-align: center;">
        <h1 style="color: white; margin: 0;">CURSOS DUO</h1>
        <p style="color: white; margin: 0;">Extrator de Destaques para Alunos</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba aqui o seu PDF do Cursos Duo", type="pdf")

if uploaded_file is not None:
    caminho_fonte = baixar_fonte()
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    highlights = []

    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8: # Marca-texto
                text = page.get_textbox(annot.rect)
                highlights.append(f"Pág. {page_num + 1}: {text.strip()}")

    if highlights:
        st.success(f"Foram identificados {len(highlights)} trechos destacados!")

        # --- GERAÇÃO DO PDF COM IDENTIDADE VISUAL ---
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", caminho_fonte)
        
        # Cabeçalho Identidade Duo [cite: 1]
        pdf.set_fill_color(*COR_VERDE_DUO)
        pdf.rect(0, 0, 210, 30, 'F') # Faixa verde no topo
        
        pdf.set_font("DejaVu", size=16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
        
        pdf.ln(20)
        
        # Conteúdo
        pdf.set_font("DejaVu", size=11)
        pdf.set_text_color(0, 0, 0)
        for h in highlights:
            pdf.multi_cell(0, 8, h)
            pdf.ln(2)
            
        # Rodapé com e-mail do curso [cite: 21]
        pdf.set_y(-20)
        pdf.set_font("DejaVu", size=8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, "Dúvidas: sugestoes@cursosduo.com.br", align='C')
        
        pdf_output = pdf.output(dest='S')
        
        st.download_button(
            label="📥 Baixar PDF Personalizado",
            data=pdf_output,
            file_name="resumo_destaques_duo.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("Nenhum destaque encontrado. Verifique se você usou a ferramenta de marca-texto no PDF.")
