**by Mayla Kersten**

The program scrapes the digital initiatives from the European parliament, from [here](https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/). It also allows for filling columns content manually and keeps the content of these columns when re-running the script.

In the terminal you'll find information on if there are new initiatives and if there are updates in the existing list of initiatives. 

The logic of the code is as follows:
![](./documentation/dataflow.png)
 
# Getting started
* Cloning the repository with: `git clone https://github.com/himayla/eu_scraper.git` 
* Create a virtual environment with `python -m venv venv` or `python3 -m venv venv`
* Activate the virutal environment with `source venv/bin/activate`
* Install the required packages with `pip install -r requirements.txt`
* Run the program with `python main.py`

# Code
*parameters.json* - Contains 