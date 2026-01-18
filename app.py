import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random

# Cor verde oficial da identidade visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138) 

def limpar_texto_total(texto):
    """Mapeamento exaustivo para converter símbolos de PDF em caracteres legíveis"""
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', # Travessões
        '\u201c': '"', '\u201d': '"', # Aspas duplas curvas
        '\u2018': "'", '\u2019': "'", # Aspas simples curvas
        '\u2022': '•', '\uf0b7': '•', # Diferentes tipos de Bullet points
        '\u2026': '...', # Reticências
        '\u00a0': ' ', # Espaço não quebrável
        '\u2010': '-', '\u2011': '-', # Hífens especiais
        '\u00ba': 'º', '\u00aa': 'ª', # Símbolos de ordem
        '\uf0d8': '>' # Seta comum em listas
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    
    # Remove quebras de linha forçadas que quebram a justificação
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓")

# --- CABEÇALHO VISUAL CURSOS DUO ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #d1e7dd;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif; letter-spacing: 2px; font-size: 2.2em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-family: Arial, sans-serif; font-size: 1.4em; font-weight: bold; opacity: 0.9;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material em PDF para processamento", type="pdf")
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
            st.success(f"Analisado com sucesso! {len(highlights)} destaques prontos.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads", "🗂️ Estudo Ativo (Flashcards/P&R)", "🧠 Desafio de Memória"])

            # --- TAB 1: DOWNLOADS RESUMO ---
            with tab1:
                # PDF FORMATO ARIAL 12 EQUIVALENTE
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
                    # Encode seguro para PDF
                    txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_pdf, align='J')
                    pdf.ln(4)
                
                # WORD FORMATO ARIAL 12 COM TÍTULO VERDE
                word_doc = Document()
                # Cria o cabeçalho e aplica a cor verde específica
                heading = word_doc.add_heading(level=0)
                run_heading = heading.add_run("RESUMO INTELIGENTE")
                run_heading.font.color.rgb = RGBColor(166, 201, 138) # Aplica o Verde Duo

                # Subtítulo Cursos Duo
                para_sub = word_doc.add_paragraph()
                run_sub = para_sub.add_run("Cursos Duo")
                run_sub.bold = True
                run_sub.font.size = Pt(14)
                
                word_doc.add_paragraph(f"Material: {nome_modulo} | Data: {date.today().strftime('%d/%m/%Y')}")

                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run_t = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
                    run_t.bold = True
                    run_t.font.color.rgb = RGBColor(166, 201, 138)
                    run_text = p.add_run(h['texto'])
                    run_text.font.name = 'Arial'
                    run_text.font.size = Pt(12)

                c1, c2 = st.columns(2)
                nome_base = nome_modulo.replace(" ", "_") if nome_modulo else "Resumo_Duo"
                with c1: st.download_button("📥 Baixar em PDF", bytes(pdf.output()), f"{nome_base}.pdf")
                with c2:
                    buf = io.BytesIO()
                    word_doc.save(buf)
                    st.download_button("📥 Baixar em Word", buf.getvalue(), f"{nome_base}.docx")

            # --- TAB 2: FLASHCARDS E P&R ---
            with tab2:
                st.subheader("Modo de Revisão Ativa")
                # PDF de Perguntas e Respostas
                pr_pdf = FPDF()
                pr_pdf.add_page()
                pr_pdf.set_font("Helvetica", "B", 16)
                pr_pdf.cell(0, 10, "ROTEIRO DE PERGUNTAS E RESPOSTAS", ln=True, align='C')
                pr_pdf.ln(10)
                for i, h in enumerate(highlights, 1):
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, f"PERGUNTA {i:02d} (Pág. {h['pag']}):", ln=True)
                    pr_pdf.set_font("Helvetica", "I", 11)
                    pr_pdf.set_text_color(50, 50, 50)
                    pr_pdf.multi_cell(0, 7, f"Qual a principal lição ou conceito extraído deste trecho?", align='L')
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, "RESPOSTA:", ln=True)
                    pr_pdf.set_font("Helvetica", size=12)
                    pr_pdf.set_text_color(0, 0, 0)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(0, 7, txt_pr, align='J')
                    pr_pdf.ln(6)
                    pr_pdf.line(10, pr_pdf.get_y(), 200, pr_pdf.get_y())
                    pr_pdf.ln(4)

                col_a, col_b = st.columns(2)
                with col_a: st.download_button("📝 Roteiro P&R (PDF)", bytes(pr_pdf.output()), "Perguntas_Respostas_Duo.pdf")
                
                # Tabela de Flashcards
                f_pdf = FPDF()
                f_pdf.add_page()
                for i, h in enumerate(highlights, 1):
                    f_pdf.set_draw_color(*COR_VERDE_DUO_RGB)
                    f_pdf.set_fill_color(245, 245, 245)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(0, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    f_pdf.set_font("Helvetica", size=12)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(0, 10, txt_f, border=1, align='J')
                    f_pdf.ln(5)
                with col_b: st.download_button("✂️ Flashcards Recortáveis", bytes(f_pdf.output()), "Flashcards_Duo.pdf")

            # --- TAB 3: QUIZ ---
            with tab3:
                st.subheader("🧠 Quiz de Memória Ativa")
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        secreta = max(palavras, key=len).strip(".,;:()")
                        pergunta = item['texto'].replace(secreta, "__________")
                        st.write(f"**Questão {idx+1}:** {pergunta}")
                        resp = st.text_input(f"Complete a lacuna (Pág {item['pag']}):", key=f"qz_{idx}")
                        if st.button(f"Verificar Questão {idx+1}"):
                            if resp.lower().strip() == secreta.lower().strip(): st.success(f"Correto! A palavra é: {secreta}")
                            else: st.warning(f"Resposta correta: {secreta}")
                        st.divider()

        st.markdown(f"<hr><p style='text-align: center; color: gray;'>Dúvidas: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
