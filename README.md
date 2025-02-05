# le blog

[![Build the blog and deploy it to Github Pages](https://github.com/rhaeguard/rhaeguard.github.io/actions/workflows/static.yml/badge.svg?branch=main)](https://github.com/rhaeguard/rhaeguard.github.io/actions/workflows/static.yml)

A custom blog engine, made for my use case, which is neither unique nor particularly challenging. It's just more fun to make my own blog engine.

This repo consists of these sections:

- [main.py](./main.py) is the engine. It coordinates everything - generation of HTML, compiling Sass, etc.
- [data.json](./data.json) is the configuration file where I keep the global data.
- [templating_engine.py](./templating_engine.py) is the templating engine. It has a very small DSL that's capable of doing all the necessary things for my use case (variables, conditionals, loops).
    - [templates](./templates/) is the folder where templates/fragments are kept; these templates are loaded by the engine to generate different parts of a page.
- [css folder](./css/) contains the Sass file.
- [posts folder](./posts/) contains all the posts written in Markdown format.
- [assets](./assets/) contains the static assets

The code has been tested with Python 3.11. To install dependencies (create a venv if you want):

```sh
pip install -r requirements.txt
```

To generate the files:

```sh
python main.py
```

To quickly serve the blog:

```sh
# go to the ./build folder and run
python -m http.server
```

The blog should be accessible at `http://localhost:8000`
