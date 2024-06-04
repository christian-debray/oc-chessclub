# oc-chessclub
Openclassrooms python course - project 4 - Chess club desktop app

General file structure

  - app
    - models/
      - baseclasses/
         - repository.abc.py
         - datastorage.abc.py
      - player.py
      - tournament.py
      - turn.py
      - match.py
    - controllers/
      - player_manager.py
      - tournament_setup_manager.py
      - tournament_manager.py
      - turn_manager.py
      - match_manager.py
    - views/
      - player_manager_views/
        - player_manager_menu_view.py
        - register_player_view.py
        - find_player_view.py
        - edit_player_data_view.py
        - list_players_view.py
      - tournament_setup_views/
        - tournament_setup_menu_view.py
        - new_tournament_view.py
        - load_tournament_view.py
        - setup_tournament_view.py
        - start_tournament_view.py
    - helpers/
    - adapters/
       - json_data_storage/
          - json_data_storage.py
          - player_json.py
          - tournament_json.py          
    - config
    - main.py
  - tests/

  - data/
    - players.json
    - tournaments/
       - 2024-01-23_petaouchnok.tournament.json
       - 2024-01-23_trifouillie-les-oies.tournament.json


