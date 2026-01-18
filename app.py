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
from typing import List, Dict, Tuple
from collections import Counter

# Constantes - Identidade Visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138)
COR_VERDE_DUO_HEX = "#A6C98A"
COR_VERDE_ESCURO = "#7A9B6E"
COR_VERDE_CLARO = "#D4E7C5"
COR_TEXTO_ESCURO = "#2C3E50"
COR_FUNDO_CLARO = "#F8FCF8"

# Configuração da página
st.set_page_config(
    page_title="Resumo Inteligente - Duo",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS customizado avançado - Identidade Visual Profissional
st.markdown(f"""
    <style>
    /* Fonte e cores base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {COR_TEXTO_ESCURO};
    }}
    
    /* Container principal */
    .main {{
        padding: 1.5rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #f8fcf8 100%);
    }}
    
    /* Cards customizados */
    .card-duo {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid {COR_VERDE_DUO_HEX};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: transform 0.2s;
    }}
    
    .card-duo:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }}
    
    /* Badges e tags */
    .badge-duo {{
        background: {COR_VERDE_CLARO};
        color: {COR_VERDE_ESCURO};
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
    }}
    
    /* Botões customizados */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }}
    
    .stDownloadButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(166, 201, 138, 0.4);
    }}
    
    /* Responsividade */
    @media (max-width: 768px) {{
        .main {{padding: 0.5rem;}}
        .card-duo {{padding: 1rem;}}
    }}
    
    /* Animações */
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .animated-content {{
        animation: slideIn 0.5s ease-out;
    }}
    </style>
""", unsafe_allow_html=True)


def analisar_conteudo_juridico(texto: str) -> Dict[str, any]:
    """Análise inteligente de conteúdo jurídico."""
    analise = {
        "tema_principal": None,
        "artigos_citados": [],
        "jurisprudencia": [],
        "palavras_chave": [],
        "nivel_complexidade": "Média",
        "tipo_conteudo": "Conceitual"
    }
    
    # Identificação de artigos
    artigos = re.findall(r'art\.?\s*(\d+[A-Z]?(?:-[A-Z])?)', texto, re.IGNORECASE)
    artigos += re.findall(r'artigo\s*(\d+)', texto, re.IGNORECASE)
    analise["artigos_citados"] = list(set(artigos))
    
    # Identificação de jurisprudência
    if any(word in texto.upper() for word in ['STF', 'STJ', 'TST', 'TSE']):
        analise["jurisprudencia"].append("Tribunais Superiores")
    if 'SÚMULA' in texto.upper() or 'SUMULA' in texto.upper():
        sumulas = re.findall(r'[SsúÚ]umula\s*(\d+)', texto)
        analise["jurisprudencia"].extend([f"Súmula {s}" for s in sumulas])
    
    # Identificação de temas
    temas_mapa = {
        "CPI": ["cpi", "comissão parlamentar", "inquérito"],
        "Imunidades": ["imunidade", "inviolabilidade", "prerrogativa"],
        "Processo Legislativo": ["processo legislativo", "emenda", "lei complementar"],
        "Poder Executivo": ["presidente", "vice-presidente", "ministro"],
        "Crime de Responsabilidade": ["impeachment", "crime de responsabilidade"],
        "Garantias Parlamentares": ["parlamentar", "deputado", "senador"],
    }
    
    texto_lower = texto.lower()
    for tema, palavras in temas_mapa.items():
        if any(palavra in texto_lower for palavra in palavras):
            analise["tema_principal"] = tema
            break
    
    # Análise de complexidade
    complexidade_alta = sum([
        len(analise["artigos_citados"]) > 3,
        len(analise["jurisprudencia"]) > 0,
        len(texto.split()) > 100,
    ])
    
    if complexidade_alta >= 3:
        analise["nivel_complexidade"] = "Alta"
    elif complexidade_alta >= 1:
        analise["nivel_complexidade"] = "Média"
    else:
        analise["nivel_complexidade"] = "Básica"
    
    # Tipo de conteúdo
    if analise["jurisprudencia"]:
        analise["tipo_conteudo"] = "Jurisprudencial"
    elif analise["artigos_citados"]:
        analise["tipo_conteudo"] = "Normativo"
    
    return analise


def limpar_texto_total(texto: str) -> str:
    """Limpa e normaliza o texto extraído do PDF."""
    if not texto:
        return ""
    
    # Remove números de rodapé
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    # Mapeamento de caracteres especiais
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '? ': '- '
    }
    
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    
    return " ".join(texto.split())


