---
title: "Télécharger et installer CocoMUD"
---

# Télécharger et installer CocoMUD

CocoMUD est prêt à l'emplois sous Windows, dans une version portable. Vous n'avez pas besoin de l'installer sur votre système, juste le télécharger sous forme d'archive (voir les liens ci-dessous), l'extraire et lancer **cocomud.exe**. La procédure est détaillée dans les sections suivantes de ce document.

## Télécharger CocoMUD

CocoMUD pour Windows est publié sur [la page des versions de CocoMUD](https://github.com/vincent-lg/cocomud/releases) (en anglais). Téléchargez le fichier nommé **CocoMUD.zip** dans le build le plus récent.

Si vous utilisez un autre système d'exploitation que Windows, vous pourriez vouloir [installer CocoMUD depuis les sources](https://github.com/vincent-lg/cocomud). CocoMUD fonctionne sous Linux et Mac OS, bien qu'il n'existe pas encore de version prête à l'emplois pour ces systèmes.

Si vous accédez à ces informations depuis une version déjà installée de CocoMUD, les liens donnés ci-dessus pourraient ne pas être à jour. Il vous est recommendé de vous rendre sur [la documentation en ligne](https://cocomud.org/fr/download.html) pour avoir les liens de téléchargement à jour.

## Installer CocoMUD

Une fois l'archive téléchargée, vous devez l'extraire dans un dossier. CocoMUD n'a pas besoin de s'installer pour fonctionner, il tourne en version portable (vous pourriez même le mettre sur une clé USB pour l'emporter avec vous si vous voulez).

1. Commencez par extraire l'archive **CocoMUD.zip** dans le dossier que vous voulez. CocoMUD ne pourra pas se lancer directement depuis l'archive, et même si il y arrive, il ne pourra pas écrire dedans.
1. Dans le dossier où vous avez extrait l'archive, vous devriez trouver un dossier **CocoMUD**. Ouvrez-le.
1. Dedans se trouve un fichier **cocomud.exe** (parmi beaucoup d'autres). Pour lancer CocoMUD, il suffit de lancer ce fichier **cocomud.exe**. CocoMUD devrait s'ouvrir sur son écran de connexion.
1. Si vous appréciez CocoMUD, n'hésitez pas à faire un raccourci menant au fichier **cocomud.exe**, cela vous simplifiera la vie.

Pour apprendre à utiliser CocoMUD, vous devriez lire [un aperçu des fonctionnalités basiques de CocoMUDD](basics.md). Ce petit tutoriel est fait pour apprendre à utiliser les fonctionnalités les plus simples de CocoMUD. D'autres documents sont disponibles pour apprendre à utiliser les fonctionnalités plus avancées du client.

## Mettre à jour CocoMUD

CocoMUD possède un updater intégré pour se mettre à jour automatiquement. Cet updater se lancera avec CocoMUD. Si il trouve une version plus récente de CocoMUD sur le site officiel, il vous proposera de l'installer. Si vous répondez "oui", CocoMUD sera refermé pendant que l'updater télécharge et installe la nouvelle version. Si tout va bien, CocoMUD s'ouvrira tout seul après la mise à jour.

Vous pouvez vérifier à tout moment si il y a des mises à jour. Dans le menu **Aide** de CocoMUD, choisissez **Vérifier les mises à jour disponibles**. La réponse pourrait se faire attendre quelques secondes, car CocoMUD regarde les mises à jour sur le site officiel. CocoMUD va vérifier si il existe des mises à jour et vous dire si il y en a. Si c'est le cas, il vous proposera de mettre à jour.

La mise à jour automatique pourrait ne pas s'exécuter correctement dans certains cas. Le pare-feu de Windows, Windows Defender, un logiciel antivirus ou un logiciel conçu pour protéger votre système pourraient élever des objections à la mise à jour automatique de CocoMUD. 

Si la mise à jour rencontre des erreurs, CocoMUD pourrait devenir corrompu (c'est-à-dire que CocoMUD pourrait ne pas se lancer, ou bien générer de nombreuses erreurs au lancement). Si cela se produit, il y a plusieurs moyens de résoudre le problème :

1. Forcer la mise à jour : dans certains cas, CocoMUD essaye de se mettre à jour, mais certains fichiers ou dossiers ne sont pas modifiés. Un logiciel qui essaye de protéger votre système pourrait augmenter les risques qu'une telle situation se produise. Le pare-feu Windows et Windows defender ne semblent pas causer ce problème. Si vous cliquez sur **cocomud.exe** et que rien ne se passe, ou bien que CocoMUD se lance en générant de nmbreuses erreurs, vous pouvez forcer la mise à jour de CocoMUD. Pour ce faire, exécutez le fichier **dbg_updater.exe** dans votre dossier CocoMUD. **dbg** indique **debug**, et cette version de l'updater se veut aussi légère que possible. Même si il semble que votre version de CocoMUD soit à jour, le **dbg_updater** va télécharger et installer la version la plus récente depuis le site officiel, en gardant votre configuration. Ce fichier devrait ouvrir une console avec une barre de progression, mais vous n'avez pas besoin de vous en inquiéter : laissez-le travailler, télécharger et installer CocoMUD. Si tout va bien, CocoMUD sera ouvert automatiquement dans sa nouvelle version. Si cela ne change rien, essayez de lancer **dbg_updater** une nouvelle fois avant de passer à l'étape 2.
1. Mise à jour manuelle : parfois, CocoMUD est tellement corrompu que **dbg_updater** ne peut même pas se lancer, ou bien qu'il n'arrive pas à faire grand chose. Si cela se produit, vous devrez réinstaller CocoMUD manuellement. Téléchargez la version la plus récente de CocoMUD (voir les liens ci-dessus). Décompressez l'archve dans un nouveau dossier. Pour conserver votre configuration, rendez-vous dans votre ancien dossier. Copiez les dossiers **settings** et **worlds** et placez-les dans votre nouveau dossier **CocoMUD**. Vous devriez ensuite pouvoir lancer CocoMUD normalement.

Si vous rencontrez toujours des erreurs, n'hésitez pas à contacter l'équipe des développeurs en [créant un rapport de bug](https://github.com/vincent-lg/cocomud/issues).

Nous vous souhaitons l'expérience de jeu la plus agréable possible avec CocoMUD !
