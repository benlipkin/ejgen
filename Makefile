SHELL := /usr/bin/env bash
EXEC = python=3.11
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