def gerar_pergunta_contextualizada(texto: str, analise: Dict = None) -> str:
    """Gera pergunta inteligente baseada no conteúdo."""
    if not analise:
        analise = analisar_conteudo_juridico(texto)
    
    perguntas_tematicas = {
        "CPI": "Quais são os requisitos constitucionais para criação de uma CPI?",
        "Imunidades": "Diferencie imunidade material de imunidade formal dos parlamentares.",
        "Processo Legislativo": "Explique as fases do processo legislativo ordinário.",
        "Crime de Responsabilidade": "Explique o procedimento bifásico do impeachment presidencial.",
    }
    
    if analise["tema_principal"] and analise["tema_principal"] in perguntas_tematicas:
        return perguntas_tematicas[analise["tema_principal"]]
    
    if analise["artigos_citados"]:
        artigo = analise["artigos_citados"][0]
        return f"Qual a importância do art. {artigo} e como ele se aplica ao tema estudado?"
    
    return "Explique os aspectos fundamentais apresentados no material."


def extrair_destaques(pdf_file) -> List[Dict[str, any]]:
    """Extrai destaques do PDF com análise inteligente."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    highlights = []
    
    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8:
                texto_extraido = page.get_textbox(annot.rect)
                texto_limpo = limpar_texto_total(texto_extraido)
                
                if texto_limpo:
                    analise = analisar_conteudo_juridico(texto_limpo)
                    
                    highlights.append({
                        "pag": page_num + 1,
                        "texto": texto_limpo,
                        "analise": analise,
                        "timestamp": datetime.now()
                    })
    
    return highlights


def gerar_estatisticas(highlights: List[Dict]) -> Dict:
    """Gera estatísticas sobre o material."""
    if not highlights:
        return {}
    
    stats = {
        "total_itens": len(highlights),
        "temas": Counter(),
        "complexidade": Counter(),
        "tipos_conteudo": Counter(),
        "artigos_mais_citados": Counter(),
    }
    
    for h in highlights:
        if "analise" in h:
            analise = h["analise"]
            
            if analise["tema_principal"]:
                stats["temas"][analise["tema_principal"]] += 1
            
            stats["complexidade"][analise["nivel_complexidade"]] += 1
            stats["tipos_conteudo"][analise["tipo_conteudo"]] += 1
            
            for artigo in analise["artigos_citados"]:
                stats["artigos_mais_citados"][artigo] += 1
    
    return stats


def criar_pdf_resumo(highlights: List[Dict], nome_modulo: str) -> bytes:
    """Cria PDF do resumo."""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(*COR_VERDE_DUO_RGB)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, nome_modulo.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.ln(25)
    
    # Conteúdo
    for i, h in enumerate(highlights, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*COR_VERDE_DUO_RGB)
        pdf.cell(0, 8, f"ITEM {i:02d} | PAG. {h['pag']}", ln=True)
        
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(0, 0, 0)
        txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 7, txt_pdf, align='J')
        pdf.ln(4)
    
    return bytes(pdf.output())


def criar_word_resumo(highlights: List[Dict], nome_modulo: str) -> bytes:
    """Cria documento Word."""
    doc = Document()
    
    # Título
    h_titulo = doc.add_heading(level=0)
    run_titulo = h_titulo.add_run("RESUMO INTELIGENTE")
    run_titulo.font.color.rgb = RGBColor(*COR_VERDE_DUO_RGB)
    
    p_modulo = doc.add_paragraph()
    run_modulo = p_modulo.add_run(nome_modulo)
    run_modulo.bold = True
    
    # Conteúdo
    for i, h in enumerate(highlights, 1):
        p = doc.add_paragraph()
        
        rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
        rt.bold = True
        rt.font.color.rgb = RGBColor(*COR_VERDE_DUO_RGB)
        
        rtx = p.add_run(h['texto'])
        rtx.font.name = 'Arial'
        rtx.font.size = Pt(12)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def criar_pdf_perguntas(highlights: List[Dict]) -> bytes:
    """Cria PDF com perguntas e respostas."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    for i, h in enumerate(highlights, 1):
        analise = h.get("analise", {})
        
        # Cabeçalho
        pdf.set_fill_color(248, 252, 248)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 90, 60)
        
        header = f"  QUESTAO {i:02d} (Pag. {h['pag']})"
        if analise.get("tema_principal"):
            header += f" - {analise['tema_principal']}"
        
        pdf.cell(190, 8, header.encode('latin-1', 'replace').decode('latin-1'), 
                ln=True, fill=True, border='B')
        
        pdf.ln(2)
        
        # Pergunta
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pergunta = gerar_pergunta_contextualizada(h['texto'], analise)
        pdf.multi_cell(190, 6, f"PERGUNTA: {pergunta}".encode('latin-1', 'replace').decode('latin-1'), align='L')
        
        pdf.ln(1)
        
        # Resposta
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*COR_VERDE_DUO_RGB)
        pdf.cell(190, 6, "RESPOSTA DO MATERIAL:", ln=True)
        
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(20, 20, 20)
        txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.set_draw_color(*COR_VERDE_DUO_RGB)
        pdf.multi_cell(190, 5, txt_pr, align='J', border='L')
        pdf.ln(6)
    
    return bytes(pdf.output())


