import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from datetime import date
import random

# Identidade Visual Cursos Duo
COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Duo Study Hub", page_icon="🎓")

# Cabeçalho do App
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Plataforma de Estudo Ativo e Revisão</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material de qualquer disciplina (PDF)", type="pdf")
nome_modulo = st.text_input("Identificação do Tema", placeholder="Ex: Aula 01 - Introdução")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        # Limpa o texto para garantir a justificação perfeita no PDF
                        texto_limpo = " ".join(text.split())
                        highlights.append({"pag": page_num + 1, "texto": texto_limpo})

        if highlights:
            st.success(f"Analisei seu material! Encontrei {len(highlights)} pontos importantes.")
            
            tab1, tab2, tab3 = st.tabs(["📄 Resumo em PDF", "🗂️ Flashcards", "🧠 Quiz de Memória"])

            with tab1:
                st.write("Gere seu arquivo de revisão numerado e justificado.")
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO)
                pdf.rect(0, 0, 210, 40, 'F')
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
                pdf.set_font("Helvetica", "I", 12)
                pdf.cell(0, 10, f"Material: {nome_modulo if nome_modulo else 'Revisão Geral'}", ln=True, align='C')
                pdf.ln(25)
                
                pdf.set_font("Helvetica", size=11)
                pdf.set_text_color(0, 0, 0)
                for i, h in enumerate(highlights, 1):
                    # Título do Item
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_text_color(*COR_VERDE_DUO)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    # Texto Justificado
                    pdf.set_font("Helvetica", size=11)
                    pdf.set_text_color(40, 40, 40)
                    txt_final = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_final, align='J')
                    pdf.ln(5)

                pdf_bytes = bytes(pdf.output())
                st.download_button("📥 Baixar PDF do Resumo", pdf_bytes, f"Resumo_{nome_modulo}.pdf", "application/pdf")

            with tab2:
                st.subheader("🗂️ Flashcards Interativos")
                st.info("Leia a referência e tente lembrar o conteúdo antes de expandir.")
                for i, h in enumerate(highlights, 1):
                    with st.expander(f"CARTÃO {i:02d} (Pág. {h['pag']})"):
                        st.write(h['texto'])

            with tab3:
                st.subheader("🧠 Quiz de Memória Ativa")
                st.write("O sistema escondeu palavras-chave dos seus próprios grifos. Você consegue completar?")
                
                # Seleciona até 5 grifos aleatórios para o Quiz
                amostra_quiz = random.sample(highlights, min(len(highlights), 5))
                
                for idx, item in enumerate(amostra_quiz):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        # Escolhe uma palavra longa (provavelmente técnica) para esconder
                        palavras_longas = [p for p in palavras if len(p) > 6]
                        if palavras_longas:
                            secreta = random.choice(palavras_longas)
                            pergunta = item['texto'].replace(secreta, "__________")
                            
                            st.markdown(f"**Questão {idx+1}:**")
                            st.write(f"*{pergunta}*")
                            resposta_aluno = st.text_input(f"Complete a palavra (Pág {item['pag']}):", key=f"q_{idx}")
                            
                            if st.button(f"Verificar Resposta {idx+1}"):
                                if resposta_aluno.lower().strip() == secreta.lower().strip().strip(".,;:"):
                                    st.success(f"Excelente! A palavra era: **{secreta}**")
                                else:
                                    st.warning(f"Quase lá! A palavra correta era: **{secreta}**")
                            st.divider()

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
