---
title: "Quoi de neuf dans les récents builds"
---

# Quoi de neuf dans les récents builds

Cette page décrit les changements apportés par chaque build. Vous pouvez naviguer entre builds en utilisant la navigation par titre.

## Build 51

- Ajout d'un logger dont le rôle est d'écrire le contenu de vos sessions automatiquement dans un fichier. Il est activé par défaut pour toutes vos sessions, mais vous pouvez le désactiver pour toutes (voir les options du client). Vous pouvez aussi l'activer ou le désactiver manuellement pour chaque session (voir le menu **Jeu**).
- Ajout de la fonction SharpScript `#pause` qui permet de faire une pause d'un temps configurable au milieu de votre script. Comme toujours, cette fonction est utilisable pour les alias, macros ou triggers. Vous pouvez l'ajouter normalement, depuis l'interface habituelle.
- Ajout des variables comme fonctionnalités du SharpScript. Les variables peuvent retenir des informations spécifiques à votre contexte de jeu (elles persistent si vous vous reconnectez à la même session). Elles permettent souvent de demander à CocoMUD de "retenir" une information que l'on pourra utiliser plus tard.

    Pour ajouter une variable, faites appel à la fonction SharpScript `#writevar` (de nouveau, vous pouvez l'ajouter depuis l'interface, que ce soit dans vos macros, alias ou triggers). Par exemple, sur un MUD définissant des vaisseaux, vous pourriez vouloir retenir votre vaisseau actuel dans une variable (appelons-la `curship`, pour `current ship`). Pour ajouter cette variable, vous pourriez créer un alias, par exemple `curship *` , dont les actions comprendront notamment `#writevar curship $1`, c'est-à-dire que le premier argument de l'alias sera envoyé dans la variable `curship`. Si donc vous entrez `curship I11Y`, la variable `curship` sera créée ou modifiée avec la valeur `I11Y`. Vous pouvez l'utiliser plus tard des plus simplement. Par exemple, vous pourriez envoyer la fonction SharpScript `#send {openhatch $curship}`, qui enverra dans notre cas `openhatch I11Y` au serveur. Ce peut être utile si vous effectuez de nombreuses opérations sur des données similaires.

    Vous avez également accès à la fonction SharpScript `#checkvar`. Celle-ci vérifie qu'une variable existe. Si ce n'est pas le cas, elle interrompt le script et peut envoyer un message d'avertissement qui sera affiché dans votre client. Cela peut être très utile pour vérifier qu'une variable existe avant de l'utiliser.

> Note : ces fonctionnalités utilisent le moteur SharpScript lui-même ainsi que l'interface correspondante. Elles ont été abondamment testées. Peu d'utilisateurs ont encore inclus Python directement dans leur configuration. Pour ceux qui l'ont fait cela dit, sachez qu'un gros travail de documentation et de développement est en cours pour rendre l'écriture de configuration en Python plus intuitive.

## Build 50

- Ajoute une fonctionnalité empêchant certains jeux de vous déconnecter si vous êtes inactif (idle out). Cette fonctionnalité, une fois active, envoie simplement des commandes vides au serveur de jeu sur une base aléatoire. À noter que la plupart des serveurs de jeu interdisent l'utilisation de ce genre de fonctionnalités.
- Ajout de la fonction `#randplay` permettant de jouer un son aléatoire parmi une liste de possibilités.
- CocoMUD reconnaît et interprète convenablement le signal Telnet Go-Ahead. En terne plus simple, CocoMUD devrait avoir bien moins tendance à couper des lignes de texte si le jeu envoie beaucoup d'informations d'un seul coup.
- Ajout de la première version des pauses (delays), permettant la mise en place des timers, speed walking et autres fonctionnalités dans des futures versions.
- Le bloc-notes CocoMUD, utilisé pour écrire et lire des notes sur le jeu, ne masque plus la fenêtre du client. Il est donc possible d'ouvrir ces deux fenêtres en même temps sans inconvénient.
- CocoMUD peut à présent répéter la dernière commande entrée à l'aide de la fonction `#repeat`. Cela permet notamment de créer un alias `!` pour répéter la dernière commande entrée.
- Corrige un bug dans les macros utilisant le moins du pavé numérique.
- Corrige un bug empêchant d'importer un univers depuis un fichier.
- Corrige un bug dans les macros utilisant le raccourci `ALT + X` ou `ALT + Shift + X`.
- Créer un nouveau personnage est le choix par défaut si aucun personnage n'existe dans cet univers.
- Corrige un bug qui faisait planter CocoMUD à l'ouverture de la console SharpScript.
- Termine l'optimisation de la fenêtre de contenu. Malheureusement, certains utilisateurs trouvent toujours CocoMUD assez lent quand il contient beaucoup de texte. Ce bug ne sera vraisemblablement pas corrigé, il n'est guère possible d'optimiser la fenêtre davantage et la solution reste d'effacer l'historique quand cela se produit.
- Ajout d'un testeur de mise à jour pour s'assurer que les versions futures n'entraîneront pas de problèmes pour CocoMUD.

