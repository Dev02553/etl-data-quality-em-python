from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .models import DQIssue
from .reporting import write_workbook
from .rules import build_rules


def _discover_csv_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted([path for path in input_path.glob("*.csv") if path.is_file()])
    raise FileNotFoundError(f"Input não encontrado: {input_path}")


def _extract(input_path: Path) -> tuple[pd.DataFrame, list[dict], list[str]]:
    csv_files = _discover_csv_files(input_path)
    if not csv_files:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em: {input_path}")

    dataframes: list[pd.DataFrame] = []
    stage_logs: list[dict] = []
    source_files: list[str] = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df = df.copy()
        df["source_file"] = csv_file.name
        dataframes.append(df)
        source_files.append(csv_file.name)
        stage_logs.append(
            {
                "stage": "extract",
                "checkpoint": f"Arquivo lido: {csv_file.name}",
                "details": f"{len(df)} linha(s) extraída(s)",
            }
        )

    extracted = pd.concat(dataframes, ignore_index=True)
    return extracted, stage_logs, source_files


def _transform(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    transformed = df.copy()

    if "email" in transformed.columns:
        transformed["email"] = transformed["email"].astype(str).str.strip().str.lower()
    if "country" in transformed.columns:
        transformed["country"] = transformed["country"].astype(str).str.strip().str.upper()
    if "signup_date" in transformed.columns:
        transformed["signup_date"] = transformed["signup_date"].astype(str).str.strip()

    transformed.insert(0, "row_number", range(1, len(transformed) + 1))

    stage_logs = [
        {
            "stage": "transform",
            "checkpoint": "Padronização aplicada",
            "details": "Normalização de email/country/signup_date e inclusão de row_number.",
        }
    ]
    return transformed, stage_logs


REQUIRED_COLUMNS = {"customer_id", "email", "country", "signup_date", "credit_limit"}


def _validate(df: pd.DataFrame) -> tuple[list[dict], list[dict], list[dict]]:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {sorted(missing)}")

    issue_rows: list[dict] = []
    summary_rows: list[dict] = []
    stage_logs: list[dict] = []

    for rule in build_rules():
        mask = rule.evaluator(df).fillna(False)
        failed = df.loc[mask]

        for _, row in failed.iterrows():
            issue = DQIssue(
                row_number=int(row["row_number"]),
                rule_name=rule.name,
                severity=rule.severity,
                column_name=rule.column_name,
                message=rule.message_builder(row),
                invalid_value=row.get(rule.column_name),
                source_file=row.get("source_file"),
            )
            issue_rows.append(
                {
                    "row_number": issue.row_number,
                    "rule_name": issue.rule_name,
                    "severity": issue.severity,
                    "column_name": issue.column_name,
                    "message": issue.message,
                    "invalid_value": issue.invalid_value,
                    "source_file": issue.source_file,
                }
            )

        summary_rows.append(
            {
                "rule_name": rule.name,
                "severity": rule.severity,
                "description": rule.description,
                "failed_rows": int(mask.sum()),
                "pass_rate": float(1 - (mask.mean() if len(df) else 0)),
            }
        )
        stage_logs.append(
            {
                "stage": "validate",
                "checkpoint": f"Regra executada: {rule.name}",
                "details": f"{int(mask.sum())} falha(s)",
            }
        )

    return issue_rows, summary_rows, stage_logs


def run_pipeline(input_path: str | Path, output_path: str | Path) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)

    extracted_df, extract_logs, source_files = _extract(input_path)
    transformed_df, transform_logs = _transform(extracted_df)
    issue_rows, summary_rows, validate_logs = _validate(transformed_df)

    evidence_df = pd.DataFrame(issue_rows)
    row_issue_count = evidence_df["row_number"].nunique() if not evidence_df.empty else 0

    transformed_df["dq_issue_count"] = 0
    transformed_df["dq_status"] = "PASS"

    if not evidence_df.empty:
        counts = evidence_df.groupby("row_number").size().to_dict()
        transformed_df["dq_issue_count"] = transformed_df["row_number"].map(counts).fillna(0).astype(int)
        transformed_df["dq_status"] = transformed_df["dq_issue_count"].gt(0).map({True: "FAIL", False: "PASS"})

    dq_score = float(1 - (row_issue_count / len(transformed_df))) if len(transformed_df) else 1.0
    failed_rules = int(sum(1 for row in summary_rows if row["failed_rows"] > 0))

    metadata = {
        "source_file": ", ".join(source_files),
        "source_count": len(source_files),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_rows": int(len(transformed_df)),
        "rows_with_issues": int(row_issue_count),
        "total_evidences": int(len(issue_rows)),
        "dq_score": dq_score,
        "failed_rules": failed_rules,
    }

    stage_logs = extract_logs + transform_logs + validate_logs + [
        {
            "stage": "load",
            "checkpoint": "Workbook gerado",
            "details": f"Saída salva em {output_path}",
        }
    ]

    write_workbook(
        output_path=output_path,
        summary_rows=summary_rows,
        evidence_rows=issue_rows,
        clean_rows=transformed_df.to_dict(orient="records"),
        metadata=metadata,
        stage_logs=stage_logs,
    )

    return {
        "summary_rows": summary_rows,
        "issue_rows": issue_rows,
        "metadata": metadata,
        "stage_logs": stage_logs,
    }