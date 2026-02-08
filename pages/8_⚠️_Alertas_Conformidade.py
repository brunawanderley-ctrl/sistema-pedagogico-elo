#!/usr/bin/env python3
"""
PÁGINA 8: ALERTAS E CONFORMIDADE
Monitoramento de registros, professores sem aulas, atrasos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import calcular_semana_letiva, carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje, _hoje

st.set_page_config(page_title="Alertas e Conformidade", page_icon="⚠️", layout="wide")
from auth import check_password, logout_button
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .alert-critical {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .alert-warning {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .alert-info {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .alert-success {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("⚠️ Alertas e Conformidade")
    st.markdown("**Monitoramento de registros e situações que requerem atenção**")

    # ========== NÍVEIS DE ALERTA (Tabela Compacta) ==========
    st.markdown("---")
    st.subheader("📊 Níveis de Alerta")

    niveis_df = pd.DataFrame({
        'Status': ['✅', 'ℹ️', '⚠️', '🔴'],
        'Nível': ['Excelente', 'Bom', 'Atenção', 'Crítico'],
        'Conformidade': ['≥95%', '85-94%', '70-84%', '<70%'],
        'Descrição': ['Registro em dia', 'Dentro do esperado', 'Monitorar', 'Ação urgente']
    })
    st.dataframe(niveis_df, use_container_width=True, hide_index=True, height=178)

    # ========== CRITÉRIOS DE ALERTA ==========
    st.markdown("---")
    st.header("📋 Critérios de Alerta")

    criterios = pd.DataFrame({
        'Alerta': ['Professor sem registro >3 dias', 'Conformidade <70%', 'Atraso >2 capítulos',
                  'Aulas sem conteúdo', 'Disciplina sem aula na semana', 'Desvio entre unidades'],
        'Gatilho': ['Nenhuma aula registrada em 3+ dias úteis', 'Aulas registradas / esperadas < 70%',
                   'Capítulo atual muito abaixo do esperado', 'Campo conteúdo vazio ou genérico',
                   'Zero aulas de uma disciplina na semana', 'Diferença > 2 capítulos entre unidades'],
        'Nível': ['CRÍTICO', 'CRÍTICO', 'CRÍTICO', 'ATENÇÃO', 'ATENÇÃO', 'ATENÇÃO'],
        'Ação Recomendada': ['Contatar professor imediatamente', 'Reunião com coordenação',
                            'Reunião com professor e coordenação', 'Orientar sobre preenchimento',
                            'Verificar horário/substituições', 'Reunião de alinhamento entre unidades']
    })

    st.dataframe(criterios, use_container_width=True, hide_index=True)

    # ========== ANÁLISE DOS DADOS ==========
    st.markdown("---")
    st.header("🔍 Análise dos Dados Atuais")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if not df_aulas.empty and not df_horario.empty:
        df_aulas = filtrar_ate_hoje(df_aulas)
        hoje = _hoje()

        # Calcula semana baseada na ultima data de registro
        if df_aulas['data'].notna().any():
            semana = calcular_semana_letiva(df_aulas['data'].max())
        else:
            semana = 1

        # Seletores
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            unidades = ['TODAS'] + sorted(df_aulas['unidade'].unique().tolist())
            un_sel = st.selectbox("Filtrar por unidade:", unidades)

        with col_f2:
            segmentos = ['TODOS', 'Anos Finais (6º-9º)', 'Ensino Médio (1ª-3ª)']
            seg_sel = st.selectbox("Filtrar por segmento:", segmentos)

        # Aplica filtros
        df_aulas_filt = df_aulas.copy()
        df_horario_filt = df_horario.copy()

        if un_sel != 'TODAS':
            df_aulas_filt = df_aulas_filt[df_aulas_filt['unidade'] == un_sel]
            df_horario_filt = df_horario_filt[df_horario_filt['unidade'] == un_sel]

        if seg_sel == 'Anos Finais (6º-9º)':
            df_aulas_filt = df_aulas_filt[df_aulas_filt['serie'].str.contains('Ano', na=False)]
            df_horario_filt = df_horario_filt[df_horario_filt['serie'].str.contains('Ano', na=False)]
        elif seg_sel == 'Ensino Médio (1ª-3ª)':
            df_aulas_filt = df_aulas_filt[df_aulas_filt['serie'].str.contains('Série|EM', na=False)]
            df_horario_filt = df_horario_filt[df_horario_filt['serie'].str.contains('Série|EM', na=False)]

        # ========== ALERTAS ATIVOS ==========
        st.subheader("🚨 Alertas Ativos")

        alertas = []

        # 1. Professores sem registro
        profs_esperados = set(df_horario_filt['professor'].unique())
        profs_registrados = set(df_aulas_filt['professor'].unique())
        profs_sem_registro = profs_esperados - profs_registrados

        if len(profs_sem_registro) > 0:
            for prof in sorted(profs_sem_registro)[:10]:  # Limita a 10
                alertas.append({
                    'nivel': 'CRÍTICO',
                    'tipo': 'Professor sem registro',
                    'detalhe': prof,
                    'acao': 'Verificar se está atuando e orientar sobre registro'
                })

        # 2. Conformidade por unidade (usando data máxima de cada unidade)
        for un in df_aulas['unidade'].unique():
            df_un = df_aulas[df_aulas['unidade'] == un]
            aulas_un = len(df_un)
            horario_un = len(df_horario[df_horario['unidade'] == un])

            # Calcula semana baseada na data máxima DA UNIDADE
            if df_un['data'].notna().any():
                data_max_un = df_un['data'].max()
                semana_un = calcular_semana_letiva(data_max_un)
            else:
                semana_un = 1

            esperado = horario_un * semana_un
            conformidade = (aulas_un / esperado * 100) if esperado > 0 else 0

            if conformidade < 70:
                alertas.append({
                    'nivel': 'CRÍTICO',
                    'tipo': 'Conformidade baixa',
                    'detalhe': f'{un}: {conformidade:.0f}% ({aulas_un}/{esperado}) - Sem {semana_un}',
                    'acao': 'Reunião urgente com coordenação da unidade'
                })
            elif conformidade < 85:
                alertas.append({
                    'nivel': 'ATENÇÃO',
                    'tipo': 'Conformidade abaixo do ideal',
                    'detalhe': f'{un}: {conformidade:.0f}% - Sem {semana_un}',
                    'acao': 'Monitorar e cobrar registros'
                })

        # 3. Aulas sem conteúdo
        sem_conteudo = df_aulas_filt[df_aulas_filt['conteudo'].isna() | (df_aulas_filt['conteudo'] == '')]
        pct_sem_conteudo = len(sem_conteudo) / len(df_aulas_filt) * 100 if len(df_aulas_filt) > 0 else 0

        if pct_sem_conteudo > 20:
            alertas.append({
                'nivel': 'ATENÇÃO',
                'tipo': 'Muitas aulas sem conteúdo',
                'detalhe': f'{pct_sem_conteudo:.0f}% das aulas ({len(sem_conteudo)})',
                'acao': 'Orientar professores sobre preenchimento do conteúdo'
            })

        # Exibe alertas em tabela compacta
        if alertas:
            # Prepara dados para tabela
            alertas_tabela = []
            for alerta in alertas:
                status_icon = '🔴' if alerta['nivel'] == 'CRÍTICO' else '⚠️'
                alertas_tabela.append({
                    'Status': status_icon,
                    'Tipo': alerta['tipo'],
                    'Detalhe': alerta['detalhe'],
                    'Ação': alerta['acao']
                })

            df_alertas = pd.DataFrame(alertas_tabela)

            # Exibe tabela
            st.dataframe(df_alertas, use_container_width=True, hide_index=True)

            # Contadores discretos
            criticos = len([a for a in alertas if a['nivel'] == 'CRÍTICO'])
            atencao = len([a for a in alertas if a['nivel'] != 'CRÍTICO'])

            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.metric("🔴 Críticos", criticos)
            with col_c2:
                st.metric("⚠️ Atenção", atencao)
            with col_c3:
                st.metric("Total", len(alertas))

            # Download
            st.download_button(
                "📥 Exportar Alertas (CSV)",
                df_alertas.to_csv(index=False).encode('utf-8-sig'),
                "alertas_ativos.csv",
                "text/csv"
            )
        else:
            st.success("✅ Nenhum alerta crítico no momento! Todos os indicadores estão dentro dos parâmetros esperados.")

        # ========== CONFORMIDADE POR PROFESSOR ==========
        st.markdown("---")
        st.subheader("👨‍🏫 Conformidade por Professor")

        # Calcula conformidade por professor
        prof_conformidade = []
        for prof in df_horario_filt['professor'].unique():
            esperado = len(df_horario_filt[df_horario_filt['professor'] == prof]) * semana
            realizado = len(df_aulas_filt[df_aulas_filt['professor'] == prof])
            conf = (realizado / esperado * 100) if esperado > 0 else 0

            prof_conformidade.append({
                'Professor': prof,
                'Esperado': esperado,
                'Registrado': realizado,
                'Conformidade': f'{conf:.0f}%',
                'Status': '✅' if conf >= 85 else ('⚠️' if conf >= 70 else '🔴')
            })

        df_prof = pd.DataFrame(prof_conformidade)
        if not df_prof.empty:
            df_prof = df_prof.sort_values('Conformidade', ascending=True)

        # Filtro de status
        status_filter = st.multiselect("Filtrar por status:",
                                       ['✅ OK (≥85%)', '⚠️ Atenção (70-84%)', '🔴 Crítico (<70%)'],
                                       default=['🔴 Crítico (<70%)', '⚠️ Atenção (70-84%)'])

        status_map = {'✅ OK (≥85%)': '✅', '⚠️ Atenção (70-84%)': '⚠️', '🔴 Crítico (<70%)': '🔴'}
        status_sel = [status_map[s] for s in status_filter]

        df_prof_filtered = df_prof[df_prof['Status'].isin(status_sel)]

        st.dataframe(df_prof_filtered, use_container_width=True, hide_index=True)

        # Gráfico
        fig = px.histogram(df_prof, x='Conformidade', nbins=10,
                          title='Distribuição de Conformidade dos Professores')
        st.plotly_chart(fig, use_container_width=True)

        # ========== CONFORMIDADE POR DISCIPLINA ==========
        st.markdown("---")
        st.subheader("📚 Conformidade por Disciplina")

        disc_conf = []
        for disc in df_horario_filt['disciplina'].unique():
            esperado = len(df_horario_filt[df_horario_filt['disciplina'] == disc]) * semana
            realizado = len(df_aulas_filt[df_aulas_filt['disciplina'] == disc])
            conf = (realizado / esperado * 100) if esperado > 0 else 0

            disc_conf.append({
                'Disciplina': disc,
                'Esperado': esperado,
                'Registrado': realizado,
                'Conformidade (%)': round(conf, 1)
            })

        df_disc = pd.DataFrame(disc_conf)
        if not df_disc.empty:
            df_disc = df_disc.sort_values('Conformidade (%)', ascending=True)

        fig = px.bar(df_disc, x='Conformidade (%)', y='Disciplina', orientation='h',
                    title='Conformidade por Disciplina',
                    color='Conformidade (%)',
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)

        # ========== RELATÓRIO DE DIVERGÊNCIAS PARA IMPRESSÃO ==========
        st.markdown("---")
        st.header("🖨️ Relatório de Divergências para Impressão")

        st.info("📋 Selecione a unidade e os tipos de divergência. O relatório pode ser baixado em TXT para impressão.")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            unidades_rel = ['TODAS'] + sorted(df_aulas['unidade'].unique().tolist())
            unidade_rel = st.selectbox("🏫 Unidade para relatório:", unidades_rel, key='un_rel')

        with col_r2:
            tipos_divergencia = st.multiselect(
                "📋 Tipos de divergência:",
                ['Professores sem registro', 'Conformidade crítica (<70%)', 'Conformidade atenção (70-84%)', 'Aulas sem conteúdo'],
                default=['Professores sem registro', 'Conformidade crítica (<70%)']
            )

        if st.button("📊 Gerar Relatório", type="primary"):
            # Gera relatório
            relatorio_linhas = []

            # Cabeçalho
            relatorio_linhas.append("=" * 80)
            relatorio_linhas.append("        RELATÓRIO DE DIVERGÊNCIAS - COLÉGIO ELO 2026")
            relatorio_linhas.append("=" * 80)
            relatorio_linhas.append("")
            relatorio_linhas.append(f"Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            relatorio_linhas.append(f"Unidade: {unidade_rel}")
            relatorio_linhas.append(f"Semana letiva atual: {semana}ª")
            relatorio_linhas.append("")
            relatorio_linhas.append("-" * 80)

            # Filtra por unidade se necessário
            if unidade_rel != 'TODAS':
                df_aulas_rel = df_aulas[df_aulas['unidade'] == unidade_rel]
                df_horario_rel = df_horario[df_horario['unidade'] == unidade_rel]
                unidades_lista = [unidade_rel]
            else:
                df_aulas_rel = df_aulas
                df_horario_rel = df_horario
                unidades_lista = sorted(df_aulas['unidade'].unique())

            total_divergencias = 0

            for un in unidades_lista:
                df_un_aulas = df_aulas_rel[df_aulas_rel['unidade'] == un] if unidade_rel == 'TODAS' else df_aulas_rel
                df_un_horario = df_horario_rel[df_horario_rel['unidade'] == un] if unidade_rel == 'TODAS' else df_horario_rel

                divergencias_un = []

                # 1. Professores sem registro
                if 'Professores sem registro' in tipos_divergencia:
                    profs_esperados_un = set(df_un_horario['professor'].unique())
                    profs_registrados_un = set(df_un_aulas['professor'].unique())
                    profs_sem_un = profs_esperados_un - profs_registrados_un

                    for prof in sorted(profs_sem_un):
                        # Pega disciplinas do professor
                        disc_prof = df_un_horario[df_un_horario['professor'] == prof]['disciplina'].unique()
                        disc_str = ', '.join(disc_prof)[:40]
                        divergencias_un.append({
                            'tipo': 'SEM REGISTRO',
                            'professor': prof,
                            'detalhe': f'Disciplinas: {disc_str}',
                            'acao': 'Verificar atuação e orientar registro'
                        })

                # 2. Conformidade crítica
                if 'Conformidade crítica (<70%)' in tipos_divergencia:
                    for prof in df_un_horario['professor'].unique():
                        esperado_p = len(df_un_horario[df_un_horario['professor'] == prof]) * semana
                        realizado_p = len(df_un_aulas[df_un_aulas['professor'] == prof])
                        conf_p = (realizado_p / esperado_p * 100) if esperado_p > 0 else 0

                        if conf_p < 70 and realizado_p > 0:  # Tem registro mas está crítico
                            divergencias_un.append({
                                'tipo': 'CONFORMIDADE CRÍTICA',
                                'professor': prof,
                                'detalhe': f'{conf_p:.0f}% ({realizado_p}/{esperado_p} aulas)',
                                'acao': 'Reunião urgente'
                            })

                # 3. Conformidade atenção
                if 'Conformidade atenção (70-84%)' in tipos_divergencia:
                    for prof in df_un_horario['professor'].unique():
                        esperado_p = len(df_un_horario[df_un_horario['professor'] == prof]) * semana
                        realizado_p = len(df_un_aulas[df_un_aulas['professor'] == prof])
                        conf_p = (realizado_p / esperado_p * 100) if esperado_p > 0 else 0

                        if 70 <= conf_p < 85 and realizado_p > 0:
                            divergencias_un.append({
                                'tipo': 'CONFORMIDADE ATENÇÃO',
                                'professor': prof,
                                'detalhe': f'{conf_p:.0f}% ({realizado_p}/{esperado_p} aulas)',
                                'acao': 'Monitorar e cobrar'
                            })

                # 4. Aulas sem conteúdo (agrupa por professor)
                if 'Aulas sem conteúdo' in tipos_divergencia:
                    for prof in df_un_aulas['professor'].unique():
                        aulas_prof = df_un_aulas[df_un_aulas['professor'] == prof]
                        sem_cont = aulas_prof[aulas_prof['conteudo'].isna() | (aulas_prof['conteudo'] == '')]
                        if len(sem_cont) > 0:
                            pct = len(sem_cont) / len(aulas_prof) * 100
                            if pct > 30:  # Mais de 30% sem conteúdo
                                divergencias_un.append({
                                    'tipo': 'AULAS SEM CONTEÚDO',
                                    'professor': prof,
                                    'detalhe': f'{len(sem_cont)} aulas ({pct:.0f}%)',
                                    'acao': 'Orientar preenchimento'
                                })

                # Adiciona ao relatório
                if divergencias_un:
                    relatorio_linhas.append("")
                    relatorio_linhas.append(f"🏫 UNIDADE: {un}")
                    relatorio_linhas.append("-" * 40)
                    relatorio_linhas.append(f"{'TIPO':<25} {'PROFESSOR':<35} {'DETALHE':<25}")
                    relatorio_linhas.append("-" * 85)

                    for div in divergencias_un:
                        prof_nome = div['professor'][:33] if len(div['professor']) > 33 else div['professor']
                        relatorio_linhas.append(f"{div['tipo']:<25} {prof_nome:<35} {div['detalhe']:<25}")
                        total_divergencias += 1

                    relatorio_linhas.append("")
                    relatorio_linhas.append(f"   Total de divergências em {un}: {len(divergencias_un)}")
                    relatorio_linhas.append("")

            # Resumo final
            relatorio_linhas.append("=" * 80)
            relatorio_linhas.append(f"RESUMO: {total_divergencias} divergências encontradas")
            relatorio_linhas.append("=" * 80)
            relatorio_linhas.append("")
            relatorio_linhas.append("Ações recomendadas:")
            relatorio_linhas.append("  - SEM REGISTRO: Contatar professor e verificar situação")
            relatorio_linhas.append("  - CONFORMIDADE CRÍTICA: Agendar reunião urgente")
            relatorio_linhas.append("  - CONFORMIDADE ATENÇÃO: Monitorar e cobrar registros")
            relatorio_linhas.append("  - SEM CONTEÚDO: Orientar sobre preenchimento detalhado")
            relatorio_linhas.append("")
            relatorio_linhas.append("-" * 80)
            relatorio_linhas.append("                    Coordenação Pedagógica - Colégio ELO")
            relatorio_linhas.append("-" * 80)

            # Junta tudo
            relatorio_texto = "\n".join(relatorio_linhas)

            # Exibe prévia
            st.subheader("📄 Prévia do Relatório")
            st.code(relatorio_texto, language=None)

            # Métricas
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total de Divergências", total_divergencias)
            with col_m2:
                st.metric("Unidades Analisadas", len(unidades_lista))
            with col_m3:
                st.metric("Semana Letiva", f"{semana}ª")

            # Download
            st.download_button(
                "📥 Baixar Relatório (TXT)",
                relatorio_texto,
                f"relatorio_divergencias_{unidade_rel}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                "text/plain"
            )

            # Download CSV detalhado
            todas_divergencias = []
            for un in unidades_lista:
                df_un_aulas = df_aulas_rel[df_aulas_rel['unidade'] == un] if unidade_rel == 'TODAS' else df_aulas_rel
                df_un_horario = df_horario_rel[df_horario_rel['unidade'] == un] if unidade_rel == 'TODAS' else df_horario_rel

                if 'Professores sem registro' in tipos_divergencia:
                    profs_esperados_un = set(df_un_horario['professor'].unique())
                    profs_registrados_un = set(df_un_aulas['professor'].unique())
                    for prof in (profs_esperados_un - profs_registrados_un):
                        disc = ', '.join(df_un_horario[df_un_horario['professor'] == prof]['disciplina'].unique())
                        todas_divergencias.append({
                            'Unidade': un,
                            'Tipo': 'Sem Registro',
                            'Professor': prof,
                            'Detalhe': disc,
                            'Ação': 'Verificar atuação'
                        })

            if todas_divergencias:
                df_div = pd.DataFrame(todas_divergencias)
                st.download_button(
                    "📥 Baixar Detalhado (CSV)",
                    df_div.to_csv(index=False).encode('utf-8-sig'),
                    f"divergencias_detalhado_{unidade_rel}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

    else:
        st.warning("Dados não carregados. Execute a extração do SIGA primeiro.")

if __name__ == "__main__":
    main()
