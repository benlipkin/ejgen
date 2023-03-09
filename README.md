# Ejusdem Generis

_UNDER DEVELOPMENT_

## Setup

```bash
make env
```

## Run
```bash
python -m model run *args **kwargs
```

__Example Usage:__
```bash
#!/bin/bash
python -m model run plot \
	--category=beverages \
	--examples=gin,whiskey,rum,tequila \
	--targets=vodka,beer,milk,pizza,car \
	--modeltype=CentroidModel \
	--embedding=GloVe \
	--smoothing=1.0 \
	--metric=euclidean \
```