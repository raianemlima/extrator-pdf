import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date, datetime
import io
import random
import re
from typing import List, Dict, Tuple # Importação necessária aqui no topo
from collections import Counter

# Constantes - Identidade Visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138)
COR_VERDE_DUO_HEX = "#A6C98A"
COR_VERDE_ESCURO = "#7A9B6E"
COR_VERDE_CLARO = "#D4E7C5"
COR_TEXTO_ESCURO = "#2C3E50"
COR_FUNDO_CLARO = "#F8FCF8"

# Configuração da página - Essencial para Mobile e Tablet
st.set_page_config(
    page_title="Resumo Inteligente - Duo",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS CUSTOMIZADO (IDENTIDADE VISUAL) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {COR_TEXTO_ESCURO}; }}
    .stApp {{ background: linear-gradient(135deg, #f5f7fa 0%, #f8fcf8 100%); }}
    .card-duo {{
        background: white; padding: 1.5rem; border-radius: 12px;
        border-left: 4px solid {COR_VERDE_DUO_HEX};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 1rem 0;
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%);
        color: white; border: none; width: 100%; border-radius: 8px; font-weight: 600;
    }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE PROCESSAMENTO ---

def analisar_conteudo_juridico(texto: str) -> Dict[str, any]:
    """Análise inteligente para identificar temas e complexidade."""
    analise = {"tema_principal": None, "artigos_citados": [], "jurisprudencia": [], "nivel_complexidade": "Média"}
    texto_upper = texto.upper()
    
    # Identificação de Temas Jurídicos
    temas_mapa = {
        "CPI": ["CPI", "COMISSÃO PARLAMENTAR", "INQUÉRITO"],
        "Imunidades": ["IMUNIDADE", "INVIOLABILIDADE", "PRERROGATIVA"],
        "Processo Legislativo": ["PROCESSO LEGISLATIVO", "EMENDA", "LEI COMPLEMENTAR"],
        "Poder Executivo": ["PRESIDENTE", "MINISTRO", "DECRETO"],
        "Improbidade": ["LIA", "IMPROBIDADE", "DOLO", "14.230"],
        "Criminologia": ["LABELLING", "ETIQUETAMENTO", "4 DS", "REAÇÃO SOCIAL"]
    }
    
    for tema, palavras in temas_mapa.items():
        if any(p in texto_upper for p in palavras):
            analise["tema_principal"] = tema
            break
            
    artigos = re.findall(r'ART\.?\s*(\d+)', texto, re.IGNORECASE)
    analise["artigos_citados"] = list(set(artigos))
    return analise

def limpar_texto_total(texto: str) -> str:
    """Extração fiel de %$()_* e remoção de resíduos de rodapé."""
    if not texto: return ""
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    mapa = {'\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"', '•': '*', '\uf0b7': '*', '? ': '- '}
    for original, substituto in mapa.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

def gerar_pergunta_contextualizada(texto: str, analise: Dict = None) -> str:
    """Gera enunciados técnicos e completos para evitar perguntas curtas."""
    if not analise: analise = analisar_conteudo_juridico(texto)
    t = texto.lower()
    
    # Enunciados específicos baseados em temas
    if analise["tema_principal"] == "CPI":
        return "Acerca das Comissões Parlamentares de Inquérito (CPI), analise a validade do ato de criação considerando a natureza de direito das minorias e a exigência de fato determinado."
    if analise["tema_principal"] == "Improbidade":
        return "Sobre a Lei de Improbidade Administrativa e suas alterações recentes (Lei 14.230/21), julgue o item quanto à exigência de dolo e conduta."
    if "stf" in t or "stj" in t:
        return "Considerando a jurisprudência atualizada dos Tribunais Superiores e as teses fixadas sobre a matéria, julgue o item a seguir."
    
    # Fallback para perguntas robustas
    palavras = [p for p in texto.split() if len(p) > 3]
    tema = " ".join(palavras[:5]).strip(".,;:- ")
    return f"Considerando os aspectos doutrinários e a fundamentação legal sobre '{tema}', analise se a afirmação abaixo está correta."

def extrair_destaques(pdf_file) -> Tuple[List[Dict], str]:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    highlights = []
    texto_completo = ""
    for page_num, page in enumerate(doc):
        texto_completo += page.get_text() + "\n"
        for annot in page.annots():
            if annot.type[0] == 8:
                txt = limpar_texto_total(page.get_textbox(annot.rect))
                if txt:
                    highlights.append({"pag": page_num + 1, "texto": txt, "analise": analisar_conteudo_juridico(txt)})
    return highlights, texto_completo

# --- INTERFACE E ABAS ---

def main():
    st.markdown(f"""<div style="background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%); padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; color: white;">
        <h1 style="margin:0;">RESUMO INTELIGENTE</h1><p style="font-weight:600;">Cursos Duo</p></div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
    nome_modulo = st.text_input("Identificação do Material", value="Revisão Ponto 6")

    if uploaded_file:
        highlights, texto_completo = extrair_destaques(uploaded_file)
        if highlights:
            st.success(f"✅ {len(highlights)} pontos de estudo identificados.")
            tab1, tab2, tab3 = st.tabs(["📄 Resumo", "🗂️ Flashcards & P&R", "🧠 Simulado C/E"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    pdf_res = FPDF() # Lógica simplificada para exemplo
                    pdf_res.add_page(); pdf_res.set_font("Arial", size=12); pdf_res.cell(200, 10, txt="Resumo Duo", ln=True)
                    st.download_button("📥 Baixar PDF", pdf_res.output(), "Resumo.pdf")
                with col2:
                    st.download_button("📥 Baixar Word", b"word_data", "Resumo.docx")

            with tab2:
                st.info("💡 Flashcards e P&R gerados a partir dos seus grifos.")
                for i, h in enumerate(highlights[:10]): # Mostra alguns na tela
                    st.markdown(f"**Pergunta:** {gerar_pergunta_contextualizada(h['texto'])}")
                    with st.expander("Ver Resposta"): st.write(h['texto'])

            with tab3:
                st.subheader("🧠 Simulado Certo ou Errado")
                st.write("Julgue os itens baseados no seu material:")
                
                # CORREÇÃO DO QUIZ: Processamento para evitar frases curtas
                texto_limpo = texto_completo.replace('\n', ' ')
                frases = [f.strip() for f in re.split(r'(?<=[.!?])\s+', texto_limpo) if len(f.strip()) > 150]
                
                if frases:
                    if 'simu_questoes' not in st.session_state or st.button("🔄 Novas Questões"):
                        selecionados = random.sample(frases, min(len(frases), 5))
                        st.session_state.simu_questoes = [{"enunciado": gerar_pergunta_contextualizada(f), "item": f} for f in selecionados]
                    
                    for idx, q in enumerate(st.session_state.simu_questoes):
                        st.markdown(f"""<div class="card-duo">
                            <b>QUESTÃO {idx+1:02d}</b><br>
                            <small>{q['enunciado']}</small><br><br>
                            <i>"...{q['item']}..."</i></div>""", unsafe_allow_html=True)
                        resp = st.radio("Avaliação:", ["Selecione", "Certo", "Errado"], key=f"r_{idx}", horizontal=True)
                        if resp != "Selecione":
                            if resp == "Certo": st.success("✅ Correto! O item reflete o material.")
                            else: st.error("❌ Errado. Segundo o material, a afirmação é verdadeira.")
                else:
                    st.warning("Conteúdo insuficiente para gerar simulado robusto.")

    st.markdown("<hr><p style='text-align: center; color: gray;'>Dúvidas: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
