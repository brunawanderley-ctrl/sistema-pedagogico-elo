"""
Motor de Inteligencia PEEX — AnalistaELO.

Gera narrativas, decisoes, roteiros e propostas usando LLM (Claude API).
Fallback: templates inteligentes quando API key nao disponivel.

Configuracao:
  - API key em .streamlit/secrets.toml: anthropic_api_key = "sk-ant-..."
  - Ou variavel de ambiente: ANTHROPIC_API_KEY
  - Sem chave: funciona com templates (graceful degradation)
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("llm_engine")

# Paths
_DOCS_DIR = Path(__file__).parent / "docs" / "obsidian"
_CACHE_DIR = Path(__file__).parent / "power_bi"  # reusa WRITABLE_DIR padrao

# ========== CONFIGURACAO ==========

def _get_api_key():
    """Obtem API key. Tenta secrets.toml, depois env var."""
    try:
        import streamlit as st
        key = st.secrets.get("anthropic_api_key", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")


def _llm_disponivel():
    """Verifica se ha API key configurada."""
    return bool(_get_api_key())


def _carregar_contexto_docs():
    """Carrega resumo dos docs Obsidian para system prompt."""
    contexto = []
    docs_prioritarios = [
        "sintese_final.md",
        "plano_definitivo.md",
        "guia_completo.md",
        "proposta_definitiva.md",
    ]
    for doc in docs_prioritarios:
        path = _DOCS_DIR / doc
        if path.exists():
            texto = path.read_text(encoding="utf-8")
            # Truncar para economizar tokens (primeiras 200 linhas)
            linhas = texto.split("\n")[:200]
            contexto.append(f"--- {doc} ---\n" + "\n".join(linhas))
    return "\n\n".join(contexto)


# ========== SYSTEM PROMPT ==========

_SYSTEM_PROMPT = """Voce e o ANALISTA do sistema PEEX (Programa de Excelencia) do Colegio ELO.
Sua funcao: gerar narrativas estrategicas, diagnosticos e propostas para a CEO.

CONTEXTO DA REDE:
- 4 unidades: Boa Viagem (BV), Candeias (CD), Janga (JG), Cordeiro (CDR)
- ~2.200 alunos, ~300 professores
- 3 fases: Sobrevivencia (sem 1-15), Consolidacao (16-33), Excelencia (34-47)
- Metafora central: Guardia da Floresta (coordenadores sao guardioes)
- 5 eixos: Conformidade, Frequencia, Desempenho, Clima, Engajamento Digital

PRINCIPIOS DO PEEX:
- "Mede quanto voce cresce, nao onde voce esta"
- Nudges comportamentais > ordens diretas
- Ritual de Floresta: Raizes, Solo, Micelio, Sementes, Chuva
- 4 formatos de reuniao: FLASH (15-20min), FOCO (30-45min), CRISE (45-60min), ESTRATEGICA (60-90min)
- Cada unidade tem sua identidade: BV=referencia, CD=equilibrio, JG=frequencia, CDR=ocorrencias

