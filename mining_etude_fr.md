# Etude sur la puissance de minage

Nous allons chercher a déterminer quel logiciel de minage de cryptominais est le plus efficace.<br>
Nous définirons l'efficacité du logiciel de minage en fonction de sa puissance de calcule soit le hash rate,<br>
nombre de hash effectuer sur une période donnée.<br>
<br>
Nous pouvons effectuer un test simple en démarrage différent logiciel de minage et regarde le hashrate reporté par<br>
le logiciel mais la facon de calculer ce hashrate peut varié celon le logiciel nous allons donc mettre en place une<br>
procédure sur et fonctionnelle.<br>
<br>

## La procédure de test
Afin de test les logiciels nous avons m'y en place un processus qui peut etre répéter un certains nombre<br>
de fois sans etre altéré.<br>
Pour cela le protocol suit les étapes suivante :
- Démarrer une pool ou les jobs / difficulté est prédéfini et invariable.
- Démarrer le logiciel de minage avec un parametre notre pool
- Récolter les informations recue sur notre pool
- Durée du protocol 20 minutes
Grace aux informations recue telque les shares nous pouvons en déterminé la puissance de calcule de chaque logiciel.<br>

# Mining traditionnelle

En procédent comme nous l'indique le chapitre précédent nous avons m'y en place un protocol simple :
- Une GPU nVIDIA 3060
- Une GPU Nvidia 3070
- Miner avec KAWPOW
- Utilisé notre pool fake
- Les jobs sont identique entre les test de chaque logiciel de minage

Nous avons comptabilisé le nombre de shares trouvé par chaque logiciel.<br>

|       GPU       | T-REX | PICKMINER | BZMINER | GMINER | NBMINER |
|:---------------:|:-----:|:---------:|:-------:|:------:|:-------:|
| NVIDIA 3060 RTX |  25   |    22     |   25    |   28   |   KO    |
| NVIDIA 3070 RTX |  33   |    28     |    9    |   41   |    9    |
|      Total      |  58   |    50     |   34    |   69   |    9    |

Au vue de ces résultats, nous pouvons penser ques les logiciels les plus performants sont<br>
GMINER > T-REX > Pickminer > BZMiner > NBMiner.<br>
<br>
Nous avons utilisé 2 GPUs lors de notre session de minages, l'utilsiation de deux GPUs vont donc entrainer un dispatch<br>
des nonce calculer et nous n'avons pas de garantie que tous les logiciel de minage utilise la meme régles.<br>
De ce fait si la regles de dispatch des nonces n'est pas la meme les logiciel de minage ne test pas le meme jeux de données.<br>

# Mining en Hashrate OneJob

Afin de garantir que tous les logiciels de minage calcule sur le meme jeu de données.<br>
C'est a dire qu'ils vont tous tester les meme nonces nous devons utilser qu'une seul GPU.<br>
Pour la suite du protocol nous allons utiliser ne `NVIDIA 3070 RTX`.<br>

## Nombre de share
Nous pouvons donc relancer le test et recolter le nombre de nonce `mining.submit`recue.<br>

| Software  | T-REX | PICKMINER | BZMINER | GMINER | NBMINER |
|:---------:|:-----:|:---------:|:-------:|:------:|:-------:|
|  Shares   |  29   |    29     |   10    |   28   |   24    |

Information : NBMiner a miné seulement 4minutes.<br>
<br>
Nous pouvons constater rapidement que le classement a radicalement changer ce qui nous donne a présent.<br>
(T-Rex = Pickminer) > GMiner > NBMiner > BZMiner.<br>

## Puissance de calcule
Le nombre de share n'est pas encore assez précis pour déterminer la puissance.<br>
Nous alons donc aussi récolté la date de la premiere share recue et la date de la derniere share recue ainsi que leur valeurs.<br>

|    Software     |        T-REX         |      PICKMINER       |       BZMINER        |        GMINER        |       NBMINER        |
|:---------------:|:--------------------:|:--------------------:|:--------------------:|:--------------------:|:--------------------:|
| Start Nonce Hex |  0xc797a500402b0115  |  0xc797a500402b0115  |  0xc797a5992e87dd12  |  0xc797a500402b0115  |  0xc797a500402b0115  |
| Start Nonce Dec | 14382145355526111509 | 14382145355526111509 | 14382146012360203538 | 14382145355526111509 | 14382145355526111509 |
|  End Nonce Hex  |  0xc797a506fcc12970  |  0xc797a506fcc12970  |  0xc797a59a5fa8c20d  |  0xc797a506fcc12970  |  0xc797a50561fd9a80  |
|  End Nonce Dec  | 14382145384459872624 | 14382145384459872624 | 14382146017479410189 | 14382145384459872624 | 14382145377568397952 |
|   Total Nonce   |     28933761115      |     28933761115      |      5119206651      |     28933761115      |     22042286443      |

Nous allons calculer le Hashrate effective en fonction du temps passé entre la premiere share et la derniere share.<br>
Formule pour trouver le Hashrate = `Total Nonce` / ((`elapsed minutes` * 60) + `Elapsed Second`) = H/S.<br>

| Software |  T-REX   | PICKMINER | BZMINER  |  GMINER  | SRBMINER | NBMINER  |
|:--------:|:--------:|:---------:|:--------:|:--------:|:--------:|:--------:|
|  Start   | 08:26:01 | 10:19:01  | 08:48:22 | 09:08:27 |    KO    | 09:28:41 |
|   End    | 08:44:57 | 10:37:54  | 08:51:43 | 09:27:15 |    KO    | 09:43:20 |
| Elapsed  | 00:18:58 | 00:18:55  | 00:04:05 | 00:19:42 |    KO    | 00:16:01 |
|   H/S    | 25425097 | 25492300  | 20894721 | 24478647 |    KO    | 22936822 |
|   MH/S   |  25.43   |   25.49   |  20.89   |  24.48   |    KO    |  22.94   |

Nous avons donc a présent un classement réaliste de la puissance de calcule de chaque logiciel.<br>
Le classement est donc :
- Pickminer
- T-Rex
- GMiner
- NBMiner
- BZMiner