---
title: "Les canaux dans CocoMUD"
---

# Les canaux dans CocoMUD

CocoMUD offre la fonctionnalité des canaux. Un canal CocoMUD est, tout simplement, une liste de messages. Vous pouvez alimenter cette liste comme bon vous semble. Il est courant d'associer un ou plusieurs canaux du jeu avec un ou plusieurs canaux CocoMUD : quand un message est reçu provenant de l'un de ces canaux (comme public ou hrp), il est capturé automatiquement dans un canal CocoMUD. Un raccourci clavier peut être associé à un canal pour afficher la liste des messages qu'il contient. Cette fonctionnalité s'avère très pratique en cas d'exploration ou de combat dans le jeu, quand on ne souhaite pas nécessairement être interrompu par ce type de messages mais désirons les conserver pour les lire plus tard.

Nous utiliserons cet exemple tout au long de la documentation : essayons de capturer le contenu du canal hrp dans un canal CocoMUD. Cet exemple est le même que celui donné pour [les triggers](triggers.md), ce qui n'est évidemment pas une coïncidence.

* Table of contents
{:toc}

## Créer un nouveau canal

La première chose à faire est de créer un canal CocoMUD, une liste vide qui pourra recevoir certains messages. Pour l'exemple, nous allons créer un canal "hrp". Souvenez-vous, les canaux CocoMUD peuvent contenir tout type d'information, bien qu'ils soient souvent utilisés pour capturer des canaux du jeu.

Dans la barre de menu du client, sélectionnez **Jeu** -> **Canaux**. Vous vous retrouvez dans une boîte de dialogue listant les canaux existants. Cette liste est probablement vide pour l'instant. Tabulez jusqu'à trouver le bouton **Ajouter** et validez. Le client vous demande le nom du canal à créer. Un nom court et explicite est préférable : ici, nous l'appellerons `hrp` .

On peut maintenant envoyer des messages à ce canal en utilisant [des triggers](triggers.md). Si vous n'êtes pas familier du concept des triggers, il est recommandé de lire [la documentation des triggers](triggers.md) avant de continuer.

## Nourrir un canal avec des triggers

Premier réflexe quand il s'agit de créer un trigger, regardons les lignes qui devraient le déclencher. Il y en a deux dans notre cas :

Quand on envoie un message sur le canal "hrp", on pourrait voir quelque chose comme :

```
[hrp] Vous dites : mon message
```

Si c'est quelqu'un d'autre qui parle sur ce canal, vous pourriez voir :

```
[hrp] Quelqu'un dit : mon message
```

Voyons ce qui reste identique et ce qui diffère entre ces deux lignes :

- Et bien, d'abord, on a "[hrp]"(c'est-à-dire "hrp"entouré de crochets) suivi d'un espace ;
- Ensuite il y a le nom de l'auteur du message, soit "Vous" soit "Quelqu'un" ;
- Il y a ensuite le mot "dit" après un nouvel espace... ha bien non, si on écrit, le mot est "dites", si c'est un autre, c'est "dit". Que faire ?
- Un nouvel espace, un signe deux points (`:`), un espace et le message.

Pour résoudre notre problème entre dit/dites, on a deux solutions :

- On peutécrire un seul trigger qui se déclenche dans les deux cas, en incluant dans le déclencheur "dit*". Cela voudra dire "dit" suivi de n'importe quoi ;
- On peut aussi créer deux triggers distincts, l'un pour la première ligne et l'un pour la seconde.

J'ai tendance à préférer la seconde solution, mais je sais que certains préféreront la première, Nous verrons donc les deux ici :

### Un seul trigger

Voyons notre déclencheur pour un seul trigger. Vous êtes prêt ?

```
[hrp] * dit*: *
```

Trois astérisques ! Le premier capturera le nom de l'auteur du message. Le second capturera rien ou "es" (en fonction de si c'est vous ou un autre qui parle). Nous ne l'utiliseront pas. Le troisième capturera le message.

Pour créer ce trigger en passant par l'interface :

- Ouvrez la barre de menu, **Jeu** -> **Triggers** ;
- Cliquez sur **Ajouter** pour créer un trigger ;
- Entrez le déclencheur `[hrp] * dit*: *` avant d'appuyer sur Tab ;
- Sélectionnez "Envoie un message dans un canal" ;
- Cliquez sur le bouton **Ajouter l'action** ;
- Dans le nom du canal dans lequel envoyer le message, écrivez `hrp` ;
- Dans le message à envoyer au canal, entrez :
```
$1: $3
```
- Cliquez sur **OK** plusieurs fois pour fermer la boîte de dialogue en sauvegardant.