def criar_pdf_flashcards(highlights: List[Dict]) -> bytes:
    """Cria PDF com flashcards."""
    pdf = FPDF()
    pdf.add_page()
    
    for i, h in enumerate(highlights, 1):
        pdf.set_fill_color(*COR_VERDE_DUO_RGB)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, f" CARTAO {i:02d} | PAGINA {h['pag']}", border=1, ln=True, fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=11)
        txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 8, txt_f, border=1, align='J')
        pdf.ln(5)
    
    return bytes(pdf.output())


def renderizar_cabecalho():
    """Renderiza o cabeçalho."""
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%); 
                    padding: 2rem 1.5rem; border-radius: 15px; text-align: center; 
                    margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h1 style="color: white; margin: 0; font-family: 'Inter', sans-serif; 
                       font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px;">
                RESUMO INTELIGENTE
            </h1>
            <p style="color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; 
                      font-weight: 600; font-size: 1.1rem;">
                Cursos Duo
            </p>
        </div>
    """, unsafe_allow_html=True)


def renderizar_rodape():
    """Renderiza o rodapé."""
    st.markdown("""
        <hr>
        <p style='text-align: center; color: gray; font-size: 0.8em;'>
            Dúvidas: sugestoes@cursosduo.com.br
        </p>
    """, unsafe_allow_html=True)


def main():
    """Função principal."""
    renderizar_cabecalho()
    
    # Upload e configuração
    uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
    nome_modulo = st.text_input("Identificação do Material", value="Revisão Ponto 6")
    
    if uploaded_file is None:
        st.info("👆 Faça upload de um PDF com destaques (highlights) para começar.")
        return
    
    try:
        # Extração de destaques
        with st.spinner("Extraindo destaques do PDF..."):
            highlights = extrair_destaques(uploaded_file)
        
        if not highlights:
            st.warning("⚠️ Nenhum destaque encontrado. Marque os trechos importantes.")
            return
        
        st.success(f"✅ {len(highlights)} pontos de estudo identificados.")
        
        # Abas
        tab1, tab2, tab3 = st.tabs(["📄 Resumo", "🗂️ Flashcards & P&R", "🧠 Simulado"])
        
        with tab1:
            st.subheader("📄 Resumo Estruturado")
            
            # Filtros
            stats = gerar_estatisticas(highlights)
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                temas_disponiveis = ["Todos"] + [t for t, _ in stats['temas'].most_common()]
                tema_filtro = st.selectbox("🎯 Filtrar por Tema", temas_disponiveis)
            
            with col_filtro2:
                niveis = ["Todos", "Alta", "Média", "Básica"]
                nivel_filtro = st.selectbox("📊 Nível", niveis)
            
            with col_filtro3:
                ordem = st.selectbox("🔢 Ordenar", ["Página", "Complexidade", "Tamanho"])
            
            # Aplicar filtros
            highlights_filtrados = highlights.copy()
            
            if tema_filtro != "Todos":
                highlights_filtrados = [h for h in highlights_filtrados 
                                       if h.get("analise", {}).get("tema_principal") == tema_filtro]
            
            if nivel_filtro != "Todos":
                highlights_filtrados = [h for h in highlights_filtrados 
                                       if h.get("analise", {}).get("nivel_complexidade") == nivel_filtro]
            
            # Ordenação
            if ordem == "Complexidade":
                ordem_complexidade = {"Alta": 3, "Média": 2, "Básica": 1}
                highlights_filtrados.sort(
                    key=lambda x: ordem_complexidade.get(
                        x.get("analise", {}).get("nivel_complexidade", "Média"), 2
                    ), reverse=True
                )
            elif ordem == "Tamanho":
                highlights_filtrados.sort(key=lambda x: len(x["texto"]), reverse=True)
            
            st.info(f"📌 Exibindo {len(highlights_filtrados)} de {len(highlights)} itens")
            
            # Prévia
            with st.expander("👁️ Visualizar prévia", expanded=False):
                for i, h in enumerate(highlights_filtrados[:5], 1):
                    st.markdown(f"**Item {i:02d} | Página {h['pag']}**")
                    st.write(h['texto'][:200] + "..." if len(h['texto']) > 200 else h['texto'])
                    st.divider()
                if len(highlights_filtrados) > 5:
                    st.caption(f"...e mais {len(highlights_filtrados) - 5} itens")
            
            # Downloads
            col1, col2 = st.columns(2)
            
            with col1:
                pdf_resumo = criar_pdf_resumo(highlights_filtrados, nome_modulo)
                st.download_button(
                    "📥 Baixar PDF",
                    pdf_resumo,
                    f"Resumo_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            
            with col2:
                word_resumo = criar_word_resumo(highlights_filtrados, nome_modulo)
                st.download_button(
                    "📥 Baixar Word",
                    word_resumo,
                    f"Resumo_{nome_modulo.replace(' ', '_')}.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        
        with tab2:
            st.subheader("🗂️ Material de Revisão")
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                pdf_perguntas = criar_pdf_perguntas(highlights)
                st.download_button(
                    "📝 Roteiro P&R",
                    pdf_perguntas,
                    f"Roteiro_PR_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            
            with col_y:
                pdf_flashcards = criar_pdf_flashcards(highlights)
                st.download_button(
                    "✂️ Flashcards",
                    pdf_flashcards,
                    f"Flashcards_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
        
        with tab3:
            st.subheader("🧠 Simulado Certo ou Errado")
            
            num_questoes = min(len(highlights), 5)
            
            if 'simulado_atual' not in st.session_state or st.button("🔄 Novo Simulado"):
                st.session_state.simulado_atual = random.sample(highlights, num_questoes)
                st.session_state.respostas_simulado = {}
            
            amostra = st.session_state.simulado_atual
            
            for idx, item in enumerate(amostra):
                st.markdown(f"**Questão {idx+1}** (Página {item['pag']})")
                st.info(item['texto'])
                
                resp = st.radio(
                    "Sua avaliação:",
                    ["Selecione", "Certo", "Errado"],
                    key=f"qz_{idx}",
                    horizontal=True
                )
                
                if resp != "Selecione":
                    if resp == "Certo":
                        st.success("✅ Correto!")
                    else:
                        st.error("❌ Errado. A afirmação está correta.")
                
                st.divider()
        
        renderizar_rodape()
    
    except Exception as e:
        st.error(f"❌ Erro no processamento: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
