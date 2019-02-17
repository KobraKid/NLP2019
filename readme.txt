# Golden Globes Project 2019

An API for parsing tweets about an awards ceremony and extracting relevant and important figures and information.
The source code for this project is located at [GitHub](https://github.com/KobraKid/NLP2019)

## Required dependencies

Spacy: `python3 -m pip install -U spacy`

## Using the API

Include `gg_api.py` in the imports: `import gg_api.py`. This will automatically execute the pre-ceremony process, which downloads a list of names of famous people from the IMDb database.

You **must** run `gg_api.main(None, years)`, where `years` is an array of strings for each year you plan to use gg_api with, e.g. `years = ['2013', '2015']`. This will load in the corresponding tweet corpora.

After doing both of the steps above, you can run any of the API functions as expected: `get_nominees('2013')`

## Authors

* **Michael Huyler** - *2020*  - [GitHub](https://github.com/KobraKid)
* **Robert Smart** - *2019*  - [GitHub](https://github.com/rbrtsmart)
* **Salome Wairimu** - *2020*  - [GitHub](https://github.com/SalomeWairimu)
* **Ulyana Kurylo** - *2020*  - [GitHub](https://github.com/ulyanakurylo)
