# Quick start

Para inicializar este projeto, tenha certeza de utilizar um sistema Linux.

Primeiramente, para clonar este projeto, use o seguinte comando no seu terminal:

```
git clone --recurse-submodules git@github.com:henriquefac/mobile-device-usage-analysis.git
```

Se você clonou este repositório sem usar a flag `--recurse-submodules`, use o seguinte comando no terminal, na raiz do projeto:

```
git submodule update --init --recursive
```

Assim, com o projeto devidamente clonado, inicialize o ambiente virtual do Python.

Use o seguinte comando, ainda na raiz do projeto (dentro do diretório que o Git clonou):

```
. configPy/bash/makenv.sh
```

Isso deve inicializar o projeto e baixar os pacotes necessários, além de configurar corretamente algumas variáveis de ambiente.

Com isso, o projeto deve estar corretamente inicializado.

## Criar dataset

O dataset utilizado foi retirado da plataforma Kaggle. Esse dataset conta com informações coletadas acerca do padrão de uso de aparelhos telefônicos por diversos usuários (700 amostras).

Você pode verificar o dataset [aqui](https://www.kaggle.com/datasets/valakhorasani/mobile-device-usage-and-user-behavior-dataset/data).

Este projeto possui um script em Python que já, automaticamente, baixa o arquivo ZIP e o extrai corretamente no diretório `<raiz>/files/dataset/<nome-do-dataset>`.

Para que esse script funcione, crie um arquivo `.env` na raiz do projeto, declarando a seguinte variável:

```
DATASET=valakhorasani/mobile-device-usage-and-user-behavior-dataset
```

Com o ambiente virtual ativado, use o seguinte comando:

```
python getData.py
```
