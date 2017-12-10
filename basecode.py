import urllib2
import urllib
from urllib import urlencode
import json, jinja2, os, webapp2
import logging

top_stories_api_key = "Add your code here"

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                        extensions=['jinja2.ext.autoescape'],
                                        autoescape=True)

# Makes the JSON file pretty and readable
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


# This method calls the API and returns the json file for the program
def getSection(section, params={"api-key": top_stories_api_key}):
    try:
        baseurl = "https://api.nytimes.com/svc/topstories/v2/"
        format = "json"
        encoded = urlencode(params)
        url = baseurl + section + "." + format + "?" + encoded
        loadTopStories = urllib2.urlopen(url).read()
        loadJsonofTopStories = json.loads(loadTopStories)
        return loadJsonofTopStories
    except:
        return "There is an error right here"


# This method creates a dictionary of all the articles in the section. In the dictionary, there are titles, updated and
# published dates of the article, thumbnail of the article, and the link to the article. The dictionary also changes
def getDictionary(json_file):
    allArticles = {}
    for article in json_file["results"]:
        allArticles[article["title"]] = {}

        author = article["byline"][3:]
        if author == "":
            author = "We couldn't find an author"
        allArticles[article["title"]]["author"] = author
        allArticles[article["title"]]["url"] = article["url"]
        allArticles[article["title"]]["articlename"] = article["title"]
        mediatypes = article["multimedia"]
        for photo in mediatypes:
            if photo["format"] == "Standard Thumbnail":
                thumbnail = photo["url"]
                allArticles[article["title"]]["thumbnail"] = thumbnail
        allArticles[article["title"]]["published-date"] = {}
        allArticles[article["title"]]["published-date"]["year"] = article["published_date"][0:4]
        allArticles[article["title"]]["published-date"]["month"] = article["published_date"][5:7]
        allArticles[article["title"]]["published-date"]["day"] = article["published_date"][8:10]
        allArticles[article["title"]]["published-date"]["hour"] = article["published_date"][11:13]
        allArticles[article["title"]]["published-date"]["minutes"] = article["published_date"][14:16]
        allArticles[article["title"]]["published-date"]["seconds"] = article["published_date"][17:19]

        allArticles[article["title"]]["updated-date"] = {}
        allArticles[article["title"]]["updated-date"]["year"] = article["updated_date"][0:4]
        allArticles[article["title"]]["updated-date"]["month"] = article["updated_date"][5:7]
        allArticles[article["title"]]["updated-date"]["day"] = article["updated_date"][8:10]
        allArticles[article["title"]]["updated-date"]["hour"] = article["updated_date"][11:13]
        allArticles[article["title"]]["updated-date"]["minutes"] = article["updated_date"][14:16]
        allArticles[article["title"]]["updated-date"]["seconds"] = article["updated_date"][17:19]

    return allArticles


# This method takes the dictionary that has been previously created, sorts based on published dates and returns a list
# of articles
def sortDatesPublishedDates(dictionary):
    # Make a list of tuples that has the different types of dates
    # Sort by the year
    # sort by the month
    # sort by the hour
    # sort by the minutes
    # sort by the seconds
    newlist = []
    for article in dictionary:
        # print(article)
        newlist.append(dictionary[article])
    sortedList = sorted(newlist, key=lambda article: (article["published-date"]["year"], article["published-date"]["month"], article["published-date"]["day"], article["published-date"]["hour"], article["published-date"]["minutes"], article["published-date"]["seconds"],), reverse=True)
    return sortedList


# This function takes the dictionary that has been previously created, sorts based on published dates and returns a list
def sortDatesUpdatedDates(dictionary):
    newlist = []
    for article in dictionary:
        # print(article)
        newlist.append(dictionary[article]["updated-date"])
    sortedList = sorted(newlist, key=lambda article: (
    article["year"], article["month"], article["day"], article["hour"], article["minutes"], article["seconds"],),
    reverse=True)
    return sortedList


# This class takes the information from each dictionary in the list and returns a formatted string
class article():
    def __init__(self, article):
        self.author = article["author"]
        self.title = article["articlename"]
        if "thumbnail" in article.keys():
            self.thumbnail = article["thumbnail"]
        self.url = article["url"]

        self.published_year = article["published-date"]["year"]
        self.published_month = article["published-date"]["month"]
        self.published_day = article["published-date"]["day"]
        self.published_hour = article["published-date"]["hour"]
        self.published_minutes = article["published-date"]["minutes"]
        self.published_seconds = article["published-date"]["seconds"]

        self.updated_year = article["updated-date"]["year"]
        self.updated_month = article["updated-date"]["month"]
        self.updated_day = article["updated-date"]["day"]
        self.updated_hour = article["updated-date"]["hour"]
        self.updated_minutes = article["updated-date"]["minutes"]
        self.updated_seconds = article["updated-date"]["seconds"]

        self.allupdated = str(self.updated_month) + "-" + str(self.updated_day) \
               + "-" + str(self.updated_year) + " at " + str(self.updated_hour) + ":" \
               + str(self.updated_minutes) + ":" + str(self.updated_seconds) + " EST"
        self.allpublished = str(self.published_month) + \
               "-"  + str(self.published_day) + "-" + str(self.published_year) + " at " + \
               str(self.published_hour) + ":" + str(self.published_minutes) + ":" + str(self.published_seconds) + " EST"
    def __str__(self):
        return self.title + "\n" + self.author + "\nUpdated: " + self.allupdated + "\nPublished: " + self.allpublished


# This class is the main handler where the first welcome screen
class Mainhandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")
        values = {}
        template = JINJA_ENVIRONMENT.get_template('welcome.html')
        self.response.write(template.render(values))


# This class that handles the results and prints the results in to an HTML page
class respondHandler(webapp2.RequestHandler):
    def post(self):
        values={}
        section = self.request.get("section")
        if section:
            values["section"] = section
            #Takes into account capitalization and
            section = self.request.get("section").lower().replace(" ","")

            articles = getSection(section)
            dictionaryofvalues = getDictionary(articles)

            listofarticles = sortDatesPublishedDates(dictionaryofvalues)
            toptenarticles = listofarticles[:10]
            listofclassarticles = []
            for x in toptenarticles:
                #print(article(x))
                listofclassarticles.append(article(x))
            values["articles"] = listofclassarticles

            template = JINJA_ENVIRONMENT.get_template('template.html')
            self.response.write(template.render(values))
        else:
            template = JINJA_ENVIRONMENT.get_template('welcome.html')
            self.response.write(template.render(values))

# Runs the program on app engine
application = webapp2.WSGIApplication([ \
                                      ('/gresponse', respondHandler),
                                      ('/.*', Mainhandler)
                                      ],
                                      debug=True)

