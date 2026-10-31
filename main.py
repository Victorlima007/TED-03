"""Interface de linha de comando do TED 03."""

import argparse
from pathlib import Path

from src.persistencia import (
    ErroPersistencia,
    converter_csv_para_json,
    converter_json_para_csv,
    gravar_json,
    ler_csv,
    ler_json,
)


def executar() -> int:
    parser = argparse.ArgumentParser(
        description="Gerenciador de persistência CSV/JSON com backup automático."
    )
    comandos = parser.add_subparsers(dest="comando", required=True)

    for nome in ("ler-csv", "ler-json"):
        sub = comandos.add_parser(nome, help=f"Lê e exibe um arquivo {nome[4:].upper()}")
        sub.add_argument("arquivo", type=Path)

    conversao = comandos.add_parser("csv-para-json", help="Converte CSV em JSON")
    conversao.add_argument("origem", type=Path)
    conversao.add_argument("destino", type=Path)

    conversao = comandos.add_parser("json-para-csv", help="Converte JSON em CSV")
    conversao.add_argument("origem", type=Path)
    conversao.add_argument("destino", type=Path)

    gravacao = comandos.add_parser("gravar-json", help="Persiste dados JSON de exemplo")
    gravacao.add_argument("destino", type=Path)

    args = parser.parse_args()
    try:
        if args.comando == "ler-csv":
            print(ler_csv(args.arquivo))
        elif args.comando == "ler-json":
            print(ler_json(args.arquivo))
        elif args.comando == "csv-para-json":
            backup = converter_csv_para_json(args.origem, args.destino)
            print(f"Conversão concluída: {args.destino}")
            print(f"Backup criado: {backup}" if backup else "Destino novo; não havia arquivo para backup.")
        elif args.comando == "json-para-csv":
            backup = converter_json_para_csv(args.origem, args.destino)
            print(f"Conversão concluída: {args.destino}")
            print(f"Backup criado: {backup}" if backup else "Destino novo; não havia arquivo para backup.")
        elif args.comando == "gravar-json":
            dados = [{"nome": "Ana", "curso": "Computação", "ativo": True}]
            backup = gravar_json(dados, args.destino)
            print(f"Dados gravados: {args.destino}")
            print(f"Backup criado: {backup}" if backup else "Arquivo novo; não havia versão anterior para backup.")
        return 0
    except (ErroPersistencia, FileNotFoundError, PermissionError, IsADirectoryError) as exc:
        print(f"Erro: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(executar())
