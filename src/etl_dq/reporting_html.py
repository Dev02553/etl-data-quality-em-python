from __future__ import annotations

from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Any


DISPLAY_RULE_NAMES = {
    "required_customer_id": "ID do cliente obrigatório",
    "required_email": "E-mail obrigatório",
    "email_format": "Formato de e-mail inválido",
    "unique_customer_id": "ID do cliente duplicado",
    "allowed_country": "País fora do domínio esperado",
    "signup_date_valid_type": "Data de cadastro inválida",
    "signup_date_not_future": "Data de cadastro no futuro",
    "credit_limit_numeric_type": "Limite de crédito não numérico",
    "credit_limit_non_negative": "Limite de crédito negativo",
}

DISPLAY_RULE_DESCRIPTIONS = {
    "required_customer_id": "Verifica se o campo customer_id foi preenchido.",
    "required_email": "Verifica se o campo email foi preenchido.",
    "email_format": "Verifica se o e-mail está em um formato válido.",
    "unique_customer_id": "Verifica se o customer_id aparece apenas uma vez na base.",
    "allowed_country": "Verifica se o país informado está dentro do domínio esperado.",
    "signup_date_valid_type": "Verifica se a data de cadastro é válida.",
    "signup_date_not_future": "Verifica se a data de cadastro não está no futuro.",
    "credit_limit_numeric_type": "Verifica se o limite de crédito é numérico.",
    "credit_limit_non_negative": "Verifica se o limite de crédito é maior ou igual a zero.",
}

DISPLAY_SEVERITY = {
    "high": "Alta",
    "medium": "Média",
    "low": "Baixa",
}


def _row_to_dict(row: Any) -> dict[str, Any]:
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    if is_dataclass(row):
        return asdict(row)
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    if hasattr(row, "__dict__"):
        return {k: v for k, v in vars(row).items() if not k.startswith("_")}
    return {"value": row}


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _translate_rule_name(rule_code: Any) -> str:
    if rule_code is None:
        return ""
    return DISPLAY_RULE_NAMES.get(str(rule_code), str(rule_code))


def _translate_severity(severity: Any) -> str:
    if severity is None:
        return ""
    return DISPLAY_SEVERITY.get(str(severity).lower(), str(severity))


def _prettify_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pretty_rows: list[dict[str, Any]] = []

    for row in rows:
        raw_rule = row.get("rule_name") or row.get("rule")
        pretty_rows.append(
            {
                "Regra": _translate_rule_name(raw_rule),
                "Criticidade": _translate_severity(row.get("severity")),
                "O que foi verificado": row.get("description")
                or DISPLAY_RULE_DESCRIPTIONS.get(str(raw_rule), ""),
                "Falhas encontradas": row.get("failed_rows")
                or row.get("issue_count")
                or row.get("count")
                or row.get("affected_rows")
                or "",
                "Taxa de conformidade": row.get("pass_rate") or row.get("status") or "",
            }
        )

    return pretty_rows


def _prettify_evidence_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pretty_rows: list[dict[str, Any]] = []

    for row in rows:
        raw_rule = row.get("rule_name") or row.get("rule")
        pretty_rows.append(
            {
                "Linha": row.get("row_number") or row.get("row") or "",
                "Problema identificado": row.get("message") or "",
                "Regra": _translate_rule_name(raw_rule),
                "Criticidade": _translate_severity(row.get("severity")),
                "Campo": row.get("column_name") or row.get("column") or "",
                "Valor encontrado": row.get("invalid_value") or row.get("value") or "",
                "Arquivo de origem": row.get("source_file") or "",
            }
        )

    return pretty_rows


def _build_table(rows: list[dict[str, Any]], preferred_columns: list[str] | None = None) -> str:
    if not rows:
        return '<p class="empty">Sem dados para exibir.</p>'

    columns: list[str] = []
    if preferred_columns:
        for col in preferred_columns:
            if any(col in row for row in rows):
                columns.append(col)

    for row in rows:
        for key in row.keys():
            if key not in columns:
                columns.append(key)

    thead = "".join(f"<th>{escape(str(col))}</th>" for col in columns)

    body_rows = []
    for row in rows:
        cells = []
        for col in columns:
            value = row.get(col, "")
            text = escape(_format_value(value))

            if col == "Criticidade":
                sev = str(value).strip().lower()
                if sev == "alta":
                    text = '<span class="badge badge-alta">Alta</span>'
                elif sev in {"média", "media"}:
                    text = '<span class="badge badge-media">Média</span>'
                elif sev == "baixa":
                    text = '<span class="badge badge-baixa">Baixa</span>'

            cells.append(f"<td>{text}</td>")

        tds = "".join(cells)
        body_rows.append(f"<tr>{tds}</tr>")

    tbody = "".join(body_rows)

    return f"""
    <div class="table-wrap">
      <table>
        <thead>
          <tr>{thead}</tr>
        </thead>
        <tbody>
          {tbody}
        </tbody>
      </table>
    </div>
    """