ESTILO DE COMUNICACAO:
- Tom executivo, direto, com empatia
- Use dados concretos (numeros, porcentagens, nomes de unidades)
- Nunca generico — sempre contextualizado
- Narrativa: conte a historia da semana, nao so numeros
- Decisoes: explique POR QUE persistem, opcoes de acao, impacto estimado
"""


# ========== CHAMADA LLM ==========

def _chamar_llm(prompt_usuario, modelo="claude-haiku-4-5-20251001", max_tokens=2000):
    """Chama a API Claude. Retorna texto ou None se falhar."""
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        contexto_docs = _carregar_contexto_docs()
        system = _SYSTEM_PROMPT
        if contexto_docs:
            system += "\n\nDOCUMENTOS DE REFERENCIA (resumo):\n" + contexto_docs[:8000]

        message = client.messages.create(
            model=modelo,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt_usuario}],
        )
        return message.content[0].text

    except Exception as e:
        logger.warning(f"LLM indisponivel: {e}")
        return None


# ========== CACHE ==========

def _cache_path(nome):
    """Retorna path do cache para um resultado."""
    return _CACHE_DIR / f"llm_cache_{nome}.json"


def _ler_cache(nome, max_idade_horas=24):
    """Le resultado do cache se existir e nao estiver expirado."""
    path = _cache_path(nome)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        gerado = datetime.fromisoformat(data.get("gerado_em", "2000-01-01"))
        idade = (datetime.now() - gerado).total_seconds() / 3600
        if idade > max_idade_horas:
            return None
        return data.get("resultado")
    except Exception:
        return None


def _salvar_cache(nome, resultado):
    """Salva resultado no cache."""
    try:
        path = _cache_path(nome)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "gerado_em": datetime.now().isoformat(),
                "resultado": resultado,
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Erro ao salvar cache {nome}: {e}")


# ========== CLASSE PRINCIPAL ==========

class AnalistaELO:
    """Motor de inteligencia PEEX."""

    def narrar_semana(self, dados_resumo, historico_semanas, missoes_rede, semana):
        """Narrativa CEO: historia da semana com insights estrategicos.

        Args:
            dados_resumo: dict com dados do resumo executivo por unidade
            historico_semanas: lista de snapshots de semanas anteriores
            missoes_rede: dict unidade -> lista de missoes
            semana: numero da semana letiva

        Returns:
            str com narrativa em paragrafos
        """
        # Tentar cache
        cache_key = f"narrativa_sem{semana}"
        cached = _ler_cache(cache_key, max_idade_horas=12)
        if cached:
            return cached

        # Montar prompt com dados
        dados_texto = self._formatar_dados_resumo(dados_resumo)
        missoes_texto = self._formatar_missoes(missoes_rede)

        prompt = f"""Gere a narrativa da Semana {semana} para a CEO do Colegio ELO.

DADOS ATUAIS:
{dados_texto}

MISSOES ATIVAS:
{missoes_texto}

HISTORICO RECENTE:
{self._formatar_historico(historico_semanas)}

Escreva 4-5 paragrafos:
1. Abertura com contexto da semana e trimestre
2. Comparativo entre unidades (quem lidera, quem precisa de atencao)
3. Evolucao vs semana anterior (tendencia)
4. Destaque positivo (algo para celebrar)
5. Alerta principal (o que requer acao imediata)

Tom: executivo, direto, com empatia. Use numeros concretos."""

        resultado = _chamar_llm(prompt)
        if resultado:
            _salvar_cache(cache_key, resultado)
            return resultado

        # Fallback: template
        return self._narrar_semana_template(dados_resumo, historico_semanas, semana)

    def analisar_decisoes(self, persistentes, dados_unidades):
        """3 decisoes com analise de opcoes e impacto.

        Args:
            persistentes: lista de missoes persistentes (4+ semanas)
            dados_unidades: dict com dados por unidade

        Returns:
            lista de dicts [{titulo, analise, opcoes, impacto, recomendacao}, ...]
        """
        if not persistentes:
            return []

        prompt = f"""Analise estas {len(persistentes)} situacoes persistentes (4+ semanas sem resolucao)
e gere ate 3 DECISOES estrategicas para a CEO:

SITUACOES:
{json.dumps(persistentes[:5], ensure_ascii=False, indent=2, default=str)}

Para cada decisao, forneça:
1. Titulo claro
2. Analise: POR QUE esta situacao persiste?
3. Opcoes de acao (2-3 alternativas)
4. Impacto estimado
5. Recomendacao

