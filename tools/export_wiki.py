"""This script exports the wiki pages from Redmine in HTML.

All wiki pages on Redmine (https://cocomud.plan.io) are saved in the
'doc' directory.

Requirements:
    This script needs 'python-redmine', which you can obtain with
        pip install python-redmine
    This script also needs BeautifulSoup:
        pip install BeautifulSoup

"""

import argparse
import os
import sys
import urllib2

from BeautifulSoup import BeautifulSoup
from redminelib import Redmine

# Create an argument parser
parser = argparse.ArgumentParser(
        description="export wiki pages in various formats")
parser.add_argument("lang", help="the language code (en, fr, es...)",
        nargs='?', choices=["en", "fr"], default="en")
args = parser.parse_args()

# Configure the system
lang = args.lang
format = "html"
doc = os.path.join("..", "doc", lang)

# Connects to the REST API
redmine = Redmine("https://cocomud.plan.io")

# Gets the wiki pages of the documentation
# Note: if the exported documentation is in English (the default),
# then pages are retreived from the 'cocomud-client' project.  Otherwise,
# they are retrieved from the project with the language code (for
# example, 'fr' for French).
if lang == "en":
    project_id = "cocomud-client"
else:
    project_id = lang

pages = redmine.wiki_page.filter(project_id=project_id)
for page in pages:
    url = "https://cocomud.plan.io/projects/{id}/wiki/{title}.html".format(
            id=project_id, title=page.title)
    response = urllib2.urlopen(url)
    content = response.read()
    soup = BeautifulSoup(content)

    # Find the links
    for link in soup.findAll("a"):
        try:
            href = link["href"]
        except KeyError:
            continue

        if href.startswith("/projects/{}/wiki/".format(project_id)):
            link["href"] = href[16 + len(project_id):] + ".html"
        elif href.startswith("/"):
            link["href"] = "https://cocomud.plan.io" + href

    exported = str(soup)

    # Write the exported file
    path = os.path.join(doc, page.title + "." + format)

    print "Writing", page.title, "in", path
    exported = exported.replace("\r", "")
    file = open(path, "w")
    file.write(exported)
    file.close()

# Export the full wiki
print "Downloading the complete HTML export."
url = "https://cocomud.plan.io/projects/{id}/wiki/export.html".format(
        id=project_id)
response = urllib2.urlopen(url)
content = response.read()
content = content.replace("\r", "")
path = os.path.join(doc, "index.html")
file = open(path, "w")
file.write(content)
file.close()
