from __future__ import annotations

import re
from datetime import timezone

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
            description="customer_id é obrigatório.",
            evaluator=lambda df: _blank(df["customer_id"]),
            message_builder=lambda row: "customer_id ausente.",
        ),
        Rule(
            name="required_email",
            severity="high",
            column_name="email",
            description="email é obrigatório.",
            evaluator=lambda df: _blank(df["email"]),
            message_builder=lambda row: "email ausente.",
        ),
        Rule(
            name="email_format",
            severity="high",
            column_name="email",
            description="email deve possuir formato válido.",
            evaluator=lambda df: (~_blank(df["email"])) & (~df["email"].astype(str).str.match(EMAIL_REGEX)),
            message_builder=lambda row: f"email inválido: {row['email']}",
        ),
        Rule(
            name="unique_customer_id",
            severity="high",
            column_name="customer_id",
            description="customer_id deve ser único.",
            evaluator=lambda df: (~_blank(df["customer_id"])) & df["customer_id"].duplicated(keep=False),
            message_builder=lambda row: f"customer_id duplicado: {row['customer_id']}",
        ),
        Rule(
            name="allowed_country",
            severity="medium",
            column_name="country",
            description="country deve pertencer ao domínio LATAM permitido.",
            evaluator=lambda df: ~df["country"].fillna("").astype(str).str.upper().isin(ALLOWED_COUNTRIES),
            message_builder=lambda row: f"country fora do domínio: {row['country']}",
        ),
        Rule(
            name="signup_date_valid_type",
            severity="high",
            column_name="signup_date",
            description="signup_date deve ser uma data válida.",
            evaluator=lambda df: (~_blank(df["signup_date"])) & (_parsed_dates(df).isna()),
            message_builder=lambda row: f"signup_date inválida: {row['signup_date']}",
        ),
        Rule(
            name="signup_date_not_future",
            severity="medium",
            column_name="signup_date",
            description="signup_date não pode estar no futuro.",
            evaluator=lambda df: _parsed_dates(df).gt(pd.Timestamp.now(tz=timezone.utc).tz_localize(None)),
            message_builder=lambda row: f"data futura identificada: {row['signup_date']}",
        ),
        Rule(
            name="credit_limit_numeric_type",
            severity="high",
            column_name="credit_limit",
            description="credit_limit deve ser numérico.",
            evaluator=lambda df: (~_blank(df["credit_limit"])) & (_parsed_numeric(df).isna()),
            message_builder=lambda row: f"credit_limit inválido: {row['credit_limit']}",
        ),
        Rule(
            name="credit_limit_non_negative",
            severity="medium",
            column_name="credit_limit",
            description="credit_limit deve ser maior ou igual a zero.",
            evaluator=lambda df: _parsed_numeric(df).fillna(0).lt(0),
            message_builder=lambda row: f"credit_limit negativo: {row['credit_limit']}",
        ),
    ]
