"""
Auditoria PEEX — Gap Analysis
Conta conceitos implementados/parciais/faltando/novos e salva resumo em JSON.

Uso:
    python audit_peex.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

# Garantir que peex_pages/ esteja no path para importar CONCEITOS_PEEX
sys.path.insert(0, str(Path(__file__).parent / "peex_pages"))
sys.path.insert(0, str(Path(__file__).parent))

from peex_pages.genealogia import CONCEITOS_PEEX
from utils import WRITABLE_DIR


def auditar_conceitos():
    """Analisa todos os conceitos PEEX e gera resumo de gap."""

    total = len(CONCEITOS_PEEX)
    contagem = Counter(c["status"] for c in CONCEITOS_PEEX)

    n_impl = contagem.get("implementado", 0)
    n_parcial = contagem.get("parcial", 0)
    n_faltando = contagem.get("faltando", 0)
    n_novo = contagem.get("novo", 0)

    pct_impl = (n_impl / total * 100) if total else 0
    pct_concluido = ((n_impl + n_parcial) / total * 100) if total else 0

    # Agrupar por origem
    origens = {}
    for c in CONCEITOS_PEEX:
        origem = c["origem"]
        if origem not in origens:
            origens[origem] = {"total": 0, "implementado": 0, "parcial": 0, "faltando": 0, "novo": 0}
        origens[origem]["total"] += 1
        origens[origem][c["status"]] += 1

    # Listar faltando
    faltando_lista = [
        {"conceito": c["conceito"], "origem": c["origem"], "sintese": c["sintese"]}
        for c in CONCEITOS_PEEX if c["status"] == "faltando"
    ]

    # Listar parciais
    parciais_lista = [
        {"conceito": c["conceito"], "origem": c["origem"], "arquivo": c["arquivo"]}
        for c in CONCEITOS_PEEX if c["status"] == "parcial"
    ]

    # Listar novos
    novos_lista = [
        {"conceito": c["conceito"], "origem": c["origem"], "arquivo": c["arquivo"]}
        for c in CONCEITOS_PEEX if c["status"] == "novo"
    ]

    resumo = {
        "gerado_em": datetime.now().isoformat(),
        "total_conceitos": total,
        "implementado": n_impl,
        "parcial": n_parcial,
        "faltando": n_faltando,
        "novo": n_novo,
        "pct_implementado": round(pct_impl, 1),
        "pct_concluido_ou_parcial": round(pct_concluido, 1),
        "por_origem": origens,
        "faltando_lista": faltando_lista,
        "parciais_lista": parciais_lista,
        "novos_lista": novos_lista,
    }

    return resumo


def salvar_resumo(resumo):
    """Salva resumo em WRITABLE_DIR/audit_peex_gap.json."""
    output_path = WRITABLE_DIR / "audit_peex_gap.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    return output_path


def main():
    """Executa auditoria e exibe resultado."""
    print("=" * 60)
    print("  AUDITORIA PEEX — Gap Analysis")
    print("=" * 60)
    print()

    resumo = auditar_conceitos()

    print(f"Total de conceitos rastreados: {resumo['total_conceitos']}")
    print()
    print(f"  Implementados:  {resumo['implementado']:>3}  ({resumo['pct_implementado']:.1f}%)")
    print(f"  Parciais:       {resumo['parcial']:>3}")
    print(f"  Faltando:       {resumo['faltando']:>3}")
    print(f"  Novos:          {resumo['novo']:>3}")
    print()
    print(f"  Concluido/Parcial: {resumo['pct_concluido_ou_parcial']:.1f}%")
    print()

    if resumo["faltando_lista"]:
        print("-" * 60)
        print("  FALTANDO:")
        for item in resumo["faltando_lista"]:
            print(f"    - {item['conceito']} (origem: {item['origem']})")
        print()

    if resumo["parciais_lista"]:
        print("-" * 60)
        print("  PARCIAIS:")
        for item in resumo["parciais_lista"]:
            print(f"    - {item['conceito']} -> {item['arquivo']}")
        print()

    if resumo["novos_lista"]:
        print("-" * 60)
        print("  NOVOS:")
        for item in resumo["novos_lista"]:
            print(f"    - {item['conceito']} -> {item['arquivo']}")
        print()

    print("-" * 60)
    print("  POR ORIGEM:")
    for origem, stats in sorted(resumo["por_origem"].items(), key=lambda x: -x[1]["total"]):
        print(f"    {origem}: {stats['total']} total, {stats['implementado']} impl, "
              f"{stats['parcial']} parcial, {stats['faltando']} faltando, {stats['novo']} novo")
    print()

    output_path = salvar_resumo(resumo)
    print("=" * 60)
    print(f"  Resumo salvo em: {output_path}")
    print("=" * 60)

    return resumo


if __name__ == "__main__":
    main()
