from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from etl_dq.pipeline import run_pipeline
from etl_dq.rules import build_rules


def test_email_format_rule_flags_invalid_values():
    df = pd.DataFrame(
        {
            "customer_id": ["1", "2"],
            "email": ["ok@example.com", "invalid-email"],
            "country": ["BR", "BR"],
            "signup_date": ["2024-01-01", "2024-01-01"],
            "credit_limit": [100, 100],
        }
    )

    rule = next(rule for rule in build_rules() if rule.name == "email_format")
    mask = rule.evaluator(df)
    assert mask.tolist() == [False, True]


def test_unique_customer_id_rule_flags_duplicates():
    df = pd.DataFrame(
        {
            "customer_id": ["A100", "A100", "B200"],
            "email": ["a@a.com", "b@b.com", "c@c.com"],
            "country": ["BR", "BR", "CL"],
            "signup_date": ["2024-01-01", "2024-01-01", "2024-01-01"],
            "credit_limit": [1, 2, 3],
        }
    )

    rule = next(rule for rule in build_rules() if rule.name == "unique_customer_id")
    mask = rule.evaluator(df)
    assert mask.tolist() == [True, True, False]


def test_type_rules_flag_invalid_date_and_non_numeric_values():
    df = pd.DataFrame(
        {
            "customer_id": ["1", "2"],
            "email": ["ok@example.com", "ok2@example.com"],
            "country": ["BR", "BR"],
            "signup_date": ["2024-01-01", "not-a-date"],
            "credit_limit": [100, "abc"],
        }
    )

    date_rule = next(rule for rule in build_rules() if rule.name == "signup_date_valid_type")
    numeric_rule = next(rule for rule in build_rules() if rule.name == "credit_limit_numeric_type")

    assert date_rule.evaluator(df).tolist() == [False, True]
    assert numeric_rule.evaluator(df).tolist() == [False, True]


def test_pipeline_generates_workbook_from_directory(tmp_path: Path):
    input_dir = tmp_path / "data"
    input_dir.mkdir()
    output_path = tmp_path / "report.xlsx"
    (input_dir / "input_a.csv").write_text(
        "\n".join(
            [
                "customer_id,email,country,signup_date,credit_limit",
                "1,valid@example.com,BR,2024-01-01,100",
                "1,invalid-email,XX,2099-01-01,-10",
            ]
        ),
        encoding="utf-8",
    )

    result = run_pipeline(input_dir, output_path)
    assert output_path.exists()
    assert result["metadata"]["source_count"] == 1
    assert result["metadata"]["total_rows"] == 2
    assert result["metadata"]["rows_with_issues"] == 2
    assert result["metadata"]["total_evidences"] >= 4

    wb = load_workbook(output_path)
    assert wb.sheetnames == ["Data_Quality", "Evidences", "Clean_Data"]
    assert wb["Data_Quality"]["A1"].value == "Data Quality Report"
