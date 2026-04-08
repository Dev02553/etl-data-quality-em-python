from __future__ import annotations

import re

import pandas as pd

from .models import Rule

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
ALLOWED_COUNTRIES = {"BR", "AR", "CL", "CO", "MX", "PE", "UY"}


def _blank(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().eq("")


def _parsed_dates(df: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(df["signup_date"], errors="coerce")


def _parsed_numeric(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["credit_limit"], errors="coerce")


def build_rules() -> list[Rule]:
    return [
        Rule(
            name="required_customer_id",
            severity="high",
            column_name="customer_id",
            description="Verifica se o campo customer_id foi preenchido.",
            evaluator=lambda df: _blank(df["customer_id"]),
            message_builder=lambda row: "O campo customer_id está vazio.",
        ),
        Rule(
            name="required_email",
            severity="high",
            column_name="email",
            description="Verifica se o campo email foi preenchido.",
            evaluator=lambda df: _blank(df["email"]),
            message_builder=lambda row: "O campo email está vazio.",
        ),
        Rule(
            name="email_format",
            severity="high",
            column_name="email",
            description="Verifica se o e-mail está em um formato válido.",
            evaluator=lambda df: (~_blank(df["email"])) & (~df["email"].astype(str).str.match(EMAIL_REGEX)),
            message_builder=lambda row: f'O e-mail "{row["email"]}" está em formato inválido.',
        ),
        Rule(
            name="unique_customer_id",
            severity="high",
            column_name="customer_id",
            description="Verifica se o customer_id aparece apenas uma vez na base.",
            evaluator=lambda df: (~_blank(df["customer_id"])) & df["customer_id"].duplicated(keep=False),
            message_builder=lambda row: f'O customer_id "{row["customer_id"]}" aparece mais de uma vez na base.',
        ),
        Rule(
            name="allowed_country",
            severity="medium",
            column_name="country",
            description="Verifica se o país informado está dentro do domínio esperado.",
            evaluator=lambda df: (
                (~_blank(df["country"]))
                & (~df["country"].astype(str).str.upper().isin(ALLOWED_COUNTRIES))
            ),
            message_builder=lambda row: f'O país "{row["country"]}" está fora do domínio esperado.',
        ),
        Rule(
            name="signup_date_valid_type",
            severity="high",
            column_name="signup_date",
            description="Verifica se a data de cadastro é válida.",
            evaluator=lambda df: (~_blank(df["signup_date"])) & (_parsed_dates(df).isna()),
            message_builder=lambda row: f'A data "{row["signup_date"]}" é inválida.',
        ),
        Rule(
            name="signup_date_not_future",
            severity="medium",
            column_name="signup_date",
            description="Verifica se a data de cadastro não está no futuro.",
            evaluator=lambda df: _parsed_dates(df).gt(pd.Timestamp.now()),
            message_builder=lambda row: f'A data "{row["signup_date"]}" está no futuro.',
        ),
        Rule(
            name="credit_limit_numeric_type",
            severity="high",
            column_name="credit_limit",
            description="Verifica se o limite de crédito é numérico.",
            evaluator=lambda df: (~_blank(df["credit_limit"])) & (_parsed_numeric(df).isna()),
            message_builder=lambda row: f'O limite de crédito "{row["credit_limit"]}" não é um número válido.',
        ),
        Rule(
            name="credit_limit_non_negative",
            severity="medium",
            column_name="credit_limit",
            description="Verifica se o limite de crédito é maior ou igual a zero.",
            evaluator=lambda df: _parsed_numeric(df).fillna(0).lt(0),
            message_builder=lambda row: f'O limite de crédito "{row["credit_limit"]}" não pode ser negativo.',
        ),
    ]