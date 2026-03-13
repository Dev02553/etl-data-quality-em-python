# ETL & Data Quality em Python

**Completo • 2024**  
Pipeline de dados com validações, rastreabilidade e geração de relatório em Excel (Data Quality).

## Stack
**Dados** • **Automação** • **Python** • **Pandas** • **OpenPyXL** • **Pytest** • **CLI**

## Foco
- **Qualidade de dados**
- **Regras + evidências**

## Saída
- **Excel (XLSX)**
- **Aba `Data_Quality`**

## Testes
- **Pytest**
- **Validações automatizadas**

## Uso
- **CLI**
- **Execução simples por comando**

## Métricas
- Total de linhas processadas
- Linhas com inconsistências
- Total de evidências geradas
- DQ score
- Regras com falha

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

## Destaques
- **Extract → Transform → Validate → Load**
- **Regras de qualidade: obrigatórios, tipos, duplicados e datas**
- **Relatório final em XLSX com aba `Data_Quality`**
- **Rastreabilidade por linha, regra e arquivo de origem**

## Estrutura do projeto
```text
etl-data-quality-python/
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
│     └─ rules.py
├─ tests/
│  ├─ conftest.py
│  └─ test_rules_and_pipeline.py
├─ .gitignore
├─ main.py
├─ pyproject.toml
└─ README.md
```

## Regras implementadas
- `required_customer_id`
- `required_email`
- `email_format`
- `unique_customer_id`
- `allowed_country`
- `signup_date_valid_type`
- `signup_date_not_future`
- `credit_limit_numeric_type`
- `credit_limit_non_negative`

## O que o pipeline faz
### Extract
- Lê um arquivo CSV ou vários CSVs dentro de uma pasta.
- Adiciona a coluna `source_file` para rastrear a origem de cada linha.

### Transform
- Padroniza `email`, `country` e `signup_date`.
- Cria a coluna `row_number` para auditoria.

### Validate
- Executa regras explícitas de qualidade separadas por domínio.
- Gera evidências detalhadas por linha, regra, severidade e coluna.

### Load
- Produz um arquivo XLSX com resumo executivo, evidências e base tratada.

## Relatório gerado
O Excel final contém:
- **`Data_Quality`**: visão executiva, métricas, resumo por regra e checkpoints do pipeline.
- **`Evidences`**: falhas detalhadas por linha, regra, coluna, mensagem, valor inválido e arquivo de origem.
- **`Clean_Data`**: dataset enriquecido com `dq_issue_count` e `dq_status`.

## Exemplo de entrada
Já deixei uma base de exemplo em:
- `data/customers.csv`

## Case Study

### Contexto / Context
**PT**  
Em rotinas operacionais e pipelines ETL, erros pequenos de tipo, data ou duplicidade viram problemas grandes em relatórios e decisões. O objetivo aqui é reduzir falhas com validações explícitas e rastreabilidade.

**EN**  
In operational ETL routines, small issues in types, dates, or duplicates become big problems in reports and decisions. This project reduces failures through explicit validations and traceability.

### Objetivo / Goal
**PT**
- Extrair e padronizar dados de entrada.
- Aplicar regras de Data Quality e gerar evidência.
- Entregar um relatório final reutilizável e fácil de auditar.

**EN**
- Extract and standardize input data.
- Apply Data Quality rules and generate evidence.
- Deliver a reusable final report that is easy to audit.

### Abordagem / Approach
**PT**
- Pipeline por etapas com logs e checkpoints.
- Validações separadas por regra: obrigatórios, tipos, duplicados e datas.
- Saída em Excel com resumo executivo e detalhes por regra.

**EN**
- Step-based pipeline with logs and checkpoints.
- Validations split by rule: required fields, types, duplicates, and dates.
- Excel output with executive summary and rule-by-rule details.

### Resultados / Results
**PT**
- Menos retrabalho: erros são detectados antes do consumo em relatórios.
- Rastreabilidade: fica claro o porquê de cada inconsistência.
- Base pronta para evoluir com CI, novas fontes e novas métricas.

**EN**
- Less rework: issues are detected before reporting and consumption.
- Traceability: the reason behind each inconsistency is explicit.
- Ready-to-evolve base for CI, new data sources, and additional metrics.
