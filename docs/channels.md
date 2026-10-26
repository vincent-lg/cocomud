---
title: "Channels in CocoMUD"
---

# Channels in CocoMUD

CocoMUD offers an interesting feature of channels.  Channels are basically lists of messages and you can put whatever you want in them.  We often use CocoMUD channels to track game channels: when we receive a message on one of these channels (lie "public" or "ooc"), we can automatically capture this message and put it in a CocoMUD channel.  A simple key press could allow to display this channel and read all the messages in it.  This is pretty useful when you're exploring or figthing on the game, and don't have time to read all messages spoken by others, but you want to read them afterward.

We'll take this example for the rest of the documentation: an attempt to capture the context of a public channel.  This example also relates to [triggers](triggers.md), which is barely a coincidence.

* Table of contents
{:toc}

## Creating a new channel

The first step is to create a channel, an empty list that will contain the messages we want to put in it.  Here, we'll create a channel named "public", for that's quite explicit.  Remember that channels can be used to capture any information, however.

In the CocoMUD menu bar, open **game** -> **channels**.  You find yourself in a dialog box showing current channels.  It's probable you don't have any at that point.  Go to the **add** button and click on it.  You will be asked the name of the channel.  Keep it short and explicit: here, we'll create a channel named `public` .

We can now send information to this channel using [triggers](triggers.md).  If you're not familiar with this feature, you might want to read the [documentation about triggers](triggers.md) first.

## Feeding a channel with triggers

Okay, let's look at the two lines we may receive from the server.  If we send a message on the public channel, it would be displayed like that:

```
[public] You say: my message to all
```

If it's someone else who sends to this channel, we would have:

```
[public] Somebody says: my message to all
```

What's common and different in our two lines?

- Well, both begin with "public" between brackets, followed by a space.
- Then there's the author.  "you" or "somebody".  So we don't know what it will be, we could use an asterisk.
- Then is the word "say" after another space.  Wait!  When it's me, it display "you say", when it's somebody, it displays "somebody says".  What to do?
- After a colon and another space is our message.

To solve our issue between say/says, we have two options:

- Either we group both cases, writing "say*" (meaning say followed by nothing or anything).
- Or we could write two triggers.

Personally I would advise the latter, but I know some of you would prefer the former.  So let's work with both.

### One single trigger

What would our trigger look like in the end?  Ready?

```
[public] * say*: *
```

Three asterisks!  The first will contain the name of the one speaking.  Either "You" or the name of the player speaking on this channel.  The second variable will contain either "s" or nothing.  We shouldn't need it.  The third variable contains the message itself.

So to create this trigger through the interface:

- Open the menu bar, **Game** -> **Triggers**.
- Click on **Add** to create a new trigger.
- Enter `[public] * say*: *` before pressing Tab.
- Select "Feed a channel with a message".
- Click on the **Add action** button.
- In the name of the channel to be fed, enter `public` (this is assuming the channel exists in CocoMUD).
- In the message to feed to the channel, enter:
```
$1: $3
```
- Click on **OK** several times to close the dialog and save the trigger.

> What was that `$1 $3`?

`$1` contains the name of the one speaking.  `$3` contains the message.  So when we receive the line:

```
[public] Jamie says: well done!
```

Our channel will be fed with the following line:

```
Jamie: well done!
```

You could have done the same thing with a single line of SharpScript:

```
#trigger {[public] * say*: *} {#feed public {$1: $3}}
```

That's a bit harder to understand, but if you're familiar with SharpScript, that's definitely quicker.

A last word regarding this trigger: you may have noticed that we don't play a sound when receiving this trigger.  Nothing prevents you from adding another action to the trigger though.  Similarly, to do it with SharpScript, you would enter:

```
#trigger {[public] * say*: *} {
    #feed public {$1: $3}
    #play sounds/public.wav
}
```

### Two different triggers

As I have explained, to solve the problem of say/says, we could have created two different triggers.  That makes for a longer configuration, a little bit, but that's easier to read, in my opinion.  Sometimes it will not be possible to do otherwise, depending on the language the MUD is in.

Our two triggers would be:

```
[public] You say: *
[public] * says: *
```

I don't know about you, but I find it much easier to read.  Our first trigger only fires when we send a message on this channel (perhaps we could say that we won't play a sound in this case) and the second one will fire when it's somebody else who's speaking.  I'll give you the SharpScript instructions to create these triggers, but as usual, you could do the same through the interface:

```
#trigger {[public] You say: *} {#feed public {You: $1}}
#trigger {[public] * says: *} {
    #feed public {$1: $2}
    #play sounds/public.wav
}
```

What you'll choose is entirely up to you and the context, pick whatever feels more comfortable.

## Bind a channel to a macro

Feeding a channel is certainly useful, but displaying it is even better.  Most often, you will bind a macro to open a specific channel.  It's pretty easy to do.

Start by creating a macro as usual.  In the interface:

- Open the menu bar **Game** -> **Macro**.
- Click on **Add** to add a new macro.
- Press the key combination you want to associate with this macro.  For instance, **CTRL + P**.
- Tab twice to find the list of possible actions.  You should find in the list the "create or display a channel" function.  Select it.
- Tab once to add the action.  You will be asked the channel name.  You will enter `public` here, in this case.
- Leave the dialogs by pressing **OK** multiple times to quit and save.  Then you can press CTRL + P: the public channel should open.  Magic!

## Remove a channel

Removing a channel is done through the same interface:

- In the menu bar, select **Game** -> **Channels**.
- Tab until you find the **Remove** button.  You will then be presented with a list of existing channels.  Select one and tab again to remove it.  If you press **OK**, the channel will be entirely removed and will not appear in your channels the next time you connect to this world.

Keep in mind, however, that triggers can still try to feed this channel.  This will fail, since the channel doesn't exist, but you will have to remove the trigger manually, as it could do other things as well.
