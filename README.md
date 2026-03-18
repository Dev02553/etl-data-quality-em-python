# ETL & Data Quality em Python

![CI](https://github.com/Dev02553/etl-data-quality-em-python/actions/workflows/ci.yml/badge.svg)
![Status](https://img.shields.io/badge/status-completo-22c55e)
![Python](https://img.shields.io/badge/Python-3.12-3776ab)
![Pytest](https://img.shields.io/badge/Pytest-12%20testes-0a9edc)

**Completo • 2024**  
Pipeline de dados com validações, rastreabilidade e geração de relatório em Excel e HTML (Data Quality).

## Stack
**Dados** • **Automação** • **Python** • **Pandas** • **OpenPyXL** • **Pytest** • **CLI**

## Como executar

### 1) Instalar dependências
```bash
pip install -e .
pip install -e .[dev]
```

### 2) Rodar testes (headless)
```bash
python -m pytest -q
```

### 3) Gerar relatório (CLI)
```bash
python main.py --input ./data --output ./output/report.xlsx
```

> Execute os comandos na raiz do repositório, onde estão o `main.py` e o `pyproject.toml`.  
> O relatório HTML é gerado automaticamente na mesma pasta do XLSX.

## Destaques
- Extract → Transform → Validate → Load com logs por etapa
- 9 regras de Data Quality: obrigatórios, tipos, duplicados, datas e domínio
- `DQIssue` como modelo de dados para evidências rastreáveis
- Validação de colunas obrigatórias antes de aplicar regras
- Relatório em XLSX + HTML navegável gerados automaticamente
- 12 testes com Pytest cobrindo todas as regras e cenários de pipeline
- CI com GitHub Actions rodando testes a cada push

## Estrutura do projeto
```text
etl-data-quality-python/
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ data/
│  └─ customers.csv
├─ output/
│  └─ .gitkeep
├─ src/
│  └─ etl_dq/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ models.py
│     ├─ pipeline.py
│     ├─ reporting.py
│     ├─ reporting_html.py
│     └─ rules.py
├─ tests/
│  ├─ conftest.py
│  └─ test_rules_and_pipeline.py
├─ .gitignore
├─ main.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

## Regras implementadas
- `required_customer_id` — customer_id é obrigatório
- `required_email` — email é obrigatório
- `email_format` — email deve ter formato válido
- `unique_customer_id` — customer_id deve ser único
- `allowed_country` — country deve pertencer ao domínio LATAM
- `signup_date_valid_type` — signup_date deve ser data válida
- `signup_date_not_future` — signup_date não pode estar no futuro
- `credit_limit_numeric_type` — credit_limit deve ser numérico
- `credit_limit_non_negative` — credit_limit deve ser >= 0

## O que o pipeline faz

### Extract
- Lê um arquivo CSV ou vários CSVs dentro de uma pasta.
- Adiciona a coluna `source_file` para rastrear a origem de cada linha.

### Transform
- Padroniza `email`, `country` e `signup_date`.
- Cria a coluna `row_number` para auditoria.

### Validate
- Valida colunas obrigatórias antes de aplicar regras — erro claro se coluna faltar.
- Executa 9 regras explícitas separadas por domínio.
- Instancia `DQIssue` para cada evidência gerada.

### Load
- Produz XLSX com resumo executivo, evidências e base tratada.
- Produz HTML navegável na mesma pasta com o mesmo conteúdo.

## Relatório gerado

**XLSX:**
- `Data_Quality` — visão executiva, métricas, resumo por regra e checkpoints.
- `Evidences` — falhas detalhadas por linha, regra, coluna e valor inválido.
- `Clean_Data` — dataset com `dq_issue_count` e `dq_status`.

**HTML:**
- Mesmo conteúdo em formato navegável no browser.
- DQ score colorido: verde ≥ 80%, amarelo ≥ 60%, vermelho < 60%.

## Case Study

### Contexto / Context
**PT**  
Em rotinas operacionais e pipelines ETL, erros pequenos de tipo, data ou duplicidade viram problemas grandes em relatórios e decisões. O objetivo é reduzir falhas com validações explícitas e rastreabilidade.

**EN**  
In operational ETL routines, small issues in types, dates, or duplicates become big problems in reports and decisions. This project reduces failures through explicit validations and traceability.

### Objetivo / Goal
**PT**
- Extrair e padronizar dados de entrada.
- Aplicar regras de Data Quality e gerar evidência rastreável.
- Entregar relatório reutilizável e fácil de auditar em XLSX e HTML.

**EN**
- Extract and standardize input data.
- Apply Data Quality rules and generate traceable evidence.
- Deliver a reusable, auditable report in both XLSX and HTML.

### Resultados / Results
**PT**
- Menos retrabalho: erros detectados antes do consumo em relatórios.
- Rastreabilidade: o porquê de cada inconsistência é explícito.
- CI automático garante que nenhum push quebra as validações.

**EN**
- Less rework: issues detected before reporting and consumption.
- Traceability: the reason behind each inconsistency is explicit.
- Automatic CI ensures no push breaks the validations.

### Próximos passos / Next steps
**PT**
- Adicionar validações por domínio de negócio.
- Suporte a múltiplos formatos de entrada (JSON, Parquet).
- Publicar relatório HTML via GitHub Pages.

**EN**
- Add business domain validations.
- Support multiple input formats (JSON, Parquet).
- Publish HTML report via GitHub Pages.