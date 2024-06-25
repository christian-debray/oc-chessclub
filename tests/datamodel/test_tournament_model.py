import unittest
import app.models.player_model as player_model
import app.models.tournament_model as tournament_model
from datetime import date, datetime
import json
import random


class utils:
    @staticmethod
    def randdigits(n: int, min: int = 0, max: int = 9) -> str:
        """Generates a random numeric string."""
        t = ""
        for _ in range(n):
            t += str(random.randint(min, max))
        return t

    @staticmethod
    def randstring(len: int) -> str:
        """Generates a random string with ASCII capital letters."""
        return "".join([chr(random.randint(65, 90)) for _ in range(len)])

    @staticmethod
    def rand_player_id() -> str:
        """Generates a random national player ID string"""
        return utils.randstring(2) + utils.randdigits(5)

    @staticmethod
    def rand_date() -> str:
        """Generates a random date string in ISO format"""
        y = random.randint(1960, 2010)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        return f"{y}-{m:0>2}-{d:0>2}"

    @staticmethod
    def make_random_player() -> player_model.Player:
        return player_model.Player(
            national_player_id=player_model.NationalPlayerID(utils.rand_player_id()),
            name=utils.randstring(8).capitalize(),
            surname=utils.randstring(8).capitalize(),
            birthdate=date.fromisoformat(utils.rand_date()),
        )

    @staticmethod
    def make_matches() -> list[tournament_model.Match]:
        """Makes a list of matches with random players, in various situations:
        match 0 ended with a draw
        match 1 was won by player 1
        match 2 has started but not ended
        match 2 has not started
        """
        matches: list[tournament_model.Match] = [
            tournament_model.Match(
                player1=(utils.make_random_player(), 0.5),
                player2=(utils.make_random_player(), 0.5),
                start_time=datetime.fromisoformat("2024-05-02 15:24:30"),
                end_time=datetime.fromisoformat("2024-05-02 15:44:30"),
            ),
            tournament_model.Match(
                player1=(utils.make_random_player(), 1),
                player2=(utils.make_random_player(), 0),
                start_time=datetime.fromisoformat("2024-05-02 15:34:25"),
                end_time=datetime.fromisoformat("2024-05-02 15:57:12"),
            ),
            tournament_model.Match(
                player1=(utils.make_random_player(), None),
                player2=(utils.make_random_player(), None),
                start_time=datetime.fromisoformat("2024-05-02 15:41:02"),
            ),
            tournament_model.Match(
                player1=(utils.make_random_player(), None),
                player2=(utils.make_random_player(), None),
            ),
        ]
        return matches

    @staticmethod
    def make_tournament_metadata(rounds: int = 4) -> tournament_model.TournamentMetaData:
        return tournament_model.TournamentMetaData(
            tournament_id=utils.randstring(5),
            start_date=date.fromisoformat("2024-05-02"),
            end_date=None,
            location=utils.randstring(12),
            description=" ".join(
                [utils.randstring(random.randint(2, 12)) for _ in range(10)]
            ),
            data_file=utils.randstring(8) + ".json",
            round_count=rounds,
        )

    @staticmethod
    def make_tournament() -> tournament_model.Tournament:
        tournament_meta = utils.make_tournament_metadata()
        tournament = tournament_model.Tournament(tournament_meta)
        match_list = utils.make_matches()
        tournament.rounds[0] = tournament_model.Round("test Round", matches=match_list)
        for m in match_list:
            tournament.participants.append(m.player1())
            tournament.participants.append(m.player2())
        return tournament