Responda em JSON: [{{"titulo": "...", "analise": "...", "opcoes": ["...", "..."], "impacto": "...", "recomendacao": "..."}}]"""

        resultado = _chamar_llm(prompt, max_tokens=3000)
        if resultado:
            try:
                # Tentar parsear JSON do resultado
                inicio = resultado.find("[")
                fim = resultado.rfind("]") + 1
                if inicio >= 0 and fim > inicio:
                    return json.loads(resultado[inicio:fim])
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback: formato simples
        return self._decisoes_template(persistentes)

    def preparar_reuniao(self, tipo_reuniao, dados_rede, unidade=None):
        """Roteiro inteligente de reuniao.

        Args:
            tipo_reuniao: 'FLASH', 'FOCO', 'CRISE' ou 'ESTRATEGICA'
            dados_rede: dict com dados consolidados
            unidade: codigo da unidade (None = toda rede)

        Returns:
            dict com roteiro estruturado
        """
        prompt = f"""Gere um roteiro de reuniao {tipo_reuniao} para o PEEX.

TIPO: {tipo_reuniao}
{'UNIDADE: ' + unidade if unidade else 'REDE: todas as 4 unidades'}

DADOS:
{json.dumps(dados_rede, ensure_ascii=False, indent=2, default=str)[:3000]}

Gere o roteiro com:
- Abertura (o que dizer, como comecar)
- Dados (quais mostrar, em que ordem)
- Discussao (perguntas-chave, pontos de atencao)
- Compromissos (o que cada um deve sair com)
- Encerramento (celebracao, mensagem final)

Para cada bloco, inclua FALAS SUGERIDAS (o que a CEO deve dizer literalmente)."""

        resultado = _chamar_llm(prompt, max_tokens=3000,
                                modelo="claude-sonnet-4-6")
        if resultado:
            return {"roteiro_llm": resultado, "tipo": tipo_reuniao, "fonte": "llm"}

        return {"roteiro_llm": None, "tipo": tipo_reuniao, "fonte": "template"}

    def competir_propostas(self, dados_rede, pergunta_ceo):
        """2-3 propostas concorrentes para a CEO decidir.

        Args:
            dados_rede: dict com dados consolidados
            pergunta_ceo: pergunta estrategica da CEO

        Returns:
            lista de dicts [{nome, resumo, pros, contras, impacto, prazo}, ...]
        """
        prompt = f"""A CEO do Colegio ELO pergunta:
"{pergunta_ceo}"

DADOS ATUAIS DA REDE:
{json.dumps(dados_rede, ensure_ascii=False, indent=2, default=str)[:2000]}

Gere 3 propostas concorrentes:

1. PROPOSTA CONSERVADORA (menor risco, baseada em praticas comprovadas)
2. PROPOSTA INOVADORA (maior impacto, mas requer mais recursos/mudanca)
3. PROPOSTA BASEADA EM DADOS (o que os numeros sugerem como melhor caminho)

Para cada proposta:
- Nome criativo (3-5 palavras)
- Resumo (2-3 frases)
- Pros (2-3 pontos)
- Contras (1-2 pontos)
- Impacto estimado
- Prazo para resultados

Responda em JSON: [{{"nome": "...", "resumo": "...", "pros": [...], "contras": [...], "impacto": "...", "prazo": "..."}}]"""

        resultado = _chamar_llm(prompt, max_tokens=3000,
                                modelo="claude-sonnet-4-6")
        if resultado:
            try:
                inicio = resultado.find("[")
                fim = resultado.rfind("]") + 1
                if inicio >= 0 and fim > inicio:
                    return json.loads(resultado[inicio:fim])
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback
        return self._propostas_template(pergunta_ceo)

    def diagnosticar_gap(self, estado_atual):
        """Compara o planejado (docs Obsidian) vs implementado.

        Args:
            estado_atual: dict com status de implementacao

        Returns:
            dict com {alinhados, parciais, faltando, recomendacoes}
        """
        contexto_docs = _carregar_contexto_docs()
        if not contexto_docs:
            return {"erro": "Documentos Obsidian nao encontrados"}

        prompt = f"""Compare o PLANEJADO (documentos de referencia) com o IMPLEMENTADO:

