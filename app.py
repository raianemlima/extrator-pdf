import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random
import re

# Cor verde oficial da identidade visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138) 

def limpar_texto_total(texto):
    """Remove referências numéricas (rodapés) e mapeia símbolos complexos"""
    # 1. Remove números colados ao final de palavras (ex: Federal5 -> Federal)
    # Protegemos casos como 'Art. 5' mantendo espaço, mas limpamos 'exercício.6'
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]+)(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto) # Remove número após ponto final
    
    # 2. Mapeamento de sinais e símbolos
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '\u2010': '-', '\u2011': '-', '\u00ba': 'º', '\u00aa': 'ª'
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓", layout="wide")

# --- CABEÇALHO VISUAL CURSOS DUO ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin: 0; font-family: 'Arial Black', sans-serif; letter-spacing: 3px; font-size: 2.8em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-family: Arial, sans-serif; font-size: 1.5em; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material em PDF", type="pdf")
nome_modulo = st.text_input("Identificação do Material", placeholder="Ex: Criminologia - Teoria Labelling Approach")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({"pag": page_num + 1, "texto": limpar_texto_total(text)})

        if highlights:
            st.success(f"Otimização concluída: {len(highlights)} pontos de estudo ativos.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads do Resumo", "🗂️ Flashcards & P&R Inteligentes", "🧠 Simulado Ativo"])

            # --- TAB 1: DOWNLOADS ---
            with tab1:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, "Cursos Duo", ln=True, align='C')
                pdf.ln(25)
                pdf.set_font("Helvetica", size=10)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Material: {nome_modulo} | Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12) 
                    pdf.set_text_color(0, 0, 0)
                    txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_pdf, align='J')
                    pdf.ln(4)
                
                word_doc = Document()
                h_word = word_doc.add_heading(level=0)
                r_h = h_word.add_run("RESUMO INTELIGENTE")
                r_h.font.color.rgb = RGBColor(166, 201, 138)
                word_doc.add_paragraph("Cursos Duo").bold = True
                word_doc.add_paragraph(f"Material: {nome_modulo} | Data: {date.today().strftime('%d/%m/%Y')}")

                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run_t = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
                    run_t.bold = True
                    run_t.font.color.rgb = RGBColor(166, 201, 138)
                    rtx = p.add_run(h['texto'])
                    rtx.font.name = 'Arial'
                    rtx.font.size = Pt(12)

                col1, col2 = st.columns(2)
                with col1: st.download_button("📥 Baixar em PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with col2:
                    buf = io.BytesIO()
                    word_doc.save(buf)
                    st.download_button("📥 Baixar em Word", buf.getvalue(), "Resumo_Duo.docx")

            # --- TAB 2: FLASHCARDS & P&R ADAPTADOS ---
            with tab2:
                st.subheader("Modo de Revisão Ativa (Estética Otimizada)")
                
                # Roteiro P&R com Formatação Inteligente
                pr_pdf = FPDF()
                pr_pdf.set_auto_page_break(auto=True, margin=15)
                pr_pdf.add_page()
                pr_pdf.set_font("Helvetica", "B", 18)
                pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                pr_pdf.cell(0, 15, "ROTEIRO P&R - ESTUDO ATIVO", ln=True, align='C')
                pr_pdf.set_draw_color(*COR_VERDE_DUO_RGB)
                pr_pdf.line(10, 25, 200, 25)
                
                for i, h in enumerate(highlights, 1):
                    pr_pdf.ln(8)
                    # Pergunta estilizada
                    pr_pdf.set_fill_color(245, 250, 245)
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(60, 100, 60)
                    pr_pdf.cell(0, 10, f"  PERGUNTA {i:02d} (Referência: Página {h['pag']})", ln=True, fill=True)
                    
                    pr_pdf.set_font("Helvetica", "I", 11)
                    pr_pdf.set_text_color(80, 80, 80)
                    pr_pdf.multi_cell(0, 8, "Com base no material de apoio, qual o ponto essencial abordado neste destaque?", align='L')
                    
                    # Resposta (O destaque limpo)
                    pr_pdf.ln(2)
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, "RESPOSTA DO MATERIAL:", ln=True)
                    
                    pr_pdf.set_font("Helvetica", size=12)
                    pr_pdf.set_text_color(0, 0, 0)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(0, 7, txt_pr, align='J')
                    pr_pdf.ln(5)

                # Flashcards Inteligentes (Grade Visual)
                f_pdf = FPDF()
                f_pdf.set_auto_page_break(auto=True, margin=10)
                f_pdf.add_page()
                f_pdf.set_font("Helvetica", "B", 16)
                f_pdf.cell(0, 15, "FLASHCARDS PARA RECORTE", ln=True, align='C')
                
                for i, h in enumerate(highlights, 1):
                    f_pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                    f_pdf.set_text_color(255, 255, 255)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(190, 8, f" FLASHCARD {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    
                    f_pdf.set_text_color(0, 0, 0)
                    f_pdf.set_font("Helvetica", size=11)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(190, 8, txt_f, border=1, align='J')
                    f_pdf.ln(6)

                col_a, col_b = st.columns(2)
                with col_a: st.download_button("📝 Baixar Roteiro P&R Adaptado", bytes(pr_pdf.output()), "Roteiro_PR_Otimizado.pdf")
                with col_b: st.download_button("✂️ Baixar Flashcards Estilizados", bytes(f_pdf.output()), "Flashcards_Duo_Visual.pdf")

            # --- TAB 3: QUIZ ---
            with tab3:
                st.subheader("🧠 Simulado Ativo")
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        secreta = max(palavras, key=len).strip(".,;:()")
                        st.write(f"**Questão {idx+1}:** {item['texto'].replace(secreta, '__________')}")
                        resp = st.text_input(f"Complete (Pág {item['pag']}):", key=f"qz_{idx}")
                        if st.button(f"Validar {idx+1}"):
                            if resp.lower().strip() == secreta.lower().strip(): st.success(f"Excelente!")
                            else: st.warning(f"Resposta: {secreta}")

        st.markdown(f"<hr><p style='text-align: center; color: gray;'>Suporte Técnico: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
