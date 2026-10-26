---
title: "Macros"
---

# Macros

CocoMUD propose un système de macros comme la plupart des autres clients MUD, qui permet de relier une touche de raccourci avec une action (comme une commande à envoyer au serveur. Ce document explique la création de macros simples et plus complexes.

* Table of contents
{:toc}

## Fonctionnalité basique

Dans sa version la plus simple, un macro fait le lien entre une touche de raccourci et une commande : par exemple, si vous appuyez sur `Ctrl + F1`, CocoMUD pourrait envoyer la commande "regarder" au serveur de jeu. Dans cette documentation, nous verrons comment créer un macro reliant la touche `F1` avec la commande "nord".

## Ajouter un macro

Il existe deux moyens d'ajouter un macro. L'interface étant l'alternative la plus simple, ce moyen sera décrit en premier.

### Via l'interface

Dans la barre de menu, cliquez sur **Jeu** -> **Macro**. Une boîte de dialogue devrait s'ouvrir, contenant la liste des macros actuellement configurés. Cette liste sera probablement vide la première fois que vous ouvrirez cette interface. Cliquez sur le bouton **Ajouter**.

Une autre boîte de dialogue devrait s'ouvrir pour ajouter un nouveau macro. Le curseur devrait se trouver sur une zone de texte, mais il ne vous est pas demandé d'entrer du texte ici : à la place, appuyez sur la combinaison de touches que vous souhaitez associer à ce macro. Par exemple, appuyez sur la touche `F1`.

Dans la zone de texte devrait apparaître le nom du raccourci, "F1" dans notre cas. Vous pouvez utiliser de nombreuses touches de raccourci pour vos macros. Par exemple, appuyez sur la touche `Ctrl`, maintenez-la enfoncée, appuyez sur la touche `I` et relâchez les deux touches. Dans la zone de texte devrait apparaître :

```
Ctrl + I
```

Vous pouvez utiliser Shift, Ctrl ou Alt dans vos macros.  En pratique, ce n'est pas conseillé d'utiliser Alt, qui est une touche réservée pour les menus (`Alt + F` ouvre le menu **fichier**, par exemple). Il y a malgré tout un grand nombre de raccourcis possibles, par exemple :

```
Shift + Backspace
Ctrl + F12
Ctrl + Shift + O
Ctrl + PavNum8
```

Si vous voulez connecter un macro à une touche du pavé numérique, vous devez activer ce dernier avant de cliquer sur le bouton **Ajouter**, ou bien naviguer dans une autre partie de la fenêtre pour ce faire. Sinon, CocoMUD va associer la touche du verrouillage de pavé numérique avec le macro, ce qui n'est pas souvent souhaitable.

Après avoir entré le raccourci voulu, appuyez sur la touche de tabulation. Le second champ de cette boîte de dialogue est également un champ de texte, celui-ci devant contenir la ou les commandes à envoyer au serveur de jeu quand on presse le raccourci renseigné précédemment. En poursuivant notre exemple, après avoir sélectionné **Ajouter**, appuyé sur la touche `F1`, puis sur la touche de tabulation, vous pouvez maintenant écrire "nord".

La zone suivante est une liste d'actions à associer à ce macro. Cette fonctionnalité sera détaillée plus bas, elle n'est pas nécessaire pour les macros simples. Tabulez jusqu'à trouver le bouton **OK** et validez. Vous devriez voir le macro que vous avez ajouté dans la liste.

Si vous voulez changer la ou les commandes à envoyer au serveur quand le macro est activé, vous devez l'éditer (en le sélectionnant dans la liste, et tabuler jusqu'à trouver le bouton **Editer**). Cependant, si vous souhaitez changer le raccourci associé à un macro, il vous suffit de le sélectionner et de tabuler une fois. Vous devriez voir une zone de texte (ou plutôt, une zone d'édition du raccourci). Appuyez sur la nouvelle combinaison de touches que vous souhaitez associer à ce macro, puis tabulez jusqu'à trouver le bouton **OK**. Si vous quittez cette boîte de dialogue sans cliquer sur **OK**, vos modifications seront perdues (cela inclut le macro que vous avez ajouté).

De retour dans la fenêtre principale de CocoMUD, appuyez sur `F1`. La commande "nord" est envoyée (silencieusement) au serveur de jeu qui devrait vous répondre, en fonction de l'univers. Pour moi, je reçois le message :

> Vous ne pouvez aller par là...

### Via le SharpScript

Vous pouvez aussi ajouter un macro via une syntaxe du scripting SharpScript. En fait, c'est comme ça que vos triggers, macros et alias sont enregistrés dans votre fichier **config.set** (une configuration par univers).

Pour créer un macro, utilisez l'action `#macro`. Elle prend deux paramètres :

- Le raccourci à associer à ce macro ;
- La commande à envoyer au serveur quand on entre ce raccourci.

Dans notre exemple, on aurait pu créer notre macro en entrant l'instruction SharpScript suivante :

```
#macro F1 nord
```

Vous pouvez coller cette instruction directement dans CocoMUD et appuyez sur Entrée, comme pour envoyer une commande. CocoMUD voit que cette commande commence par un seul signe dièse et l'envoie à l'interpréteur SharpScript. Si vous ajoutez un macro de cette manière (et si vous n'avez pas fait d'erreurs de syntaxe), le macro sera visible instantanément dans la barre de menu **Jeu** -> **Macro**.

Si l'un des paramètres contient des espaces, n'oubliez pas de l'entourer d'accolades :

```
#macro {Ctrl + Shift + O} {dire c'est plutôt une longue commande.}
```

Les accolades ne sont absolument nécessaires que si le paramètre contient des espaces. Mais vous pouvez mettre des accolades autour des paramètres même si ils n'ont pas d'espaces, le moteur SharpScript les retirera sans faire d'histoire.

## Editer un macro

Nous avons vu plus haut comment éditer un macro. Il n'y a rien de très compliqué, en vérité. L'important à retenir, c'est que si vous voulez changer le raccourci associé à un macro, vous devez juste le sélectionner et faire Tab pour entrer le nouveau raccourci. Si vous souhaitez changer la ou les commandes associées à ce macro, cependant, vous devez le sélectionner et cliquer sur le bouton **Editer**. La boîte de dialogue est identique à celle pour ajouter un macro, décrite précédemment.

## Supprimer un macro

Supprimer un macro se fait des plus simplement.  Dans la boîte de dialogue (menu **Jeu** -> **Macro**), sélectionnez le macro que vous voulez supprimer, et tabulez jusqu'à trouver le bouton **Supprimer**. Une confirmation de suppression sera affichée. N'oubliez pas de validez en cliquant sur le bouton **OK**, sans quoi le macro ne sera pas complètement supprimé.

## Macros un peu plus complexes

Les macros relient souvent une touche de raccourci à une ou plusieurs commandes à envoyer au serveur. Cependant, vous pouvez aussi relier un raccourci clavier avec une action plus complexe, comme jouer un son, afficher un message (avec variables, éventuellement) ou afficher un canal. L'intérêt de telles action n'est pas forcément apparent tout d'abord. Un exemple de macro plus complexe peut se trouver dans l'utilisation des prompts sonores.

Le principe d'un prompt sonorisé est que la barre de prompt (contenant vos points de vie, magie et mouvement, par exemple) est interceptée par un trigger et n'apparaît plus. Votre vie, magie et mouvement actuels sont conservés dans des variables à part. Ceci dépasse le cadre de cette documentation, mais l'important est qu'un macro peut être créé pour afficher ces variables. Par exemple, si vous appuyez sur `Ctrl + J`, vous pourriez voir votre vie actuelle.

Nous avons utilisé la seconde zone de texte pour préciser quelles commandes envoyer au serveur de jeu quand on entre le raccourci indiqué. En vérité, on peut entrer des instructions SharpScript dans cette zone de texte. Mais puisque écrire les instructions SharpScript à la main n'est pas le plus facile, on peut passer par l'éditeur SharpScript. Cela n'est vraiment pas compliqué : dans l'interface d'ajout ou d'édition d'un macro, laissez le second champ de texte vide, et tabulez une fois pour vous trouver sur la liste des actions. Sélectionnez une action, par exemple "Affiche un message et l'envoie au lecteur d'écran". Cliquez sur le bouton **Ajouter l'action**. On vous demandera d'entrer d'autres informations (dans notre cas, le message à afficher, et des informations sur comment l'afficher). Validez une fois ces informations renseignées. N'oubliez pas d'appuyer sur **OK** pour fermer la boîte de dialogue en sauvegardant les modifications.
