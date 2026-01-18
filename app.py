import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF

# Identidade Visual Duo: Verde das barras de título
COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Extrator Duo", page_icon="📝")

# Interface do App
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Extração de Destaques para Revisão</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arraste seu PDF aqui", type="pdf")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: # Highlight
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({"pag": page_num + 1, "texto": text.strip()})

        if highlights:
            st.success(f"Encontramos {len(highlights)} trechos destacados!")

            # --- GERAÇÃO DO PDF ---
            pdf = FPDF()
            pdf.add_page()
            
            # Faixa Verde no Topo
            pdf.set_fill_color(*COR_VERDE_DUO)
            pdf.rect(0, 0, 210, 35, 'F')
            
            # Título do Cabeçalho
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 15, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
            
            pdf.ln(25)
            
            # Conteúdo
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0, 0, 0)
            
            for h in highlights:
                # Proteção contra caracteres especiais (acentos)
                txt = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                pdf.set_draw_color(*COR_VERDE_DUO)
                pdf.set_line_width(0.5)
                pdf.multi_cell(0, 8, f"PAGINA {h['pag']}: {txt}", border='L')
                pdf.ln(3)
            
            # Rodapé institucional
            pdf.set_y(-20)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')
            
            # CORREÇÃO DO ERRO BINÁRIO: Convertendo explicitamente para bytes
            pdf_output = pdf.output()
            final_pdf = bytes(pdf_output)
            
            st.download_button(
                label="📥 Baixar PDF do Resumo",
                data=final_pdf,
                file_name="resumo_destaques_duo.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Nenhum grifo encontrado no material.")
            
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
