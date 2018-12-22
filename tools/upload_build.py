"""This script upload a newly-build version of CocoMUD for Windows.

The Download wiki page on Redmine are updated.

Requirements:
    This script needs 'python-redmine', which you can obtain with
        pip install python-redmine

"""

import argparse
from json import dumps
import os
import re
import sys
from urllib import request

from redminelib import Redmine
from redminelib.exceptions import ResourceNotFoundError

# Create an argument parser
parser = argparse.ArgumentParser(
        description="upload a new CocoMUD build")
parser.add_argument("key", help="the API key to upload to Redmine")
args = parser.parse_args()

# Configure the system
key = args.key

# Connects to the REST API
redmine = Redmine("https://cocomud.plan.io", key=key)

# Check that the file exists
path = os.path.abspath("../src/build/CocoMUD.zip")
if not os.path.exists(path):
    print("The file {} cannot be found.".format(path))
    sys.exit(1)

# Then upload this file
print("Retrieving the Download wiki page on 'cocomud-client'...")
page = redmine.wiki_page.get("Download", project_id="cocomud-client")
print("Uploading {}...".format(path))
text = page.text
page.uploads = [{"path": path, "filename": "CocoMUD.zip"}]
page.text = text
print("Saving the page...", page.save())

# Get the new resource URL
url = list(page.attachments)[-1].content_url

# Retrieve the version number
with open("../src/version.py", encoding="utf-8") as file:
    content = file.read()

version = content.partition("=")[2].strip()

# Now we get ALL wiki pages with the title 'Download' and replace the URL
for project in redmine.project.all():
    identifier = project.identifier

    # Try to get the 'Download' page
    try:
        page = redmine.wiki_page.get("Download", project_id=identifier)
    except ResourceNotFoundError:
        pass
    else:
        print("Updating the Download page for the {} project...".format(
                identifier))
        text = page.text
        text = re.sub(r"https\://cocomud\.plan\.io/attachments/" \
                r"download/\d+/CocoMUD\.zip", url, text)
        text = re.sub(r"\+\*\d+\*\+", "+*" + version + "*+", text)
        page.text = text
        success = page.save()
        if success:
            print("Correctly saved the wiki page.")
        else:
            print("Error while saving the wiki page.")

# Update the build information in the custom field
build = dumps({version: {"windows": url}})
print("Updating the custom field")
redmine.project.update(resource_id=2,
        custom_fields=[{"id": 3, "value": build}])
print("URL", url)
