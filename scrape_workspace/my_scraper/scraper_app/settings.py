BOT_NAME = 'livingsocial'

SPIDER_MODULES = ['scraper_app.spiders']

#This was the original database instructions from the tutorial
#DATABASE = {
#    'drivername': 'postgres',
#    'host': 'localhost',
#    'port': '5432',
#    'username': 'postgres',
#    'password': 'scrape',
#    'database': 'scrape'
#}

#These are the database instructions that I came up with
DATABASE = {
    'drivername': 'postgres',
    'database': 'postgres'
}

ITEM_PIPELINES = ['scraper_app.pipelines.LivingSocialPipeline']
