"""This script diff3 the wiki pages to generate a translation.

The process of translating wiki pages can be summarized this way:
1. The wiki page is created in English.
2. This script is called for a translation (like 'fr', or 'es'...).
3. The English version of the wiki is downloaded and put into the translation.
4. The translator translates this file into another language.
(At this point, the translated wiki can be uploaded).
5. The English wiki page is modified.
6. This script is called again to update the translated page.
7. The old version of the wiki page in English is downloaded.
8. The newer version of the wiki page in English is downloaded.
9. With diff3, these files are compared with the translated page.
10. The translated page is marked with the new verison.
11. The translator can translate it and upload it.
12. ... And so on

For this reason, the version of the new English wiki page has to be
stored in the translated page.  This doesn't prevent conflicts when
several translators modify the same file at the same time (which,
hopefully, shouldn't occur), but several translators can work on
different files without bothering each other.

Requirements:
    This script needs 'python-redmine', which you can obtain with
        pip install python-redmine
    It also needs a 'diff3' application accessible through the standard
    path.  It may require some installing on Linux.  On Windows, 'diff3'
    can be found in Cygwin.  If a better solution can be found, you're
    welcome to update this script.

"""

import argparse
import os
import sys

from redmine import Redmine

# Create an argument parser
parser = argparse.ArgumentParser(
        description="prepare wiki pages for translation")
parser.add_argument("lang", help="the language code (en, fr, es...)",
        choices=["fr"])
parser.add_argument("-i", "--interactive", action="store_true",
        help="should confirmation be asked for each file?")
args = parser.parse_args()

# Configure the system
lang = args.lang
interactive = args.interactive

# Connects to the REST API
redmine = Redmine("https://cocomud.plan.io")

# Gets the most recent version of the wiki pages
if lang == "en":
    project_id = "cocomud-client"
else:
    project_id = lang

# Look for pages that already exist
l_pages = redmine.wiki_page.filter(project_id="cocomud-client")
pages = {}
for page in l_pages:
    pages[page.title] = page

path = os.path.join("..", "doctext", lang)
for page in pages.values():
    title = page.title
    filepath = os.path.join(path, title + ".txt")
    if os.path.exists(filepath):
        # Get the older version
        file = open(filepath, "r")
        content = file.read()
        file.close()
        lines = content.splitlines()
        first = lines[0]
        content = "\n".join(lines[1:])

        # We try to convert the version
        version = int(first)
        if page.version == version:
            print "Tried to update", title, ", visibly at the top version"
        else:
            old_page = redmine.wiki_page.get(title,
                    project_id="cocomud-client", version=version)

            # Save these three files
            old_path = os.path.join(path, "old.txt")
            old_file = open(old_path, "w")
            old_file.write(old_page.text)
            old_file.close()
            new_path = os.path.join(path, "new.txt")
            new_file = open(new_path, "w")
            new_file.write(page.text)
            new_file.close()
            tr_path = os.path.join(path, "tr.txt")
            tr_file = open(tr_path, "w")
            tr_file.write(content)
            tr_file.close()

            # Call 'diff3' on these three files
            if interactive:
                answer = raw_input("Should the 'diff3' operation be " \
                        "performed for fhe file '{}' (Y/N)?".format(title))
                if answer.lower() != "y":
                    continue

            diff3 = os.popen("diff3 -m {tr} {old} {new} -L translated " \
                    "-L common -L newer".format(old=old_path,
                    new=new_path, tr=tr_path)).read()

            # Write the result in the file
            file = open(filepath, "w")
            file.write(str(page.version) + "\n" + diff3)
            file.close()

            # Remove all three files
            os.remove(os.path.join(path, "old.txt"))
            os.remove(os.path.join(path, "new.txt"))
            os.remove(os.path.join(path, "tr.txt"))
            print "Updated the file", filepath, "at version", page.version
    else:
        file = open(filepath, "w")
        file.write(str(page.version) + "\n")
        file.write(page.text)
        file.close()
        print "Created the file", filepath, "at version", page.version
