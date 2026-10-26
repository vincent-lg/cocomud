---
title: "Les alias dans CocoMUD"
---

# Les alias dans CocoMUD

Les alias sont une fonctionnalité des clients MUD afin d'abréger une ou plusieurs commandes. Un alias est en vérité une commande, mais au lieu d'être envoyée au serveur, elle est d'abord analysée par le client, qui peut la modifier et la transmettre au serveur si besoin. Il est même possible de créer des alias qui n'ont de sens que pour le client et ne sont pas envoyés au serveur du tout.

Ce document décrit le concept d'alias et explique la façon de les créer et les gérer dans CocoMUD.

* Table of contents
{:toc}

## Ajouter un alias

Vous pouvez créer un alias via l'interface ou en utilisant la [syntaxe du SharpScript](#syntaxe-du-sharpscript).  L'interface étant plus intuitive, elle sera décrite en premier.

### Création grâce à l'interface

Dans la barre de menu, sélectionnez Jeu -> Alias.  Vous vous trouverez dans une boîte de dialogue listant les alias existants pour cet univers. Notez que les alias sont généralement propres à un univers et partagés par les personnages de cet univers, ce qui changera dans les prochaines versions.

Dans cette boîte de dialogue, vous pouvez ajouter, éditer et supprimer des alias. Par défaut, la liste des alias de cet univers sera probablement vide, vous pouvez cliquer sur **Ajouter** pour en ajouter un.

Vous devrez ensuite choisir le nom de l'alias que vous voulez créer. C'est le nom de la commande que vous devrez entrer pour exécuter l'alias. Dans cet exemple, nous allons créer un alias "tts" qui permet d'activer ou de désactiver le TTS (text-to-speech).

Entrez donc "tts" dans ce champ de texte, puis appuyez sur la tabulation. Vous vous trouvez ensuite dans une liste d'actions possibles à lier à cet alias. Par exemple, vous pourriez vouloir créer un alias "rs" qui envoie deux commandes au serveur quand exécuté : "reload" et "shoot". Dans ce cas, vous devrez sélectionner l'action "Envoie une ou plusieurs commandes au serveur".

Poursuivant notre exemple, nous devrons choisir "Active/Désactive le TTS", puisque c'est ce que devrait faire notre alias "tts" quand exécuté. Sélectionnez donc ce choix et faites tabulation pour cliquer sur le bouton **Ajouter l'action**.

Vous vous trouverez dans une nouvelle boîte de dialogue vous demandant des informations supplémentaires. Dans le cas de cette action, il n'y en a aucune, appuyez donc sur "OK" pour ajouter l'action.

