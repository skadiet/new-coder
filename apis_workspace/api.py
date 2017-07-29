from __future__ import print_function
from matplotlib import pyplot as plt
import numpy as np
import requests
import logging
import argparse
import tablib
import os

CPI_DATA_URL = 'http://research.stlouisfed.org/fred2/data/CPIAUCSL.txt'

class CPIData(object):
    def __init__(self):
        self.year_cpi = {}
        self.last_year = None
        self.first_year = None

    def load_from_url(self, url, save_as_file=None):
        fp = requests.get(url, stream=True, headers={'Accept-Encoding': None}).raw
        if save_as_file==None:
            return self.load_from_file(fp)
        else:
            with open(save_as_file, 'wb+') as out:
                while True:
                    buffer = fp.read(81920)
                    if not buffer:
                        break
                    out.write(buffer)
            with open(save_as_file) as fp:
                return self.load_from_file(fp)
        
    def load_from_file(self, fp):
        """Loads CPI data from a file-like object"""
        current_year = None
        year_cpi = []
        for line in fp:
            if line.startswith('DATE '):
                break
        for line in fp:
            data = line.rstrip().split()
            year = int(data[0].split('-')[0])
            cpi = float(data[1])
            if self.first_year is None:
                self.first_year = year
            self.last_year = year
            if current_year!=year:
                if current_year is not None:
                    self.year_cpi[current_year] = sum(year_cpi) / len(year_cpi)
                year_cpi = []
                current_year = year
            year_cpi.append(cpi)
        if current_year is not None and current_year not in self.year_cpi:
            self.year_cpi[current_year] = sum(year_cpi) / len(year_cpi)

    def get_adjusted_price(self, price, year, current_year=None):
        '''returns the price of a given item from a given year compared to the current year specified'''
        if current_year == None or current_year>2013:
            current_year = 2013
        if year<self.first_year:
            year=self.first_year
        elif year>self.last_year:
            year=self.last_year

        year_cpi = self.year_cpi[year]
        current_cpi = self.year_cpi[current_year]
        
        return float(price) / year_cpi * current_cpi    

class GiantbombAPI(object):
    """This is the API to Giantbomb.com"""
    base_url = 'http://www.giantbomb.com/api'

    def __init__(self, api_key):
        self.api_key = api_key

    def get_platforms(self, sort=None, filter=None, field_list=None):
        '''Generator yielding platforms matching the given criteria'''
        params = {}
        if sort is not None:
            params['sort']=sort
        if field_list is not None:
            params['field_list'] = ','.join(field_list)
        if filter is not None:
            params['filter']=filter
            parsed_filters = []
            for k, v in filter.iteritems():
                parsed_filter.append('{0}:{1}'.format(k,v))
            params['filter'] = ','.join(parsed_filter)

        #Remember to add this to the tutorial!!
        user_agent = {'User-Agent': 'ScottTestScott'}
 
        params['api_key'] = self.api_key
        params['format'] = 'json'
        
        incomplete_result = True
        num_total_results = None
        num_fetched_results = 0
        counter = 0

        while incomplete_result:
            params['offset'] = num_fetched_results
            #Remember to add this to the tutorial!!!
            result = requests.get(self.base_url + '/platforms/', params=params, headers=user_agent)
            result = result.json()
            if num_total_results is None:
                num_total_results = int(result['number_of_total_results'])
            num_fetched_results += int(result['number_of_page_results'])
            if num_fetched_results >= num_total_results:
                incomplete_result = False
            for item in result['results']:
                logging.debug("Yielding platform {0} of {1}".format(
                    counter + 1,
                    num_total_results))

                if 'original_price' in item and item['original_price']:
                    item['original_price'] = float(item['original_price'])

                yield item
                counter +=1

def is_valid_dataset(platform):
    """Filters out datasets that we can't use since they are either lacking
    a release date or an original price. For rendering the output we also
    require the name and abbreviation of the platform.

    """
    if 'release_date' not in platform or not platform['release_date']:
        logging.warn(u"{0} has no release date".format(platform['name']))
        return False
    if 'original_price' not in platform or not platform['original_price']:
        logging.warn(u"{0} has no original price".format(platform['name']))
        return False
    if 'name' not in platform or not platform['name']:
        logging.warn(u"No platform name found for given dataset")
        return False
    if 'abbreviation' not in platform or not platform['abbreviation']:
        logging.warn(u"{0} has no abbreviation".format(platform['name']))
        return False
    return True

