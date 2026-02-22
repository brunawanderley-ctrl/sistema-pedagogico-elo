# PEEX 2026 — Documentacao Preservada do Obsidian

Copia completa dos documentos originais de planejamento PEEX.
Fonte: `/Users/brunaviegas/Documents/Obsidian Vault/Planejamento Pedagógico Integrado 2026/`
Data da copia: 2026-02-21

## Documentos (13 arquivos, ~12.661 linhas)

| Arquivo | Linhas | Descricao |
|---------|--------|-----------|
| `guia_completo.md` | 637 | PEEX Command Center — Guia completo de operacao |
| `plano_definitivo.md` | 846 | Plano Definitivo PEEX 2026 — versao final aprovada |
| `sintese_final.md` | 1345 | Sintese Final — fusao dos 4 planos + 2 competidores |
| `plano_pedagogico_original.md` | 1217 | Plano Pedagogico Original (Time Vermelho) |
| `plano_sinais_original.md` | 1341 | Plano Sinais e Redes Original (Time Azul) |
| `plano_pedagogico_rival.md` | 997 | Plano Pedagogico Rival (contra-proposta) |
| `plano_sinais_rival.md` | 1239 | Plano Sinais Rival (contra-proposta) |
| `competidor_a.md` | 1252 | Competidor A — Anos Finais + EM |
| `competidor_b.md` | 1362 | Competidor B — Abordagem Disruptiva |
| `equipe_a_melhorias.md` | 1472 | Equipe A — Propostas de Melhorias BI |
| `equipe_b_melhorias.md` | 1246 | Equipe B — Propostas de Melhorias BI |
| `proposta_definitiva.md` | 415 | Proposta Definitiva do PEEX Command Center (Streamlit) |
| `indice_visao_geral.md` | 292 | Indice e Visao Geral do Planejamento Pedagogico |

## Arvore Intelectual

```
4 Planos Originais:
  ├── Plano Pedagogico Original (plano_pedagogico_original.md)
  ├── Plano Sinais Original (plano_sinais_original.md)
  ├── Plano Pedagogico Rival (plano_pedagogico_rival.md)
  └── Plano Sinais Rival (plano_sinais_rival.md)
      │
      ▼
2 Competidores:
  ├── Competidor A (competidor_a.md)
  └── Competidor B (competidor_b.md)
      │
      ▼
2 Equipes de Melhorias:
  ├── Equipe A (equipe_a_melhorias.md)
  └── Equipe B (equipe_b_melhorias.md)
      │
      ▼
Sintese Final (sintese_final.md)
      │
      ▼
Plano Definitivo (plano_definitivo.md) + Guia (guia_completo.md)
      │
      ▼
Proposta Definitiva (proposta_definitiva.md)
      │
      ▼
Implementacao (Sistema Streamlit atual)
```

## Como Usar

Estes documentos sao a base intelectual do PEEX. O motor LLM (`llm_engine.py`)
carrega-os como contexto para gerar narrativas, diagnosticos e propostas
alinhadas com a filosofia original do programa.

Para rastrear a genealogia de cada conceito implementado, consulte:
- `peex_pages/genealogia.py` (pagina Streamlit)
- `audit_peex.py` (script de auditoria planejado vs implementado)
