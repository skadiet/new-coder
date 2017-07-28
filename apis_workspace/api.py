from __future__ import print_function
from matplotlib import pyplot as plt
import numpy as np
import requests
import logging

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
            while not line.startswith('Date'):
                pass
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
    MY_KEY = 'c778a444e694e45e1a2fffcbf6d906a9d528052e'
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
        labels.insert(0,u"{0}\n$ {1}\n$ {2}".format(name, price, round(adjusted_price,2))
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

    plt.show(dpi=72)    
    #uncomment if you want to save the file
    #plt.savefig(output_file, dpi=72)

def main():
    a = list(GiantbombAPI('c778a444e694e45e1a2fffcbf6d906a9d528052e'))
    print(a)

if __name__ == '__main__':
    main()