## Build 49

- CocoMUD est à présent disponible en espagnol ! Un grand merci au contributeur qui a traduit CocoMUD dans cette langue et a participé à d'autres demandes pendant cette version.
- CocoMUD tourne à présent sous Python 3, à la place de Python 2. Quelques erreurs mineures de compatibilité pourraient persister, n'hésitez pas à les signaler si vous en rencontrez.
- Les macros et d'autres éléments de configuration sont maintenant correctement liés à une session, pas à un univers. Il n'y a donc plus de conflit si vous ouvrez plusieurs onglets sur le même univers.
- CocoMUD peut maintenant jouer des fichiers audio dans les format MP3, OGG et WAV sans distinction. L'ancienne dépendance sur `pygame` a été rejetée, CocoMUD utilise à présent une bibliothèque audio bien plus légère et efficace.
- La console est à présent masquée quand CocoMUD se met à jour. Cela fait parti d'un effort pour rendre la mise à jour plus agréable.
- La console Python a été retirée du menu **Fichier**. À la place, un nouveau menu **Outils** a été ajouté la contenant.
- Une console SharpScript a été ajoutée dans le menu **Outils**. Si vous avez utilisé CocoMUD depuis le début, vous vous souviendrez peut-être qu'il était possible d'entrer des instructions SharpScript (comme `#say`) directement dans le client. Cette option a été retirée car elle créait trop de conflit avec certains jeux. Vous pouvez maintenant entrer les exemples de configuration rapide dans cette console.
- CocoMUD prend à présent un argument de ligne de commande optionnel, permettant de spécifier un dossier de configuration différent. Par défaut, CocoMUD conserve ses données dans le répertoire courant (celui où se trouve **cocomud.exe**). On peut maintenant lui préciser un autre répertoire. Cette option ne sera sans doute pas utilisée par la plupart des utilisateurs, mais elle est bien pratique pour les développeurs. Exemple d'utilisation : `cocomud.exe --config-dir=D:\CocoMUD`
- Le compteur de notifications non lues augmentait systématiquement même si l'information reçue était dissimulée par un trigger muet. Cela a été corrigé.
- CocoMUD plantait à l'ouverture si aucune connexion Internet n'était disponible. Cela a été corrigé.
- Une régression a été corrigée, interdisant de créer et charger des personnages. Notez également qu'afin de rendre CocoMUD plus facile à utiliser pour une population internationale croissante, la configuration des univers et mondes (principalement les fichiers `config.set` pour commencer) seront convertis dans l'encodage utf-8. Cette opération se fait automatiquement et ne nécessite généralement aucune action de votre part.
- Les erreurs générées dans la console Python n'étaient pas correctement affichées. Cela a été corrigé.
- Les couleurs en jeu n'étaient pas toujours affichées. Cela a été corrigé et optimisé.
- Note pour les développeurs : CocoMUD utilise maintenant `pipenv` pour le support de ses dépendances, ce qui permet une installation depuis les sources bien plus simple. Une documentation plus détaillée sera fournie prochainement.

## Build 48

- Une option dans la barre de menu (**Jeu** -> **Canaux**) permet d'éditer les canaux. Vous trouverez [la documentation sur les canaux ici](channels.md).
- Une nouvelle fonction SharpScript `#randplay` a été ajoutée, permettant de jouer un son aléatoirement choisi dans une liste. La fonction est utilisable, mais elle n'est pas encore présente dans l'interface du client.
- Le travail pour supporter les options globales a été fait et sera probablement disponible lors de la prochaine mise à jour.
- On peut maintenant vider la fenêtre de contenu grâce à l'option dans la barre de menu **Jeu** -> **Nettoyer la fenêtre de contenu**.
- Plusieurs correctifs pour rendre l'importation d'univers depuis le site web de nouveau possible.
- Correction de l'erreur en modifiant les préférences.

## Build 47

