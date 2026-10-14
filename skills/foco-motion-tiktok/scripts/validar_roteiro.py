#!/usr/bin/env python3
"""Validação estrutural simples do JSON de episódio Foco Motion. Uso: python validar_roteiro.py episodio.json"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Uso: python validar_roteiro.py episodio.json")
        return 2
    dados = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    ep = dados["episodio"]
    cenas = ep["cenas"]
    erros = []
    total = ep["duracao_total_s"]
    if total <= 60:
        erros.append("A duração precisa superar 60 segundos para o objetivo atual de teste.")
    if not 12 <= len(cenas) <= 18:
        print("Aviso: quantidade sugerida para ~75s é 12 a 18 cenas.")
    anterior = 0
    requeridos = ["narracao", "visual", "movimento_camera", "motion_design", "prompt_visual", "sfx_musica", "transicao", "restricoes", "objetivo_de_retencao", "texto_tela", "ato"]
    for i, c in enumerate(cenas, 1):
        ini, fim, dur = c["inicio_s"], c["fim_s"], c["duracao_s"]
        if ini != anterior:
            erros.append(f"Cena {i} tem início {ini}, esperado {anterior}.")
        if fim <= ini or abs((fim - ini) - dur) > 0.001:
            erros.append(f"Cena {i} com tempos inválidos.")
        for campo in requeridos:
            if campo not in c or c[campo] is None:
                erros.append(f"Cena {i} sem campo {campo}.")
        anterior = fim
    if anterior != total:
        erros.append(f"Fim das cenas {anterior} não corresponde ao total {total}.")
    texto_cenas = " ".join(str(c.get("narracao", "")).strip() for c in cenas).strip()
    if ep.get("tts_text", "").strip() != texto_cenas:
        erros.append("tts_text deve ser a concatenação exata da narração das cenas.")
    if erros:
        print("FALHOU:\n- " + "\n- ".join(erros))
        return 1
    print(f"OK: {len(cenas)} cenas, {total} segundos e texto TTS consistente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
