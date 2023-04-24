SHELL := /usr/bin/env bash
EXEC = python=3.10
NAME = ejusdemgeneris
PACKAGE = model
INSTALL = python -m pip install
ACTIVATE = source activate $(NAME)
.DEFAULT_GOAL := help

## help      : print available build commands.
.PHONY : help
help : Makefile
	@sed -n 's/^##//p' $<

## update    : update repo with latest version from GitHub.
.PHONY : update
update :
	@git pull origin main

## env       : setup environment and install dependencies.
.PHONY : env
env : $(PACKAGE).egg-info/
$(PACKAGE).egg-info/ : setup.py requirements.txt
	@conda create -yn $(NAME) $(EXEC)
	@$(ACTIVATE) ; $(INSTALL) -e .

## test      : run testing pipeline.
.PHONY : test
test : mypy pylint
mypy : env html/mypy/index.html
pylint : env html/pylint/index.html
html/mypy/index.html : $(PACKAGE)/*.py
	@$(ACTIVATE) ; mypy \
	-p $(PACKAGE) \
	--ignore-missing-imports \
	--html-report $(@D)
html/pylint/index.html : html/pylint/index.json
	@$(ACTIVATE) ; pylint-json2html -o $@ -e utf-8 $<
html/pylint/index.json : $(PACKAGE)/*.py
	@mkdir -p $(@D)
	@$(ACTIVATE) ; pylint $(PACKAGE) \
	--disable C0114,C0115,C0116 \
	--output-format=colorized,json:$@ \
	|| pylint-exit $$?

## norms	 : run norming pipeline.
.PHONY : norms
norms : analysis/materials/norms.csv
analysis/materials/norms.csv : \
analysis/materials/norm_all_text-davinci-003_results.csv \
analysis/src/eval_norms.py
	@$(ACTIVATE) ; cd analysis/src; python -m eval_norms
analysis/materials/norm_all_text-davinci-003_results.csv : \
analysis/materials/norm_all.json \
analysis/src/probsem/probsem.egg-info/
	@cd analysis/src/probsem; \
	source activate probsem; \
	python -m probsem \
	--prompt norm \
	--test all \
	--input_dir $(shell pwd)/analysis/materials \
	--output_dir $(shell pwd)/analysis/materials \
	--model text-davinci-003
analysis/materials/norm_all.json : analysis/src/collect_samples.py
	@mkdir -p analysis/materials
	@$(ACTIVATE) ; cd analysis/src; python -m collect_samples
analysis/src/probsem/probsem.egg-info/ : 
	@cd analysis/src; \
	git clone git@github.com:benlipkin/probsem.git; \
	cd probsem; \
	git reset --hard 28e10026532cab9e1eacc3d879aff668ad011836; \
	make env
