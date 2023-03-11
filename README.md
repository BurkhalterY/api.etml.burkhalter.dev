# api.etml.burkhalter.dev

The backend of [etml.burkhalter.dev](https://github.com/BurkhalterY/etml.burkhalter.dev)

## Installation

```bash
poetry install
poetry shell
piccolo migrations forwards user
piccolo migrations forwards app
```

## Run

```bash
poetry run start
```

## Dev tips

Creating migration:

```bash
poetry shell
piccolo migrations new app --auto
```
