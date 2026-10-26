---
title: "Fonctionnalités basiques de CocoMUD"
---

# Fonctionnalités basiques de CocoMUD

CocoMUD est un [client MUD](https://en.wikipedia.org/wiki/MUD_client) conçu pour être accessible et agréable avec un lecteur d'écran.  Il supporte nativement un système de TTS (Text-to-Speech) pour la plupart des lecteurs d'écran sous Windows, ainsi que la gestion de plages tactiles.

Ce document décrit les fonctionnalités basiques de CocoMUD, savoir ce qu'il permet et comment l'utiliser, avec des exemples. Certaines fonctionnalités plus complexes sont décrites dans des documents à part.

* Table of contents
{:toc}

## À l'ouverture de CocoMUD

Quand vous ouvrez CocoMUD, vous devriez voir une liste de serveurs configurés (ou d'univers, dans le vocabulaire du client).  C'est une liste, vous pouvez sélectionner un autre univers avec les flèches ou vous déplacer plus rapidement en entrant les premières lettres de l'univers en question.  Il est possible que le serveur de jeu auquel vous souhaitez vous connecter ne soit pas présent dans la configuration par défaut : pour cela, il vous faut [l'ajouter avant de continuer](#ajouter-un-univers).

Quand vous avez sélectionné l'univers auquel vous souhaitez vous connecter, appuyez sur Entrée (ou cliquez sur le bouton **se connecter**).

## La fenêtre principale du client

La fenêtre principale de CocoMUD est aussi simple que possible. Elle ne contient qu'une seule zone de texte, dans laquelle vous pouvez vous déplacer en utilisant les flèches, sélectionner et copier du texte, vous déplacer au début ou à la fin de la fenêtre, etc.

Quand vous écrivez dans ce champ de texte, le curseur est automatiquement déplacé en bas de la fenêtre. Vous pouvez considérer cette zone de texte comme une zone en lecture seule, à l'exception de la dernière ligne. Vous pouvez envoyer votre commande en appuyant sur Entrée comme d'habitude. Vous pourrez ensuite remonter avec les flèches pour voir la réponse du serveur. Cette navigation peut sembler assez étrange de prime abord, mais elle devient très intuitive après quelques essais seulement.

Quand vous appuyez sur Entrée après avoir sélectionné un univers, CocoMUD essaye de se connecter au serveur. Si tout se passe bien, le client se connecte et le message d'accueil du jeu s'affiche dans la zone de texte (vous pouvez le lire en utilisant les flèches). Le message d'accueil devrait également être envoyé au lecteur d'écran (et, si vous avez une plage tactile, le message devrait apparaître dessus également). La plupart des MUD vous demanderont un nom d'utilisateur et un mot de passe.

## Historique des commandes

Quand vous appuyez sur Entrée pour envoyer une commande, elle est ajoutée à votre historique de commandes. Vous pouvez naviguer dans cette historique de commande pour envoyer de nouveau une commande ou bien la modifier si nécessaire. Il existe deux façons d'utiliser l'historique des commandes :

- En utilisant CTRL + les flèches haut ou bas, vous pouvez naviguer dans l'historique des commandes. Si vous appuyez sur CTRL + flèche haut, le client affichera la commande que vous venez d'entrer. Vous pouvez l'envoyer de nouveau en appuyant sur Entrée, ou bien la modifier avant envoi si nécessaire. Appuyez sur CTRL + flèche bas pour descendre dans votre historique de commandes.
- En utilisant le mode verrouillé. Pour entrer dans ce mode, appuyez sur échappe. Vous pourrez maintenant naviguer avec les flèches haut et bas pour parcourir l'historique des commandes. Pour repasser en mode non-verrouillé et lire le résultats de vos commandes, appuyez sur échappe de nouveau.

## Auto-complétion

CocoMUD propose une fonctionnalité d'auto-complétion. Quand vous commencez à écrire un mot, vous pouvez appuyer sur la touche de tabulation, le client essayera de trouver la fin du mot que vous étiez en train de taper, en se basant sur le texte que vous avez reçu du serveur. Par exemple, si vous écrivez "po" dans le client, puis appuyez sur la touche de tabulation, le client écrira "porte", "portail" ou "potion" ou autre, en fonction des mots les plus fréquents qu'il a reçu. Les mots apparaissant le plus souvent sont proposés en premier.

Quand vous appuyez sur la touche de tabulation, le mot est écrit juste avant le curseur. Vous pouvez continuer à écrire votre commande ou l'envoyer telle qu'elle. Si le mot trouvé par l'auto-complétion n'est pas le bon, vous pouvez de nouveau appuyer sur la touche de tabulation : le client cherchera un autre mot en se basant sur les premières lettres que vous aviez écrites. Vous pouvez appuyer sur la touche de tabulation autant de fois que nécessaire pour trouver votre mot : la sélection se base sur la fréquence (le plus souvent un mot apparaît, les meilleures chances il a d'être choisi pour l'auto-complétion). Si le client ne trouve plus de résultat, il vous remettra les lettres initialement écrites et vous devrez finir le mot vous-même.

## Commandes multiples

L'envoi de commandes multiples (command stacking en anglais) est une fonctionnalité permettant d'envoyer plusieurs commandes à la fois. Par exemple :

```
say sounds;say good
```

Cette syntaxe est identique à :

```
say sounds
say good
```

Envoyer plusieurs commandes à la fois peut être utile dans certains cas. Par défaut, le délimiteur pour les commandes multiples est le point virgule (;), mais vous pouvez le modifier dans les options, onglet commandes. Si vous voulez retirer la fonctionnalité des commandes multiples, supprimez simplement le délimiteur dans les options.

Vous pouvez entrer le délimiteur plusieurs fois pour l'envoyer dans vos commandes. Si vous avez laissé le délimiteur par défaut (;) par exemple :

```
say une commande;say une autre commande avec un clin d'oeil ;;)
```

Cette commande enverra :

```
say une commande
say une autre commande avec un clin d'oeil ;)
```

Quand le délimiteur est présent plus d'une fois, il est ignoré par le système des commandes multiples. Ainsi :

| Commande | Équivalent |
|---|---|
| `say ;;)` | `say ;)` |
| `say ;;;)` | `say ;;)` |
| `say ;;;;)` | `say ;;;)` |

## La barre de menu

Certaines options sont accessibles dans la barre de menu. Dans Fichier -> Options, vous verrez plusieurs options que vous pouvez modifier pour rendre votre expérience avec CocoMUD plus agréable.

## Les options

Quand vous sélectionnez Fichier -> Options dans la barre de menu, ou entrez *Alt + Entrée*, vous devriez voir une boîte de dialogue avec plusieurs onglets.  L'onglet sélectionné par défaut est **général**. Pour l'heure, il ne contient que le réglage de la langue de CocoMUD. Le client devrait être dans la langue de votre système, si une traduction existe dans le logiciel, ou bien anglais si ce n'est pas le cas.

Dans l'onglet **affichage**, vous pouvez sélectionner un encodage différent. Par défaut, CocoMUD utilise un encodage Latin, mais vous pouvez le changer si besoin est.

Dans l'onglet **commandes**, vous pouvez modifier le caractère utilisé pour l'envoi de commandes multiples (command stacking en anglais).

Dans l'onglet **accessibilité** se trouvent plusieurs options qui modifient le comportement d'accessibilité du client. Les voici plus en détail :

- Activer le TTS (Text-to-Speech): vous pouvez ici désactiver le TTS (Text-to-Speech). Le TTS permet d'envoyer au lecteur d'écran les messages reçus par le serveur. Parfois, avoir le TTS actif n'est pas utile, et vous pouvez le désactiver ici.
- Activer le TTS hors de la fenêtre: par défaut, CocoMUD active le TTS même si vous vous trouvez dans une autre fenêtre. Ainsi, vous pourriez être sur le web, ou un livre, ou envoyer un e-mail, quand le lecteur d'écran se met à parler pour vous avertir de messages reçus sur le MUD auquel vous êtes connectés. Cela peut être utile, mais cela peut aussi être problématique, et vous pouvez le désactiver ici.

## Ajouter un univers

Si vous voulez ajouter un univers (un serveur de jeu), dans la sélection des univers (à l'ouverture du client), cliquez sur le bouton **Ajouter**. Une boîte de dialogue s'ouvrira, vous demandant trois informations :

- Le nom de l'univers : quel nom donner à ce serveur ? En général, ce sera le nom du MUD, comme VanciaMUD ou MultiMUD.
- Le nom d'hôte du serveur.
- Le numéro de port du serveur.

Le nom de l'univers, nom d'hôte du serveur et numéro de port peuvent être modifiés après coup. Cependant, le nom du serveur est celui donné à son dossier, où les options de connexion et autres informations seront conservées. Changer le nom ne changera pas le nom du dossier.

Une fois créé, vous verrez l'univers dans la liste et pourrez vous y connecter.
