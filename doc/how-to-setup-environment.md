# How to setup environment

## Install python3 and virtualenv

Install python3 on windows

    https://www.python.org/downloads/

Install python3 on macos

    brew install python3

Install virtualenv

    pip3 install virtualenv

## Setup virtualenv

Create a python virtual environment

    virtualenv -p python3 venv

Activate 

    source ./venv/bin/activate

Install development dependencies:

    pip3 install -r requirements-dev.txt

## Before commit

Auto fix code style with yapf

    yapf --recursive app.py core

Check code style with flake8

    tox -e pep8
