---
title: "Characters in CocoMUD"
---

# Characters in CocoMUD

CocoMUD offers to have several characters set on a world.  Having a configured character has several advantages:

- Connecting to a character will enter your username and password automatically, and other commands if needed.
- Your username and password will be stored and encrypted, they will not appear in clear either in your command history or in one of CocoMUD's files.
- If you use a secure connection (like SSL or SSH), your password will be protected, from your computer to the MUD server itself.
- You can have separate notepads for different characters.

In short, when you select a world to connect to, you can choose to specifically connect to one of your configured characters.  You can still, however, ask CocoMUD to connect to the world without any specific character.

## Add a character to a world

By default you have no configured character in any of your world.  To add a character, you should connect to a world.  When you open CocoMUD and you find yourself in the list of configured worlds, select one and press RETURN.

CocoMUD will attempt to connect to the world you have selected.  But it will not enter any information on login.  To create a character, go to the menu bar, select **game** -> **Change this character's setting...**.

A dialog box will open, prompting you for several information:

- **Name**: the character's name.  This is just for CocoMUD.  The name that you enter will be shown on the connection screen (see below).
- **Username or other commands to send before the password**: this is the first command, or commands, that CocoMUD has to send when the connection is established to the game.  Usually, this is a username.  On some games, you might have other commands to enter.  Don't enter the password here, just the commands to send before the password.  If you have several commands to enter, put them on separate lines.
- **Password if any**: it's now time to enter the character's password.  Not only is this a password field (into where you will see only asterisks), the information will be encrypted by CocoMUD and will not appear in clear in CocoMUD's configuration.
- **Commands, if any, to send after the password**: on most games, you'll have to just enter your username and password to connect.  Other games will require additional commands however.  You can enter them here.  Like the commands to send before the password, you can separate them with a new line.
- **Set this character as the default choice**: if this box is checked, when you select the world on the connection screen, this character will be selected automatically.  You can only have one default character per world.

Press **OK** to confirm the options.  Then, you can close the tab and re-open it: in the connection screen, select the world.  Then press the tab key: you should find yourself on another list, which is the list of characters associated with this world.  The first item at the top of the list is "any character", which will connect you to the world but will not enter any command.  If you have set a default character, however, the cursor will select this character, somewhere down the list.  You can use the up and down arrow keys to choose another character and press RETURN to connect to it.

By default, when you move in the list of worlds (the list on which you are when CocoMUD opens), if you select a world, its default character is selected.  You can press RETURN without pressing tab to select the character.

## Editing the character's configuration

If you have changed the password to connect to the game, or any other information, you can just connect to the character, and then go back to **Game** -> **Change this character's setting**. The dialog box will open again, with the values you have set earlier.  You can change them and press **OK**.

## Adding several characters to a world

Adding several characters is quite similar to adding one: the only trick here is when connecting to the world.  You have to select the world and tab to select "any character" (which means no character will be chosen).  Then, you can go to **Game** -> **Change this character's setting** and just add the new character.  When next time you open the connection screen, if you press tab on this world, you will find the new character in your list.  Remember, you can only have one default character.  Characters are stored in alphabetical order, so you can easily navigate between the default character and alternatives.  You can have as many characters per world as you like.

## A word on configuration

For the time being, all configuration is set in a world.  It means that all characters created on a world will share the same [aliases](alias.md), [triggers](triggers.md), or channels.
