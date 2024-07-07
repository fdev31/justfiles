# justfiles

## Quickstart

Install `python-poetry` and `npm` then:

```sh
npm run build
poetry install

export SHARED="/path/to/the/folder/you/want/to/share"
poetry run uvicorn justfiles:app --reload --port 5566
xdg-open http://localhost:5566
```

## Moving static files

Point to the folder containing the index.html & assets:

```sh
export STATIC=/path/to/folder/
```
