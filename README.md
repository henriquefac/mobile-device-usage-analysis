# Quick start

Para inicializar esse projeto, tenha certeza de utilizar o sistema linux

Primeiramente, para clonar esse projeto use o seguinte comando no seu terminal:

```
git clone --recurse-submodules git@github.com:henriquefac/mobile-device-usage-analysis.git
```

Se você clonou esse repositório sem usar as flag --recurse-submodules, use o seguinte comando no terminal na raiz do prpjeto:

```
git submodule update --init --recursive
```

Assim, como o projeto devidamente clonado, incialize o ambeinte virtual do python

Use o seguinte comando, ainda na raiz do projeto (dentro do diretório que o git clonou o repositório):

```
. configPy/bash/makenv.sh
```

Isso deve incializar o projeto e baixar os pacotes necessários, além de configurar corretamente algumas variáveis de ambiente.

Com isso, o projeto deve estar corretamente incializado.


## Criar dataset

O dataset utilizado foi retirado da plataforma kaggle. Esse dataset conta com informações coletadas a cerca do padrão de uso de aparelhos de telefone por diversos usuários (700 amostras).

Você pode verificar o datasete [aqui](https://www.kaggle.com/datasets/valakhorasani/mobile-device-usage-and-user-behavior-dataset/data).

Esse projeeto possui um script em python que já, automaticamente, carrega o arquivo zip e extrai corretamente no diretório \<raiz\>/files/dataset/\<nome-do-dataset\>.

Para esse script funcionar, crie um arquivo `.env` na raiz do projeto, declarando a seguinte variável:

```
DATASET=valakhorasani/mobile-device-usage-and-user-behavior-dataset
```

Com o ambiente virtual ativado, use o seguinte comando:

```
python getData.py
```


