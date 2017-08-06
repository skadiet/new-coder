#!usr/bin/env bash

# be sure to change both virtualenv directory and scrape/living_social
# directory to where your venv and code is.
#SHELL=//bin/bash
#source $WORKON_HOME/ScrapeProj/bin/activate
. $HOME/.virtualenvs/ScrapeProj/bin/activate
cd ~/projects/new-coder/scrape_workspace/my_scraper/scraper_app
scrapy crawl livingsocial_spider
