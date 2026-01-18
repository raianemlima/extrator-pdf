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
    
    /* Estatísticas */
    .stat-box {{
        background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
        margin: 0;
    }}
    
    .stat-label {{
        font-size: 0.9rem;
        opacity: 0.95;
        margin-top: 0.5rem;
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
    
    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {COR_VERDE_DUO_HEX};
        color: white;
    }}
    
    /* Expander customizado */
    .streamlit-expanderHeader {{
        background: {COR_FUNDO_CLARO};
        border-radius: 8px;
        font-weight: 600;
    }}
    
    /* Progress bar */
    .stProgress > div > div {{
        background: {COR_VERDE_DUO_HEX};
    }}
    
    /* Responsividade */
    @media (max-width: 768px) {{
        .main {{padding: 0.5rem;}}
        .stat-number {{font-size: 2rem;}}
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
    """
    Análise inteligente de conteúdo jurídico com identificação de temas,
    artigos, jurisprudência e conceitos-chave.
    
    Args:
        texto: Texto do destaque
        
    Returns:
        Dicionário com análise completa
    """
    analise = {
        "tema_principal": None,
        "artigos_citados": [],
        "jurisprudencia": [],
        "palavras_chave": [],
        "nivel_complexidade": "Médio",
        "tipo_conteudo": "Conceitual"
    }
    
    # Identificação de artigos da CF/88 e outras normas
    artigos = re.findall(r'art\.?\s*(\d+[A-Z]?(?:-[A-Z])?)', texto, re.IGNORECASE)
    artigos += re.findall(r'artigo\s*(\d+)', texto, re.IGNORECASE)
    analise["artigos_citados"] = list(set(artigos))
    
    # Identificação de jurisprudência
    if any(word in texto.upper() for word in ['STF', 'STJ', 'TST', 'TSE']):
        analise["jurisprudencia"].append("Tribunais Superiores")
    if 'SÚMULA' in texto.upper() or 'SUMULA' in texto.upper():
        sumulas = re.findall(r'[SsúÚ]umula\s*(\d+)', texto)
        analise["jurisprudencia"].extend([f"Súmula {s}" for s in sumulas])
    
    # Identificação de temas principais (baseado no documento)
    temas_mapa = {
        "CPI": ["cpi", "comissão parlamentar", "inquérito"],
        "Imunidades": ["imunidade", "inviolabilidade", "prerrogativa"],
        "Processo Legislativo": ["processo legislativo", "emenda", "lei complementar"],
        "Poder Executivo": ["presidente", "vice-presidente", "ministro"],
        "Crime de Responsabilidade": ["impeachment", "crime de responsabilidade"],
        "Garantias Parlamentares": ["parlamentar", "deputado", "senador"],
        "Controle": ["fiscalização", "controle", "contas"],
        "Organização": ["congresso nacional", "câmara", "senado"]
    }
    
    texto_lower = texto.lower()
    for tema, palavras in temas_mapa.items():
        if any(palavra in texto_lower for palavra in palavras):
            analise["tema_principal"] = tema
            break
    
    # Extração de palavras-chave (substantivos importantes)
    palavras_importantes = re.findall(r'\b[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+\b', texto)
    counter = Counter(palavras_importantes)
    analise["palavras_chave"] = [p for p, _ in counter.most_common(5)]
    
    # Análise de complexidade baseada em indicadores
    complexidade_alta = sum([
        len(analise["artigos_citados"]) > 3,
        len(analise["jurisprudencia"]) > 0,
        len(texto.split()) > 100,
        bool(re.search(r'(entretanto|todavia|outrossim|destarte)', texto, re.IGNORECASE))
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
    elif any(word in texto.lower() for word in ['exemplo:', 'ex:', 'caso']):
        analise["tipo_conteudo"] = "Prático"
    
    return analise


def limpar_texto_total(texto: str) -> str:
    """
    Limpa e normaliza o texto extraído do PDF.
    
    Args:
        texto: Texto bruto extraído
        
    Returns:
        Texto limpo e normalizado
    """
    if not texto:
        return ""
    
    # Remove números de rodapé colados
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
    """
    Limpa e normaliza o texto extraído do PDF.
    
    Args:
        texto: Texto bruto extraído
        
    Returns:
        Texto limpo e normalizado
    """
    if not texto:
        return ""
    
    # Remove números de rodapé colados
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
    """
    Gera pergunta inteligente baseada no conteúdo E na análise jurídica.
    
    Args:
        texto: Texto do destaque
        analise: Análise prévia do conteúdo
        
    Returns:
        Pergunta contextualizada e específica
    """
    if not analise:
        analise = analisar_conteudo_juridico(texto)
    
    t = texto.lower()
    
    # Perguntas baseadas em temas específicos identificados
    perguntas_tematicas = {
        "CPI": [
            "Quais são os requisitos constitucionais para criação de uma CPI?",
            "Quais poderes investigatórios a CPI possui e quais são seus limites?",
            "Explique a diferença entre CPI federal, estadual e municipal."
        ],
        "Imunidades": [
            "Diferencie imunidade material de imunidade formal dos parlamentares.",
            "A partir de qual momento o parlamentar passa a ter imunidades?",
            "Quais são os limites das imunidades parlamentares?"
        ],
        "Processo Legislativo": [
            "Explique as fases do processo legislativo ordinário.",
            "Qual a diferença entre lei ordinária e lei complementar?",
            "Como funciona o processo de aprovação de emendas constitucionais?"
        ],
        "Crime de Responsabilidade": [
            "Explique o procedimento bifásico do impeachment presidencial.",
            "Qual o papel da Câmara e do Senado no crime de responsabilidade?",
            "Quais são as penas aplicáveis em caso de condenação?"
        ]
    }
    
    # Se tema identificado, usa pergunta específica
    if analise["tema_principal"] and analise["tema_principal"] in perguntas_tematicas:
        return random.choice(perguntas_tematicas[analise["tema_principal"]])
    
    # Perguntas baseadas em artigos citados
    if analise["artigos_citados"]:
        artigo = analise["artigos_citados"][0]
        return f"Qual a importância do art. {artigo} mencionado e como ele se aplica ao tema estudado?"
    
    # Perguntas baseadas em jurisprudência
    if analise["jurisprudencia"]:
        return f"Qual o entendimento jurisprudencial apresentado sobre este tema e qual sua relevância?"
    
    # Pergunta genérica melhorada
    tema = analise["palavras_chave"][0] if analise["palavras_chave"] else "este instituto"
    return f"Explique os aspectos fundamentais sobre {tema} conforme apresentado no material."


def extrair_destaques(pdf_file) -> List[Dict[str, any]]:
    """
    Extrai destaques (highlights) do PDF com análise inteligente.
    
    Args:
        pdf_file: Arquivo PDF carregado
        
    Returns:
        Lista de dicionários com página, texto e análise
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    highlights = []
    
    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8:  # Tipo 8 = Highlight
                texto_extraido = page.get_textbox(annot.rect)
                texto_limpo = limpar_texto_total(texto_extraido)
                
                if texto_limpo:
                    # Análise inteligente do conteúdo
                    analise = analisar_conteudo_juridico(texto_limpo)
                    
                    highlights.append({
                        "pag": page_num + 1,
                        "texto": texto_limpo,
                        "analise": analise,
                        "timestamp": datetime.now()
                    })
    
    return highlights


def gerar_estatisticas(highlights: List[Dict]) -> Dict:
    """
    Gera estatísticas inteligentes sobre o material estudado.
    
    Args:
        highlights: Lista de destaques
        
    Returns:
        Dicionário com estatísticas
    """
    if not highlights:
        return {}
    
    stats = {
        "total_itens": len(highlights),
        "total_palavras": sum(len(h["texto"].split()) for h in highlights),
        "media_palavras": 0,
        "temas": Counter(),
        "complexidade": Counter(),
        "tipos_conteudo": Counter(),
        "artigos_mais_citados": Counter(),
        "paginas_cobertas": len(set(h["pag"] for h in highlights)),
        "tempo_leitura_estimado": 0
    }
    
    # Análise detalhada
    for h in highlights:
        if "analise" in h:
            analise = h["analise"]
            
            if analise["tema_principal"]:
                stats["temas"][analise["tema_principal"]] += 1
            
            stats["complexidade"][analise["nivel_complexidade"]] += 1
            stats["tipos_conteudo"][analise["tipo_conteudo"]] += 1
            
            for artigo in analise["artigos_citados"]:
                stats["artigos_mais_citados"][artigo] += 1
    
    # Cálculos
    stats["media_palavras"] = stats["total_palavras"] // stats["total_itens"] if stats["total_itens"] > 0 else 0
    stats["tempo_leitura_estimado"] = stats["total_palavras"] // 200  # ~200 palavras/minuto
    
    return stats


def renderizar_dashboard_estatisticas(stats: Dict):
    """Renderiza dashboard visual com estatísticas do estudo."""
    if not stats:
        return
    
    st.markdown("### 📊 Dashboard de Análise Inteligente")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-box">
                <p class="stat-number">{stats['total_itens']}</p>
                <p class="stat-label">Pontos de Estudo</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-box">
                <p class="stat-number">{stats['tempo_leitura_estimado']}</p>
                <p class="stat-label">Minutos de Leitura</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-box">
                <p class="stat-number">{stats['paginas_cobertas']}</p>
                <p class="stat-label">Páginas Cobertas</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-box">
                <p class="stat-number">{stats['media_palavras']}</p>
                <p class="stat-label">Palavras/Item</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Análises temáticas
    col_a, col_b = st.columns(2)
    
    with col_a:
        if stats['temas']:
            st.markdown("#### 🎯 Temas Principais")
            for tema, count in stats['temas'].most_common(5):
                porcentagem = (count / stats['total_itens']) * 100
                st.markdown(f"""
                    <div class="card-duo">
                        <strong>{tema}</strong><br>
                        <small>{count} itens ({porcentagem:.1f}%)</small>
                        <div style="background: {COR_VERDE_CLARO}; height: 6px; border-radius: 3px; margin-top: 8px;">
                            <div style="background: {COR_VERDE_DUO_HEX}; height: 6px; width: {porcentagem}%; border-radius: 3px;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    with col_b:
        if stats['complexidade']:
            st.markdown("#### 📈 Distribuição de Complexidade")
            for nivel, count in stats['complexidade'].most_common():
                emoji = {"Alta": "🔥", "Média": "📊", "Básica": "✅"}.get(nivel, "📌")
                st.markdown(f"""
                    <div class="card-duo">
                        {emoji} <strong>{nivel}</strong>: {count} itens
                    </div>
                """, unsafe_allow_html=True)
    
    # Artigos mais citados
    if stats['artigos_mais_citados']:
        st.markdown("#### 📜 Artigos Mais Citados")
        artigos_top = stats['artigos_mais_citados'].most_common(8)
        
        badges_html = " ".join([
            f'<span class="badge-duo">Art. {art} ({count}x)</span>'
            for art, count in artigos_top
        ])
        st.markdown(f'<div>{badges_html}</div>', unsafe_allow_html=True)
    """Cria PDF do resumo formatado."""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(*COR_VERDE_DUO_RGB)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, nome_modulo, ln=True, align='C')
    pdf.ln(25)
    
    # Conteúdo
    for i, h in enumerate(highlights, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*COR_VERDE_DUO_RGB)
        pdf.cell(0, 8, f"ITEM {i:02d} | PÁG. {h['pag']}", ln=True)
        
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(0, 0, 0)
        txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 7, txt_pdf, align='J')
        pdf.ln(4)
    
    return bytes(pdf.output())


def criar_word_resumo(highlights: List[Dict], nome_modulo: str) -> bytes:
    """Cria documento Word do resumo."""
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
    
    # Salvar em buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def criar_pdf_perguntas(highlights: List[Dict]) -> bytes:
    """Cria PDF com roteiro de perguntas e respostas INTELIGENTE."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    for i, h in enumerate(highlights, 1):
        analise = h.get("analise", {})
        
        # Cabeçalho da questão com badges de análise
        pdf.set_fill_color(248, 252, 248)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 90, 60)
        
        header = f"  QUESTAO {i:02d} (Pag. {h['pag']})"
        if analise.get("tema_principal"):
            header += f" - {analise['tema_principal']}"
        
        pdf.cell(190, 8, header.encode('latin-1', 'replace').decode('latin-1'), 
                ln=True, fill=True, border='B')
        
        # Badges de metadados
        pdf.set_font("Helvetica", size=8)
        pdf.set_text_color(120, 120, 120)
        badges = []
        if analise.get("nivel_complexidade"):
            badges.append(f"Nivel: {analise['nivel_complexidade']}")
        if analise.get("tipo_conteudo"):
            badges.append(f"Tipo: {analise['tipo_conteudo']}")
        if badges:
            pdf.cell(190, 5, " | ".join(badges).encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.ln(2)
        
        # Pergunta contextualizada
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pergunta = gerar_pergunta_contextualizada(h['texto'], analise)
        pdf.multi_cell(190, 6, f"PERGUNTA: {pergunta}".encode('latin-1', 'replace').decode('latin-1'), align='L')
        
        # Artigos citados (se houver)
        if analise.get("artigos_citados"):
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            artigos_str = ", ".join([f"Art. {a}" for a in analise["artigos_citados"][:5]])
            pdf.cell(190, 5, f"Base normativa: {artigos_str}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
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
        
        # Dica de estudo
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(80, 120, 80)
        dica = gerar_dica_estudo(analise)
        if dica:
            pdf.ln(2)
            pdf.multi_cell(190, 4, f"Dica: {dica}".encode('latin-1', 'replace').decode('latin-1'))
        
        pdf.ln(6)
    
    return bytes(pdf.output())


def gerar_dica_estudo(analise: Dict) -> str:
    """Gera dicas personalizadas baseadas na análise."""
    dicas = []
    
    if analise.get("nivel_complexidade") == "Alta":
        dicas.append("Revisar este ponto multiplas vezes e criar mapa mental")
    elif analise.get("artigos_citados"):
        dicas.append(f"Memorizar os artigos: {', '.join(analise['artigos_citados'][:3])}")
    
    if analise.get("jurisprudencia"):
        dicas.append("Anotar entendimento jurisprudencial para prova discursiva")
    
    if analise.get("tipo_conteudo") == "Normativo":
        dicas.append("Praticar questoes objetivas sobre este tema")
    
    return " | ".join(dicas) if dicas else "Fazer resumo proprio com suas palavras"


def criar_pdf_flashcards(highlights: List[Dict]) -> bytes:
    """Cria PDF com flashcards para impressão."""
    pdf = FPDF()
    pdf.add_page()
    
    for i, h in enumerate(highlights, 1):
        pdf.set_fill_color(*COR_VERDE_DUO_RGB)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=11)
        txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 8, txt_f, border=1, align='J')
        pdf.ln(5)
    
    return bytes(pdf.output())


def renderizar_cabecalho():
    """Renderiza o cabeçalho profissional da aplicação."""
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
    """Renderiza o rodapé da aplicação."""
    st.markdown("""
        <hr>
        <p style='text-align: center; color: gray; font-size: 0.8em;'>
            Dúvidas: sugestoes@cursosduo.com.br
        </p>
    """, unsafe_allow_html=True)


# ==================== INTERFACE PRINCIPAL ====================

def main():
    """Função principal da aplicação."""
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
            st.warning("⚠️ Nenhum destaque (highlight) encontrado no PDF. Certifique-se de marcar os trechos importantes.")
            return
        
        st.success(f"✅ Pronto! {len(highlights)} pontos de estudo identificados.")
        
        # Abas de conteúdo
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Resumo", "🗂️ Flashcards & P&R", "🧠 Simulado", "🗺️ Mapa Mental"])
        
        with tab1:
            st.markdown('<div class="animated-content">', unsafe_allow_html=True)
            
            # Dashboard de estatísticas
            stats = gerar_estatisticas(highlights)
            renderizar_dashboard_estatisticas(stats)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📄 Resumo Estruturado")
            
            # Filtros inteligentes
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                temas_disponiveis = ["Todos"] + [t for t, _ in stats['temas'].most_common()]
                tema_filtro = st.selectbox("🎯 Filtrar por Tema", temas_disponiveis)
            
            with col_filtro2:
                niveis = ["Todos", "Alta", "Média", "Básica"]
                nivel_filtro = st.selectbox("📊 Nível de Complexidade", niveis)
            
            with col_filtro3:
                ordem = st.selectbox("🔢 Ordenar por", 
                                    ["Página", "Complexidade", "Tamanho"])
            
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
            
            # Prévia com análise
            with st.expander("👁️ Visualizar prévia detalhada", expanded=False):
                for i, h in enumerate(highlights_filtrados[:5], 1):
                    analise = h.get("analise", {})
                    
                    st.markdown(f"""
                        <div class="card-duo">
                            <strong style="color: {COR_VERDE_ESCURO};">
                                Item {i:02d} | Página {h['pag']}
                            </strong>
                    """, unsafe_allow_html=True)
                    
                    # Badges
                    badges = []
                    if analise.get("tema_principal"):
                        badges.append(f"🎯 {analise['tema_principal']}")
                    if analise.get("nivel_complexidade"):
                        emoji_nivel = {"Alta": "🔥", "Média": "📊", "Básica": "✅"}
                        badges.append(f"{emoji_nivel.get(analise['nivel_complexidade'], '📌')} {analise['nivel_complexidade']}")
                    
                    if badges:
                        st.markdown(" • ".join(badges))
                    
                    st.write(h['texto'][:300] + "..." if len(h['texto']) > 300 else h['texto'])
                    
                    # Artigos citados
                    if analise.get("artigos_citados"):
                        artigos_badges = " ".join([
                            f'<span class="badge-duo">Art. {a}</span>' 
                            for a in analise["artigos_citados"][:5]
                        ])
                        st.markdown(artigos_badges, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.divider()
                
                if len(highlights_filtrados) > 5:
                    st.caption(f"...e mais {len(highlights_filtrados) - 5} itens")
            
            # Downloads
            st.markdown("### 💾 Downloads")
            col1, col2 = st.columns(2)
            
            with col1:
                pdf_resumo = criar_pdf_resumo(highlights_filtrados, nome_modulo)
                st.download_button(
                    "📥 Baixar PDF Resumo",
                    pdf_resumo,
                    f"Resumo_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            
            with col2:
                word_resumo = criar_word_resumo(highlights_filtrados, nome_modulo)
                st.download_button(
                    "📥 Baixar Word Resumo",
                    word_resumo,
                    f"Resumo_{nome_modulo.replace(' ', '_')}.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Material de Revisão Ativa")
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                pdf_perguntas = criar_pdf_perguntas(highlights)
                st.download_button(
                    "📝 Baixar Roteiro P&R",
                    pdf_perguntas,
                    f"Roteiro_PR_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf"
                )
            
            with col_y:
                pdf_flashcards = criar_pdf_flashcards(highlights)
                st.download_button(
                    "✂️ Baixar Flashcards",
                    pdf_flashcards,
                    f"Flashcards_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf"
                )
        
        with tab3:
            st.markdown('<div class="animated-content">', unsafe_allow_html=True)
            st.subheader("🧠 Simulado Inteligente Certo ou Errado")
            
            # Configurações do simulado
            col_config1, col_config2 = st.columns(2)
            
            with col_config1:
                num_questoes = st.slider("Número de questões", 3, min(15, len(highlights)), 5)
            
            with col_config2:
                filtro_nivel = st.selectbox(
                    "Filtrar por nível",
                    ["Todos", "Alta", "Média", "Básica"],
                    key="filtro_simulado"
                )
            
            # Filtrar por complexidade se solicitado
            pool_questoes = highlights.copy()
            if filtro_nivel != "Todos":
                pool_questoes = [h for h in pool_questoes 
                                if h.get("analise", {}).get("nivel_complexidade") == filtro_nivel]
            
            if len(pool_questoes) < num_questoes:
                st.warning(f"⚠️ Apenas {len(pool_questoes)} questões disponíveis com este filtro.")
                num_questoes = len(pool_questoes)
            
            # Gerar questões
            if num_questoes > 0:
                # Inicializar estado da sessão
                if 'simulado_atual' not in st.session_state or st.button("🔄 Gerar Novo Simulado"):
                    st.session_state.simulado_atual = random.sample(pool_questoes, num_questoes)
                    st.session_state.respostas_simulado = {}
                    st.session_state.gabarito_revelado = False
                
                amostra = st.session_state.simulado_atual
                
                # Questões
                acertos = 0
                total_respondidas = 0
                
                for idx, item in enumerate(amostra):
                    analise = item.get("analise", {})
                    
                    st.markdown(f"""
                        <div class="card-duo">
                            <strong style="color: {COR_VERDE_ESCURO};">
                                Questão {idx+1} de {len(amostra)}
                            </strong> • Página {item['pag']}
                    """, unsafe_allow_html=True)
                    
                    # Badge de complexidade
                    if analise.get("nivel_complexidade"):
                        emoji_nivel = {"Alta": "🔥", "Média": "📊", "Básica": "✅"}
                        nivel = analise["nivel_complexidade"]
                        st.markdown(f'<span class="badge-duo">{emoji_nivel.get(nivel, "📌")} {nivel}</span>', 
                                  unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.info(item['texto'])
                    
                    # Resposta
                    resp = st.radio(
                        f"Sua avaliação:",
                        ["Selecione", "Certo", "Errado"],
                        key=f"qz_{idx}",
                        horizontal=True
                    )
                    
                    if resp != "Selecione":
                        total_respondidas += 1
                        st.session_state.respostas_simulado[idx] = resp
                        
                        if st.session_state.get('gabarito_revelado', False):
                            if resp == "Certo":
                                st.success("✅ Correto! Afirmação condizente com o material.")
                                acertos += 1
                            else:
                                st.error("❌ Errado. De acordo com o material, a afirmação está correta.")
                                
                                # Dica de revisão
                                if analise.get("artigos_citados"):
                                    st.info(f"💡 Revise os artigos: {', '.join(analise['artigos_citados'][:3])}")
                    
                    st.divider()
                
                # Botão para revelar gabarito
                if total_respondidas > 0 and not st.session_state.get('gabarito_revelado', False):
                    if st.button("📊 Revelar Gabarito e Ver Desempenho", type="primary"):
                        st.session_state.gabarito_revelado = True
                        st.rerun()
                
                # Estatísticas finais
                if st.session_state.get('gabarito_revelado', False) and total_respondidas > 0:
                    st.markdown("### 🎯 Resultado do Simulado")
                    
                    # Contar acertos após revelação
                    acertos_final = sum(1 for resp in st.session_state.respostas_simulado.values() if resp == "Certo")
                    percentual = (acertos_final / total_respondidas) * 100
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    
                    with col_res1:
                        st.markdown(f"""
                            <div class="stat-box">
                                <p class="stat-number">{acertos_final}/{total_respondidas}</p>
                                <p class="stat-label">Acertos</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_res2:
                        st.markdown(f"""
                            <div class="stat-box">
                                <p class="stat-number">{percentual:.1f}%</p>
                                <p class="stat-label">Aproveitamento</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_res3:
                        emoji_desempenho = "🏆" if percentual >= 80 else "📈" if percentual >= 60 else "📚"
                        status = "Excelente!" if percentual >= 80 else "Bom!" if percentual >= 60 else "Revisar"
                        st.markdown(f"""
                            <div class="stat-box">
                                <p class="stat-number">{emoji_desempenho}</p>
                                <p class="stat-label">{status}</p>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="animated-content">', unsafe_allow_html=True)
            st.subheader("🗺️ Mapa Mental Interativo")
            
            st.info("📌 Visualização hierárquica dos temas estudados com conexões lógicas")
            
            # Gerar estrutura do mapa mental
            stats = gerar_estatisticas(highlights)
            
            if stats.get('temas'):
                # Criar estrutura de dados para mapa mental
                mapa_data = {
                    "nome": nome_modulo,
                    "filhos": []
                }
                
                for tema, count in stats['temas'].most_common():
                    # Itens deste tema
                    itens_tema = [h for h in highlights 
                                 if h.get("analise", {}).get("tema_principal") == tema]
                    
                    tema_node = {
                        "nome": f"{tema} ({count})",
                        "artigos": [],
                        "complexidade": Counter()
                    }
                    
                    # Coletar artigos e complexidade
                    for item in itens_tema:
                        analise = item.get("analise", {})
                        if analise.get("artigos_citados"):
                            tema_node["artigos"].extend(analise["artigos_citados"])
                        if analise.get("nivel_complexidade"):
                            tema_node["complexidade"][analise["nivel_complexidade"]] += 1
                    
                    mapa_data["filhos"].append(tema_node)
                
                # Renderizar mapa mental em HTML
                col_mapa1, col_mapa2 = st.columns([2, 1])
                
                with col_mapa1:
                    st.markdown("### 📊 Estrutura Hierárquica")
                    
                    # Renderizar árvore
                    st.markdown(f"""
                        <div class="card-duo" style="background: linear-gradient(135deg, {COR_FUNDO_CLARO} 0%, white 100%);">
                            <h3 style="color: {COR_VERDE_ESCURO}; margin-top: 0;">
                                📚 {mapa_data['nome']}
                            </h3>
                    """, unsafe_allow_html=True)
                    
                    for tema_node in mapa_data["filhos"]:
                        # Calcular cor baseada na complexidade dominante
                        complexidade_dom = tema_node["complexidade"].most_common(1)
                        cor_badge = COR_VERDE_DUO_HEX
                        
                        if complexidade_dom:
                            nivel = complexidade_dom[0][0]
                            if nivel == "Alta":
                                cor_badge = "#E74C3C"
                            elif nivel == "Média":
                                cor_badge = "#F39C12"
                            else:
                                cor_badge = "#27AE60"
                        
                        st.markdown(f"""
                            <div style="margin-left: 2rem; margin-bottom: 1.5rem; 
                                        border-left: 3px solid {cor_badge}; padding-left: 1rem;">
                                <h4 style="color: {COR_VERDE_ESCURO}; margin: 0.5rem 0;">
                                    🎯 {tema_node['nome']}
                                </h4>
                        """, unsafe_allow_html=True)
                        
                        # Artigos relacionados
                        if tema_node["artigos"]:
                            artigos_unicos = list(set(tema_node["artigos"]))[:6]
                            badges_artigos = " ".join([
                                f'<span class="badge-duo">Art. {a}</span>' 
                                for a in artigos_unicos
                            ])
                            st.markdown(f"<div style='margin-top: 0.5rem;'>{badges_artigos}</div>", 
                                      unsafe_allow_html=True)
                        
                        # Distribuição de complexidade
                        if tema_node["complexidade"]:
                            distrib = " • ".join([
                                f"{nivel}: {count}" 
                                for nivel, count in tema_node["complexidade"].most_common()
                            ])
                            st.markdown(f"<small style='color: #666;'>📊 {distrib}</small>", 
                                      unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_mapa2:
                    st.markdown("### 🎨 Legenda")
                    
                    st.markdown(f"""
                        <div class="card-duo">
                            <p><strong>Níveis de Complexidade:</strong></p>
                            <p>🔥 <span style="color: #E74C3C;">■</span> Alta</p>
                            <p>📊 <span style="color: #F39C12;">■</span> Média</p>
                            <p>✅ <span style="color: #27AE60;">■</span> Básica</p>
                            <br>
                            <p><strong>Dicas de Uso:</strong></p>
                            <ul style="font-size: 0.9rem; line-height: 1.8;">
                                <li>Revise temas com mais itens primeiro</li>
                                <li>Foque em temas de alta complexidade</li>
                                <li>Memorize artigos relacionados</li>
                                <li>Crie conexões entre temas</li>
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Botão para exportar mapa mental
                st.markdown("### 💾 Exportar Mapa Mental")
                
                # Criar versão texto do mapa mental
                mapa_texto = f"MAPA MENTAL - {nome_modulo}\n{'='*60}\n\n"
                for tema_node in mapa_data["filhos"]:
                    mapa_texto += f"🎯 {tema_node['nome']}\n"
                    if tema_node["artigos"]:
                        artigos_str = ", ".join(list(set(tema_node["artigos"]))[:10])
                        mapa_texto += f"   📜 Artigos: {artigos_str}\n"
                    if tema_node["complexidade"]:
                        for nivel, count in tema_node["complexidade"].most_common():
                            mapa_texto += f"   📊 {nivel}: {count} itens\n"
                    mapa_texto += "\n"
                
                st.download_button(
                    "📥 Baixar Mapa Mental (TXT)",
                    mapa_texto.encode('utf-8'),
                    f"Mapa_Mental_{nome_modulo.replace(' ', '_')}.txt",
                    "text/plain",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ Não há temas suficientes para gerar o mapa mental. Adicione mais destaques.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Erro no processamento: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