class TestTournamentJSON(unittest.TestCase):
    """Test JSON encoding and decoding of Tournament entities"""

    def test_match_asdict(self):
        """Dump a valid match to dict without failure, and check data is consistent."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        m = tournament_model.Match(
            player1=(p1, 0.0),
            player2=(p2, 0.0),
            start_time=datetime.fromisoformat("2024-05-02 15:45:03"),
            end_time=datetime.fromisoformat("2024-05-02 16:17:54"),
        )
        match_dict = m.asdict()
        self.assertIsInstance(match_dict, dict)
        self.assertEqual(match_dict.get("start_time"), m.start_time.isoformat())
        self.assertEqual(match_dict.get("end_time"), m.end_time.isoformat())
        player_data: tuple[tuple[str, float]] = match_dict.get("players")
        self.assertIsInstance(player_data, list)
        self.assertEqual(player_data[0], [str(m.players[0][0].id()), m.players[0][1]])
        self.assertEqual(player_data[1], [str(m.players[1][0].id()), m.players[1][1]])

    def test_round_asdict(self):
        """Dump a valid Round to dict without failure, and check data is consistent."""
        match_list = utils.make_matches()
        Round = tournament_model.Round("test Round", matches=match_list)

        test_dict = Round.asdict()
        self.assertIsInstance(test_dict, dict)
        self.assertEqual(test_dict.get("name"), Round.name)
        test_dict_matches = test_dict.get("matches")
        self.assertIsInstance(test_dict_matches, list)
        match_0: dict = test_dict_matches[0]

        self.assertIsInstance(match_0, dict)
        self.assertEqual(
            match_0.get("start_time"), match_list[0].start_time.isoformat()
        )
        self.assertEqual(match_0.get("end_time"), match_list[0].end_time.isoformat())

        self.assertEqual(len(test_dict_matches), len(Round.matches))
        for m in range(len(Round.matches)):
            dict_match_m: dict = test_dict_matches[m]
            round_match_m = Round.matches[m]
            match_start_time = (
                round_match_m.start_time.isoformat()
                if round_match_m.start_time is not None
                else None
            )
            match_end_time = (
                round_match_m.end_time.isoformat()
                if round_match_m.end_time is not None
                else None
            )
            self.assertEqual(dict_match_m.get("start_time"), match_start_time)
            self.assertEqual(dict_match_m.get("end_time"), match_end_time)
            dict_match_m_players: tuple = dict_match_m.get("players")
            for p in range(len(round_match_m.players)):
                self.assertEqual(
                    dict_match_m_players[p][0], round_match_m.players[p][0].id()
                )
                self.assertEqual(dict_match_m_players[p][1], round_match_m.players[p][1])

    def test_tournament_asdict(self):
        """Export tournament data to a dict object."""
        tournament = utils.make_tournament()
        t_data = tournament.asdict()
        self.assertIsInstance(t_data, dict)
        t_metadata: dict = t_data.get("metadata")
        self.assertIsInstance(t_metadata, dict)
        self.assertEqual(t_metadata.get("location"), tournament.metadata.location)
        self.assertEqual(t_metadata.get("description"), tournament.metadata.description)
        self.assertEqual(
            t_metadata.get("start_date"),
            (
                tournament.metadata.start_date.isoformat()
                if tournament.metadata.start_date is not None
                else None
            ),
        )
        self.assertEqual(
            t_metadata.get("end_date"),
            (
                tournament.metadata.end_date.isoformat()
                if tournament.metadata.end_date is not None
                else None
            ),
        )

        self.assertEqual(len(t_data["rounds"]), len(tournament.rounds))
        for t in range(len(tournament.rounds)):
            if tournament.rounds[t] is None:
                self.assertIsNone(t_data["rounds"][t])
            else:
                self.assertDictEqual(t_data["rounds"][t], tournament.rounds[t].asdict())

    def test_tournament_metadata_json(self):
        """Tournament Metadata can be safely exported to JSON and imported from JSON."""
        tournament = utils.make_tournament()
        dump_str = json.dumps(
            tournament.metadata, cls=tournament_model.TournamentMetaDataJSONEncoder
        )
        dump_dict = json.loads(dump_str)
        self.assertDictEqual(tournament.metadata.asdict(), dump_dict)
        loaded = json.loads(
            dump_str, cls=tournament_model.TournamentMetaDataJSONDecoder
        )
        self.assertIsInstance(loaded, tournament_model.TournamentMetaData)
        self.assertEqual(tournament.metadata, loaded)


class TestMatch(unittest.TestCase):
    """Test Match"""

    def test_match_start(self):
        """Starting a match sets the startime."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(player1=(p1, 0.0), player2=(p2, 0.0))
        match.start()
        self.assertIsNotNone(match.start_time)
        self.assertIsNone(match.end_time)
        self.assertAlmostEqual(
            match.start_time.timestamp(), datetime.now().timestamp(), 3
        )

    @unittest.expectedFailure
    def test_match_start_failure(self):
        """Starting a match that has already started should fail."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(
            player1=(p1, 0.0), player2=(p2, 0.0), start_time=datetime.now()
        )
        match.start()

    def test_match_end_draw(self):
        """Ending a match with no Player ID should record a draw."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(
            player1=(p1, 0.0), player2=(p2, 0.0), start_time=datetime.now()
        )
        end_time = datetime.fromtimestamp(match.start_time.timestamp() + 1800)
        match.end(end_time=end_time)
        self.assertIsNotNone(match.end_time)
        self.assertEqual(match.scores(), ((p1, 0.5), (p2, 0.5)))

    def test_match_end_victory_1(self):
        """Ending a match with first player ID as winner should set
        scores accordingly.
        """
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(
            player1=(p1, 0.0), player2=(p2, 0.0), start_time=datetime.now()
        )
        end_time = datetime.fromtimestamp(match.start_time.timestamp() + 1800)
        match.end(end_time=end_time, winner=p1.id())
        self.assertIsNotNone(match.end_time)
        self.assertEqual(match.scores(), ((p1, 1.0), (p2, 0.0)))

    def test_match_end_victory_2(self):
        """Ending a match with second player ID as winner should set
        scores accordingly."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(
            player1=(p1, 0.0), player2=(p2, 0.0), start_time=datetime.now()
        )
        end_time = datetime.fromtimestamp(match.start_time.timestamp() + 1800)
        match.end(end_time=end_time, winner=p2.id())
        self.assertIsNotNone(match.end_time)
        self.assertEqual(match.scores(), ((p1, 0.0), (p2, 1.0)))

    @unittest.expectedFailure
    def test_match_end_fails_with_wrong_id(self):
        """Ending a match with a wrong Player ID should raise an Exception."""
        p1 = utils.make_random_player()
        p1.set_id("FR12345")
        p2 = utils.make_random_player()
        p2.set_id("FR22346")
        match = tournament_model.Match(
            player1=(p1, 0.0), player2=(p2, 0.0), start_time=datetime.now()
        )
        match.end(winner="FR76923")

    @unittest.expectedFailure
    def test_match_end_fails_with_wrong_time(self):
        """Ending a match with a date prior to start_date should raise an Exception."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(
            player1=(p1, 0.0), player2=(p2, 0.0), start_time=datetime.now()
        )
        date_before_start = datetime.fromtimestamp(match.start_time.timestamp() - 0.1)
        match.end(end_time=date_before_start)

    def test_match_player_score(self):
        """A Match object serves the correct player scores."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        match = tournament_model.Match(
            player1=(p1, 0.0),
            player2=(p2, 0.0),
            start_time=datetime.fromtimestamp(datetime.now().timestamp() - 1800),
        )
        match.end(winner=p1.id())
        self.assertEqual(match.player_score(p1.id()), 1.0)
        self.assertEqual(match.player_score(p2.id()), 0.0)
        self.assertEqual(match.scores(), ((p1, 1.0), (p2, 0.0)))


class TestTurn(unittest.TestCase):
    """Test the Round class"""

    def test_round_setup(self):
        """Setting up a Round with a list of pairs of players
        will create as many matches, and no match has started yet."""
        Round = tournament_model.Round("a Round")
        player_pairs = [
            (utils.make_random_player(), utils.make_random_player()) for _ in range(10)
        ]
        Round.setup(player_pairs)
        self.assertEqual(len(Round.matches), len(player_pairs))
        for m in range(len(Round.matches)):
            m_match = Round.matches[m]
            players = player_pairs[m]
            self.assertEqual(m_match.player1(), players[0])
            self.assertEqual(m_match.player2(), players[1])
            self.assertEqual(m_match.scores(), ((players[0], 0.0), (players[1], 0.0)))
            self.assertEqual(m_match.has_started(), False)

    def test_round_find_player_match(self):
        """Find a match in a Round where a player participates."""
        Round = tournament_model.Round("a Round")
        player_pairs = [
            (utils.make_random_player(), utils.make_random_player()) for _ in range(10)
        ]
        Round.setup(player_pairs)
        player = player_pairs[4][1]
        m = Round.find_player_match(player.id())
        self.assertIsNotNone(m)
        self.assertEqual(m, Round.matches[4])
        self.assertEqual(m.player2(), player)


class TestTournament(unittest.TestCase):
    """Test the tournament class."""

    def test_add_participant(self):
        """When adding a new participant, the player's score must equal 0
        and the tournament should not have started."""
        tournament = tournament_model.Tournament(
            metadata=utils.make_tournament_metadata()
        )
        players = [utils.make_random_player() for _ in range(10)]
        for p in players:
            tournament.add_participant(p)
            self.assertEqual(tournament.player_score(p.id()), 0.0)
        self.assertIs(tournament.has_started(), False)

    def test_player_is_registered(self):
        """When adding a participant, player_is_registered() should return True
        with the player's ID."""
        tournament = tournament_model.Tournament(
            metadata=utils.make_tournament_metadata()
        )
        player = utils.make_random_player()
        player.set_id('FR12345')
        self.assertEqual(player.id(), 'FR12345')
        tournament.add_participant(player)
        self.assertIs(tournament.player_is_registered('FR12345'), True)
        self.assertIs(tournament.player_is_registered(player.id()), True)
        self.assertIs(tournament.player_is_registered('FR 12345'), False)
        self.assertIs(tournament.player_is_registered('FR54321'), False)

    def test_start_first_round(self):
        """Starting the first Round starts the tournament and sets up matches for all pairs of players.
        None of the matches has started at this point."""
        tournament = tournament_model.Tournament(
            metadata=utils.make_tournament_metadata()
        )
        players = [utils.make_random_player() for _ in range(10)]
        check_players = {}
        for p in players:
            tournament.add_participant(p)
            check_players[p.id()] = False  # see assignement chekc below
        tournament.start_next_round()
        self.assertIs(tournament.has_started(), True)
        self.assertIsInstance(tournament.current_round(), tournament_model.Round)
        # 1 match for 2 players
        self.assertEqual(len(tournament.current_round().matches), 5)
        # check all players have been assigned once
        for m in tournament.current_round().matches:
            self.assertIs(m.has_started(), False)
            self.assertIs(check_players.get(m.player1().id()), False)
            self.assertIs(check_players.get(m.player2().id()), False)
            check_players[m.player1().id()] = True
            check_players[m.player2().id()] = True
        self.assertEqual(
            len(list(filter(lambda x: x, check_players.values()))), len(players)
        )

    def test_match_making(self):
        """When assigning players to matches, avoid repeating matches played before."""
        #
        # To perfrom this test,
        # we'll forge the first two rounds to force a situation where
        # all players have the same score and rank.
        #
        tournament = tournament_model.Tournament(
            metadata=utils.make_tournament_metadata()
        )
        player_names = [(x * 3).capitalize() for x in "ABCDEF"]
        for p in range(len(player_names)):
            tournament.add_participant(
                player_model.Player(
                    national_player_id=player_model.NationalPlayerID(f"PL{p:0>5}"),
                    surname=player_names[p],
                    name=player_names[p],
                    birthdate=date.today(),
                )
            )
        pairs = [
            (tournament.participants[p], tournament.participants[p + 1])
            for p in range(0, len(tournament.participants), 2)
        ]
        self.assertEqual(len(pairs), len(tournament.participants) / 2)
        tournament.start_next_round(player_pairs=pairs)
        for match in tournament.current_round().matches:
            match.start()
            match.end()
        tournament.update_score_board()
        expected_ranklist = [
            (tournament.participants[0].id(), 1, 0.5),
            (tournament.participants[1].id(), 1, 0.5),
            (tournament.participants[2].id(), 1, 0.5),
            (tournament.participants[3].id(), 1, 0.5),
            (tournament.participants[4].id(), 1, 0.5),
            (tournament.participants[5].id(), 1, 0.5),
        ]
        self.assertListEqual(expected_ranklist, tournament.ranking_list())

        # play the same matches, but this time player 2 wins to even the scores.
        for p1, p2 in pairs:
            self.assertEqual(tournament._can_play(p1.id(), p2.id()), 0.5)
        new_pairs = tournament._make_player_pairs()
        for p1, p2 in new_pairs:
            self.assertEqual(tournament._can_play(p1.id(), p2.id()), 1.0)
