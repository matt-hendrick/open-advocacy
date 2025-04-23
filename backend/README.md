## Some useful commands are below that add example data to the DB instance

To setup the environment to run the commands below, cd into the backend directory.
If you do not have poetry install, [install poetry](https://python-poetry.org/docs/).
Then run:
```
poetry shell
```

You can then run the following commands

```
python -m scripts.chicago_city_council_setup --create-tables --random-statuses --drop
```

```
python -m scripts.import_chicago_ward_geojson data/chicago-wards.geojson
```
