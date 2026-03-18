from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd


@dataclass(slots=True)
class DQIssue:
    row_number: int
    rule_name: str
    severity: str
    column_name: str
    message: str
    invalid_value: Any
    source_file: str | None = None


@dataclass(slots=True)
class Rule:
    name: str
    severity: str
    column_name: str
    description: str
    evaluator: Callable[[pd.DataFrame], pd.Series]
    message_builder: Callable[[pd.Series], str]