# urls_regex_finding
Script for fetching &amp; storing URLs content against predefined list of regex
Design overview:
- CLI arguments for URLs and regex lists are used as input arguments
- each URL HTML content is fetched asynchronously
- all matching results are written asynchronously to the output .txt file

# Prerequisites:
- Python version 3.6+

# Step 1: install all necessary packages from the root folder:
- python3 install_packages.py

# Step 2: run the command from terminal:
- python3 --urls [some urls delimited by space] --regex [some regex delimited by space]
- ready examples in command_examples.txt file