def write_html_report(
    output_path: str | Path,
    summary_rows: list[Any],
    evidence_rows: list[Any],
    metadata: dict[str, Any] | None = None,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = metadata or {}
    summary_raw = [_row_to_dict(r) for r in (summary_rows or [])]
    evidence_raw = [_row_to_dict(r) for r in (evidence_rows or [])]

    total_rows = (
        metadata.get("total_rows")
        or metadata.get("rows_total")
        or metadata.get("input_rows")
        or 0
    )
    rows_with_issues = (
        metadata.get("rows_with_issues")
        or metadata.get("problem_rows")
        or metadata.get("invalid_rows")
        or len({r.get("row_number") or r.get("row") for r in evidence_raw if r})
        or 0
    )
    dq_score = (
        metadata.get("dq_score")
        or metadata.get("quality_score")
        or metadata.get("score")
        or 0
    )

    if isinstance(dq_score, (int, float)) and dq_score <= 1:
        dq_score_display = f"{dq_score * 100:.1f}%"
    else:
        try:
            dq_score_display = f"{float(dq_score):.1f}%"
        except Exception:
            dq_score_display = str(dq_score)

    try:
        score_value = float(str(dq_score_display).replace("%", "").strip())
    except Exception:
        score_value = 0.0

    if score_value >= 80:
        score_class = "score-good"
    elif score_value >= 60:
        score_class = "score-medium"
    else:
        score_class = "score-bad"

    summary = _prettify_summary_rows(summary_raw)
    evidence = _prettify_evidence_rows(evidence_raw)

    summary_table = _build_table(
        summary,
        preferred_columns=[
            "Regra",
            "Criticidade",
            "O que foi verificado",
            "Falhas encontradas",
            "Taxa de conformidade",
        ],
    )

    evidence_preview = _build_table(
        evidence[:50],
        preferred_columns=[
            "Linha",
            "Problema identificado",
            "Regra",
            "Criticidade",
            "Campo",
            "Valor encontrado",
            "Arquivo de origem",
        ],
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Relatório de Qualidade dos Dados</title>
  <style>
    body {{
      font-family: Arial, Helvetica, sans-serif;
      margin: 0;
      padding: 32px 24px 40px;
      background: #f5f7fb;
      color: #111827;
    }}
    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.2;
    }}
    h2 {{
      margin: 0 0 16px;
      font-size: 18px;
    }}
    .intro {{
      color: #4b5563;
      max-width: 950px;
      line-height: 1.7;
      margin: 0 0 24px;
      font-size: 15px;
    }}
    .metrics {{
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      margin: 20px 0 28px;
    }}
    .card {{
      background: #ffffff;
      border-radius: 14px;
      padding: 18px 22px;
      min-width: 220px;
      border: 1px solid #e5e7eb;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
    }}
    .card .label {{
      font-size: 13px;
      color: #6b7280;
      margin-bottom: 8px;
    }}
    .card .value {{
      font-size: 30px;
      font-weight: 700;
      color: #111827;
    }}
    .section {{
      background: #ffffff;
      border-radius: 14px;
      padding: 22px;
      margin-bottom: 22px;
      border: 1px solid #e5e7eb;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid #e5e7eb;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f3f4f6;
      color: #111827;
      font-weight: 600;
      position: sticky;
      top: 0;
      z-index: 1;
    }}
    tbody tr:nth-child(even) {{
      background: #fafafa;
    }}
    tbody tr:hover {{
      background: #f9fafb;
    }}
    .table-wrap {{
      overflow-x: auto;
      border-radius: 10px;
    }}
    .empty {{
      color: #6b7280;
      font-style: italic;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      line-height: 1.2;
      white-space: nowrap;
    }}
    .badge-alta {{
      background: #fee2e2;
      color: #991b1b;
    }}
    .badge-media {{
      background: #fef3c7;
      color: #92400e;
    }}
    .badge-baixa {{
      background: #dcfce7;
      color: #166534;
    }}
    .score-good {{
      color: #166534;
    }}
    .score-medium {{
      color: #92400e;
    }}
    .score-bad {{
      color: #991b1b;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Relatório de Qualidade dos Dados</h1>
    <p class="intro">
      Este relatório apresenta os principais problemas encontrados na base analisada
      e ajuda a identificar rapidamente quais registros precisam de ajuste antes do uso
      em relatórios, análises ou processos operacionais.
    </p>

    <div class="metrics">
      <div class="card">
        <div class="label">Registros analisados</div>
        <div class="value">{escape(str(total_rows))}</div>
      </div>
      <div class="card">
        <div class="label">Registros com inconsistências</div>
        <div class="value">{escape(str(rows_with_issues))}</div>
      </div>
      <div class="card">
        <div class="label">Índice de qualidade</div>
        <div class="value {score_class}">{escape(dq_score_display)}</div>
      </div>
    </div>

    <div class="section">
      <h2>Visão geral das validações</h2>
      {summary_table}
    </div>

    <div class="section">
      <h2>Principais inconsistências encontradas</h2>
      {evidence_preview}
    </div>
  </div>
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
    return output_path