---
title: "CocoMUD basics"
---

# CocoMUD basics

CocoMUD is a [MUD client](https://en.wikipedia.org/wiki/MUD_client) specifically designed to enhance accessibility with screen readers.  It supports a native TTS (Text-to-Speech) for most common screen readers on Windows, as well as Braille.

This document aims at explaining the basic features of CocoMUD client in a practical way, to tell you what you can do with it and how to do it.  More complex features will have a document of their own.

* Table of contents
{:toc}

## When opening CocoMUD

When opening CocoMUD, it should display a list of configured servers (or worlds, in MUD client terminology).  It's a list, you can select another world by pressing the arrow keys or move more quickly by typing the first letters of a server.  It's possible that the server you would like to connect to doesn't appear in the list: you may need to [add it before going on](#adding-a-world).

When you have selected the world to which to connect, press RETURN (or click on the **connect** button).

## The client's main window

CocoMUD client's main window is as simple as it can be.  There's only one text field, through which you can navigate using the arrow keys, select and copy text, move at the beginning of the end of the window, and so on.

If you start typing in this text field, the cursor is moved to the last line.  Consider this text field like a read-only area, except for the last line.  You can type your command as usual and press RETURN to send it.  You can then arrow up to see the result of your command (and up again to see previous messages).  This should be quite straightforward after just a minute or so.

When you press RETURN on a world, CocoMUD tries to connect to the server.  If everything goes well, the client connects and the welcome message of the server is displayed (you can read it with the arrow keys).  The welcome message should also be sent to the screen reader (and, if you have a Braille display, you should see it there as well).  Most MUD servers will ask for your username and password.

## The command history

Whenever you press RETURN to send a command, it is added into the command history.  You can browse through the command history to see what has been send, send a command again or even modify a command you have entered.  There are two ways to use the command history:

- Using the CTRL + Up and Down arrow keys, you can browse through the command history.  If you press CTRL + up arrow key, you will be prompted with the command you entered previously.  You can press RETURN or modify this command at will.  Press CTRL + down arrow key to go down into your command history.
- Using the lock mode.  To enter into lock mode, press Escape.  You can now navigate through the history using the arrow keys.  You have to leave the lock mode to see the result of your commands, by pressing Escape again.

## Tab-completion

CocoMUD client supports tab-completion.  If you start typing a word, you can press tab and the client will try to finish it, based on what you have received during this session.  For instance, if you type "st" in the client, then press tab, the client will try to complete the word with what you have received.  Perhaps it will suggest "street" or "status".  Words that are more frequent will be suggested first.

When you press tab, the word will be written under the cursor.  You can continue typing or press RETURN to send the full command.  If you press tab again, the client will look for another possibility beginning with the same letters you had initially entered.  You can press tab as many times as you want, the client will write suggestions from most frequent to less frequent.  If the client can't find anything, it will just enter your initial letters and you'll have to type the rest of the word.

## Command stacking

Command stacking is a feature that allows users to send multiple commands at once.  For instance:

```
say sounds;say good
```

This syntax is equivalent to writing:

```
say sounds
say good
```

Sending multiple commands at once can be useful in some situations.  By default, the character for command stacking is the semicolon (;), but it can be changed in the preferences, input tab.  If you wish to remove command stacking, simply remove the character in the setting.

You can double the command stacking character to actually send one.  If you have set the semicolon (;) as a delimiter for command stacking (the default), you can type:

```
say one command;say another command with a wink emoticon ;;)
```

This command is equivalent to writing:

```
say one command
say another command with a wink emoticon ;)
```

Once the delimiter is present more than one time, it is not used as delimiter in the command stacking.  Therefore:

| Command | Equivalent |
|---|---|
| `say ;;)` | `say ;)` |
| `say ;;;)` | `say ;;)` |
| `say ;;;;)` | `say ;;;)` |

## The menu bar

Some options are accessible through the menu bar.  In File -> Preferences, you will see some settings that you can modify to have your experience with CocoMUD more comfortable.

## The preferences

When you select File -> Preferences in the menu bar, or press *Alt + Enter*, you should see a dialog with several tabs.  The first tab (selected by default) is **general**.  It only contains the language selection for the time being.  CocoMUD should be in the language of your system, if it is translated in this language.  Otherwise, English should be selected.

In the **display** tab, you can select a different encoding.  By default, CocoMUD is set to use a Latin encoding, but you can change it.  If you connect to only-English MUDs, you may not need this setting.

In the **input**  tab, you can change the delimiter for [command stacking](#command-stacking).

In the **accessibility** tab are several options that affect accessibility.  Here they are, in more details:

- Enable TTS (Text-to-Speech): you can here disable the TTS (Text-to-Speech).  The TTS is what sends the content of the output field to your screen reader.  Sometimes, it's really not necessary, and you can turn it off.
- Enable TTS on a different window: by default, CocoMUD client enables its TTS even if you're not currently in the CocoMUD application.  It means that, you can be reading a web page, or a book, or sending an email, and suddenly your screen reader starts on the messages you have received on the MUD.  As this can be useful, this can sometimes be annoying, so you can turn this option off to let TTS only speak when you are in the CocoMUD client.

## Adding a world

If you want to add a new world, in the world selection (when the client opens), select the **add** button.  You will be asked three information:

- The world's name: what name should the world be given?  Most likely, you will use the MUD's name, like Alter Aeon or T2T.
- The server's hostname.
- The server's port number.

The name, hostname and port number can be changed if needed.  Notice, however, that the name is used to determine the location.  This will be a directory created for the world in which settings are stored.  If you change the name, the location won't be changed.

Once you have created a new world, it will appear in the world list and you will be able to connect to it.
