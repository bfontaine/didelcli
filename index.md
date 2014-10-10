---
layout: default
title: Didel CLI by bfontaine
# poor man's i18n
project_title: Didel CLI
project_subtitle: DidEL in the command-line
view_on_gh: View on GitHub
download: download
generated_with: Generated with
using: using
this_prj_by: This project by
can_be_found_on: can be found on
---

**Didel CLI** is a command-line application to interact with Paris Diderot
University's online courses system, [DidEL][didel-web]. It allows you to :

* get your user profile
* get a course's infos
* (un)enroll in a course

This page is [available in French](fr.html).

## Install

You’ll need `pip` and Python 2 or 3.

    $ pip install didelcli

Check if it's installed:

    $ didel -h

## Usage

    $ didel <subcommand> <args...>

Use `didel -h` for more details.

[didel-web]: http://didel.script.univ-paris-diderot.fr
