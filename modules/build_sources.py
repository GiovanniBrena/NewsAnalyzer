import tweepy
import json
import sys
# from langdetect import detect
import csv
import sys
import getopt

'''
This script converts a .csv file of sources with headers to a json array

-x : input csv file name
-o : output json file name
'''

def parse_sources(file_name):
    sources = []
    headers = None
    iter = 0
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            if iter == 0:
                headers = row
            else:
                entry = {}
                for i in range(0,len(headers)):
                    entry[headers[i]]=row[i]
                sources.append(entry)
            iter=iter+1
    return sources

def save_sources(data, file_name):
    j = json.dumps(data)
    file = open(file_name, 'w')
    file.write(j)
    return

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'x:o:')
    except getopt.GetoptError as err:
        # print help information and exit:
        print('err')  # will print something like "option -a not recognized"
        #        usage()
        sys.exit(2)

    input_file = None
    output_file = None
    for o, a in opts:
        if o == "-x":
            input_file = a
        elif o == "-o":
            output_file = a

    sources = parse_sources(input_file)
    save_sources(sources, output_file)


if __name__ == "__main__":
    main()
