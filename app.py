import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from datetime import date

# Identidade Visual Duo: Verde das barras de título [cite: 27]
COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Extrator Duo", page_icon="📝")

# Interface do App estilizada
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Organizador de Destaques para Alunos</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arraste o PDF do material aqui", type="pdf")
nome_modulo = st.text_input("Identificação do Material", placeholder="Ex: Direitos Difusos e Coletivos - Ponto 6")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        # Remove quebras de linha para garantir a justificação perfeita
                        texto_limpo = " ".join(text.split())
                        highlights.append({"pag": page_num + 1, "texto": texto_limpo})

        if highlights:
            st.success(f"Sucesso! Identificamos {len(highlights)} itens destacados.")

            # --- GERAÇÃO DO PDF ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Cabeçalho Superior Duo [cite: 1, 5]
            pdf.set_fill_color(*COR_VERDE_DUO)
            pdf.rect(0, 0, 210, 40, 'F')
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
            
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, f"Material: {nome_modulo if nome_modulo else 'Revisão Geral'}", ln=True, align='C')
            
            pdf.ln(25)
            
            # Data seguindo o padrão do material [cite: 4, 22]
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
            pdf.ln(5)
            
            # Listagem Numerada e Justificada
            for i, h in enumerate(highlights, 1):
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(*COR_VERDE_DUO)
                pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                
                pdf.set_font("Helvetica", size=11)
                pdf.set_text_color(40, 40, 40)
                
                # Tratamento de caracteres e justificação total ('J')
                txt_final = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 7, txt_final, align='J')
                pdf.ln(5) 
            
            # Rodapé com e-mail institucional [cite: 21, 30]
            pdf.set_y(-20)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')
            
            # Preparação segura para download
            pdf_bytes = bytes(pdf.output())
            nome_arq = f"Resumo_{nome_modulo.replace(' ', '_')}.pdf" if nome_modulo else "resumo_duo.pdf"
            
            st.download_button(
                label="📥 Baixar PDF do Resumo",
                data=pdf_bytes,
                file_name=nome_arq,
                mime="application/pdf",
            )
        else:
            st.warning("Nenhum destaque encontrado no material.")
            
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
