# api.etml.burkhalter.dev

The backend of [etml.burkhalter.dev](https://github.com/BurkhalterY/etml.burkhalter.dev)

## Installation

- Copy `.env.sample` to `.env` and change default settings.
  - `ENVIRONMENT`: `prod` or `dev`
  - `WEB_PORT`: `8000` _(default)_
  - `JWT_SECRET`: _generate a random JWT secret_
  - `SQLITE_PATH`: `etml.db` _(default)_

```bash
poetry install
poetry shell
piccolo migrations forwards user
piccolo migrations forwards app
poetry run init
```

You can also use the [docker image](https://hub.docker.com/r/burkhaltery/api.etml.burkhalter.dev) from Docker Hub. In this case, you'll need to mount the SQLite db file.

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

Note: `grant` and `ungrant` commands support many users at the same time.
