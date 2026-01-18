import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
import requests
import os

# Função corrigida para baixar a fonte de um link direto (RAW)
def baixar_fonte():
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        # Link direto para o arquivo binário da fonte
        url = "https://raw.githubusercontent.com/reingart/pyfpdf/master/font/DejaVuSans.ttf"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(font_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            st.error(f"Erro ao baixar a fonte: {e}")
    return font_path

# Identidade Visual Duo baseada no material enviado
COR_VERDE_DUO = (166, 201, 138) # Verde das barras de título

st.set_page_config(page_title="Extrator Duo", page_icon="📝")

# Cabeçalho da Interface Estilizado
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #d1e7dd;">
        <h1 style="color: #2d5a27; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: #2d5a27; margin: 0; font-weight: bold;">Ferramenta de Apoio ao Aluno</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arraste o PDF do material aqui", type="pdf")

if uploaded_file is not None:
    caminho_fonte = baixar_fonte()
    
    if os.path.exists(caminho_fonte):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: # Tipo Highlight
                    text = page.get_textbox(annot.rect)
                    highlights.append({
                        "pág": page_num + 1,
                        "texto": text.strip()
                    })

        if highlights:
            st.success(f"Sucesso! Encontramos {len(highlights)} trechos destacados.")

            # --- GERAÇÃO DO PDF ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Tenta carregar a fonte baixada
            pdf.add_font("DejaVu", "", caminho_fonte)
            
            # Cabeçalho do PDF personalizado
            pdf.set_fill_color(*COR_VERDE_DUO)
            pdf.rect(0, 0, 210, 35, 'F')
            
            pdf.set_font("DejaVu", size=16)
            pdf.set_text_color(255, 255, 255)
            # Título solicitado
            pdf.cell(0, 15, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
            
            pdf.ln(25)
            
            # Lista de Destaques
            pdf.set_font("DejaVu", size=11)
            pdf.set_text_color(0, 0, 0)
            
            for h in highlights:
                # Pequena barra lateral para cada item
                pdf.set_draw_color(*COR_VERDE_DUO)
                pdf.set_line_width(0.5)
                
                texto_formatado = f"PÁGINA {h['pág']}: {h['texto']}"
                pdf.multi_cell(0, 8, texto_formatado, border='L')
                pdf.ln(4)
            
            # Rodapé institucional [cite: 21, 30]
            pdf.set_y(-20)
            pdf.set_font("DejaVu", size=8)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')
            
            pdf_output = pdf.output(dest='S')
            
            st.download_button(
                label="📥 Baixar PDF Finalizado",
                data=pdf_output,
                file_name="resumo_destaques_duo.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Nenhum marca-texto encontrado no arquivo.")
    else:
        st.error("Falha ao carregar os componentes de texto. Tente atualizar a página.")
