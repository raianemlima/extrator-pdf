import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from datetime import date

# Cor verde extraída do cabeçalho das seções do material [cite: 27]
COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Extrator Duo", page_icon="📝")

# Estilização da Interface
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Organizador de Destaques e Revisão</p>
    </div>
    <br>
""", unsafe_allow_html=True)

# 1. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste o PDF da aula aqui", type="pdf")

# 2. Campo para Nome do Módulo
nome_modulo = st.text_input("Identificação do Material (ex: Direitos Difusos - Ponto 6)", placeholder="Digite o nome aqui...")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({"pag": page_num + 1, "texto": text.strip()})

        if highlights:
            st.success(f"Sucesso! Encontramos {len(highlights)} trechos destacados.")

            # --- GERAÇÃO DO PDF ---
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho Identidade Duo
            pdf.set_fill_color(*COR_VERDE_DUO)
            pdf.rect(0, 0, 210, 40, 'F')
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
            
            # Subtítulo com o nome do módulo fornecido pelo aluno
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, f"Material: {nome_modulo if nome_modulo else 'Geral'}", ln=True, align='C')
            
            pdf.ln(25)
            
            # Data de geração (seguindo o padrão do material) [cite: 4, 32]
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
            pdf.ln(5)
            
            # Conteúdo dos Grifos
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0, 0, 0)
            
            for h in highlights:
                txt = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                pdf.set_draw_color(*COR_VERDE_DUO)
                pdf.set_line_width(0.5)
                pdf.multi_cell(0, 8, f"PAGINA {h['pag']}: {txt}", border='L')
                pdf.ln(3)
            
            # Rodapé com e-mail institucional [cite: 21, 30, 54]
            pdf.set_y(-20)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')
            
            # Conversão segura para download
            pdf_bytes = bytes(pdf.output())
            
            nome_arquivo = f"Resumo_{nome_modulo.replace(' ', '_')}.pdf" if nome_modulo else "resumo_duo.pdf"
            
            st.download_button(
                label="📥 Baixar PDF do Resumo",
                data=pdf_bytes,
                file_name=nome_arquivo,
                mime="application/pdf",
            )
        else:
            st.warning("Nenhum grifo encontrado. Certifique-se de que o PDF possui marcações de texto.")
            
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
