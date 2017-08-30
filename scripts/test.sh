#!/bin/bash
flake8 --exclude=.venv,venv,snowboy,build &&
pytest --ignore=build --ignore=venv --ignore=.venv
