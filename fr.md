---
layout: default
title: Didel CLI par bfontaine
# poor man's i18n
project_title: Didel CLI
project_subtitle: DidEL en ligne de commande
view_on_gh: Voir sur GitHub
download: télécharger en
generated_with: Généré par
using: avec
this_prj_by: Ce projet de
can_be_found_on: est hébergé sur
---
**Didel CLI** est une application en ligne de commande pour interagir avec la
plateforme [DidEL][didel-web]. L’outil est loin d’être complet, et ce n’est pas
son but. Il permet pour le moment :

* d’accéder à son profil personnel
* d’obtenir des informations sur un cours à partir de son code
* de s’inscrire/se désinscrire d’un cours

Il n’a rien d’officiel, n’est pas développé ni supporté par l’Université. Il
est pour l’instant complètement expérimental.

Note : Cette page est [disponible en anglais](index.html).

## Installation

Il est nécessaire d’avoir `pip` ainsi que Python 2 ou 3.

    $ pip install didelcli

Vérifiez qu’il est correctement installé :

    $ didel -h

## Utilisation

Commencez par configurer vos identifiants :

    $ didel login:init <votre nom d'utilisateur>

L’outil va vous demander votre mot de passe, entrez-le (il ne s’affichera pas).
Il est nécessaire pour que l’outil se connecte à DidEL avec votre compte. Il
est stocké de façon chiffrée en local et ne quittera pas votre ordinateur (en
dehors de la connexion à DidEL). Cette opération n’est nécessaire que la
première fois.

### Cours

Obtenir des informations sur un cours : `didel courses:show <code>`

    $ didel courses:show IO2
    Internet & Outils (Christophe Prieur)

    Visitez très régulièrement le blog du cours : didiode.fr.

S’inscrire à un cours : `didel courses:enroll <code> [<clef>]`

    $ didel courses:enroll M2MOX
    # Certains cours nécessitent une clef pour s’inscrire
    $ didel courses:enroll PSYN9 topsecret

Se désinscrire d’un cours : `didel courses:unenroll <code>`

    $ didel courses:unenroll PSYN9

Lister les devoirs à rendre d’un cours : `didel assignments:list <code>`

    $ didel assignments:list M2T2INFOEMB
    1) Rendu intermédiaire du TP N°1 (Vendredi 03 Octobre 2014 à 14:00)
    2) TP N°1 (Jeudi 16 Octobre 2014 à 23:59)

Obtenir des informations sur un devoir en particulier :
`didel assignments:show <code> <indice>`

    $ didel assignments:show M2T2INFOEMB 1
    Rendu intermédiaire du TP N°1
    Vendredi 03 Octobre 2014 à 11:14 -> Vendredi 03 Octobre 2014 à 14:00
    Type: Fichier (fichier requis, description du fichier facultative)
    Visibility: Visible uniquement par le(s) gestionnaire(s) et le(s) propriétaire(s)
    Work Type: Individuel

Soumettre un devoir sous forme de fichier :
`didel assignments:submit <code> <indice> <titre> <fichier>`

    $ didel assignments:submit M2T2INFOEMB 1 "TP 1 WIP" mon/tp1.tgz

### Documents

Depuis la version `0.1.2` il est possible de télécharger tous les documents des
cours que l’on suit en une seul ligne de commande. La première fois, utilisez
`didel pull:save <chemin>` :

    $ didel pull:save mondossier

L’outil va récupérer la liste de vos matières et télécharger tous les documents
associés dans des sous-répertoires de `mondossier`. Vous pourrez ensuite
utiliser tout simplement `didel pull` pour mettre à jour ce répertoire.
Didelcli se souvient de l’emplacement du répertoire, il n’est pas nécessaire de
le re-spécifier. De plus, il vérifie la date des fichiers téléchargés et ne
re-télécharge pas un fichier qui n’a pas été mis à jour.

Cette fonctionnalité permettant de récupérer les documents de Didel en local a
été ajoutée par [@tsalmon][ts].

[ts]: https://github.com/tsalmon

### Profil

Obtenir des informations sur votre profil DidEL : `didel profile:show`

    $ didel profile:show
    Alice Tappart (atappa42)

    Student number: 2190041X
    Email: alice.tappart@demo.univ-paris-diderot.fr

## Module Python

L’outil `didel` en ligne de commande n’est qu’une interface pour le module
Python du même nom, qui permet de faire toutes les opérations décrites
ci-dessus via un programme Python. Par exemple :

    >>> from didel.student import Student
    >>> s = Student("toto42", password="topsecret")
    >>> io2 = s.get_course("io2")
    >>> io2.title
    Internet & Outils
    >>> io2.enroll()
    True

## Comment ça marche ?

DidEL n’a pas d’[API][api-wp], donc l’outil ne fait que reproduire le
comportement d’un utilisateur normal : il se connecte et parcours les pages,
récupérant les informations depuis celles-ci.

## Contribuer

Le code-source complet de **DidEL CLI** est disponible sur [GitHub][gh]. Vous
pouvez le récupérer en local via `git` :

    $ git clone https://github.com/bfontaine/didelcli.git
    $ cd didelcli

L’outil est entièrement écrit en Python.

[gh]: https://github.com/bfontaine/didelcli
[api-wp]: https://fr.wikipedia.org/wiki/Interface_de_programmation
[didel-web]: http://didel.script.univ-paris-diderot.fr
