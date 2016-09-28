"""This script exports the wiki pages from Redmine.

All wiki pages on Redmine (https://cocomud.plan.io) are saved in the
'doc' directory.

Requirements:
    This script needs 'python-redmine', which you can obtain with
        pip install python-redmine
    This script also needs BeautifulSoup:
        pip install BeautifulSoup

"""

import os
import urllib2

from BeautifulSoup import BeautifulSoup
from redmine import Redmine

lang = "en"
doc = "../doc/{lang}".format(lang=lang)

# Connects to the REST API
redmine = Redmine("https://cocomud.plan.io")

# Gets the wiki pages
pages = redmine.wiki_page.filter(project_id="cocomud-client")
for page in pages:
    url = "https://cocomud.plan.io/projects/cocomud-client/wiki/" \
            "{title}.html".format(title=page.title)
    print "Triggering URL", url
    response = urllib2.urlopen(url)
    content = response.read()
    soup = BeautifulSoup(content)

    # Find the links
    for link in soup.findAll("a"):
        try:
            href = link["href"]
        except KeyError:
            continue

        if href.startswith("/projects/cocomud-client/wiki/"):
            link["href"] = href[30:] + ".html"
        elif href.startswith("."):
            link["href"] = "https://cocomud.plan.io" + href

    # Write the exported HTML file
    path = os.path.join(doc, page.title + ".html")
    print "Writing", page.title, "in", path
    file = open(path, "w")
    file.write(str(soup))
    file.close()
