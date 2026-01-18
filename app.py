import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF

# Cor verde extraída do material "Breve Introdução ao Tema" 
COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Extrator Duo", page_icon="📝")

# Interface do App com estilo Cursos Duo [cite: 5]
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Gerador de Resumos de Destaques</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arraste o PDF da aula aqui", type="pdf")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        # Extração dos grifos
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: # Tipo 8 é o marca-texto
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({
                            "pag": page_num + 1,
                            "texto": text.strip()
                        })

        if highlights:
            st.success(f"Sucesso! Identificamos {len(highlights)} trechos destacados.")

            # --- GERAÇÃO DO PDF USANDO FONTES PADRÃO ---
            # Usamos 'latin-1' para evitar erros de codificação com acentos
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho do PDF - Estilo Cursos Duo
            pdf.set_fill_color(*COR_VERDE_DUO)
            pdf.rect(0, 0, 210, 35, 'F')
            
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(255, 255, 255)
            # Título conforme solicitado pelo usuário
            pdf.cell(0, 15, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
            
            pdf.ln(25)
            
            # Corpo do Texto
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0, 0, 0)
            
            for h in highlights:
                # Limpa caracteres que o PDF padrão não reconhece para evitar erros
                texto_limpo = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                pdf.set_draw_color(*COR_VERDE_DUO)
                pdf.set_line_width(0.5)
                
                # Formatação: PÁGINA X: Trecho...
                pdf.multi_cell(0, 8, f"PAGINA {h['pag']}: {texto_limpo}", border='L')
                pdf.ln(3)
            
            # Rodapé com e-mail do curso [cite: 21, 30]
            pdf.set_y(-20)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')
            
            pdf_bytes = pdf.output(dest='S')
            
            st.download_button(
                label="📥 Baixar PDF do Resumo",
                data=pdf_bytes,
                file_name="resumo_destaques_duo.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Nenhum destaque (marca-texto) foi encontrado neste PDF.")
            
    except Exception as e:
        st.error(f"Ocorreu um erro no processamento: {e}")