> Qu'est-ce que c'est que `$1 $3`?

`$1` contient l'auteur du message (vous ou quelqu'un).  `$3` contient le message envoyé. Quand on reçoit la ligne :

```
[hrp] Jamie dit : bien joué !
```

Notre canal CocoMUD devrait recevoir le message :

```
Jamie: bien joué !
```

Vous pouvez entrer `#channel hrp` pour voir la liste des messages sur ce canal. Il est possible de relier cette action à un macro, pour afficher le canal quand on presse une touche de raccourci.

Vous pourriez avoir fait la même chose en utilisant une seule ligne de SharpScript:

```
#trigger {[hrp] * dit*: *} {#feed hrp {$1: $3}}
```

C'est peut-être un peu plus dur à comprendre en SharpScript, mais si vous êtes habitué à la syntaxe, c'est définitivement plus rapide.

Un dernier mot concernant ce trigger : vous aurez peut-être remarqué qu'on ne joue pas de son si ce trigger se déclenche. Rien ne vous empêche de le faire au travers de l'interface (d'avoir deux actions liés à un trigger). La même chose peut se faire en SharpScript :

```
#trigger {[hrp] * dit*: *} {
    #feed hrp {$1: $3}
    #play sounds/public.wav
}
```

### Deux triggers distincts

Comme dit plus haut, il y a deux façons de régler le problème posé par dit/dites. L'une de ces solutions est de créer deux triggers, l'un pour quand on est l'auteur, l'autre pour les autres.  Cela demandera un peu plus de configuration, mais cela reste plus lisible, je trouve. Parfois il sera impossible de faire autrement, cela dépend de la langue dans laquelle le MUD se trouve.

Nos deux déclencheurs seraient donc :

```
[hrp] Vous dites : *
[hrp] * dit : *
```

Je ne peux pas dire pour vous, mais ça me semble personnellement bien plus clair. Le premier trigger ne se déclenche que quand on est l'auteur du message (peut-être qu'on ne jouera pas de son à ce moment), le second se déclenche quand c'est quelqu'un d'autre qui parle sur le canal. Voici les instructions SharpScript pour créer ces triggers, mais comme d'habitude, vous pouvez le faire via l'interface :

```
#trigger {[hrp] Vous dites : *} {#feed hrp {Vous : $1}}
#trigger {[hrp] * dit : *} {
    #feed hrp {$1 : $2}
    #play sounds/public.wav
}
```

Choisissez la méthode qui vous para^8it la plus simple, en fonction du contexte.

## Associer un macro à un canal

Envoyer des messages à un canal est certainement utile, sous réserve de pouvoir l'afficher. La plupart du temps, on crée un macro pour afficher le contenu du canal. C'est assez facile à faire :

Commencez par créer un macro comme d'habitude. Dans l'interface du client :

- Ouvrez la barre de menu **Jeu** -> **Macros**.
- Cliquez sur **Ajouter** pour ajouter un nouveau macro.
- Appuyez sur les touches à associer à ce macro. Par exemple : `CTRL + H`.
- Tabulez deux fois pour trouver la liste des actions possibles. Dans cette liste, vous devriez trouver l'action "Crée ou affiche un canal".
- Tabulez une fois pour ajouter cette action. Le client vous demande le nom du canal à afficher. Entrez `hrp` dans cet exemple.
- Fermez ces boîtes de dialogue en appuyant plusieurs fois sur **OK** pour enregistrer. Vous pouvez à présenter entrer le raccourci `CTRL + H` pour afficher le canal HRP. Victoire !

## Supprimer un canal

On peut supprimer un canal en utilisant la même interface :

- Ouvrez la barre de menu **Jeu** -> **Canaux**.
- Tabulez jusqu'à trouver le bouton **Supprimer**. Le client vous demandera quel canal supprimer. Sélectionnez-en un, tabulez de nouveau pour le supprimer. Si vous validez en appuyant sur **OK** ensuite, le canal sera retiré de votre configuration.

Gardez à l'esprit cependant qu'un ou plusieurs triggers peuvent toujours essayer d'alimenter ce canal. Cela ne marchera pas, le canal n'existant plus, mais le trigger existera toujours car il pourrait faire d'autres choses.
