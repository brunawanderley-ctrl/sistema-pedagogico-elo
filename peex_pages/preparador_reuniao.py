#!/usr/bin/env python3
"""
PREPARADOR DE REUNIAO — Redesenhado com roteiros da Sintese Final.

Auto-detecta formato correto (FLASH/FOCO/CRISE/ESTRATEGICA).
Mostra roteiro minuto-a-minuto com falas sugeridas.
CEO: roteiro completo + script + export.
Diretor: sua unidade + como abordar coordenadores.
Coordenador: preview do que sera discutido.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, get_user_unit, ROLE_CEO, ROLE_DIRETOR
from utils import WRITABLE_DIR, UNIDADES_NOMES, calcular_semana_letiva
from peex_config import (
    FORMATOS_REUNIAO, DIFERENCIACAO_UNIDADE, ROTEIROS,
    detectar_formato_reuniao,
)
from peex_utils import info_semana, proximas_reunioes


# ========== CARREGAR DADOS ==========

def _carregar_json(nome):
    """Carrega JSON pre-gerado do WRITABLE_DIR."""
    path = WRITABLE_DIR / nome
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


# ========== CSS ==========
st.markdown("""
<style>
    .reuniao-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white; padding: 24px; border-radius: 12px; margin-bottom: 20px;
    }
    .reuniao-header h2 { color: white !important; border: none !important; margin: 0; }
    .reuniao-header p { margin: 5px 0; opacity: 0.9; }
    .formato-badge {
        display: inline-block; padding: 6px 16px; border-radius: 20px;
        font-weight: bold; font-size: 0.95em; color: white; margin: 4px 0;
    }
    .bloco-roteiro {
        border-left: 4px solid; padding: 16px 20px; margin: 10px 0;
        border-radius: 0 8px 8px 0; background: #f8f9fa;
    }
    .bloco-tempo {
        font-size: 0.8em; color: #666; font-weight: bold;
        text-transform: uppercase; margin-bottom: 4px;
    }
    .bloco-nome { font-size: 1.1em; font-weight: bold; margin-bottom: 8px; }
    .bloco-script {
        font-style: italic; background: white; padding: 10px 14px;
        border-radius: 6px; border: 1px solid #e0e0e0; margin: 8px 0;
        line-height: 1.6;
    }
    .bloco-pagina {
        font-size: 0.8em; color: #1565C0; margin-top: 6px;
    }
    .saida-obrigatoria {
        background: #FFF3E0; border: 2px solid #FF9800; padding: 16px;
        border-radius: 8px; margin: 16px 0;
    }
    .saida-obrigatoria strong { color: #E65100; }
    .protocolo-unidade {
        background: #FCE4EC; border-left: 4px solid #C62828;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 6px 6px 0;
    }
    .ponto-critico {
        background: #FFF3E0; border-left: 3px solid #FF9800;
        padding: 12px; margin: 8px 0; border-radius: 0 6px 6px 0;
    }
    .ponto-positivo {
        background: #E8F5E9; border-left: 3px solid #4CAF50;
        padding: 12px; margin: 8px 0; border-radius: 0 6px 6px 0;
    }
    .prep-item {
        background: #E3F2FD; padding: 12px; border-radius: 8px; margin: 6px 0;
    }
    .cinco-porques {
        background: #F3E5F5; border: 2px solid #7B1FA2; padding: 16px;
        border-radius: 8px; margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)


# ========== PAGINA ==========

role = get_user_role()
user_unit = get_user_unit()
semana = calcular_semana_letiva()

st.title("Preparador de Reuniao")

# Dados
preparador = _carregar_json("preparador_output.json")
conselheiro = _carregar_json("conselheiro_output.json")
comparador = _carregar_json("comparador_output.json")
missoes_data = _carregar_json("missoes_pregeradas.json")
preditor_data = _carregar_json("preditor_output.json")
info = info_semana(semana)
prox_reunioes = proximas_reunioes(semana, n=5)

import pandas as pd
from utils import DATA_DIR
resumo_path = DATA_DIR / "resumo_Executivo.csv"
resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()

# ========== DETECTAR FORMATO ==========

prox = info.get('proxima_reuniao', {})
formato_calendario = info.get('formato_reuniao', {})

# Auto-detectar formato baseado nos dados (nao so calendario)
missoes_rede = missoes_data.get('unidades', {})
formato_detectado = detectar_formato_reuniao(missoes_rede, resumo_df, semana)

# Pegar formato do calendario
formato_cal = formato_calendario.get('nome', 'FLASH') if formato_calendario else 'FLASH'

# Usar o mais severo entre calendario e detectado
_SEVERIDADE = {'FLASH': 0, 'FOCO': 1, 'CRISE': 2, 'ESTRATEGICA': 3}
if _SEVERIDADE.get(formato_detectado, 0) > _SEVERIDADE.get(formato_cal, 0):
    formato_final = formato_detectado
    formato_override = True
else:
    formato_final = formato_cal
    formato_override = False

roteiro = ROTEIROS.get(formato_final, ROTEIROS.get('FLASH'))
formato_info = {
    'FLASH': {'cor': '#43A047', 'icone': '⚡'},
    'FOCO': {'cor': '#FFA000', 'icone': '🔍'},
    'CRISE': {'cor': '#C62828', 'icone': '🚨'},
    'ESTRATEGICA': {'cor': '#1565C0', 'icone': '🎯'},
}.get(formato_final, {'cor': '#607D8B', 'icone': '📅'})


# ========== HEADER ==========

if prox:
    override_msg = ""
    if formato_override:
        override_msg = f" (elevado de {formato_cal} para {formato_final} pelos indicadores)"

    st.markdown(f"""
    <div class="reuniao-header">
        <h2>{formato_info['icone']} {prox.get('titulo', 'Reuniao da Semana')}</h2>
        <p><strong>Semana {prox.get('semana', semana)}</strong> | {prox.get('cod', '')} |
           {prox.get('tipo_reuniao', 'RU')}</p>
        <p><span class="formato-badge" style="background:{formato_info['cor']};">
            {formato_info['icone']} {formato_final} ({roteiro['duracao']})
        </span>{override_msg}</p>
        <p>Foco: {prox.get('foco', '')}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Nenhuma reuniao programada para esta semana.")


# ========== SAIDA OBRIGATORIA ==========

st.markdown(f"""
<div class="saida-obrigatoria">
    <strong>Saida Obrigatoria:</strong> {roteiro['saida_obrigatoria']}
</div>
""", unsafe_allow_html=True)


# ========== VISAO CEO ==========

if role == ROLE_CEO:

    # Objetivo
    if preparador.get('objetivo_da_reuniao'):
        st.subheader("Objetivo da Reuniao")
        st.markdown(f"**{preparador['objetivo_da_reuniao']}**")
    elif prox:
        st.subheader("Objetivo da Reuniao")
        st.markdown(f"**{prox.get('foco', 'Acompanhamento semanal.')}**")

    # Preparacao CEO
    prep_ceo = preparador.get('preparacao_ceo', {})
    if prep_ceo:
        st.subheader("Preparacao")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Antes da reuniao:**")
            for item in prep_ceo.get('antes_da_reuniao', []):
                st.markdown(f"- {item}")
        with col_b:
            st.markdown("**O que levar:**")
            for item in prep_ceo.get('o_que_levar', []):
                st.markdown(f"- {item}")
        if prep_ceo.get('tom_recomendado'):
            st.info(f"Tom recomendado: {prep_ceo['tom_recomendado']}")

    # ========== ROTEIRO MINUTO-A-MINUTO ==========

    st.subheader(f"Roteiro {formato_final} — Minuto a Minuto")
    st.caption(f"Quando usar: {roteiro['quando']}")

    cores_blocos = ['#8D6E63', '#5D4037', '#4CAF50', '#FF9800', '#2196F3', '#9C27B0']

    for i, bloco in enumerate(roteiro['blocos']):
        cor = cores_blocos[i % len(cores_blocos)]
        pagina_link = ""
        if bloco.get('pagina'):
            pagina_link = f'<div class="bloco-pagina">Dados: pagina {bloco["pagina"]}</div>'

        st.markdown(f"""
        <div class="bloco-roteiro" style="border-color: {cor};">
            <div class="bloco-tempo">{bloco['tempo']}</div>
            <div class="bloco-nome" style="color: {cor};">{bloco['nome']}</div>
            <div class="bloco-script">"{bloco['script']}"</div>
            {pagina_link}
        </div>
        """, unsafe_allow_html=True)

        # Dados inline para blocos de dados (Ato 2 / Solo)
        if bloco['nome'] in ('Numeros-chave', 'Dados Criticos', 'Diagnostico', 'Balanco Completo'):
            if not resumo_df.empty:
                dados_cols = st.columns(4)
                for j, un_code in enumerate(['BV', 'CD', 'JG', 'CDR']):
                    row = resumo_df[resumo_df['unidade'] == un_code]
                    if not row.empty:
                        r = row.iloc[0]
                        conf = r.get('pct_conformidade_media', 0)
                        with dados_cols[j]:
                            st.metric(
                                UNIDADES_NOMES.get(un_code, un_code),
                                f"{conf:.0f}%",
                            )

    # ========== PROTOCOLOS DE CRISE POR UNIDADE ==========

    if formato_final == 'CRISE' and 'protocolos_unidade' in roteiro:
        st.subheader("Protocolos de Crise por Unidade")
        for un_code, protocolo in roteiro['protocolos_unidade'].items():
            un_nome = UNIDADES_NOMES.get(un_code, un_code)
            st.markdown(f"""
            <div class="protocolo-unidade">
                <strong>{un_nome}:</strong> {protocolo}
            </div>
            """, unsafe_allow_html=True)

        # Workflow 5 Porques (interativo)
        st.markdown("""
        <div class="cinco-porques">
            <strong>Workflow: 5 Porques</strong>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Aplicar 5 Porques (interativo)"):
            problema = st.text_input("Problema detectado:", key="crise_problema")
            porques = []
            for n in range(1, 6):
                resp = st.text_input(f"Por que #{n}?", key=f"pq_{n}")
                if resp:
                    porques.append(resp)
            if len(porques) >= 3:
                st.success(f"Causa raiz provavel: {porques[-1]}")
                st.markdown("**Acao corretiva:**")
                acao = st.text_input("O que sera feito para resolver a causa raiz?", key="acao_raiz")

    # ========== ROTEIRO POR UNIDADE ==========

    st.subheader("Roteiro por Unidade")

    roteiro_prep = preparador.get('roteiro_por_unidade', {})

    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        un_nome = UNIDADES_NOMES.get(un_code, un_code)
        un_data = roteiro_prep.get(un_code, {})
        un_missoes = missoes_rede.get(un_code, [])
        un_conselheiro = conselheiro.get('pautas', {}).get(un_code, {})
        diff = DIFERENCIACAO_UNIDADE.get(un_code, {})

        n_missoes = len(un_missoes)
        n_urgentes = len([m for m in un_missoes if m.get('nivel') == 'URGENTE'])

        with st.expander(f"{un_nome} — {n_missoes} missoes ({n_urgentes} urgentes)", expanded=(n_urgentes > 0)):
            if un_data.get('situacao_resumida'):
                st.markdown(f"**Situacao:** {un_data['situacao_resumida']}")
            elif n_urgentes > 0:
                st.markdown(f"**Situacao:** {n_urgentes} missao(oes) urgente(s) requerem atencao imediata.")
            elif n_missoes > 0:
                st.markdown(f"**Situacao:** {n_missoes} missao(oes) ativa(s), sem urgencias.")
            else:
                st.markdown("**Situacao:** Tudo em ordem.")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Pontos criticos:**")
                criticos = un_data.get('pontos_criticos', [])
                if criticos:
                    for pc in criticos:
                        st.markdown(f"""
                        <div class="ponto-critico">
                            <strong>{pc.get('tema', '')}</strong><br>
                            <small>Como abordar: {pc.get('como_abordar', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    for m in un_missoes[:3]:
                        if m.get('nivel') in ('URGENTE', 'IMPORTANTE'):
                            st.markdown(f"""
                            <div class="ponto-critico">
                                <strong>{m.get('tipo', '')}</strong>: {m.get('o_que', '')[:120]}<br>
                                <small>Acao: {m.get('como', [''])[0] if m.get('como') else ''}</small>
                            </div>
                            """, unsafe_allow_html=True)

            with col2:
                st.markdown("**Pontos positivos:**")
                positivos = un_data.get('pontos_positivos', [])
                if positivos:
                    for pp in positivos:
                        st.markdown(f'<div class="ponto-positivo">{pp}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ponto-positivo">Foco: {diff.get('foco', 'Acompanhamento geral')}</div>
                    """, unsafe_allow_html=True)

            pergunta = un_data.get('pergunta_para_diretor', '')
            if not pergunta and un_conselheiro.get('perguntas'):
                pergunta = un_conselheiro['perguntas'][0]
            if pergunta:
                st.markdown(f"**Pergunta para a direcao:** _{pergunta}_")

            compromisso = un_data.get('compromisso_esperado', '')
            if compromisso:
                st.markdown(f"**Compromisso esperado:** {compromisso}")

    # ========== PROJECOES (se disponivel) ==========

    if preditor_data.get('projecoes'):
        st.subheader("Projecoes do PREDITOR")
        alertas = preditor_data.get('alertas', [])
        if alertas:
            for alerta in alertas:
                st.warning(f"{alerta.get('mensagem', '')}")

        proj_cols = st.columns(4)
        for i, un_code in enumerate(['BV', 'CD', 'JG', 'CDR']):
            proj = preditor_data['projecoes'].get(un_code, {})
            if proj:
                with proj_cols[i]:
                    un_nome = UNIDADES_NOMES.get(un_code, un_code)
                    tend = proj.get('tendencia', 'estavel')
                    icone = '📈' if tend == 'subindo' else ('📉' if tend == 'caindo' else '➡️')
                    st.metric(
                        un_nome,
                        f"{proj.get('atual', 0):.0f}%",
                        f"{icone} +1sem: {proj.get('proj_sem_mais_1', 0):.0f}% | +2sem: {proj.get('proj_sem_mais_2', 0):.0f}%",
                    )

    # ========== PROXIMAS REUNIOES ==========

    st.subheader("Proximas Reunioes")
    for r in prox_reunioes[1:4]:
        fmt = FORMATOS_REUNIAO.get(r.get('formato', 'F'), {})
        st.markdown(
            f"**Sem {r.get('semana', '?')}** — {r.get('cod', '')} "
            f"({fmt.get('nome', '?')}, {fmt.get('duracao', 30)}min): "
            f"{r.get('titulo', '')} | _{r.get('foco', '')}_"
        )

    # ========== CHECKLIST SAIDA ==========

    st.subheader("Checklist — Saida Obrigatoria")
    st.markdown(f"**{roteiro['saida_obrigatoria']}**")

    if formato_final == 'FLASH':
        st.checkbox("1 nome definido", key="ck_nome")
        st.checkbox("1 acao concreta registrada", key="ck_acao")
        st.checkbox("1 prazo estabelecido", key="ck_prazo")
    elif formato_final == 'FOCO':
        st.checkbox("Diagnostico documentado", key="ck_diag")
        st.checkbox("Plano de 2 semanas com responsaveis", key="ck_plano2")
        st.checkbox("Compromissos registrados", key="ck_comp")
    elif formato_final == 'CRISE':
        st.checkbox("Declaracao de crise formalizada", key="ck_decl")
        st.checkbox("Responsavel unico nomeado", key="ck_resp")
        st.checkbox("Plano de 48h definido", key="ck_48h")
        st.checkbox("Check amanha 17h agendado", key="ck_check")
    elif formato_final == 'ESTRATEGICA':
        st.checkbox("Balanco completo apresentado", key="ck_bal")
        st.checkbox("3 metas do proximo periodo definidas", key="ck_metas")
        st.checkbox("Reconhecimento/celebracao realizado", key="ck_celeb")

    # ========== EXPORTAR ==========

    st.markdown("---")
    export_txt = _gerar_export_completo(preparador, prox, roteiro, formato_final, missoes_data)
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            "Exportar Roteiro (TXT)",
            data=export_txt,
            file_name=f"roteiro_{formato_final}_sem{semana}.txt",
            mime="text/plain",
        )
    with col_exp2:
        # Versao WhatsApp (mais curta)
        wpp = _gerar_export_whatsapp(prox, roteiro, formato_final, semana)
        st.download_button(
            "Exportar WhatsApp",
            data=wpp,
            file_name=f"roteiro_wpp_sem{semana}.txt",
            mime="text/plain",
        )


# ========== VISAO DIRETOR ==========

elif role == ROLE_DIRETOR:
    un_code = user_unit or 'BV'
    un_nome = UNIDADES_NOMES.get(un_code, un_code)

    st.subheader(f"Preparacao — {un_nome}")

    versao_dir = preparador.get('versao_diretor', {}).get(un_code, {})
    un_missoes = missoes_rede.get(un_code, [])
    un_conselheiro = conselheiro.get('pautas', {}).get(un_code, {})

    # Topicos
    st.markdown("**Topicos principais:**")
    topicos = versao_dir.get('topicos_principais', [])
    if not topicos and un_conselheiro.get('topicos'):
        topicos = un_conselheiro['topicos']
    if not topicos:
        topicos = [m.get('o_que', '')[:80] for m in un_missoes[:3]]
    for t in topicos:
        st.markdown(f"- {t}")

    if versao_dir.get('abordagem_sugerida'):
        st.info(f"Abordagem sugerida: {versao_dir['abordagem_sugerida']}")

    # Perguntas
    st.markdown("**Perguntas para os coordenadores:**")
    perguntas = versao_dir.get('perguntas', [])
    if not perguntas and un_conselheiro.get('perguntas'):
        perguntas = un_conselheiro['perguntas']
    for p in perguntas:
        st.markdown(f"- _{p}_")

    # Campo complementar
    st.markdown("---")
    st.text_area(
        "Adicionar pontos proprios",
        placeholder="Escreva aqui observacoes que voce quer adicionar a pauta...",
        key="dir_complemento",
    )

    # Compromissos anteriores
    st.markdown("**Compromissos da reuniao anterior:**")
    retro = _carregar_json("retroalimentador_output.json")
    verif = retro.get('verificacoes', {}).get(un_code, {})
    if verif:
        taxa = verif.get('taxa_execucao', 0)
        total = verif.get('acoes_total', 0)
        resolvidas = verif.get('acoes_resolvidas', 0)
        cor = '#4CAF50' if taxa >= 80 else '#FF9800' if taxa >= 60 else '#F44336'
        st.markdown(
            f"Taxa de execucao: <span style='color:{cor}; font-weight:bold;'>"
            f"{taxa:.0f}%</span> ({resolvidas}/{total} acoes)",
            unsafe_allow_html=True,
        )
    else:
        st.caption("Sem dados de execucao anteriores.")


# ========== VISAO COORDENADOR ==========

else:
    un_code = user_unit or 'BV'
    un_nome = UNIDADES_NOMES.get(un_code, un_code)

    st.subheader(f"Preview da Proxima Reuniao — {un_nome}")

    if prox:
        st.markdown("**O que sera discutido:**")
        st.markdown(f"- Foco: {prox.get('foco', '')}")
        st.markdown(f"- Formato: {formato_final} ({roteiro['duracao']})")

    un_missoes = missoes_rede.get(un_code, [])
    n_total = len(un_missoes)
    n_urgentes = len([m for m in un_missoes if m.get('nivel') == 'URGENTE'])

    st.markdown(f"**Suas missoes:** {n_total} ativa(s), {n_urgentes} urgente(s)")

    if un_missoes:
        st.markdown("**Missoes em aberto:**")
        for m in un_missoes[:5]:
            nivel = m.get('nivel', 'MONITORAR')
            cor = '#F44336' if nivel == 'URGENTE' else '#FF9800' if nivel == 'IMPORTANTE' else '#607D8B'
            st.markdown(
                f"<span style='color:{cor}; font-weight:bold;'>[{nivel}]</span> "
                f"{m.get('o_que', '')[:100]}",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("**Sugestao de preparacao:**")
    un_conselheiro = conselheiro.get('pautas', {}).get(un_code, {})
    if un_conselheiro.get('perguntas'):
        st.markdown("Esteja preparado(a) para responder:")
        for p in un_conselheiro['perguntas']:
            st.markdown(f"- _{p}_")
    else:
        st.markdown("- Revise suas missoes ativas e prepare status de cada uma")
        st.markdown("- Traga dados atualizados dos professores criticos")
        st.markdown("- Pense em 1 conquista da semana para compartilhar")


# ========== HELPERS: EXPORT ==========

def _gerar_export_completo(preparador, reuniao, roteiro, formato, missoes_data):
    """Gera texto completo do roteiro para download."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"ROTEIRO DE REUNIAO PEEX — {formato}")
    lines.append(f"Semana {preparador.get('reuniao', {}).get('semana', semana)}")
    lines.append("=" * 60)

    if reuniao:
        lines.append(f"\nReuniao: {reuniao.get('titulo', '')}")
        lines.append(f"Formato: {formato} | Duracao: {roteiro['duracao']}")
        lines.append(f"Foco: {reuniao.get('foco', '')}")

    lines.append(f"\nSAIDA OBRIGATORIA: {roteiro['saida_obrigatoria']}")

    obj = preparador.get('objetivo_da_reuniao', '')
    if obj:
        lines.append(f"\nOBJETIVO: {obj}")

    lines.append(f"\n{'=' * 40}")
    lines.append(f"ROTEIRO MINUTO-A-MINUTO")
    lines.append(f"{'=' * 40}")

    for bloco in roteiro['blocos']:
        lines.append(f"\n[{bloco['tempo']}] {bloco['nome']}")
        lines.append(f'  Fala: "{bloco["script"]}"')
        if bloco.get('pagina'):
            lines.append(f"  Dados: pagina {bloco['pagina']}")

    # Por unidade
    rot_un = preparador.get('roteiro_por_unidade', {})
    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        un_data = rot_un.get(un_code, {})
        if un_data:
            un_nome = UNIDADES_NOMES.get(un_code, un_code)
            lines.append(f"\n--- {un_nome} ---")
            if un_data.get('situacao_resumida'):
                lines.append(f"Situacao: {un_data['situacao_resumida']}")
            if un_data.get('pergunta_para_diretor'):
                lines.append(f"Pergunta: {un_data['pergunta_para_diretor']}")
            if un_data.get('compromisso_esperado'):
                lines.append(f"Compromisso: {un_data['compromisso_esperado']}")

    # Protocolos de crise
    if formato == 'CRISE' and 'protocolos_unidade' in roteiro:
        lines.append(f"\n{'=' * 40}")
        lines.append("PROTOCOLOS DE CRISE POR UNIDADE")
        for un, prot in roteiro['protocolos_unidade'].items():
            lines.append(f"  {UNIDADES_NOMES.get(un, un)}: {prot}")

    lines.append(f"\n\nGerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    return '\n'.join(lines)


def _gerar_export_whatsapp(reuniao, roteiro, formato, semana):
    """Gera versao resumida para WhatsApp."""
    lines = []
    lines.append(f"*REUNIAO PEEX — {formato}*")
    lines.append(f"Semana {semana}")
    if reuniao:
        lines.append(f"Foco: {reuniao.get('foco', '')}")
    lines.append(f"\n*Saida obrigatoria:* {roteiro['saida_obrigatoria']}")
    lines.append(f"\n*Roteiro:*")
    for bloco in roteiro['blocos']:
        lines.append(f"  {bloco['tempo']} — {bloco['nome']}")
    lines.append(f"\n_Gerado em {datetime.now().strftime('%d/%m %H:%M')}_")
    return '\n'.join(lines)