- Vous pouvez simplement exporter un univers dans un fichier ZIP, en choisissant quoi exporter (**Fichier** -> **Exporter cet univers**). Vous pouvez ensuite partager ce fichier ZIP avec d'autres utilisateurs qui pourront l'importer depuis **Fichier** -> **Importer un univers**.
- CocoMUD gère mieux le contenu du presse-papier, en particulier sous Linux.  Une case à cocher a été ajoutée dans les options pour désactiver l'envoi automatique du texte quand on colle depuis le presse-papier.
- CocoMUD supporte et affiche les fichiers au format **WAV** et **OGG** pour jouer des sons.
- Le rich-text a été désactivé par défaut pour offrir une expérience utilisateur plus fluide pour les nouveaux utilisateurs.
- Plusieurs améliorations et corrections de bug pour Linux (#105, #106).
- CocoMUD ouvre et enregistre les préférences utilisateurs convenablement même si la langue de l'utilisateur n'est pas supportée par le client.
- Importer un univers depuis le site web ne génère plus d'erreur d'encodage.
- CocoMUD affiche à présent le texte utilisant une police de caractère plus agréable (merci encore aux contributeurs voyants).
- Note : pour des raisons de compatibilité, l'encodage des fichiers de configuration a été modifié. CocoMUD devrait supporter les anciens fichiers de configuration et les convertir à l'ouverture, mais il est possible que certaines erreurs surviennent avec des fichiers contenant de nombreux caractères spéciaux.

## Build 46

- Les commandes multiples fonctionnent de nouveau et sont à présent systématiquement testées.
- Les commandes multiples supportent maintenant les caractères spéciaux.
- CocoMUD gère mieux les variables dont les valeurs contiennent des caractères spéciaux.

## Build 45

- CocoMUD ne fait plus planter le lecteur d'écran en bloquant la fenêtre.
- CocoMUD supporte maintenant le protocole SSL, permettant de crypter la connexion telnet.
  SSL n'est pas proposé par tous les jeux, et est configuré sur un port différent du protocole telnet.
- Ajoute une option dans la barre de menu pour désactiver tous les sons du client comme ceux générés par des triggers.

## Build 44

- Ajoute une action SharpScript pour répéter la dernière commande entrée :
  Cette action, appelée `#repeat`, peut être utilisée pour répéter la dernière commande entrée ou envoyer une commande plusieurs fois.
- Quand un raccourci associé à un macro est utilisé, le curseur va automatiquement en bas de la fenêtre .
- Corrige plusieurs conflits quand un univers était ouvert plusieurs fois dans différents onglets.

## Build 43

- Ajout d'une page de documentation pour [télécharger et installer CocoMUD](download.md).
- Ajout de raccourcis clavier pour ajouter, éditer ou supprimer dans toutes les boîtes de dialogue.

## Build 42

- Ajoute les triggers avec substitution :
  Les triggers peuvent maintenant remplacer une ou plusieurs lignes directement dans le client, quand ils s'exécutent.
- Mise à jour des couleurs et du style de la fenêtre en mode rich-text.
- Corrige un bug avec le curseur instable quand plusieurs onglets sont ouverts.

## Build 41

- Ajout des personnages par défaut :
  Dans la boîte de dialogue pour configurer un personnage, on peut maintenant préciser si ce personnage doit être chargé par défaut. Si oui, à la connexion, en choisissant un univers dans la liste, CocoMUD sélectionne automatiquement ce personnage. Cela permet de gagner du temps si l'on se connecte souvent au même personnage d'un univers, et n'empêche pas de se connecter à d'autres.
- Quand on crée un personnage avec des caractères spéciaux (comme des lettres accentuées), CocoMUD ne plante plus au démarrage.
  Un merci tout particulier au contributeur qui a signalé ce bug sur le site.
- Quand CocoMUD perd la connexion au serveur, il essaye de se reconnecter, entrant le nom d'utilisateur / mot de passe si configuré pour :
  Cette correction n'est pas parfaite, il est difficile de gérer les erreurs de connexion.
- Quand aucune mise à jour n'est disponible, le message s'affiche correctement.

## Build 40

- Ajoute une option pour désactiver le "rich text" dans le client.
  Cette option se trouve dans le menu **Fichier** -> **Options**, onglet **Accessibilité**. Désactiver le "rich text" est parfois utile pour l'accessibilité, bien que cela retire toute couleur du client.
- Créer un univers et fermer la boîte de dialogue ne crée plus d'erreur.
  Un merci tout particulier au testeur qui a reporté ce bug.
- Corrige un bug quand on ferme tous les onglets de CocoMUD.

## Build 39

- Ajoute un bouton pour importer un univers depuis l'écran de connexion:
  Il est désorlmais possible d'importer un univers avant de se connecter (ce qui est assez logique la plupart du temps). Cliquez simplement sur le bouton **Importer** sur l'écran de connexion, et choisissez si vous désirez importer l'univers depuis un fichier ou depuis le site Web.
- Affiche une boîte de dialogue pour confirmer que l'installation d'un univers s'est bien déroulée.
- Installer un univers avec canaux n'ouvre plus de boîtes de dialogues secondaires.
- Redémarrer CocoMUD après avoir installé un univers n'est plus nécessaire.

## Build 38

- Ajout de bloc-notes pour chaque univers et chaque personnage:
  CocoMUD permet désormais d'accéder à des bloc-notes indépendants, des fichiers de texte que vous pouvez utiliser pour conserver certains points de repère, des informations de quête ou autre. Il y a un bloc-notes différent pour chaque univers, que vous pouvez ouvrir via la barre de menu -> **Jeu** -> **Bloc-notes** -> **Pour cet univers...**. Vous pouvez écrire du texte dans ce bloc-notes, appuyer sur échappe pour le fermer et l'enregistrer. Le second bloc-notes fonctionne selon le même principe, et est accessible via la barre de menu **Jeu** -> **Bloc-notes** -> **Pour ce personnage...**. Ce second bloc-notes ne sera pas partagé entre les personnages de cet univers.
- Ajoute une documentation pour les [macros](macros.md).
- Ajoute les triggers marqués dans la boîte de dialogue des triggers.
- Autorise les triggers sans action, particulièrement utile pour les triggers marqués.
- Corrige plusieurs bugs d'affichage dans l'interface.

## Build 37

- Ajout une fonctionnalité pour créer des personnages :
  On peut désormais configurer un univers avec plusieurs personnages. Un personnage possède des informations de configuration plus spécifiques (comme des alias, macros ou triggers qui lui sont propres), mais il possède surtout des informations de connexion (un nom d'utilisateur et mot de passe, par exemple). Ces informations sont conservées dans un fichier crypté.
  Pour créer un nouveau personnage, dans la boîte de dialogue de connexion, sélectionnez l'univers auquel vous souhaitez vous connecer, puis faites Tab pour voir la liste des personnages associés à cet univers. Par défaut, il ne devrait y en avoir qu'un seul, appelé "aucun". Validez sur ce personnage (ou cliquez sur le bouton **se connecter**). CocoMUD vous connecte à un univers sans personnage. Pour créer un personnage, rendez-vous dans la barre de menu, **jeu** -> **Changer les options de ce personnage...**. Précisez dans cette boîte de dialogue le nom du personnage. Vous pouvez préciser les commandes à entrer avant le mot de passe (généralement un nom d'utilisateur), le mot de passe-même et les commandes à entrer après le mot de passe (si il y en). Cliquez sur **OK** pour sauvegarder le personnage dans un fichier crypté. À la prochaine connexion, vous verrez ce personnage dans la liste (choisissez l'univers, faites Tab pour vous retrouver dans la liste des personnages associées à cet univers). Les commandes que vous avez entrées dans la boîte de dialogue seront envoyées au serveur de jeu dès l'ouverture de la session, pour vous connecter plus rapidement. Elles seront de nouveau envoyées si vous souhaitez vous reconnecter.
- Corrige un bug empêchant de créer un univers.
- Ajout de la boîte de dialogue en cas de crash :
  Cette boîte de dialogue apparaît quand une erreur imprévue survient dans le client. Elle vous donne plus d'informations sur l'origine du bug, ainsi que des explications sur la façon de rapporter ce bug à l'équipe des développeurs.

## Build 36

- Ajoute les triggers marqués.
  Une marque peut être placée sur un trigger, ce qui déplace le curseur automatiquement sur la ligne reçue ayant déclenché le trigger. Cela peut être utile quand vous recevez un nouveau message, si un trigger y est associé. Cela peut aussi être utile pendant l'exploration, pour déplacer directement le curseur sur la liste des sorties, par exemple.
- Met à jour la fenêtre visuellement pour essayer de la rendre plus agréable.
- Ajoute la gestion des couleurs ANSI dans le client.

## Build 35

- Ajoute la fonctionnalité pour importer un univers depuis un fichier, ou depuis Internet.
  Dans le menu **fichier**, il y a un nouveau menu "importer un univers". Dedans se trouve deux sous-menus : le premier sert à importer un univers depuis un fichier, le second depuis Internet. Ce dernier regardera les univers configurés sur le site web du projet. Vous pourrez télécharger l'un d'entre eux depuis cette interface.

## Build 34

- Ajoute un système de canaux:
Les canaux sont utiles pour surveiller plusieurs évènements. Ils sont surtout utiles pour conserver les messages de canaux de communication sur un jeu. Grâce au système de triggers, il est possible d'envoyer les messages à un canal spécifique. Grâce aux macros ou alias, il est possible d'afficher cette liste dans une boîte de dialogue séparée.
- Dans les préférences, onglet **accessibilité**, il est maintenant possible de configurer l'interruption du TTS si de nouveaux messages arrivent pendant la lecture.
- Quand les options du TTS sont modifiées dans les préférences, les changements sont appliqués instantanément.
- Corrige quelques bugs dans le moteur SharpScript.

## Build 33

- Les alias/macros/triggers décrits sur plusieurs lignes marchent de nouveau.
- On peut maintenant écrire des instructions SharpScript dans des macros.
- Les variables sont à présent expliquées dans [la documentation des alias](alias.md).
- Le titre de la fenêtre quand plusieurs onglets sont ouverts est mis à jour correctement.

## Build 32

- Ajoute une syntaxe pour écrire des variables en SharpScript.
  La syntaxe est `$variable`.  Les variables ont été ajoutées aux alias et aux triggers.
- Corrige un bug mineur dans les commandes multiples.
- Ajoute les triggers muets, très utiles pour sonoriser un prompt.

## Build 31

- Améliore le système de logging.
- Met à jour les catalogues utilisés pour la traduction.

## Build 30

- Ajout d'un système de logging pour débug les évènements automatiques.

## Build 29

- Corrige un bug des triggers sonores quand plusieurs univers sont ouverts en même temps.

## Build 28

- Ajout des [commandes multiples](basics.md#commandes-multiples) (command stacking en anglais), pour envoyer plusieurs commandes à la fois, en utilisant le point virgule ou un autre caractère.

## Build 27

- Permet d'ouvrir plusieurs univers dans des onglets :
  Il est maintenant possible d'ouvrir plusieurs univers dans des onglets séparés, ou même d'ouvrir le même univers plusieurs fois. Dans le menu fichier se trouve à présent trois options pour créer un univers, ouvrir un univers dans un onglet différent et fermer l'onglet actuel. Pour naviguer entre les onglets, utilisez Ctrl + tab et Ctrl + Shift + tab comme d'habitude.
  La fonctionnalité permettant de changer le titre de la fenêtre si des messages non lus sont reçus par le client prend maintenant en compte l'onglet sélectionné uniquement.
- Ajout de menus pour se déconnecter et se reconnecter à un univers:
  Un nouveau menu dans la barre de menu, appelé connexion, permet de se déconnecter ou se reconnecter à l'univers actuellement sélectionné.
- Le client ne lag plus quand il essaye de se connecter à un serveur distant.

## Build 26

- Quand l'utilisateur ne se trouve pas dans la fenêtre du client, si des messages sont reçus, le titre de la fenêtre change pour avertir l'utilisateur que des notifications l'attendent sur le client.

## Build 25

- Ajout de l'historique des commandes
  L'historique des commandes se souvient de chaque commande que vous avez entrée. Vous pouvez l'utiliser en appuyant sur CTRL + flèche haut ou bas pour naviguer dans vos commandes entrées. Vous pouvez aussi utiliser l'historique de commande en mode verrouillé. Pour ce faire, appuyez sur échappe. Vous pourrez ensuite naviguer dans l'historique en utilisant les flèches. Repassez en mode non-verrouillé en appuyant sur échappe de nouveau.
- Vous pouvez maintenant coller plusieurs lignes dans le client pour envoyer plusieurs commandes d'un coup.

## Build 24

- Met à jour la documentation des fonctionnalités basiques.
- Retire les options obsolètes se basant sur une zone d'entrée qui n'existe plus.
- Quand un utilisateur appuie sur la touche de tabulation pour l'auto-complétion, le TTS prononce (et affiche) le résultat.

## Build 23

- Ajout de l'auto-complétion:
  Quand le client reçoit des messages du serveur de jeu, tous les mots contenus dans ces messages sont classés par fréquence (du plus fréquent au moins fréquent). Si vous commencez à écrire une lettre ou plusieurs, puis appuyez sur la touche de tabulation, le client cherchera à finir le mot que vous aviez commencé à écrire. Si le résultat trouvé par le client ne vous convient pas, vous pouvez appuyer de nouveau sur la touche de tabulation jusqu'à trouver le mot que vous vouliez entrer.
