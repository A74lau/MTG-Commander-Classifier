# MTG Commander Classifier

A Python-based tool for analyzing and classifying Magic: The Gathering Commander cards using data from EDHREC and Scryfall.

## Overview

This project aims to create a comprehensive dataset of Magic: The Gathering Commander cards by combining data from EDHREC (for deck statistics and tags) and Scryfall (for card information). The resulting dataset can be used for various machine learning and data analysis purposes related to MTG Commander format.

## Features

- Fetches card data from Scryfall API
- Retrieves deck statistics and tags from EDHREC
- Combines data from both sources
- Generates comprehensive CSV files for analysis
- Handles mismatches between data sources

## Scripts and Outputs

### `all_together.py`
Main script that combines data from both EDHREC and Scryfall. Outputs:
- `all_together_output.csv`: Combined card information with tags/class labels
- `non_matching_commander_cards.csv`: Cards that couldn't be matched with EDHREC data
- `commander_cards_w_tag.csv`: EDHREC data with commander names, tags, and deck counts

### `edhrec_csv_generator_tags.py`
Fetches data from EDHREC. Outputs:
- `commander_cards_w_tag.csv`: Commander names, tags, and deck counts
- `tags_parsed.csv`: List of tag URLs used for finding relevant commanders

### `scryfall_csv_generator.py`
Fetches data from Scryfall. Outputs:
- `commander_cards.csv`: Basic card information without tags/class labels

## Setup and Usage

1. Ensure you have Python 3.x installed
2. Install required dependencies:
   ```bash
   pip install requests pandas
   ```
3. Run the scripts in the following order:
   ```bash
   python scryfall_csv_generator.py
   python edhrec_csv_generator_tags.py
   python all_together.py
   ```

## Data Sources

- [Scryfall API](https://scryfall.com/docs/api)
- [EDHREC](https://edhrec.com/)


## Contributing

Feel free to submit issues and enhancement requests!
