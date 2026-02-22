#!/usr/bin/env python3
"""
GLOSSARIO — Glossario completo de termos do sistema PEEX e plataforma pedagogica.
Referencia rapida para coordenadores, gestores e professores.
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Dados do glossario
# ---------------------------------------------------------------------------

GLOSSARIO = {
    "Dados": [
        {
            "termo": "Conformidade",
            "definicao": (
                "Percentual de aulas efetivamente registradas no SIGA em relacao "
                "ao total de aulas esperadas pela grade curricular. Calculado como "
                "(aulas registradas / aulas esperadas) x 100."
            ),
            "exemplo": (
                "Um professor com 20 aulas esperadas na semana que registrou 18 "
                "tem conformidade de 90%."
            ),
            "importancia": (
                "Indica se o professor esta cumprindo a carga horaria prevista. "
                "Conformidade abaixo de 80% acende alerta amarelo; abaixo de 60%, vermelho."
            ),
        },
        {
            "termo": "Frequencia",
            "definicao": (
                "Percentual de presenca do aluno nas aulas ao longo do periodo. "
                "Calculado como (dias presentes / dias letivos) x 100."
            ),
            "exemplo": (
                "Aluno com 55 presencas em 60 dias letivos tem frequencia de 91,7%."
            ),
            "importancia": (
                "Frequencia abaixo de 75% coloca o aluno em situacao de risco de "
                "reprovacao por faltas. E um dos indicadores mais precoces de evasao."
            ),
        },
        {
            "termo": "Ritmo SAE",
            "definicao": (
                "Comparativo entre o capitulo do material SAE Digital em que o "
                "professor se encontra e o capitulo esperado para a semana letiva "
                "atual. Baseado na formula de progressao: 42 semanas de conteudo "
                "divididas em 12 capitulos (~3,5 semanas por capitulo)."
            ),
            "exemplo": (
                "Na semana 8 o capitulo esperado e o 2. Se o professor esta no "
                "capitulo 1, o ritmo esta atrasado em 1 capitulo."
            ),
            "importancia": (
                "Garante que o conteudo programatico sera concluido ate o fim do ano. "
                "Atrasos acumulados comprometem o fechamento trimestral e a preparacao "
                "para avaliacoes externas."
            ),
        },
        {
            "termo": "Ocorrencia",
            "definicao": (
                "Registro disciplinar feito no SIGA (endpoint aluno_observacao). "
                "Cada ocorrencia tem data, aluno, descricao e gravidade "
                "(Leve, Media ou Grave)."
            ),
            "exemplo": (
                "Aluno recebe ocorrencia de gravidade 'Media' por uso de celular "
                "em sala de aula."
            ),
            "importancia": (
                "Acumulo de ocorrencias e um indicador comportamental que, cruzado "
                "com notas e frequencia, ajuda a identificar alunos em situacao "
                "critica antes que a evasao ocorra."
            ),
        },
        {
            "termo": "SIGA",
            "definicao": (
                "Sistema Integrado de Gestao Academica, fornecido pela Activesoft. "
                "E o sistema oficial onde professores registram aulas, frequencias e "
                "notas. A API SIGA e a fonte primaria de dados do painel pedagogico."
            ),
            "exemplo": (
                "O professor acessa o SIGA para lancar a frequencia da turma do dia "
                "e registrar o conteudo trabalhado em aula."
            ),
            "importancia": (
                "Todo dado de conformidade, frequencia e nota parte do SIGA. "
                "Se o professor nao registra no SIGA, o sistema nao consegue "
                "acompanhar a turma."
            ),
        },
        {
            "termo": "SAE Digital",
            "definicao": (
                "Plataforma de conteudo e exercicios do Sistema de Apoio ao Ensino. "
                "Fornece materiais didaticos digitais, avaliacoes, trilhas de "
                "aprendizagem e biblioteca. Organizada em 12 capitulos por "
                "disciplina por ano."
            ),
            "exemplo": (
                "O aluno acessa a SAE Digital para resolver exercicios do capitulo 3 "
                "de Matematica e o sistema registra seu progresso."
            ),
            "importancia": (
                "O cruzamento entre dados do SIGA (aula dada) e SAE Digital "
                "(engajamento do aluno) permite identificar gaps entre ensino e "
                "aprendizagem."
            ),
        },
    ],
    "PEEX": [
        {
            "termo": "IE (Indice ELO)",
            "definicao": (
                "Score de 0 a 100 que mede a saude pedagogica de uma unidade. "
                "Combina conformidade de aulas, ritmo SAE, frequencia dos alunos "
                "e indicadores comportamentais em uma unica metrica."
            ),
            "exemplo": (
                "A unidade Boa Viagem tem IE de 78 esta semana: conformidade alta "
                "mas frequencia caindo. Candeias tem IE de 65 por atraso no ritmo SAE."
            ),
            "importancia": (
                "Permite comparar unidades de forma objetiva e direcionar atencao "
                "da gestao para onde o impacto sera maior."
            ),
        },
        {
            "termo": "Missao",
            "definicao": (
                "Antes chamada de 'Batalha'. E um problema detectado pelo sistema "
                "que precisa de acao concreta. Classificada em tres niveis de "
                "prioridade: URGENTE, IMPORTANTE ou MONITORAR."
            ),
            "exemplo": (
                "Missao URGENTE: '3 professores do 7o Ano com conformidade abaixo "
                "de 50% — agendar conversa individual esta semana.'"
            ),
            "importancia": (
                "Transforma dados em acoes claras. Sem missoes, o coordenador "
                "veria numeros mas nao saberia o que fazer primeiro."
            ),
        },
        {
            "termo": "Estrela",
            "definicao": (
                "Reconhecimento semanal dado a professores ou turmas que "
                "demonstraram evolucao significativa nos indicadores. Nao premia "
                "o melhor absoluto, mas quem mais evoluiu."
            ),
            "exemplo": (
                "Professor que saiu de 60% para 95% de conformidade em uma semana "
                "recebe uma Estrela no resumo semanal."
            ),
            "importancia": (
                "Reforco positivo baseado em ciencia comportamental. Reconhecer "
                "evolucao motiva mais do que cobrar resultado absoluto."
            ),
        },
        {
            "termo": "Escalacao",
            "definicao": (
                "Processo formal de escalar um problema para o nivel hierarquico "
                "superior quando a acao local nao resolveu. Segue o fluxo: "
                "Coordenador -> Diretor -> Gestao Central."
            ),
            "exemplo": (
                "Professor com 3 semanas consecutivas abaixo de 50% de conformidade "
                "e escalado do coordenador para o diretor da unidade."
            ),
            "importancia": (
                "Garante que problemas persistentes nao fiquem estagnados. "
                "Cada nivel tem ferramentas diferentes para intervir."
            ),
        },
        {
            "termo": "Nudge",
            "definicao": (
                "Mensagem motivacional curta, baseada em ciencia comportamental, "
                "enviada no momento certo para incentivar uma acao desejada. "
                "Pode ser direcionada a professores, alunos ou coordenadores."
            ),
            "exemplo": (
                "'Voce registrou 18 de 20 aulas esta semana — faltam so 2 para "
                "atingir 100%. Que tal completar hoje?'"
            ),
            "importancia": (
                "Pequenos empurroes no momento certo tem mais efeito do que "
                "grandes cobrancas esporadicas. Baseado na teoria de Thaler e "
                "Sunstein."
            ),
        },
        {
            "termo": "Fase",
            "definicao": (
                "O ano letivo e dividido em 3 fases que determinam a postura "
                "do sistema: Sobrevivencia (inicio — foco em estabelecer rotinas), "
                "Consolidacao (meio — foco em manter e ajustar), "
                "Excelencia (fim — foco em fechar bem e celebrar)."
            ),
            "exemplo": (
                "Em fevereiro (Fase Sobrevivencia), o sistema prioriza alertas "
                "de conformidade basica. Em outubro (Fase Excelencia), prioriza "
                "fechamento de conteudo."
            ),
            "importancia": (
                "Adapta o tom e a prioridade das acoes ao momento do ano. "
                "Nao faz sentido cobrar excelencia quando as rotinas ainda "
                "nao estao estabelecidas."
            ),
        },
        {
            "termo": "Estacao",
            "definicao": (
                "Tom da comunicacao do sistema baseado no momento do ano letivo. "
                "Determina como as mensagens, nudges e alertas sao redigidos — "
                "mais acolhedor no inicio, mais direto no meio, mais celebratorio "
                "no fim."
            ),
            "exemplo": (
                "Inicio do ano (tom acolhedor): 'Estamos comecando — vamos "
                "construir juntos.' Meio do ano (tom direto): 'Precisamos "
                "recuperar o ritmo agora.'"
            ),
            "importancia": (
                "Comunicacao que ignora o contexto temporal perde eficacia. "
                "A Estacao garante que a mensagem certa chegue no tom certo."
            ),
        },
        {
            "termo": "Vacina",
            "definicao": (
                "Intervencao preventiva aplicada antes que um problema se agrave. "
                "Acionada quando indicadores mostram tendencia de queda mas ainda "
                "nao atingiram nivel critico."
            ),
            "exemplo": (
                "Aluno com frequencia caindo de 90% para 82% em 3 semanas recebe "
                "uma Vacina: contato preventivo com a familia antes que chegue "
                "a 75%."
            ),
            "importancia": (
                "Prevenir e mais barato e eficaz do que remediar. A Vacina age "
                "na janela de oportunidade antes da crise se instalar."
            ),
        },
    ],
    "Reunioes": [
        {
            "termo": "RR (Reuniao de Rede)",
            "definicao": (
                "Reuniao que envolve todas as unidades do Colegio ELO ao mesmo "
                "tempo. Serve para alinhar estrategias, compartilhar boas praticas "
                "e tratar temas que afetam a rede como um todo."
            ),
            "exemplo": (
                "RR mensal: diretores e coordenadores das 4 unidades (BV, CD, JG, "
                "CDR) revisam o IE comparativo e definem acoes conjuntas."
            ),
            "importancia": (
                "Garante coerencia pedagogica entre unidades e evita que cada "
                "escola resolva os mesmos problemas de forma isolada."
            ),
        },
        {
            "termo": "RU (Reuniao de Unidade)",
            "definicao": (
                "Reuniao interna de uma unica unidade. Focada nos indicadores "
                "e problemas especificos daquela escola."
            ),
            "exemplo": (
                "RU semanal de Boa Viagem: coordenadora Bruna Vitoria revisa "
                "conformidade dos professores do 6o ao 9o Ano."
            ),
            "importancia": (
                "Permite aprofundamento nos problemas locais que nao caberiam "
                "no tempo de uma reuniao de rede."
            ),
        },
        {
            "termo": "FLASH",
            "definicao": (
                "Formato de reuniao de 30 minutos para check rapido de "
                "indicadores. Estrutura fixa: 5min contexto, 20min dados, "
                "5min encaminhamentos."
            ),
            "exemplo": (
                "FLASH segunda-feira: coordenador abre o painel, revisa os "
                "3 principais alertas da semana e define responsaveis."
            ),
            "importancia": (
                "Reunioes curtas e frequentes sao mais eficazes do que reunioes "
                "longas e esporadicas para manter o ritmo."
            ),
        },
        {
            "termo": "FOCO",
            "definicao": (
                "Formato de reuniao de 45 minutos para aprofundamento em 1 ou 2 "
                "temas especificos. Usa dados detalhados do painel para analise."
            ),
            "exemplo": (
                "FOCO sobre evasao no 9o Ano: analise dos 15 alunos Tier C, "
                "cruzamento frequencia x ocorrencias, plano de acao individual."
            ),
            "importancia": (
                "Nem todo problema se resolve com um check rapido. O FOCO permite "
                "a profundidade necessaria para temas complexos."
            ),
        },
        {
            "termo": "CRISE",
            "definicao": (
                "Formato de reuniao de 60 minutos acionado quando ha 5 ou mais "
                "missoes urgentes simultaneas. Convoca coordenador e diretor."
            ),
            "exemplo": (
                "CRISE: 7 professores abaixo de 40% de conformidade, 12 alunos "
                "com frequencia abaixo de 60%, e 3 turmas sem registro ha 2 semanas."
            ),
            "importancia": (
                "Situacoes criticas precisam de tempo e atencao dedicados. "
                "O formato CRISE prioriza resolucao sobre rotina."
            ),
        },
        {
            "termo": "ESTRATEGICA",
            "definicao": (
                "Formato de reuniao de 90 minutos para balanco trimestral. "
                "Revisa todos os indicadores do trimestre, avalia eficacia das "
                "acoes tomadas e planeja o trimestre seguinte."
            ),
            "exemplo": (
                "ESTRATEGICA de fim do 1o Trimestre: revisao do IE das 4 unidades, "
                "analise de evolucao dos Tiers, definicao de metas para o 2o Tri."
            ),
            "importancia": (
                "Sem balanco trimestral, a operacao do dia a dia engole a visao "
                "estrategica. Esta reuniao garante o olhar de longo prazo."
            ),
        },
        {
            "termo": "Ritual de Floresta",
            "definicao": (
                "Estrutura narrativa das reunioes PEEX composta por 5 atos: "
                "Raizes (dados fundamentais), Solo (contexto da semana), "
                "Micelio (conexoes entre indicadores), Sementes (acoes planejadas) "
                "e Chuva (reconhecimentos e motivacao)."
            ),
            "exemplo": (
                "Ato 1 - Raizes: IE da unidade. Ato 2 - Solo: eventos da semana. "
                "Ato 3 - Micelio: cruzamento conformidade x frequencia. "
                "Ato 4 - Sementes: 3 acoes priorizadas. Ato 5 - Chuva: Estrelas."
            ),
            "importancia": (
                "Uma reuniao sem estrutura vira conversa dispersa. O Ritual de "
                "Floresta guia o grupo por uma narrativa logica do dado a acao."
            ),
        },
    ],
    "Classificacoes": [
        {
            "termo": "Tier A / B / C",
            "definicao": (
                "Classificacao de alunos por nivel de risco. "
                "Tier A = OK (indicadores saudaveis, sem intervencao necessaria). "
                "Tier B = Atencao (indicadores em queda, monitorar de perto). "
                "Tier C = Critico (indicadores graves, intervencao imediata)."
            ),
            "exemplo": (
                "Aluno Tier C: frequencia 68%, 4 ocorrencias no mes, nota media "
                "abaixo de 5. Acao: contato com familia + acompanhamento individual."
            ),
            "importancia": (
                "Permite priorizar recursos limitados. Coordenadores focam energia "
                "nos Tier C sem perder de vista a prevencao nos Tier B."
            ),
        },
        {
            "termo": "Verde / Amarelo / Vermelho",
            "definicao": (
                "Semaforo de conformidade do professor. "
                "Verde: 80% ou mais de aulas registradas. "
                "Amarelo: entre 60% e 79%. "
                "Vermelho: abaixo de 60%."
            ),
            "exemplo": (
                "Professor com 15 de 20 aulas registradas = 75% = Amarelo. "
                "Professor com 19 de 20 = 95% = Verde."
            ),
            "importancia": (
                "Visualizacao rapida que permite ao coordenador identificar "
                "em segundos quem precisa de atencao sem analisar planilha."
            ),
        },
        {
            "termo": "URGENTE / IMPORTANTE / MONITORAR",
            "definicao": (
                "Niveis de prioridade das missoes. "
                "URGENTE: requer acao imediata (mesma semana). "
                "IMPORTANTE: requer acao planejada (proximas 2 semanas). "
                "MONITORAR: nao requer acao agora mas deve ser acompanhado."
            ),
            "exemplo": (
                "URGENTE: turma sem registro de aulas ha 10 dias. "
                "IMPORTANTE: professor com ritmo SAE atrasado em 2 capitulos. "
                "MONITORAR: aluno com frequencia estavel em 78%."
            ),
            "importancia": (
                "Sem priorizacao, tudo parece urgente e nada e tratado. "
                "A classificacao em 3 niveis disciplina a atencao da gestao."
            ),
        },
        {
            "termo": "Score de Risco",
            "definicao": (
                "Pontuacao de 0 a 100 atribuida a alunos, professores ou turmas. "
                "Quanto maior o score, mais urgente a situacao. Combina multiplos "
                "indicadores (frequencia, notas, ocorrencias, conformidade) em um "
                "unico numero comparavel."
            ),
            "exemplo": (
                "Aluno com Score de Risco 85: frequencia 70%, 3 ocorrencias graves, "
                "nota media 4,2. Aluno com Score 15: tudo dentro do esperado."
            ),
            "importancia": (
                "Permite ranquear e priorizar de forma objetiva. O coordenador "
                "atende primeiro quem tem Score mais alto, otimizando o tempo "
                "limitado da equipe."
            ),
        },
    ],
}


# ---------------------------------------------------------------------------
# Funcao de filtragem
# ---------------------------------------------------------------------------

def filtrar_termos(termos: list, busca: str) -> list:
    """Filtra termos por nome ou definicao (case-insensitive)."""
    if not busca:
        return termos
    busca_lower = busca.lower()
    return [
        t for t in termos
        if busca_lower in t["termo"].lower() or busca_lower in t["definicao"].lower()
    ]


def renderizar_termo(t: dict) -> None:
    """Renderiza um termo dentro de um expander."""
    with st.expander(t["termo"]):
        st.markdown(f"**Definicao:** {t['definicao']}")
        st.markdown(f"**Exemplo pratico:** {t['exemplo']}")
        st.markdown(f"**Por que importa:** {t['importancia']}")


# ---------------------------------------------------------------------------
# Layout da pagina
# ---------------------------------------------------------------------------

st.title("Glossario PEEX")
st.caption(
    "Referencia completa dos termos utilizados no sistema de acompanhamento "
    "pedagogico e no PEEX (Programa de Excelencia ELO)."
)

busca = st.text_input(
    "Buscar termo",
    placeholder="Digite para filtrar por nome ou definicao...",
    key="glossario_busca",
)

tab_dados, tab_peex, tab_reunioes, tab_classif = st.tabs(
    ["Dados", "PEEX", "Reunioes", "Classificacoes"]
)

# --- Aba Dados ---
with tab_dados:
    termos = filtrar_termos(GLOSSARIO["Dados"], busca)
    if termos:
        for t in termos:
            renderizar_termo(t)
    else:
        st.info("Nenhum termo encontrado para a busca informada.")

# --- Aba PEEX ---
with tab_peex:
    termos = filtrar_termos(GLOSSARIO["PEEX"], busca)
    if termos:
        for t in termos:
            renderizar_termo(t)
    else:
        st.info("Nenhum termo encontrado para a busca informada.")

# --- Aba Reunioes ---
with tab_reunioes:
    termos = filtrar_termos(GLOSSARIO["Reunioes"], busca)
    if termos:
        for t in termos:
            renderizar_termo(t)
    else:
        st.info("Nenhum termo encontrado para a busca informada.")

# --- Aba Classificacoes ---
with tab_classif:
    termos = filtrar_termos(GLOSSARIO["Classificacoes"], busca)
    if termos:
        for t in termos:
            renderizar_termo(t)
    else:
        st.info("Nenhum termo encontrado para a busca informada.")

# --- Rodape ---
st.divider()
total = sum(len(v) for v in GLOSSARIO.values())
st.caption(f"{total} termos no glossario | 4 categorias")
