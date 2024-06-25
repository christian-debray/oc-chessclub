# oc-chessclub
Openclassrooms python course - project 4 - Chess club desktop app

Manage Chess tournaments
========================

## Abstract
This app helps managing a small player database and tournaments organized
by the local chess club.

A Chess tournament is played at a location, at a given date.
Participants are registered with their national player ID.
A tournament is divided in rounds where each participant plays exactly 1 match against
another participant. Players are paired basing on their current score.

## Available Features

 The chess club manager is a desktop app running in text mode on a console, and should work fine on linux,
 windows and MacOS.

  - Maintain a small player database:
    - register new players
    - edit player data
    - list players
  - Manage tournament data:
    - create new tournament
    - edit tournament general infos
  - Run tournaments:
    - register players
    - start next round
    - record match results
    - round overview
  - Display reports
  - Store data locally

## Installing the app

You will need Python 3.8+ to run this app: https://www.python.org/downloads/
(also see pyenv if you need multiple versions of Python on the same system: https://github.com/pyenv/pyenv)

After installing Python, first clone this repo:


first clone the repository:
```
    git clone https://github.com/christian-debray/oc-chessclub.git
```

then create a pyhton virtual environment:
```
  cd chessclub-app
  python -m venv .env
  source ./env/bin/activate
```

finally, install all dependencies:
```
  pip install -r requirements.txt
```

## Running the app

After having started the python virtual environment, simply invoke the main script:

```
  python main.py
```

The menus displayed by the app will guide you through the different features and processes.

## Data files

The app stores its data in the `data/` folder, in JSON format.

  - **Player details** are stored separately in the `data/players.json` file.
  - **Tournaments** are stored in the `data/tournament` folder:
     - Each tournament has its own JSON file in the tournament folder.
     - A special `tournament_index.json` stores an index and metadata of all tournaments.

## General implementation notes

### PEP8 compliance
The python code of this app is compliant with PEP8 Style guide.

Compliance with the PEP8 style guide is enforced using Flake8: https://flake8.pycqa.org/en/latest/.
The latest report for this app can be found in the `flake8_rapport/` folder.

 ### Design Patterns

 The app's architecture follows these patterns:

  - ***MVC* for the general architecture**

    We separate business logic from presentation and behaviour concerns:
      - Classes in the `views` modules specialize in the presentation and behaviour layer (UI)
      - Classes in the `models` modules specialize in business logic and data storage
      - Classes in the `controllers` modules control the application flow, expose model data
      to the views and update data models basing on user interaction reported by the views.

  - ***Command Pattern* for the integration of views and controllers**:

    Views communicate with the app by issuing command objects pre-built by the controllers.
    The commands are received by the main controller, who dispatches the execution of the next
    task to the appropriate controller.

  - ***Entity-Repository Pattern* for the datamodel**:

     Business objects (Player, Tournament, Round, Match, ...) are agnostic of any data storage mechanisms.
     Data consistency and persitence is enforced by Repository objects.

### General file structure
```
  + (app root dir)
  |
  +-- main.py (main script to launch the app)
  +--+ data/ (data folder)
  |  |
  |  +-- players.json
  |  +-- tournaments/ (tournament json files, including tournament index)
  |
  +--+ app/ (the app python files)
  |  |
  |  +-- adapters/ (adapters used to store JSON data)
  |  +-- commands/ (command pattern toolkit)
  |  +-- controllers/ (controller classes)
  |  +-- helpers/ (various helpers: validation, ui toolkits, string formatters, ...)
  |  +-- models/ (data model classes)
  |  +-- views (UI classes)
  |   
  +-- flake8_rapport/
  |
  +-- tests/
```