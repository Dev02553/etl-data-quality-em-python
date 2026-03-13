from __future__ import annotations

import argparse

from .pipeline import run_pipeline



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa pipeline ETL com Data Quality.")
    parser.add_argument("--input", required=True, help="Caminho do CSV de entrada ou pasta com CSVs.")
    parser.add_argument("--output", required=True, help="Caminho do XLSX de saída.")
    return parser



def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    result = run_pipeline(args.input, args.output)
    metadata = result["metadata"]
    print("Pipeline concluído com sucesso.")
    print(f"Arquivos fonte: {metadata['source_count']}")
    print(f"Total de linhas: {metadata['total_rows']}")
    print(f"Linhas com problemas: {metadata['rows_with_issues']}")
    print(f"Total de evidências: {metadata['total_evidences']}")
    print(f"DQ score: {metadata['dq_score']:.1%}")


if __name__ == "__main__":
    main()
