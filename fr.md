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
<!-- Note : Cette page est [disponible en anglais](index.html). -->

**Didel CLI** est une application en ligne de commande pour interagir avec la
plateforme [DidEL][didel-web]. L’outil est loin d’être complet, et ce n’est pas
son but. Il permet pour le moment :

* d’accéder à son profil personnel
* d’obtenir des informations sur un cours à partir de son code
* de s’inscrire/se désinscrire d’un cours
* de lister les devoirs associés à un cours

Il n’a rien d’officiel, n’est pas développé ni supporté par l’Université.

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

## Comment ça marche ?

DidEL n’a pas d’[API][api-wp], donc l’outil ne fait que reproduire le
comportement d’un utilisateur normal : il se connecte et parcours les pages,
récupérant les informations depuis celles-ci.

### Cours

Obtenir des informations sur un cours : `didel courses:show <code>`

    $ didel courses:show IO2
    Internet & Outils (Christophe Prieur)

    Visitez très régulièrement le blog du cours : didiode.fr.

### Profil

Obtenir des informations sur votre profil DidEL : `didel profile:show`

    $ didel profile:show
    Alice Tappart (atappa42)
    Student number: 2190041X
    Email: alice.tappart@etu.univ-paris-diderot.fr

## Contribuer

Le code-source complet de **DidEL CLI** est disponible sur [GitHub][gh]. Vous
pouvez le récupérer en local via `git` :

    $ git clone https://github.com/bfontaine/didelcli.git
    $ cd didelcli

L’outil est entièrement écrit en Python.

[gh]: https://github.com/bfontaine/didelcli
[api-wp]: https://fr.wikipedia.org/wiki/Interface_de_programmation
[didel-web]: http://didel.script.univ-paris-diderot.fr
