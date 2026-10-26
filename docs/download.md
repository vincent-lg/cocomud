---
title: "Downloading and installing CocoMUD"
---

# Downloading and installing CocoMUD

CocoMUD is pre-built on Windows as a portable archive.  It means that the only thing you'll have to do, if you are using Windows, is downloading the archive (see link below), extract it and open the **cocomud.exe** file.  The details are provided in the following sections.

## Downloading CocoMUD

CocoMUD for Windows is published on the [CocoMUD releases page](https://github.com/vincent-lg/cocomud/releases).  Download the file named **CocoMUD.zip** from the most recent build.

If you are using another platform, you might wish to [install CocoMUD from source](https://github.com/vincent-lg/cocomud).  CocoMUD can run on Linux or Mac OS, although there's no pre-built version yet.

If you are accessing this page from a version of CocoMUD already installed, please note that the links given above may be out-of-date.  You should refer to the [online documentation](https://cocomud.org/download.html) to download the correct file.

## Installing CocoMUD

Once you have downloaded the archive, you can extract it in a folder.  CocoMUD doesn't require installation, it will run as a portable software (you can even put it on a USB flash drive and take it with you).

1. Extract the **CocoMUD.zip** file in your desired folder.  Note that CocoMUD cannot run from the archive itself (if it does, it will not be able to write anything).
1. In the extracted archive, you should find a folder named **CocoMUD**.  Open it.
1. In it is a file **cocomud.exe**.  Click on it.  CocoMUD should open and display the connection screen.
1. Should you like CocoMUD, don't hestitate to create a shortcut leading to **cocomud.exe** to make your life a bit easier.

To learn how to use CocoMUD, you might want to read [the basics of CocoMUD](basics.md).  It will give you a step-by-step explanation and demonstration of some of the basic features.  More advanced topics will be convered in the rest of the documentation.

## Updating CocoMUD

CocoMUD has a built-in updater that opens when you launch CocoMUD.  The updater will check for new versions of CocoMUD and, if found, will ask you if you wish to update.  If you reply **yes**, CocoMUD will close and the updater will download and install CocoMUD, before starting the program again.

You can also see if there are updates by opening CocoMUD.  In the menu bar, select **Help**, then **Check for updates**.  The dialog might take a few seconds to load, since CocoMUD checks for updates on the website.  If everything goes well, the updater should tell you that there is no update, or that there is one and ask you if you want to install it.

Several things can prevent the updater of running properly.  Windows Firewall, Windows Defender, an anti-virus software or another software to protect your system might deny the updater the right to install CocoMUD.

If you run into problems while updating, CocoMUD might become corrupted, meaning it can't even start, or if it does, it displays aa lot of errors.  If that happens, there are a few steps you can take to solve the issue:

1. Forcing update: in some cases, CocoMUD tries to update, but some folders are incorrectly changed.  A software to protect your system might increase the risks of this situation to arise.  With Windows firewall and Windows Defender, that situation doesn't occur very often.  If you click on **cocomud.exe** after updating and nothing happens, or if CocoMUD opens but creates a lot of errors, try to force update.  To do this, close CocoMUD (if it were open at all) and click on the file named **dbg_updater.exe**.  **dbg** stands for **debug**, and it will run a debug update with minimal data.  Even if it looks like you're up-to-date, **dbg_updater** will just download the lattest version of CocoMUD, keeping your configuration.  This file will open a console with a progress bar, but you are not expected to do anything, just let it do its work.  If everything goes well, CocoMUD should open in its new version after updating.  If that still doesn't fix the problem, try to run it again before moving to step 2.
1. Manual update: sometimes, CocoMUD is so corrupted that **dbg_updater** can't run, or can't do much.  A manual installation is then the next step.  Simply download CocoMUD again (see the link above), and extract it in a folder.  To transfer your old configuration in your fresh copy, just go in your old directory.  Copy both the **settings** folder and the **worlds** folder.  These contains your configuration.  Go into your fresh copy, remove these folders and replace them with the ones you had in your old configuration.  Then launch CocoMUD.

If that doesn't fix the problem, you can definitely contact the team of developers by [creating a bug report](https://github.com/vincent-lg/cocomud/issues).

We wish you the best of gaming experiences with CocoMUD!
