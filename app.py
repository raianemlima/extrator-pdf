import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from datetime import date

# Cor verde oficial das barras de título do material
COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Extrator Duo", page_icon="📝")

# Estilização da Interface baseada na identidade visual do curso
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Gerador de Resumos Organizados</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arraste o PDF do Cursos Duo aqui", type="pdf")
nome_modulo = st.text_input("Nome do Módulo/Tema", placeholder="Ex: Direitos Difusos e Coletivos")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        # LIMPEZA CRUCIAL: Remove quebras de linha internas para permitir a justificação
                        texto_limpo = " ".join(text.split())
                        highlights.append({"pag": page_num + 1, "texto": texto_limpo})

        if highlights:
            st.success(f"Encontramos {len(highlights)} destaques para processar.")

            # --- GERAÇÃO DO PDF ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Cabeçalho Identidade Duo
            pdf.set_fill_color(*COR_VERDE_DUO)
            pdf.rect(0, 0, 210, 40, 'F')
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
            
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, f"Material: {nome_modulo if nome_modulo else 'Conteúdo de Estudo'}", ln=True, align='C')
            
            pdf.ln(25)
            
            # Data de emissão (seguindo padrão do curso)
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
            pdf.ln(5)
            
            # Listagem dos Destaques Justificados
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0, 0, 0)
            
            for h in highlights:
                # Título da página em negrito
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(*COR_VERDE_DUO)
                pdf.cell(0, 8, f"PÁGINA {h['pag']}", ln=True)
                
                # Texto do destaque com JUSTIFICAÇÃO TOTAL ('J')
                pdf.set_font("Helvetica", size=11)
                pdf.set_text_color(30, 30, 30)
                
                # Tratamento de caracteres especiais para evitar erros binários
                txt_final = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                
                pdf.multi_cell(0, 7, txt_final, align='J')
                pdf.ln(5) # Espaço entre os blocos
            
            # Rodapé institucional 
            pdf.set_y(-20)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')
            
            # Preparação do arquivo para download
            pdf_bytes = bytes(pdf.output())
            nome_arq = f"Resumo_{nome_modulo.replace(' ', '_')}.pdf" if nome_modulo else "resumo_duo.pdf"
            
            st.download_button(
                label="📥 Baixar PDF com Texto Justificado",
                data=pdf_bytes,
                file_name=nome_arq,
                mime="application/pdf",
            )
        else:
            st.warning("Nenhum grifo identificado. Verifique se utilizou a ferramenta de marca-texto.")
            
    except Exception as e:
        st.error(f"Erro técnico: {e}")
