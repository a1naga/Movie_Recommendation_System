# This web crawler program scrapes the imdb website
# to fetch poster images of movies and writes the image url and movie url to an output file

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import HTTPError
import csv
import re
import time

#Beautiful soup API reads the html content from the given url
def make_soup(in_url):
    try:
        html = urlopen(in_url)
    except HTTPError as e:
        print(e)
        return None
    else:
        soupdata = BeautifulSoup(html, "html.parser")
        return soupdata

# Handling the error when url not found for the movie
def error_handling():
    print("Url Not Found for movieid{0}".format(line[0]))
    line[2] = "Image not found"
    writer.writerow([line[0], line[1], line[2]])

#  Links of input and output csv files
links_url = "/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/links.csv"
output_csv_url = "/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/links_with_url.csv"

# This segment of code opens and reads the input file -- links.csv
# to get the imdb movie id and forms the url string for each id,
# and scrapes the imdb webpage to get the respective poster image of the movie,
# and writes the image url into the output csv file for later usage
with open(links_url, "r") as csvfile:
    with open(output_csv_url, "w") as outcsv:
        headers = ['movieId', 'imdbId', 'poster_url','reference_link']
        writer = csv.writer(outcsv)
        writer.writerow(headers)
        imdbid_reader = csv.reader(csvfile)
        headers = next(imdbid_reader,None)
        print(headers)
        counter = 0
        for line in imdbid_reader:
            if line != headers:
                imdbid = line[1]
                if(len(imdbid) == 5):
                    imdbid_full = "tt00" + str(imdbid)
                elif(len(imdbid) == 6):
                    imdbid_full = "tt0" + str(imdbid)
                elif(len(imdbid) == 7):
                    imdbid_full = "tt" + str(imdbid)
                image_url = "http://www.imdb.com/title/{0}/".format(imdbid_full)
                soup = make_soup(image_url)
                counter += 1
                # Make the code sleep for 5 seconds in order to avoid the continuous hit on the imdb website
                if counter % 100 == 0:
                    print("------------------------------------------------------------")
                    print("Finished processing {0} records".format(counter))
                    print("------------------------------------------------------------")
                    # time.sleep()

                if soup is None:
                    print("SoupData Not Found for movieid: {0}, imdbid: {1}".format(line[0], imdbid_full))
                    line[2] = "Image not found"
                    writer.writerow([line[0], line[1], line[2], image_url])

                else:
                    image = soup.find("img", {"alt" : re.compile(r".* Poster")}, itemprop="image")
                    # check if the image or the image['src'] is None and insert records accordingly
                    if (image is None) or (image['src'] is None):
                        print("Url Not Found for movieid{0}".format(line[0]))
                        line[2] = "Image not found"
                        writer.writerow([line[0], line[1], line[2], image_url])
                    else:
                        # print("image_url", image['content'])
                        out_url = image['src']
                        # print(out_url)
                        writer.writerow([line[0],line[1],out_url, image_url])

csvfile.close()
outcsv.close()