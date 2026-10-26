---
title: "Configuration des personnages dans CocoMUD"
---

# Configuration des personnages dans CocoMUD

CocoMUD permet de configurer un ou plusieurs personnages par univers. Un personnage configuré offre plusieurs avantages :

- Se connecter par un personnage entrera automatiquement votre nom d'utilisateur, mot de passe et autres informations nécessaires.
- Le nom d'utilisateur et mot de passe sont cryptés par CocoMUD, ces informations n'apparaîtront pas en clair, ni dans votre historique de commande, ni dans l'un des fichiers de configuration de CocoMUD.
- Si vous utilisez une connexion sécurisée (comme SSL ou SSH) votre mot de passe sera protégé et invisible depuis votre ordinateur ou depuis le réseau.
- Vous pouvez avoir des bloc-notes CocoMUD séparés pour chacun de vos personnages.

Quand vous choisissez un univers auquel se connecter, vous pouvez choisir plus spécifiquement un des personnages configurés sur cet univers. Cependant, vous pourrez toujours, peu importe le nombre de personnages configurés, demander à CocoMUD de vous connecter au jeu sans utiliser un personnage.

## Ajouter un personnage à un univers

Par défaut, vous n'avez aucun personnage configuré sur vos univers. Pour ajouter un personnage, il vous faut vous connecter à l'univers pour commencer. Quand vous ouvrez CocoMUD et que vous vous trouvez sur la liste des univers configurés, choisissez-en un et appuyez sur ENTRÉE pour s'y connecter.

CocoMUD essayera alors de se connecter à cet univers. Il n'entrera aucune information automatiquement. Pour créer un personnage, ouvrez la barre de menu, sélectionnez **Jeu** -> **Changer les options de ce personnage...**.

Une boîte de dialogue s'ouvrira alors, vous demandant plusieurs informations :

- **Nom** : le nom du personnage à ajouter. Cette information n'est utilisée que par CocoMUD et ne sera pas envoyée au serveur de jeu. Le nom entré sera affiché sur l'écran de connexion pour vous permettre de vous connecter plus rapidement (voir ci-dessous).
- **Nom d'utilisateur ou autres commandes à envoyer avant le mot de passe** : vous devez entrer ici la première commande (ou commandes) à entrer une fois connecté au jeu. En général, le jeu vous demande le nom d'utilisateur dès la connexion. Sur d'autres jeux, vous pourriez avoir d'autres commandes à entrer. N'écrivez pas votre mot de passe dans ce champ, entrez juste la ou les commandes à entrer avant votre mot de passe. Si vous avez plusieurs commandes à entrer, placez-les sur des lignes distinctes en appuyant sur ENTRÉE.
- **Mot de passe optionnel** : il vous faut ici préciser votre mot de passe (si il y en a un à envoyer au jeu pour vous connecter, ce qui est souvent le cas). Ce champ n'est pas seulement protégé (vous ne verrez que des signes `*` à la place de chaque lettre), le mot de passe sera crypté par CocoMUD et n'apparaîtra pas en clair dans la configuration du client.
- **Les commandes optionnelles à envoyer après le mot de passe** : sur la plupart des jeux, vous n'aurez que votre nom d'utilisateur et mot de passe à entrer pour vous connecter. D'autres attendront des informations supplémentaires, que vous pouvez entrer ici. De même que les commandes à envoyer avant le mot de passe, vous pouvez préciser plusieurs commandes en les séparant sur plusieurs lignes.
- **Positionner ce personnage comme choix par défaut** : si cette case est cochée, quand vous sélectionnerez l'univers pour vous y connecter, ce personnage sera automatiquement sélectionné. Vous ne pouvez avoir qu'un seul personnage par défaut configuré sur chaque univers.

Cliquez sur **OK** pour confirmer vos options. Vous pouvez ensuite fermer l'onglet et le ré-ouvrir : sur l'écran de connexion, sélectionnez l'univers avec les flèches. Appuyez sur la touche de tabulation: vous devriez vous retrouver sur une seconde liste, qui est la liste des personnages associés à cet univers. Le premier élément en haut de la liste est "aucun personnage", un choix qui vous permet de vous connecter au jeu sans entrer les commandes spécifiques à un personnage. Si vous avez configuré un personnage par défaut, le curseur sera sur ce choix automatiquement. Utilisez les flèches pour naviguer dans la liste des personnages et appuyez sur ENTRÉE pour se connecter à l'univers en utilisant ce personnage.

Quand vous vous déplacez dans la liste des univers (la liste sur laquelle vous vous trouvez quand CocoMUD s'ouvre), si vous sélectionnez un univers avec les flèches, son personnage par défaut sera automatiquement sélectionné. Nul besoin de faire **tab** pour le sélectionner. Vous pouvez appuyez sur ENTRÉE après avoir sélectionné l'univers si vous souhaitez vous connecter au personnage par défaut.

## Changer la configuration du personnage

Si vous avez changé le mot de passe du personnage sur le jeu ou une autre information, vous pouvez vous connecter sur ce personnage et retourner dans la barre de menu, **Jeu** -> **Changer les options de ce personnage...**. La boîte de dialogue s'ouvrira de nouveau avec les options déjà renseignées pour ce personnage. Vous pouvez les modifier et cliquez sur **OK**.

## Ajouter plusieurs personnages à un univers

Ajouter plusieurs personnages est assez semblable à ajouter un seul personnage : l'astuce ici est dans la façon de se connecter à l'univers. Vous devez sélectionner l'univers sur l'écran de connexion et tabuler une fois pour sélectionner "aucun personnage", ce qui veut dire qu'aucun personnage associé à cet univers ne sera choisi. De nouveau, rendez-vous dans la barre de menu, **Jeu** -> **Changer les options de ce personnage...**. La prochaine fois que vous vous trouverez sur l'écran de connexion, vous verrez que le nouveau personnage est bel et bien présent dans la liste. Souvenez-vous, vous ne pouvez avoir qu'un seul personnage par défaut configuré par univers. Tous les personnages sont affichés dans l'ordre alphabétique, vous pouvez aisément naviguer entre le personnage par défaut et d'autres personnages configurés.

## Une note concernant la configuration

Pour l'instant, la configuration est seulement propre à l'univers. Cela signifie que tous les personnages configurés sur un univers partageront les mêmes [alias](alias.md), [triggers](triggers.md) ou canaux.
