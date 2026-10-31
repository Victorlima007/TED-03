"""Leitura, conversão e gravação segura de arquivos CSV e JSON.

CSV representa cada célula como texto. Ao exportar JSON, valores não textuais
recebem uma representação JSON explícita; ao importar CSV, cada célula é
mantida como texto, sem inferir tipos e alterar valores como "001".
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


class ErroPersistencia(Exception):
    """Erro compreensível para operações de persistência."""


def _validar_arquivo(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"O arquivo não foi encontrado: {path}")


def ler_csv(caminho: str | Path) -> list[dict[str, str]]:
    """Lê CSV com cabeçalho e retorna uma lista de registros textuais."""
    path = Path(caminho)
    _validar_arquivo(path)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo, strict=True)
            if not leitor.fieldnames:
                raise ErroPersistencia("O CSV está vazio ou não possui cabeçalho.")
            if len(set(leitor.fieldnames)) != len(leitor.fieldnames):
                raise ErroPersistencia("O CSV possui nomes de coluna duplicados.")
            registros = []
            for numero, linha in enumerate(leitor, start=2):
                if None in linha:
                    raise ErroPersistencia(f"A linha {numero} tem mais valores que o cabeçalho.")
                registros.append({chave: valor if valor is not None else "" for chave, valor in linha.items()})
            return registros
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ErroPersistencia(f"Não foi possível ler o CSV '{path}': {exc}") from exc


def ler_json(caminho: str | Path) -> Any:
    """Lê e decodifica um arquivo JSON UTF-8."""
    path = Path(caminho)
    _validar_arquivo(path)
    try:
        with path.open("r", encoding="utf-8-sig") as arquivo:
            return json.load(arquivo)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ErroPersistencia(f"Não foi possível ler o JSON '{path}': {exc}") from exc


def _backup(caminho: Path, pasta_backup: str | Path | None = None) -> Path | None:
    """Cria cópia binária do original antes de qualquer alteração."""
    if not caminho.exists():
        return None
    _validar_arquivo(caminho)
    pasta = Path(pasta_backup) if pasta_backup else caminho.parent / "backups"
    pasta.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destino = pasta / f"{caminho.stem}_{instante}{caminho.suffix}.bak"
    try:
        with caminho.open("rb") as origem, destino.open("xb") as copia:
            shutil.copyfileobj(origem, copia)
    except OSError as exc:
        try:
            destino.unlink(missing_ok=True)
        except OSError:
            pass
        raise ErroPersistencia(f"Backup não foi criado; arquivo original preservado: {exc}") from exc
    return destino


def _gravar_atomico(caminho: Path, conteudo: str, pasta_backup: str | Path | None = None) -> Path | None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    backup = _backup(caminho, pasta_backup)
    temporario: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=caminho.parent,
            prefix=f".{caminho.name}.", suffix=".tmp", delete=False,
        ) as arquivo:
            temporario = arquivo.name
            arquivo.write(conteudo)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    except (OSError, UnicodeError) as exc:
        if temporario:
            try:
                Path(temporario).unlink(missing_ok=True)
            except OSError:
                pass
        raise ErroPersistencia(f"Não foi possível gravar '{caminho}': {exc}") from exc
    return backup


def gravar_json(dados: Any, caminho: str | Path, pasta_backup: str | Path | None = None) -> Path | None:
    """Grava JSON UTF-8 formatado; retorna o caminho do backup, se criado."""
    try:
        conteudo = json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise ErroPersistencia(f"Os dados não podem ser serializados em JSON: {exc}") from exc
    return _gravar_atomico(Path(caminho), conteudo, pasta_backup)


def _celula_csv(valor: Any) -> str:
    # Strings permanecem legíveis; demais tipos usam JSON compacto e sem ambiguidade.
    return valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def gravar_csv(registros: list[dict[str, Any]], caminho: str | Path,
               pasta_backup: str | Path | None = None) -> Path | None:
    """Grava uma lista de objetos JSON em CSV, preservando os nomes das colunas."""
    if not isinstance(registros, list) or any(not isinstance(item, dict) for item in registros):
        raise ErroPersistencia("Para gerar CSV, o JSON deve conter uma lista de objetos.")
    if not registros:
        raise ErroPersistencia("A lista JSON está vazia; não há registros para definir as colunas do CSV.")
    campos: list[str] = []
    for registro in registros:
        for campo in registro:
            if not isinstance(campo, str):
                raise ErroPersistencia("Os nomes dos campos JSON devem ser textos.")
            if campo not in campos:
                campos.append(campo)
    from io import StringIO
    buffer = StringIO(newline="")
    escritor = csv.DictWriter(buffer, fieldnames=campos, extrasaction="raise", lineterminator="\n")
    if campos:
        escritor.writeheader()
        for registro in registros:
            escritor.writerow({campo: _celula_csv(registro.get(campo, "")) for campo in campos})
    conteudo = buffer.getvalue()
    buffer.close()
    return _gravar_atomico(Path(caminho), conteudo, pasta_backup)


def converter_csv_para_json(origem: str | Path, destino: str | Path,
                            pasta_backup: str | Path | None = None) -> Path | None:
    return gravar_json(ler_csv(origem), destino, pasta_backup)


def converter_json_para_csv(origem: str | Path, destino: str | Path,
                            pasta_backup: str | Path | None = None) -> Path | None:
    return gravar_csv(ler_json(origem), destino, pasta_backup)

