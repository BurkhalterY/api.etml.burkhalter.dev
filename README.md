# api.etml.burkhalter.dev

The backend of [etml.burkhalter.dev](https://github.com/BurkhalterY/etml.burkhalter.dev)

## Installation

- Copy `database.sample.toml` to `database.toml` and configure access to database.
- Copy `app/config/settings.sample.toml` to `app/config/settings.toml` and set environment to "dev" or "prod".

```bash
poetry install
poetry shell
piccolo migrations forwards user
piccolo migrations forwards app
poetry run init
```

## Run

```bash
poetry run start
```

## CLI

Grant a user as admin:

```bash
poetry run grant me@mail.com
```

Ungrant a user:

```bash
poetry run ungrant me@mail.com
```

Note: grant and ungrant commands can support many users at the same time.
