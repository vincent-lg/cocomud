"""This script imports the wiki pages from the disk to Redmine.

All wiki pages on disk (doctext/{lang}) are saved on Redmine
(https://cocomud.plan.io).

Requirements:
    This script needs 'python-redmine', which you can obtain with
        pip install python-redmine

"""

import argparse
import os
import sys

from redmine import Redmine

# Create an argument parser
parser = argparse.ArgumentParser(
        description="import wiki pages in various languages")
parser.add_argument("lang", help="the language code (en, fr, es...)",
        nargs='?', choices=["en", "fr"], default="en")
parser.add_argument("-k", "--key", required=True,
        help="your Redmine API key")
args = parser.parse_args()

# Configure the system
lang = args.lang
key = args.key

# Connects to the REST API
redmine = Redmine("https://cocomud.plan.io", key=key)

# Gets the wiki pages of the documentation
# Import the wiki pages from disk
# then pages are retreived from the 'cocomud-client' project.  Otherwise,
# they are retrieved from the project with the language code (for
# example, 'fr' for French).
if lang == "en":
    project_id = "cocomud-client"
else:
    project_id = lang

# Look for pages that already exist
defaults = redmine.wiki_page.filter(project_id="cocomud-client")
pages = redmine.wiki_page.filter(project_id=project_id)
existing = {}
parents = {}
for page in pages:
    existing[page.title] = page

# Determine the parents
for page in defaults:
    page.refresh()
    print list(page)
    parents[page.title] = page.parent

print parents
exit(1)
# Import the pages from disk
path = os.path.join("..", "doctext", lang)
for filename in os.listdir(path):
    filepath = os.path.join(path, filename)
    title = filename[:-4]
    answer = raw_input("Do you want to export '{}' (Y/N)?".format(title))
    if answer.lower() != "y":
        continue

    file = open(filepath, "r")
    text = file.read()
    file.close()

    # Create the page if needed
    if title in existing.keys():
        page = existing[title]
        page.text = text
        page.save()
    else:
        page = redmine.wiki_page.create(project_id=project_id,
                title=title, text=text)

    print "Imported '{}' in wiki '{}'.".format(lang, project_id)
