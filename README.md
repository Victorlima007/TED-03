# TED 03 — Gerenciador de Persistência CSV e JSON

Projeto em Python para leitura, conversão e gravação de dados em arquivos CSV e JSON, com UTF-8, tratamento de falhas e backup automático antes de substituir um arquivo existente.

## Integrantes

- Jadson Paz Sales (26.1.13308)
- Victor Gabriel Guida Lima ()

## Requisitos

- Python 3.10 ou superior
- Nenhuma dependência externa

## Executar

Na pasta do projeto, use:

```powershell
python main.py --help
python main.py ler-csv data/alunos.csv
python main.py csv-para-json data/alunos.csv data/alunos_convertidos.json
python main.py ler-json data/alunos.json
python main.py json-para-csv data/alunos.json data/alunos_convertidos.csv
python main.py gravar-json data/registro.json
```

Se o destino já existir, sua versão anterior será copiada para `backups/` antes da gravação. A mensagem do programa informa o caminho do backup. Se o destino for novo, não há versão anterior para copiar.

## Funcionalidades

- Leitura de CSV com cabeçalho via `csv.DictReader`.
- Leitura e escrita de JSON via módulo `json`.
- Conversão CSV → JSON e JSON → CSV.
- Uso de `with` e UTF-8 em todas as operações de arquivos; gravações usam arquivo temporário e substituição atômica.
- Tratamento de arquivo ausente, permissão, erros de codificação, CSV malformado e JSON inválido.
- Backup binário com data e hora antes de qualquer alteração em destino existente.

## Representação dos dados

CSV é tratado como formato textual: os valores lidos de um CSV são strings, preservando inclusive zeros à esquerda, como `001`. Na exportação de JSON para CSV, strings são gravadas como texto e outros tipos JSON (número, booleano, `null`, lista ou objeto) são representados por sua serialização JSON compacta dentro da célula. JSON→CSV aceita uma lista de objetos; colunas ausentes em um registro ficam vazias. CSV vazio ou sem cabeçalho produz uma mensagem de erro porque não contém informação suficiente para definir as colunas.