def generate_plot(platforms, output_file):
    """generates a bar chart out of the given platforms and saves as a png"""
    labels = []
    values = []
    for platform in platforms:
        name = platform['name']
        adapted_price = platform['adjusted_price']
        price = platform['original_price']
        if price > 2000:
            continue #i.e. skip
        if len(name)>15:
            name=platform['abbreviation']
        #This needs to be changed in the demo
        labels.insert(0,u"{0}\n$ {1}\n$ {2}".format(name, price, round(adapted_price,2)))
        values.insert(0, adapted_price)

    #define the size of the bar and size of the graph    
    width = 0.3
    ind = np.arange(len(values))
    fig = plt.figure(figsize=(len(labels) * 1.8, 10))

    ax = fig.add_subplot(1, 1, 1)
    ax.bar(ind, values, width, align='center')

    # Format the X and Y axis labels. Also set the ticks on the x-axis slightly
    # farther apart and give then a slight tilting effect.
    plt.ylabel('Adjusted price')
    plt.xlabel('Year / Console')
    ax.set_xticks(ind + 0.3)
    ax.set_xticklabels(labels)
    fig.autofmt_xdate()
    plt.grid(True)

    #plt.show(dpi=72)    
    #uncomment if you want to save the file
    plt.savefig(output_file, dpi=72)

def generate_csv(platforms, output_file):
    dataset = tablib.Dataset(headers=['Abbreviation', 'Name', 'Year', 'Price', 'Adjusted Price'])
    for p in platforms:
        dataset.append([p['abbreviation'],p['name'], p['year'], p['original_price'], p['adjusted_price']])
    if isinstance(output_file, basestring):
        with open(output_file, 'w+') as fp:
            fp.write(dataset.csv)
    else:
        output_file.write(dataset.csv)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--giantbomb-api-key', required=True, help='API key provided by Giantbomb.com')
    parser.add_argument('--cpi-file',
                        default=os.path.join(os.path.dirname(__file__),
                                             'CPIAUCSL.txt'),
                        help='Path to file containing the CPI data (also acts'
                             ' as target file if the data has to be downloaded'
                             'first).')
    parser.add_argument('--cpi-data-url', default=CPI_DATA_URL,
                        help='URL which should be used as CPI data source')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Increases the output level.')
    parser.add_argument('--csv-file',
                        help='Path to CSV file which should contain the data'
                             'output')
    parser.add_argument('--plot-file',
                        help='Path to the PNG file which should contain the'
                             'data output')
    parser.add_argument('--limit', type=int,
                        help='Number of recent platforms to be considered')
    opts = parser.parse_args()
    if not (opts.plot_file or opts.csv_file):
        parser.error("You have to specify either a --csv-file or --plot-file!")
    return opts

def main():
    opts = parse_args()

    if opts.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cpi_data = CPIData()
    gb_api = GiantbombAPI(opts.giantbomb_api_key)

    print ("Disclaimer: This script uses data provided by FRED, Federal"
           " Reserve Economic Data, from the Federal Reserve Bank of St. Louis"
           " and Giantbomb.com:\n- {0}\n- http://www.giantbomb.com/api/\n"
           .format(CPI_DATA_URL))

    if os.path.exists(opts.cpi_file):
        with open(opts.cpi_file) as fp:
            cpi_data.load_from_file(fp)
    else:
        cpi_data.load_from_url(opts.cpi_data_url, save_as_file=opts.cpi_file)

    platforms = []
    counter = 0

    # Now that we have everything in place, fetch the platforms and calculate
    # their current price in relation to the CPI value.
    for platform in gb_api.get_platforms(sort='release_date:desc',field_list=['release_date','original_price', 'name','abbreviation']):
        # Some platforms don't have a release date or price yet. These we have
        # to skip.
        if not is_valid_dataset(platform):
            continue

        year = int(platform['release_date'].split('-')[0])
        price = platform['original_price']
        adjusted_price = cpi_data.get_adjusted_price(price, year)
        platform['year'] = year
        platform['original_price'] = price
        platform['adjusted_price'] = adjusted_price
        platforms.append(platform)

        # We limit the resultset on this end since we can only here check
        # if the dataset actually contains all the data we need and therefor
        # can't filter on the API level.
        if opts.limit is not None and counter + 1 >= opts.limit:
            break
        counter += 1

    if opts.plot_file:
        generate_plot(platforms, opts.plot_file)
    if opts.csv_file:
        generate_csv(platforms, opts.csv_file)

if __name__ == '__main__':
    main()
