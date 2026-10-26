---
title: "What's new in recent builds"
---

# What's new in recent builds

This page describes the new features added and changes made to each build.  You can browse through each build using headings.

## Build 51

- Add a logger which writes your sessions' text (and the output you give) into a file on disk.  The logger is on by default, but it can be turned off for all sessions (see the logging preferences).  It can also be turned on and off for individual sessions (see the **Game** menu).
- Add the `#pause` functions in SharpScript, to add a pause in your script between actions (like commands) to send to the MUD.  As usual, this is usable in aliases, macros or triggers.  You can add the `#pause` function directly from the interface.
- Add the variable functionality to SharpScript.  SharpScript variables can retain information while the session is running (variables will remain if you reconnect to the same session).  Variables can store contextual information which can be used later.

    To add a variable, you can use the `#writevar` SharpScript function (once again, you can add it directly from the interface, have it set on aliases, macros or triggers).  On a MUD with spacecrafts, for instance, you might want to create a variable `curship` which contains the name of your current ship.  You would set it through an alias (add an alias `curship *` that does `#writevar curship $1`, that is, what's after the space will be set in the `curship` variable).  You can then use it later very simply in all your SharpScript, like `#send {openhatch $curship}`.  If you have to perform a lot of operations on a ship, this could save time.

    You also have access to the `#checkvar` SharpScript function which checks that the variable exists.  If it does not, `#checkvar` can send you a message and will stop the script right there.  This is very useful in some contexts to make sure varibles exist before proceeding.

> Note: these features are used from the SharpScript interface.  They have been tested in different contexts.  Few users have played with Python in SharpScript.  If you are one of them, though, know that additional documentation and better code is currently being written to support more intuitive Python code inside the SharpScript engine.

## Build 50

- Add a feature to prevent some games from disconnecting you based on "idle out".  This simply sends empty commands randomly to the server.  Notice that most game servers forbid this kind of automatic playing.
- Add the `#randplay` function, to randomly play a sound from a list of files.
- CocoMUD now recognizes and act according to the Telnet Go-Ahead.  In non-technical terms, users should see an improvement in CocoMUD's behavior when receiving long blocks of text that used to be cut in the middle.
- Add the first version of delays in CocoMUD, paving the way for timers, speed walking and such.
- The notepad dialog, used to write/read notes in CocoMUD, doesn't hide the client window anymore.  It is possible to have them both open at once.
- CocoMUD now correctly handles the action to repeat the last entered command in the history.  This means you can configure a `!` alias to repeat the last command.
- Fix a bug to use macros using the minus of the numeric keypad.
- Fix a bug preventing importing a world from a file.
- Fix a bug with macros using the combination `ALT + X` or `ALT + Shift + X`.
- Creating a new character is only the default choice if no character exists in this world.
- Fix a bug where CocoMUD crashed on opening the SharpScript console.
- Complete optimization of the output window.  Unfortunately, some users are still complaining about strange sluggishness, but as it is, no better solution has been found, except clearing the output window.
- Add an updater to make sure future releases don't break compatibility with CocoMUD.

## Build 49

- CocoMUD is now available in Spanish!  Many thanks to the contributor who helped in translating CocoMUD in this language and offered additional help during this build.
- CocoMUD now runs on Python 3, instead of Python 2.  Some minor errors with compatibility may still exist, please report if you find any.
- Macros and other scripting configuration shouldn't run in the wrong window, resulting in conflicting game play when running the same world in different tabs.
- CocoMUD now supports playing audio files in .mp3, .wav and .ogg formats.  The old dependency on `Pygame` was replaced with a much lighter and more efficient library.
- The console window is now hidden whenever updating.  This is still a work in progress in designing a better updating system.
- The Python console was removed from the **File** menu.  A new menu named **Tools** was added to support more advanced tools.
- A SharpScript console was added in the **Tools** menu.  If you have been using CocoMUD for a long time, you may remember one could enter SharpScript commands (like `#say`) directly in the client.  This was removed as it created issues.  Now you can enter your custom configuration in this SharpScript console.
- CocoMUD now takes an optional command-line argument to run a different configuration directory.  That is, you can run CocoMUD's version but give it a different directory than the current directory.  This feature is not likely to be used by many but it now exists.  For instance: `cocomud.exe --config-dir=D:\CocoMUD`
- The notification counter used to increase even with messages that were interpreted by mute triggers.  This is now fixed.
- CocoMUD used to crash on opening if no Internet connection was available.  This is now fixed.
- A regression problem was fixed, which prevented to load and run characters.  Also note that your world and character configuration (mainly your `config.set` files for the time being) will be converted to the utf-8 encoding from now on, since this encoding is much more appropriate to the international spreading of CocoMUD.
- Errors in the Python console weren't displayed correctly.  This is now fixed.
- Colors in game weren't always displayed.  This is now fixed.
- Note for developers: CocoMUD now runs and build with `pipenv`, which makes it much easier to develop and support all CocoMUD's dependencies.  Some additional documentation will shortly be posted.

## Build 48

- A new option in the menu bar (**Game** -> **Channels**) allows to edit channels.  You will find the [documentation on channels here](channels.md).
- A new sharp script function `#randplay` has been added, to play a random sound in a list.  This function is usable but not yet present in the graphical user interface.
- Some work has been done on general configuration.  This will be available on the next update.
- One can now clear the output window through the menu **Game** -> * Clear the output window*.
- Several fixes on importing worlds from the website.
- Fixes the error in changing preferences.

## Build 47

- You can now easily export a world in a ZIP archive, choosing what you want to export (**File** -> **Export this world**).  You can share this file and others can import it through **File** -> **Import a world**.
- CocoMUD better handles the clipboard and pasting, particularly under Linux.  It also provides a checkbox to disable auto send when pasting text.
- CocoMUD now supports and displays both **wav** and **OGG** files for playing sounds.
- Rich-text was disabled by default to offer a better user experience with fewer bugs.
- Several bug fixes and improvements under Linux (#105, #106).
- CocoMUD now opens and correctly closes preferences when the user language isn't supported.
- Importing a world from the website doesn't generate encoding errors anymore.
- CocoMUD now displays text using a more appropriate font, thank you again, sighted contributors.
- Note: for compatibility reasons, file encoding was updated.  CocoMUD should support older versions of configuration files and convert them at startup, but there might be issues with some heavily modified configuration with special characters.

## Build 46

- Command stacking is now working again and systematically checked.
- Command stacking now supports special characters.
- CocoMUD better handles variables if their value contains special characters.

## Build 45

- CocoMUD no longer makes the screen reader freeze.
- CocoMUD now supports the SSL protocol, to encrypt the telnet connection.
  SSL is not supported by all games, and is usually set on a different port than the plain telnet protocol.
- Add a new menu item to disable trigger sounds.

## Build 44

- Add a SharpScript action to repeat the last command:
  This action, called `#repeat`, can be used to repeat the last entered command or send a command multiple times.  It can easily be connected to a macro.
- When pressing a shortcut to a macro, go to the end of the window.
- Fix several conflicts when opening the same world in different tabs.

## Build 43

- Add a documentation file to [download and install CocoMUD](download.md).
- Add shortcut keys to add, edit or remove in all dialog boxes.

## Build 42

- Add the triggers with substitution:
  Triggers can now handle substitution, that is replace one or more lines in the client.
- Update proper colors with the rich-text setting.
- Fix a bug with the cursor moving a bit randomly when several tabs were opened.

## Build 41

- Add default characters:
  In the character dialog, one can now specify that a character should be loaded by default.  When selecting a world in the connection list, the default character of this world (if any) is automatically selected.  This saves time if you often login to the same character of a world, and doesn't prevent login on others.
- When creating a new character with special characters (like accents), CocoMUD doesn't crash at startup.
- When CocoMUD loses connection, it will attempt to reconnect and enter the username / password if a character is set:
  This fix is not perfect, it remains difficult to handle connection errors.
- When no update is available, the message is correctly displayed.

## Build 40

- Add a setting to disable rich text control.
  You will find this setting in the menu bar, **File** -> **Preferences**, **Accessibility** tab.  Disabling the rich text control can be useful for accessibility, although it removes colors from the client.
- Creating a new world and closing the dialog does not lead to an error.
- Fix a bug when closing all tabs in the client.

## Build 39

- Add a button to import a world right in the connection window:
  It is now possible to import a world before connecting (which makes more sense in most cases).  Simply click on the **Import**  button in the connection window and select whether you want to import a world online or on disk.
- Display a dialog box to announce the world was correctly installed.
- Installing a world with channels doesn't create "popup" windows.
- Restarting CocoMUD after installing a new world isn't required anymore.

## Build 38

- Add notepads for each world and characters:
  CocoMUD now keeps track of separate files, where you can store any information, like exploring landmarks, quest reminders and so on.  You have a specific notepad for each world, which can be opened through the menu bar -> **Game** -> **Notepad** -> **For this world...** menu.  Simply type in your text, press Escape when you want to close it and save it.  The same system holds true for character-specific notepads, which you can open in the menu bar, **Game** -> **Notepad** -> **For this character...** menu.  This second notepad will not be accessible through other characters of this world.
- Add a documentation for [macros](macros.md).
- Add the mark triggers in the trigger dialog.
- Allow triggers without action (most useful for mark triggers).
- Fix several visual errors in the interface.

## Build 37

- Add the ability to configure characters in worlds:
  This feature allows to create several characters per world.  Characters can contain more specific configuration (like aliases, macros or triggers), but also login information.  A character will store the information in an encrypted file, to login more quickly.
  To create a character, choose a world from the list in the connection area, then press tab and select "any" (the default choice).  Press RETURN or click the **connect** button.  You have opened a random character associated with this world.  To now save it, go to the menu bar, **game** -> **Change this character's setting...**.  In this dialog, enter a name for the newly-created character, a username (or a list of commands to be sent before the password), the password itself and then a list of commands to be sent after the password (if any).  Click **OK** to save in an encrypted file.  The next time you connect, you should see this character in the available list (select the world, then press Tab to find this character).  CocoMUD will enter the commands you have provided, and will do so if you ask to be reconnected as well.
- Fix a bug when trying to create a new world.
- Add the crash report dialog:
  This dialog appears when an error occurs during a given task.  It will provide you with additional information about the bug, and will explain you how to report this bug to the team of developers.

## Build 36

- Add the marked trigger.
  Marked triggers can ask to move the cursor to a specific line.  For instance, if one receives a message, the cursor can be moved right on this message.  This can also help to explore, to move the cursor on the list of exits, for instance.
- Update the client's design and window.
- Add support for handling colors.

## Build 35

- Add the feature to import a world, from a file or online.
  There is now a new menu, "import", in the menu bar -> **file** menu.  In it are two options, one to import a world from a file, the other to import one online.  The second option tries to find the worlds already configured on the project's website.  One can download and install them directly.

## Build 34

- Add the system of channels:
Channels can keep track of a list of events.  They are particularly useful to log communication channels on the MUD.  Through the trigger system, users can feed a channel.  Through a macro or alias, this channel can be displayed in a list, in a separate dialog box.
- In the preferences dialog, **accessibility** tab, users now can set whether the TTS is interrupted or not.
- When changing the TTS options in the preferences, the options are taken into account immediately.
- Fix some bugs in the SharpScript engine.

## Build 33

- Multiline aliases/macros/triggers do not bug anymore.
- One can now enter SharpScript in macros.
- Variables are now described in the [alias](alias.md) documentation.
- The title of the window with several open tabs is now accurately updated.

## Build 32

- Add a syntax to write variables in SharpScript:
  The syntax is `$variable`.  Variables have been added to aliases and triggers.
- Fix a minor bug in command stacking.
- Add mute triggers, which will be useful to support audio prompts.

## Build 31

- Improve the debug logging system.
- Restructure the catalogs for translation.

## Build 30

- Add a logging system to debug events.

## Build 29

- Attempt to fix a bug using the `#play` function while several worlds are opened.

## Build 28

- Add [command stacking](basics.md#command-stacking), to send multiple commands at once, using the semicolon or another character.

## Build 27

- Open multiple worlds in tabs:
  It is now possible to open several worlds in tabs, or even a world several times in tabs.  In the file menu are three new options, to create a new world, open a world in a different tab and close the current tab.  One can navigate between tabs using Ctrl + tab or Ctrl + Shift + tab as usual.
  The feature to change the window's title when unread messages are received now takes into account the selected tab only.
- New menus to disconnect and reconnect from a world:
  A new menu item in the menu bar, named connection, has been added.  In it are options to disconnect from the current world, and reconnect to it.
- The client doesn't lag if connection to a distant server takes some time.

## Build 26

- When outside of the window, if messages are received, the window title changes to let the user know notifications are waiting on the client.

## Build 25

- Add the command history
  The command history remembers all commands you have entered.  You can use it by pressing CTRL + up or down to go up or down into your list of commands.  Alternatively, you can use command history in lock mode, by pressing Escape, then navigating in the history using the arrow keys.  You can leave lock mode by pressing Escape again.
- One can now paste several lines to send multiple commands.

## Build 24

- Update the documentation of the basic features.
- Remove the obsolete settings based on an input and output field.
- When tabbing to tab-complete, the TTS speaks (and displays) the found result.

## Build 23

- Add the tab-completion:
  When the client receives messages from the server, it stores all words by frequency.  When you begin typing a letter or more and then press tab, the client will try to finish the word you were typing.  If you're not satisfied with this choice, you can press tab again and the client will display another result.
