# api.etml.burkhalter.dev

The backend of [etml.burkhalter.dev](https://github.com/BurkhalterY/etml.burkhalter.dev)

## Installation

- Copy `.env.sample` to `.env` and change default settings.

```bash
poetry install
poetry shell
piccolo migrations forwards app
```

## Run

```bash
poetry run start
```
