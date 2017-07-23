#!/bin/python

import sys
import csv
MY_FILE = '../data/sample_sfpd_incident_all.csv'

def parse(raw_file, delimiter):

    #open csv file
    opened_file = open(raw_file)
    
    #read csv data
    csv_data = csv.reader(opened_file, delimiter = delimiter)

    #map fields into dict
    parsed_data = []
    fields = csv_data.next()
    for row in csv_data:
           parsed_data.append(dict(zip(fields, row)))

    #close file
    opened_file.close()

    return parsed_data

def main():
    parsed_text = parse(MY_FILE, ',')
    print parsed_text

if __name__ == '__main__':
    main()
