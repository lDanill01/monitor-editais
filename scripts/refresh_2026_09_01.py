#!/usr/bin/env python3
"""Consolida a rodada de monitoramento de 01/09/2026 a partir da base anterior.

As inclusoes, exclusoes e correcoes deste ciclo foram conferidas nas paginas
oficiais listadas no relatorio gerado. O script preserva os campos estruturados
e recalcula os prazos em relacao a data de referencia.
"""
import json
from datetime import date, datetime
from pathlib import Path
from md_to_json import parse_markdown

ROOT = Path(__file__).resolve().parent.parent
REF = date(2026, 9, 1)
OUT = ROOT / "data" / "Monitoramento_Editais_Inovacao_2026-09-01.md"


def deadline(value):
    """Devolve a primeira data dd/mm/aaaa presente no prazo, se existir."""
    import re
    match = re.search(r"(\d{2}/\d{2}/\d{4})", value)
    return datetime.strptime(match.group(1), "%d/%m/%Y").date() if match else None


def cell(value):
    return str(value or "—").replace("|", "/").replace("\n", " ")


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(cell(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def main():
    source = json.loads((ROOT / "data" / "editais.json").read_text(encoding="utf-8"))
    # As justificativas detalhadas pertencem à rodada de 27/08; o JSON atual
    # pode já ter sido regenerado e, portanto, não deve ser a única cópia.
    legacy = parse_markdown((ROOT / "data" / "Monitoramento_Editais_Inovacao_2026-08-27.md").read_text(encoding="utf-8"))
    adhesion_source = legacy["aderencia"]
    editais = source["editais"]

    # Comunicado oficial da Finep, publicado em 28/08, prorrogou seis chamadas
    # da Rodada 2. Quatro haviam saído da base na rodada anterior e são
    # reincorporadas a partir do relatório de 27/08.
    finep_prorrogados = {
        "FINEP Mais Inovação Brasil R2 – Transição Energética": "02/09/2026",
        "FINEP Mais Inovação Brasil R2 – Transformação Mineral": "04/09/2026",
        "FINEP Mais Inovação Brasil R2 – Saúde (Empresas)": "18/09/2026",
        "FINEP Mais Inovação Brasil R2 – Mobilidade Sustentável": "25/09/2026",
        "FINEP Mais Inovação Brasil R2 – Base Industrial de Defesa": "02/10/2026",
    }
    existing = {x["edital"] for x in editais}
    editais.extend(x.copy() for x in legacy["editais"] if x["edital"] in finep_prorrogados and x["edital"] not in existing)
    for edital in editais:
        if edital["edital"] in finep_prorrogados:
            edital["encerramento"] = finep_prorrogados[edital["edital"]]
            edital["status"] = "aberto"
            edital["link"] = "https://faleconosco.finep.gov.br/web/guest/w/aten%C3%A7%C3%A3o-novos-prazos"
            edital["exigencias"] = edital["exigencias"].replace("fluxo contínuo", "prazo prorrogado")

    # Encerrados ate a data de referencia saem da tabela principal.
    active = []
    for edital in editais:
        end = deadline(edital["encerramento"])
        if edital["status"] == "aberto" and end and end < REF:
            continue
        if edital["status"] == "aberto" and end:
            edital["dias"] = "0 (hoje)" if end == REF else str((end - REF).days)
        active.append(edital)

    fica = {
        "edital": "FICA-SP – Fixação e Incentivo à Carreira Acadêmica em São Paulo (Ciclo 1)",
        "fonte": "FAPESP/CNPq/CAPES",
        "status": "aberto",
        "abertura": "01/09/2026",
        "encerramento": "30/09/2026",
        "dias": "29",
        "tipo_publico": "Pessoa Física",
        "publico": "Pesquisadores doutores vinculados a ICTs/IES de São Paulo",
        "valor": "Até R$ 1,5 mi/proposta",
        "contrapartida": "Não exige",
        "exigencias": "Submissão via SAGe; elegibilidade conforme edital; execução em SP",
        "link": "https://fapesp.br/chamadas/",
        "grupo": None,
    }
    # A execução deve ser idempotente: a chamada já pode estar na base gerada
    # por uma rodada anterior deste mesmo script.
    active = [x for x in active if x["edital"] != fica["edital"]]
    active.append(fica)

    order = {"aberto": 0, "continuo": 1, "breve": 2}
    active.sort(key=lambda x: (order[x["status"]], deadline(x["encerramento"]) or date.max, x["edital"]))

    # A base anterior usava rótulos abreviados na tabela de aderência. Esta
    # chave explicita a ligação e impede que a atualização descarte avaliações.
    aliases = {
        "FINEP Mais Inovação Brasil R2 – Transição Energética": "FINEP Transição Energética",
        "FINEP Mais Inovação Brasil R2 – Transformação Mineral": "FINEP Transformação Mineral",
        "FINEP Mais Inovação Brasil R2 – Saúde (Empresas)": "FINEP Saúde (Empresas)",
        "FINEP Mais Inovação Brasil R2 – Mobilidade Sustentável": "FINEP Mobilidade Sustentável",
        "Base Industrial de Defesa": "FINEP Base Industrial de Defesa",
        "Cadeias Agroindustriais": "FINEP Agroindustriais Sustentáveis",
        "Tecnologias Digitais": "FINEP Tecnologias Digitais",
        "Semicondutores": "FINEP Semicondutores",
        "Biotecnologia": "CNPq Biotecnologia",
        "RHAE IA": "CNPq RHAE IA",
        "MAI/DAI": "CNPq MAI/DAI",
        "Atlânticas": "CNPq Atlânticas",
        "ERC-CONFAP": "CNPq ERC-CONFAP",
        "Apoio a Eventos": "CNPq Eventos de Empreendedorismo",
        "PAE-MS": "FUNDECT PAE-MS",
        "PICTEC": "FUNDECT PICTEC",
        "Centelha 3 RJ": "FAPERJ Centelha 3 RJ",
        "SC Inovadora": "FAPESC SC Inovadora",
        "Transição Energética (Fase 1)": "FAPESP PIPE (Soberania Digital / Jornada / Transição Energética)",
        "1ª Rodada": "FAPESP PIPE (Soberania Digital / Jornada / Transição Energética)",
        "JSPS Japão": "FAPESP–JSPS Japão",
        "RCN (Noruega)": "FINEP-RCN Noruega",
        "Eurostars": "Eurostars Call 11",
        "British Council": "British Council Researcher Challenges",
        "Raw Materials": "RAMP (Raw Materials)",
        "Ohio State": "FAPESP–Ohio State",
        "PRONEX": "FAPESP PRONEX",
        "Spain (CDTI)": "Spain-CDTI Brazil",
        "Biorrefinarias": "FAPESP–NWO Biorrefinarias",
        "Desafios da Amazônia": "Desafios da Amazônia",
        "Tecnova": "Tecnova 2026/2027",
        "BNDES": "BNDES Mais Inovação",
        "EMBRAPII": "EMBRAPII (fluxo contínuo)",
        "Agricultura Familiar": "FINEP Agricultura Familiar",
        "Saúde Digital": "Ministério da Saúde – Saúde Digital",
        "Water4All": "Water4All (Em breve)",
        "Biodiversa": "Biodiversa+ (Em breve)",
        "Sustainable Blue": "Sustainable Blue Economy (Em breve)",
    }
    adh = []
    for edital in active:
        alias = next((value for key, value in aliases.items() if key in edital["edital"]), edital["edital"])
        previous = next((x for x in adhesion_source if x["edital"] == edital["edital"]), None)
        if previous is None:
            previous = next((x for x in adhesion_source if x["edital"].startswith(alias) or alias.startswith(x["edital"])), None)
        if previous:
            adh.append({**previous, "edital": edital["edital"]})
        else:
            adh.append({"edital": edital["edital"], "institutos": "Não avaliado com confiança", "grau": "none", "foco_educacional": "Não encontrado", "justificativa": "A fonte oficial não permitiu avaliar a aderência institucional com confiança."})
    adh = [x for x in adh if x["edital"] != fica["edital"]]
    adh.append({
        "edital": fica["edital"],
        "institutos": "IST Alimentos; IST Eficiência Operacional; ISI Biomassa",
        "grau": "media",
        "foco_educacional": "Não",
        "justificativa": "Abrange linhas estratégicas de alimentos, biotecnologia, energia e transição digital, mas é restrito a ICTs/IES de São Paulo.",
    })
    adh.sort(key=lambda x: x["edital"])

    nao_confirmado = [x for x in source["nao_confirmado"] if "Universal" not in x["edital"]]
    abertos = [x for x in active if x["status"] == "aberto"]
    continuos = [x for x in active if x["status"] == "continuo"]
    breves = [x for x in active if x["status"] == "breve"]
    urgentes = [x for x in abertos if (deadline(x["encerramento"]) - REF).days <= 7]

    edital_rows = []
    for e in active:
        status = {"aberto": "Aberto", "continuo": "Fluxo contínuo", "breve": "Em breve"}[e["status"]]
        edital_rows.append({"Edital": e["edital"], "Fonte": e["fonte"], "Status": status,
                            "Abertura": e["abertura"], "Encerramento": e["encerramento"], "Dias restantes": e["dias"],
                            "Público-alvo": e["publico"], "Valor/Faixa": e["valor"], "Contrapartida": e["contrapartida"],
                            "Principais exigências": e["exigencias"], "Link": e["link"]})

    lines = [
        "# Monitoramento de Editais de Inovação",
        "**Data de referência:** 2026-09-01 · terça-feira — base para toda classificação de status/prazos.",
        "**Escopo:** Nacional (BR), estadual (prioridade MS/Centro-Oeste) e internacionais com elegibilidade do Brasil.",
        "**Metodologia:** Pesquisa e revalidação em fontes oficiais em 01/09/2026. Status e prazos foram comparados com a data do sistema; dados ausentes permanecem explicitamente sinalizados.",
        "",
        "## Novidades desde a última atualização (27/08/2026)",
        "",
        "### Novos editais abertos desde 27/08",
        "",
        table(["Edital", "Fonte", "Abertura", "Encerramento", "Destaque"], [{"Edital": fica["edital"], "Fonte": fica["fonte"], "Abertura": fica["abertura"], "Encerramento": fica["encerramento"], "Destaque": "Até R$ 1,5 mi por proposta; execução restrita ao estado de São Paulo."}]),
        "",
        "### Editais encerrados desde 27/08",
        "",
        table(["Edital", "Fonte", "Motivo do encerramento"], [
            {"Edital": "SENAI+GIZ – Fit for Carbon Pricing (CBAM)", "Fonte": "SENAI + GIZ", "Motivo do encerramento": "Prazo informado: 28/08/2026."},
            {"Edital": "FINEP Mais Inovação Brasil R2 – Economia Circular e Cidades Sustentáveis", "Fonte": "MCTI/FINEP/FNDCT", "Motivo do encerramento": "Prazo informado: 31/08/2026; não consta no comunicado de prorrogação de 28/08."},
            {"Edital": "FAPESP-FACEPE 2026; CNPq ProÁfrica 2026", "Fonte": "FAPESP/FACEPE; CNPq/MCTI", "Motivo do encerramento": "Prazo informado: 31/08/2026."},
        ]),
        "",
        "### Alterações de prazo",
        "",
        table(["Edital", "Alteração"], [{"Edital": "FINEP Mais Inovação Brasil R2 – seis chamadas da Rodada 2", "Alteração": "Comunicado oficial de 28/08 prorrogou Transição Energética (02/09), Transformação Mineral (04/09), Saúde (18/09), Mobilidade Sustentável (25/09) e Base Industrial de Defesa (02/10); os quatro primeiros foram reincorporados."}]),
        "",
        "## Resumo Executivo",
        "",
        f"- **Abertos agora:** {len(abertos)} editais com inscrições vigentes em 01/09/2026, mais {len(continuos)} linhas de fluxo contínuo.",
        f"- **Em breve:** {len(breves)} chamadas internacionais com abertura programada para setembro de 2026.",
        f"- **Alerta (encerramento em ≤ 7 dias):** {len(urgentes)} editais fecham em até 7 dias: " + "; ".join(f"{x['edital']} ({x['encerramento']})" for x in urgentes) + ".",
        f"- **Não confirmado:** {len(nao_confirmado)} itens permanecem sem cronograma oficial claro após busca aprofundada; estão listados ao final.",
        "",
        "> **Alerta de prazo:** O Programa Desafios da Amazônia encerra a pré-proposta hoje (01/09); FINEP Transição Energética e PIPE Transição Energética, em 02/09; FAPESP-JSPS, em 03/09; e FINEP Transformação Mineral, em 04/09.",
        "",
        "## Tabela de Editais (ordenada por encerramento mais próximo)",
        "",
        table(["Edital", "Fonte", "Status", "Abertura", "Encerramento", "Dias restantes", "Público-alvo", "Valor/Faixa", "Contrapartida", "Principais exigências", "Link"], edital_rows),
        "",
        "## Editais \"Não confirmado\" (datas não extraídas após busca aprofundada)",
        "",
        table(["Edital", "Fonte", "Motivo"], [{"Edital": x["edital"], "Fonte": x["fonte"], "Motivo": x["motivo"]} for x in nao_confirmado]),
        "",
        "## Aderência com os institutos SENAI/MS",
        "",
        table(["Edital", "Instituto(s) com maior aderência", "Grau de aderência", "Foco educacional?", "Justificativa"], [{"Edital": x["edital"], "Instituto(s) com maior aderência": x["institutos"], "Grau de aderência": {"alta": "Alta", "media": "Média", "baixa": "Baixa", "none": "Sem aderência identificada"}[x["grau"]], "Foco educacional?": x["foco_educacional"], "Justificativa": x["justificativa"]} for x in adh]),
        "",
        "## Observações de método",
        "",
        "> A busca mantém o escopo amplo; a aderência é apenas uma camada de sinalização e não exclui editais da tabela principal.",
        "> FINEP: os prazos da Rodada 2 foram rechecados no comunicado oficial de 28/08; onde houve prorrogação, prevalece a nova data indicada pela Finep.",
        "> O CNPq/FNDCT nº 06/2026 – Universal foi removido de “Não confirmado”: a fonte anterior já indicava encerramento em 03/08/2026.",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Relatório salvo: {OUT}")
    print(f"Abertos={len(abertos)}; contínuos={len(continuos)}; em breve={len(breves)}; urgentes={len(urgentes)}; não confirmado={len(nao_confirmado)}")


if __name__ == "__main__":
    main()
