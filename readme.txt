# Golden Globes Project 2019

An API for parsing tweets about an awards ceremony and extracting relevant and important figures and information.
The source code for this project is located at [GitHub](https://github.com/KobraKid/NLP2019)

## Required dependencies

spaCy:
`python3 -m pip install -U spacy
python3 -m spacy download en_core_web_sm`

## Using the API

The simplest way of obtaining the desired json and human-readable output is to run gg_api.py. To use a specific set of tweets, it is necessary to specify the name of the file in the command line. For example, `python gg_api.py 2015` uses the 2015 tweets.

Alternatively, you might want to call the functions in the API individually, as the autograder does. To do so, follow the instructions below.

Include `gg_api.py` in the imports: `import gg_api.py`. This will automatically execute the pre-ceremony process, which downloads a list of names of famous people from the IMDb database.

You **must** run `gg_api.main(None, years)`, where `years` is an array of strings for each year you plan to use gg_api with, e.g. `years = ['2013', '2015']`. This will load in the corresponding tweet corpora.

After doing both of the steps above, you can run any of the API functions as expected: `get_nominees('2013')`. This works so long as the order used in the autograder is maintained, as some of the functions use the results of previous functions. (This ensures, for example, that the winner is one of the nominees.) This will not, however, generate the json or the human-readable output.

## Authors

* **Michael Huyler** - *2020*  - [GitHub](https://github.com/KobraKid)
* **Robert Smart** - *2019*  - [GitHub](https://github.com/rbrtsmart)
* **Salome Wairimu** - *2020*  - [GitHub](https://github.com/SalomeWairimu)
* **Ulyana Kurylo** - *2020*  - [GitHub](https://github.com/ulyanakurylo)
