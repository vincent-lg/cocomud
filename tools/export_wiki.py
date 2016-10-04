"""This script exports the wiki pages from Redmine.

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
from redmine import Redmine

# Create an argument parser
parser = argparse.ArgumentParser(
        description="export wiki pages in various formats")
parser.add_argument("lang", help="the language code (en, fr, es...)",
        nargs='?', choices=["en", "fr"], default="en")
group = parser.add_mutually_exclusive_group()
group.add_argument("-t", "--txt", help="export in txt format",
        action="store_true")
group.add_argument("-l", "--html", help="export in html format",
        action="store_true")
args = parser.parse_args()

# Configure the system
lang = args.lang
if args.txt:
    format = "txt"
elif args.html:
    format = "html"
else:
    print "You must specify the format in which to export."
    sys.exit(1)

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

# If the exported format is txt, the directory differs
if format == "txt":
    doc = "../doctext/{lang}".format(lang=lang)
else:
    doc = "../doc/{lang}".format(lang=lang)

pages = redmine.wiki_page.filter(project_id=project_id)
for page in pages:
    # HTML export if needed
    url = "https://cocomud.plan.io/projects/{id}/wiki/{title}.html".format(
            id=project_id, title=page.title)
    if format == "txt":
        exported = page.text
    elif format == "html":
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
    else:
        raise ValueError("unknown format {}".format(format))

    # Write the exported file
    path = os.path.join(doc, page.title + "." + format)

    # If the file contains a version number, do not override it
    version = None
    if os.path.exists(path):
        file = open(path, "r")
        content = file.read()
        file.close()
        lines = content.splitlines()
        if lines[0].isdigit():
            version = int(lines[0])

    print "Writing", page.title, "in", path, "version", version
    exported = exported.replace("\r", "").decode("utf-8").encode("latin-1")
    file = open(path, "w")
    if version is not None:
        file.write(str(version) + "\n")
    file.write(exported)
    file.close()

# If exporting in HTML, also get the full file
if format == "html":
    print "Downloading the complete HTML export."
    url = "https://cocomud.plan.io/projects/{id}/wiki/export.html".format(
            id=project_id)
    response = urllib2.urlopen(url)
    content = response.read()
    path = os.path.join(doc, "index.html")
    file = open(path, "w")
    file.write(content)
    file.close()