ESTADO ATUAL:
{json.dumps(estado_atual, ensure_ascii=False, indent=2, default=str)[:3000]}

Identifique:
1. Conceitos ALINHADOS (implementados conforme planejado)
2. Conceitos PARCIAIS (implementados mas incompletos)
3. Conceitos FALTANDO (planejados mas nao implementados)
4. Recomendacoes de priorizacao

Responda em JSON: {{"alinhados": [...], "parciais": [...], "faltando": [...], "recomendacoes": [...]}}"""

        resultado = _chamar_llm(prompt, max_tokens=4000,
                                modelo="claude-sonnet-4-6")
        if resultado:
            try:
                inicio = resultado.find("{")
                fim = resultado.rfind("}") + 1
                if inicio >= 0 and fim > inicio:
                    return json.loads(resultado[inicio:fim])
            except (json.JSONDecodeError, ValueError):
                pass

        return {"alinhados": [], "parciais": [], "faltando": [], "recomendacoes": ["Execute audit_peex.py para analise detalhada"]}

    # ========== HELPERS TEMPLATE (FALLBACK) ==========

    def _formatar_dados_resumo(self, dados):
        """Formata dados do resumo para o prompt."""
        if not dados:
            return "Dados indisponiveis."
        linhas = []
        for un, vals in dados.items():
            if un == "TOTAL":
                continue
            conf = vals.get("pct_conformidade_media", 0)
            freq = vals.get("frequencia_media", 0)
            risco = vals.get("pct_alunos_risco", 0)
            linhas.append(f"  {un}: Conf={conf:.0f}%, Freq={freq:.0f}%, Risco={risco:.0f}%")
        return "\n".join(linhas) if linhas else "Sem dados por unidade."

    def _formatar_missoes(self, missoes_rede):
        """Formata missoes para o prompt."""
        if not missoes_rede:
            return "Nenhuma missao ativa."
        linhas = []
        for un, missoes in missoes_rede.items():
            urgentes = sum(1 for m in missoes if m.get("nivel") == "URGENTE")
            linhas.append(f"  {un}: {len(missoes)} missoes ({urgentes} urgentes)")
        return "\n".join(linhas)

    def _formatar_historico(self, historico):
        """Formata historico para o prompt."""
        if not historico:
            return "Sem historico."
        ultimas = historico[-3:]
        linhas = []
        for h in ultimas:
            linhas.append(f"  Sem {h.get('semana', '?')}: Conf Rede={h.get('conformidade_rede', 0):.0f}%")
        return "\n".join(linhas)

    def _narrar_semana_template(self, dados_resumo, historico, semana):
        """Narrativa via template (fallback quando LLM indisponivel)."""
        from narrativa import gerar_narrativa_ceo
        import pandas as pd
        from utils import DATA_DIR

        resumo_path = DATA_DIR / "resumo_Executivo.csv"
        resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()
        return gerar_narrativa_ceo(resumo_df, historico, semana)

    def _decisoes_template(self, persistentes):
        """Decisoes via template (fallback)."""
        from narrativa import gerar_decisoes_ceo
        return gerar_decisoes_ceo(persistentes)

    def _propostas_template(self, pergunta):
        """Propostas via template (fallback quando LLM indisponivel)."""
        return [
            {
                "nome": "Manutencao de Curso",
                "resumo": "Continuar com as estrategias atuais, reforçando o acompanhamento semanal.",
                "pros": ["Menor resistencia", "Sem custos adicionais"],
                "contras": ["Resultados lentos"],
                "impacto": "Incremental",
                "prazo": "4-6 semanas",
            },
            {
                "nome": "Intervencao Focada",
                "resumo": "Concentrar recursos nas 2 unidades com piores indicadores.",
                "pros": ["Impacto rapido onde mais precisa", "Mensuravel"],
                "contras": ["Outras unidades podem sentir falta de atencao"],
                "impacto": "Medio-alto nas unidades foco",
                "prazo": "2-3 semanas",
            },
            {
                "nome": "Redesenho Estrutural",
                "resumo": "Revisao completa das rotinas e processos com envolvimento de toda equipe.",
                "pros": ["Resolve raiz do problema", "Engaja equipe"],
                "contras": ["Demanda tempo e energia", "Risco de resistencia"],
                "impacto": "Transformacional",
                "prazo": "6-8 semanas",
            },
        ]


# ========== FUNCAO PUBLICA DO ROBO ANALISTA ==========

_ANALISTA_FILE = Path(__file__).parent / "power_bi" / "analista_output.json"


def executar_analista():
    """Roda domingo 23h (apos ESTRATEGISTA).
    Le TODOS os outputs dos outros robos + docs Obsidian.
    Gera narrativa enriquecida + diagnostico semanal.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    logger.info("Analista: iniciando analise integrada...")

    try:
        from utils import WRITABLE_DIR, DATA_DIR, calcular_semana_letiva
        import pandas as pd

        semana = calcular_semana_letiva()
        analista = AnalistaELO()

        # Carregar dados
        resumo_path = DATA_DIR / "resumo_Executivo.csv"
        resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()

        # Converter resumo para dict
        dados_resumo = {}
        if not resumo_df.empty:
            for _, row in resumo_df.iterrows():
                dados_resumo[row.get("unidade", "")] = row.to_dict()

        # Carregar historico
        hist_path = WRITABLE_DIR / "historico_semanas.json"
        historico = []
        if hist_path.exists():
            try:
                with open(hist_path, "r", encoding="utf-8") as f:
                    historico = json.load(f)
            except Exception:
                pass

        # Carregar missoes
        missoes_path = WRITABLE_DIR / "missoes_pregeradas.json"
        missoes_rede = {}
        if missoes_path.exists():
            try:
                with open(missoes_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                missoes_rede = data.get("unidades", {})
            except Exception:
                pass

        # Carregar persistentes
        from missoes_historico import obter_persistentes
        persistentes = obter_persistentes(min_semanas=4)

        # Gerar narrativa enriquecida
        narrativa = analista.narrar_semana(dados_resumo, historico, missoes_rede, semana)

        # Gerar decisoes analisadas
        decisoes = analista.analisar_decisoes(persistentes, dados_resumo)

        # Diagnostico gap (simplificado)
        estado_atual = {
            "semana": semana,
            "conformidade_rede": dados_resumo.get("TOTAL", {}).get("pct_conformidade_media", 0),
            "n_missoes": sum(len(ms) for ms in missoes_rede.values()),
            "n_persistentes": len(persistentes),
            "robos_ativos": ["VIGILIA", "ESTRATEGISTA", "CONSELHEIRO", "COMPARADOR", "PREDITOR", "RETROALIMENTADOR", "PREPARADOR", "ANALISTA"],
        }

        output = {
            "gerado_em": inicio.isoformat(),
            "semana": semana,
            "narrativa_enriquecida": narrativa,
            "decisoes_analisadas": decisoes,
            "estado_atual": estado_atual,
            "llm_disponivel": _llm_disponivel(),
            "fonte": "llm" if _llm_disponivel() else "template",
        }

        with open(_ANALISTA_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Analista: concluido em {duracao:.1f}s (fonte: {output['fonte']})")

        return {
            "ok": True,
            "semana": semana,
            "duracao": duracao,
            "fonte": output["fonte"],
        }

    except Exception as e:
        logger.error(f"Analista: erro - {e}", exc_info=True)
        return {"ok": False, "erro": str(e)}


def carregar_analista():
    """Carrega output do analista pre-gerado."""
    if _ANALISTA_FILE.exists():
        try:
            with open(_ANALISTA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}