La nouvelle action a bien été ajoutée. Le curseur se trouvera sur la liste des actions actuellement liées à cet alias. Vous pouvez lier un alias à plusieurs actions, si besoin lier un alias à la même action plusieurs fois (pour par exemple jouer différents sons en même temps, même si cela n'est peut-être pas bien utile).

La liste des actions liées à cet alias fait un peu peur. Elle ne contient que les informations en résumé. Si vous avez choisi "Active/Désactive le TTS", la ligne d'action `#tts` sera créée. C'est un raccourci, une ligne d'action décrite en utilisant la syntaxe du SharpScript. Vous n'avez pas vraiment besoin de vous en inquiéter, à moins de vouloir toucher au scripting dans CocoMUD.

Pour résumer le contenu de cette boîte de dialogue quand vous ajoutez ou éditez un alias, vous avez:

- Le nom de l'alias (un champ de texte).
- La liste des actions liées à cet alias. Si l'alias n'est lié à aucune action, cette liste n'apparaîtra pas.
- Un bouton pour éditer la ligne d'action sélectionnée. Si l'alias n'est lié à aucune action, ce bouton n'apparaîtra pas.
- Un bouton pour supprimer la liste d'action sélectionnée. Si l'alias n'est lié à aucune action, ce bouton n'apparaîtra pas.
- Une liste d'actions que vous pouvez relier à cet alias.
- Le bouton pour ajouter une de ces actions.

Vous devriez vous habituer autant que possible à cette boîte de dialogue, car elle sera présente pour la plupart des fonctionnalités incluant du SharpScript dans CocoMUD. Il s'agit en fait de l'éditeur de SharpScript, qui vous permet d'éditer la configuration avancée du client sans ouvrir le fichier de configuration. Vous verrez bien d'autres exemples dans le reste de la documentation.

Pour enregistrer cet alias, n'oubliez pas de sélectionner "OK" plusieurs fois pour bien refermer toutes les boîtes de dialogues ouvertes.

Si dans le client, vous entrez "tts", vous devriez voir :

```
TTS off.
```

Entrez cette commande de nouveau pour l'activer. Le TTS (text-to-speech) sera donc activé ou désactivé en entrant cet alias.

### Syntaxe du SharpScript

Vous pouvez aussi ajouter un alias en éditant un fichier de configuration. Cette solution sera peut-être préférée par certains.

Le fichier de configuration lié à cet univers se trouve dans le dossier "worlds", sous-dossier portant le nom de votre univers, fichier "config.set". Vous pouvez ouvrir ce fichier avec un éditeur simple, comme bloc-notes.

Pour ajouter un alias, utilisez l'action `#alias` avec deux paramètres :

- Le nom de l'alias.
- Les actions liées à cet alias.

Si vous voulez créer un alias "tts" qui active ou désactive le TTS (text-to-speech), écrivez dans votre fichier de configuration :

```
#alias tts #tts
```

Si vous voulez lier votre alias à plusieurs actions, n'hésitez pas à l'écrire sur plusieurs lignes :

```
#alias go {
    #play sounds/go.wav
    #say {C'est parti !}
}
```

Pour une explication plus détaillée de la syntaxe du SharpScript, référez-vous à [la section consacrée au SharpScript](../sharpscript.md).

## Editer un alias

A tout moment, que vous ayez créé l'alias depuis l'interface ou depuis le fichier de configuration, vous pouvez l'éditer. Si vous l'avez créé via le fichier de configuration, vous pouvez l'éditer via l'interface, et réciproquement.

Souvenez-vous : la configuration est chargée quand l'univers est sélectionnée, vraisemblablement à l'ouverture du programme. Si vous modifiez le fichier de configuration, redémarrez le programme pour voir ces modifications.

## Supprimer un alias

Vous pouvez retirer un alias depuis l'interface ou le fichier de configuration. Souvenez-vous de bien quitter l'interface en cliquant sur "OK" même après avoir supprimé un alias, sans quoi la modification ne sera pas sauvegardée.

## Les alias avec variables

CocoMUD offre une gestion des variables. On peut les utiliser n'importe où dans les scripts du client, incluant dans toutes les fonctionnalités qui utilisent le moteur du SharpScript (comme les alias, macros ou triggers).

Les variables peuvent être très utiles pour les alias, pour créer des raccourcis de commande avec des paramètres inconnus. Par exemple :

> Je voudrais créer un alias qui commence par `=`. Ce qui vient après le signe égal doit être envoyé au serveur comme une commande `say`. Si j'entre "=coucou !", la commande "say coucou !" devrait être envoyée au serveur.

Dans ce cas, on devra utiliser des variables. L'alias doit commencer par un signe égal (`=`), mais on ne sait pas ce qui vient après. Comment l'indiquer au client ? On va utiliser le signe `*` dans notre alias qui veut dire "n'importe quoi, de n'importe quelle longueur".

Si on entre `=*` comme alias, CocoMUD l'interprétera comme "n'importe quelle commande commençant par un signe égal".

Cependant, on n'a pas seulement besoin de déclencher cet alias. On doit récupérer ce que l'utilisateur a entré après le signe égal. Voici le détail de la création de cet alias, pas à pas, en utilisant l'interface :

- Dans la barre de menu, sélectionnez **Jeu** puis **Alias**.
- Cliquez sur le bouton **Ajouter** pour ajouter un nouvel alias.
- Dans le champ de texte contenant l'alias, entrez `=*` (le signe égal et un signe astérisque).
- Appuyez sur tab pour vous déplacer sur la liste d'actions pouvant être liées à cet alias.
- Sélectionnez "envoie une ou plusieurs commandes au serveur", appuyez sur tab et cliquez sur **Ajouter l'action**.
- Le client vous demande de configurer cette action. Appuyez sur tab jusqu'à entendre "Commandes à envoyer au serveur". Dans ce champ de texte, entrez `say $1` (le `$1` est expliqué plus bas).
- Appuyez sur **OK**. L'action devrait être ajoutée, et vous devriez la voir dans la liste :
```
#send {say $1}
```
La syntaxe est expliquée plus bas.
- Appuyez sur tab jusqu'à trouver le bouton **OK** et cliquez dessus. Vous vous retrouvez dans la liste d'alias, appuyez sur "OK" une nouvelle fois pour fermer cette boîte de dialogue en sauvegardant les modifications.

Si vous écrivez dans le client :

```
=Coucou !
```

L'alias enverra "say Coucou !" au serveur.

Ce qui se passe est assez simple :

- Vous entrez "=quelque chose".
- CocoMUD trouve un alias correspondant à cette commande.
- Ce que vous avez entré après le signe égal ("quelque chose", dans notre exemple) est capturé dans la variable `$1`.
- Quand vous envoyez `$1` au serveur, le `$1` sera remplacé par "quelque chose".

La variable s'appelle `$1` car vous pouvez créer de nombreuses variables. Si vous entrez l'alias :

```
-*+*
```

Vous pourrez entrer comme actions liés à cet alias :

```
remove $1
wear $2
```

Et utiliser cet alias ainsi :

```
-cape+armure
```

Les variables en SharpScript sont davantage expliquées dans [la documentation consacrée au SharpScript](../sharpscript.md).
