# ETL & Data Quality em Python

**Completo • 2024**

Pipeline ETL em Python com foco em Data Quality, rastreabilidade de inconsistências e geração automatizada de relatórios em Excel e HTML.

## Stack
**Dados • Automação • Python • Pandas • openpyxl • XlsxWriter • Pytest • CLI • GitHub Actions**

## Como executar

### 1) Instalar dependências
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
2) Rodar testes
python -m pytest -q
3) Gerar relatório pela CLI
dq-pipeline --input ./sample_data/customers.csv --output ./output/report.xlsx
4) Execução rápida no Windows
.\run.ps1

Execute os comandos na raiz do repositório, onde estão o pyproject.toml, requirements.txt e o README.md.

O relatório HTML é gerado automaticamente na mesma pasta do XLSX.

Destaques
Pipeline Extract → Transform → Validate → Load com rastreabilidade por etapa
9 regras de Data Quality cobrindo obrigatoriedade, formato, duplicidade, datas, domínio e valores numéricos
Modelo DQIssue para evidências rastreáveis
Validação prévia de colunas obrigatórias antes da aplicação das regras
Geração automática de relatórios em XLSX + HTML
12 testes com Pytest cobrindo regras e cenários da pipeline
CI com GitHub Actions executando testes a cada push
Estrutura do projeto
etl-data-quality-python/
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ data/
│  └─ customers.csv
├─ output/
│  └─ .gitkeep
├─ sample_data/
│  └─ customers.csv
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
├─ run.ps1
└─ README.md
Regras implementadas
required_customer_id — customer_id é obrigatório
required_email — email é obrigatório
email_format — email deve ter formato válido
unique_customer_id — customer_id deve ser único
allowed_country — country deve pertencer ao domínio LATAM
signup_date_valid_type — signup_date deve ser uma data válida
signup_date_not_future — signup_date não pode estar no futuro
credit_limit_numeric_type — credit_limit deve ser numérico
credit_limit_non_negative — credit_limit deve ser maior ou igual a zero
O que o pipeline faz
Extract
Lê um CSV único ou vários CSVs dentro de uma pasta
Adiciona a coluna source_file para rastrear a origem de cada linha
Transform
Padroniza email, country e signup_date
Cria a coluna row_number para auditoria
Validate
Verifica colunas obrigatórias antes da aplicação das regras
Executa 9 regras explícitas de Data Quality
Gera uma instância DQIssue para cada evidência identificada
Load
Produz um arquivo XLSX com resumo executivo, evidências e base tratada
Produz um HTML navegável com o mesmo conteúdo do relatório
Relatório gerado
XLSX
Data_Quality — visão executiva, métricas e resumo por regra
Evidences — falhas detalhadas por linha, regra, coluna e valor inválido
Clean_Data — dataset tratado com dq_issue_count e dq_status
HTML
Mesmo conteúdo em formato navegável no navegador
DQ score com destaque visual:
verde: ≥ 80%
amarelo: ≥ 60%
vermelho: < 60%
Case Study
Contexto / Context

PT
Em rotinas operacionais e pipelines ETL, erros pequenos de tipo, data ou duplicidade podem virar problemas grandes em relatórios e decisões. O objetivo deste projeto é reduzir falhas por meio de validações explícitas e rastreabilidade.

EN
In operational ETL routines, small issues in types, dates, or duplicates can become major problems in reports and decision-making. This project reduces failures through explicit validations and traceability.

Objetivo / Goal

PT

Extrair e padronizar dados de entrada
Aplicar regras de Data Quality e gerar evidências rastreáveis
Entregar um relatório reutilizável e fácil de auditar em XLSX e HTML

EN

Extract and standardize input data
Apply Data Quality rules and generate traceable evidence
Deliver a reusable, auditable report in both XLSX and HTML
Resultados / Results

PT

Menos retrabalho: problemas detectados antes do consumo em relatórios
Mais rastreabilidade: cada inconsistência possui causa explícita
CI automático garantindo que novos pushes não quebrem as validações

EN

Less rework: issues detected before reporting and downstream consumption
More traceability: each inconsistency has an explicit cause
Automatic CI ensures new pushes do not break validations
Próximos passos / Next steps

PT

Adicionar validações por domínio de negócio
Suportar múltiplos formatos de entrada, como JSON e Parquet
Publicar o relatório HTML via GitHub Pages

EN

Add business-domain validations
Support additional input formats such as JSON and Parquet
Publish the HTML report via GitHub Pages
