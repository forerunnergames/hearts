import unittest
import hearts
from unittest.mock import patch

test_player_names = ["Test Player 1", "Test Player 2", "Test Player 3", "Test Player 4"]
test_card_suits = ["Suit A", "Suit B", "Suit C"]
test_card_ranks = ["Rank 1", "Rank 2", "Rank 3", "Rank 4"]
test_starting_card_rank = "Rank 1"
test_starting_card_suit = "Suit A"
test_starting_card = hearts.Card(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
test_card_count = len(test_card_suits) * len(test_card_ranks)


class TestCard(unittest.TestCase):
    def test_init_1(self):
        card_rank = "Rank 2"
        card_suit = "Suit A"
        c1 = hearts.Card(card_rank, card_suit, test_card_suits, test_card_ranks)
        self.assertEqual(card_rank, c1.rank)
        self.assertEqual(card_suit, c1.suit)

    def test_init_2(self):
        with self.assertRaises(ValueError):
            hearts.Card("Rank " + str(len(test_card_ranks) + 1), "Suit A", test_card_suits, test_card_ranks)

    def test_init_3(self):
        with self.assertRaises(ValueError):
            hearts.Card("Rank 1", "Suit F", test_card_suits, test_card_ranks)

    def test_eq(self):
        c1 = hearts.Card("Rank 2", "Suit A", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 3", "Suit A", test_card_suits, test_card_ranks)
        c3 = hearts.Card("Rank 2", "Suit B", test_card_suits, test_card_ranks)
        c4 = hearts.Card("Rank 2", "Suit A", test_card_suits, test_card_ranks)
        self.assertTrue(c1 != c2)
        self.assertTrue(c2 != c1)
        self.assertFalse(c1 == c2)
        self.assertFalse(c2 == c1)
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(c2, c1)
        self.assertTrue(c1 != c3)
        self.assertTrue(c3 != c1)
        self.assertFalse(c1 == c3)
        self.assertFalse(c3 == c1)
        self.assertNotEqual(c1, c3)
        self.assertNotEqual(c3, c1)
        self.assertTrue(c1 == c4)
        self.assertTrue(c4 == c1)
        self.assertFalse(c1 != c4)
        self.assertFalse(c4 != c1)
        self.assertEqual(c1, c4)
        self.assertEqual(c4, c1)


class TestDeck(unittest.TestCase):
    def test_init_1(self):
        deck = hearts.Deck(test_card_suits, test_card_ranks)
        self.assertEqual(test_card_count, len(deck.cards))

    def test_init_2(self):
        deck = hearts.Deck(test_card_suits, test_card_ranks)
        [self.assertTrue(sum(c.rank == r and c.suit == s for c in deck.cards) == 1) for s in test_card_suits for r in
         test_card_ranks]

    def test_count(self):
        deck = hearts.Deck(test_card_suits, test_card_ranks)
        self.assertEqual(test_card_count, deck.count())

    def test_shuffle(self):
        deck = hearts.Deck(test_card_suits, test_card_ranks)
        deck.shuffle()
        self.assertEqual(test_card_count, deck.count())
        [self.assertTrue(sum(c.rank == r and c.suit == s for c in deck.cards) == 1) for s in test_card_suits for r in
         test_card_ranks]

    def test_take(self):
        deck = hearts.Deck(test_card_suits, test_card_ranks)
        c1 = deck.take()
        self.assertEqual(test_card_count - 1, deck.count())
        self.assertTrue(sum(c1.rank == c2.rank and c1.suit == c2.suit for c2 in deck.cards) == 0)


class TestTrick(unittest.TestCase):
    def test_init_1(self):
        trick_index = 1
        trick = hearts.Trick(trick_index, test_starting_card, test_card_suits, test_card_ranks)
        self.assertEqual(trick_index, trick.index)
        self.assertEqual({}, trick.cards_by_player)

    def test_add(self):
        t = hearts.Trick(1, test_starting_card, test_card_suits, test_card_ranks)
        p = hearts.Player("Test Player 1")
        c = hearts.Card("Rank 2", "Suit A", test_card_suits, test_card_ranks)
        t.add(p, c)
        self.assertEqual(c, t.cards_by_player[(1, p)])

    def test_first_1(self):
        t = hearts.Trick(1, test_starting_card, test_card_suits, test_card_ranks)
        self.assertTrue(t.first())

    def test_first_2(self):
        t = hearts.Trick(2, test_starting_card, test_card_suits, test_card_ranks)
        self.assertFalse(t.first())

    def test_empty_1(self):
        t = hearts.Trick(1, test_starting_card, test_card_suits, test_card_ranks)
        self.assertTrue(t.empty())

    def test_empty_2(self):
        t = hearts.Trick(1, test_starting_card, test_card_suits, test_card_ranks)
        p = hearts.Player("Test Player 1")
        c = hearts.Card("Rank 2", "Suit B", test_card_suits, test_card_ranks)
        t.add(p, c)
        self.assertFalse(t.empty())


class TestPlayer(unittest.TestCase):
    def test_init(self):
        player_name = "Test Player 1"
        p = hearts.Player(player_name)
        self.assertEqual(player_name, p.name)

    def test_init_2(self):
        p = hearts.Player("Test Player 1")
        self.assertTrue(len(p.cards) == 0)

    def test_receive_card(self):
        p = hearts.Player("Test Player 1")
        c1 = hearts.Card("Rank 1", "Suit A", test_card_suits, test_card_ranks)
        p.receive_card(c1)
        self.assertTrue(len(p.cards) == 1)
        self.assertTrue(sum(c1.rank == c2.rank and c1.suit == c2.suit for c2 in p.cards) == 1)
        self.assertTrue(sum(c1.rank != c2.rank or c1.suit != c2.suit for c2 in p.cards) == 0)

    def test_receive_cards(self):
        p = hearts.Player("Test Player 1")
        c1 = hearts.Card("Rank 1", "Suit C", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 1", "Suit B", test_card_suits, test_card_ranks)
        p.receive_cards([c1, c2])
        self.assertTrue(len(p.cards) == 2)
        self.assertTrue(sum(c1.rank == c3.rank and c1.suit == c3.suit for c3 in p.cards) == 1)
        self.assertTrue(sum(c2.rank == c3.rank and c2.suit == c3.suit for c3 in p.cards) == 1)
        self.assertTrue(sum(
            (c1.rank != c3.rank or c1.suit != c3.suit) and (c2.rank != c3.rank or c2.suit != c3.suit) for c3 in
            p.cards) == 0)

    def test_has_card(self):
        p = hearts.Player("Test Player 1")
        c1 = hearts.Card("Rank 4", "Suit A", test_card_suits, test_card_ranks)
        p.receive_card(c1)
        self.assertTrue(p.has_card(c1))

    def test_has_cards(self):
        p = hearts.Player("Test Player 1")
        c1 = hearts.Card("Rank 4", "Suit A", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 3", "Suit B", test_card_suits, test_card_ranks)
        p.receive_cards([c1, c2])
        self.assertTrue(p.has_all_cards_of([c1, c2]))

    def test_has_card_with(self):
        p = hearts.Player("Test Player 1")
        rank = "Rank 3"
        suit = "Suit A"
        c1 = hearts.Card(rank, suit, test_card_suits, test_card_ranks)
        p.receive_card(c1)
        self.assertTrue(p.has_card_with(rank, suit))

    def test_has_card_with_2(self):
        p = hearts.Player("Test Player 1")
        rank = "Rank 3"
        suit = "Suit A"
        c1 = hearts.Card(rank, suit, test_card_suits, test_card_ranks)
        p.receive_card(c1)
        self.assertFalse(p.has_card_with("Rank 4", "Suit A"))

    def test_has_card_with_suit(self):
        p = hearts.Player("Test Player 1")
        suit = "Suit C"
        c1 = hearts.Card("Rank 1", suit, test_card_suits, test_card_ranks)
        p.receive_card(c1)
        self.assertTrue(p.has_card_with_suit(suit))

    def test_get_card_with(self):
        p = hearts.Player("Test Player 1")
        rank = "Rank 4"
        suit = "Suit B"
        c1 = hearts.Card(rank, suit, test_card_suits, test_card_ranks)
        p.receive_card(c1)
        self.assertTrue(p.get_card_with(rank, suit) == c1)

    def test_pass_three_cards_to_1(self):
        p1 = hearts.Player("Test Player 1")
        p2 = hearts.Player("Test Player 2")
        c1 = hearts.Card("Rank 2", "Suit A", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 1", "Suit B", test_card_suits, test_card_ranks)
        c3 = hearts.Card("Rank 4", "Suit A", test_card_suits, test_card_ranks)
        p1.receive_cards([c1, c2, c3])
        p1.pass_three_cards_to(p2)
        self.assertTrue(p2.has_all_cards_of([c1, c2, c3]))
        self.assertFalse(p1.has_all_cards_of([c1, c2, c3]))

    # TODO Implement
    def test_should_shoot_the_moon(self):
        p1 = hearts.Player("Test Player 1")
        self.assertFalse(p1.should_shoot_the_moon())

    def test_eq(self):
        p1 = hearts.Player("Test Player 1")
        p2 = hearts.Player("Test Player 2")
        p3 = hearts.Player("Test Player 1")
        self.assertTrue(p1 == p3)
        self.assertTrue(p3 == p1)
        self.assertFalse(p1 == p2)
        self.assertFalse(p2 == p1)
        self.assertEqual(p1, p3)
        self.assertEqual(p3, p1)
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p2, p3)

    @patch.object(hearts.Trick, 'first', return_value=True)
    @patch.object(hearts.Trick, 'empty', return_value=True)
    def test_play_1(self, _, __):
        p1 = hearts.Player("Test Player 1")
        c1 = hearts.Card("Rank 2", "Suit C", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 4", "Suit C", test_card_suits, test_card_ranks)
        c3 = hearts.Card("Rank 3", "Suit A", test_card_suits, test_card_ranks)
        p1.receive_cards([c1, c2, c3, test_starting_card])
        trick = p1.play(hearts.Trick(0, test_starting_card, test_card_suits, test_card_ranks))
        self.assertFalse(p1.has_card(test_starting_card))
        self.assertEqual(1, len(trick.cards_by_player))
        self.assertEqual(test_starting_card, trick.cards_by_player[(1, p1)])

    @patch.object(hearts.Trick, 'first', return_value=False)
    @patch.object(hearts.Trick, 'empty', return_value=True)
    def test_play_2(self, _, __):
        p1 = hearts.Player("Test Player 1")
        c1 = hearts.Card("Rank 2", "Suit C", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 4", "Suit C", test_card_suits, test_card_ranks)
        c3 = hearts.Card("Rank 3", "Suit A", test_card_suits, test_card_ranks)
        p1.receive_cards([c1, c2, c3])
        trick = p1.play(hearts.Trick(0, test_starting_card, test_card_suits, test_card_ranks))
        self.assertFalse(p1.has_card(trick.cards_by_player[(1, p1)]))
        self.assertEqual(1, len(trick.cards_by_player))


class TestUtils(unittest.TestCase):

    def test_sort_player_cards(self):
        p1 = hearts.Player("Test Player 1")
        p2 = hearts.Player("Test Player 2")
        c1 = hearts.Card("Rank 2", "Suit C", test_card_suits, test_card_ranks)
        c2 = hearts.Card("Rank 4", "Suit C", test_card_suits, test_card_ranks)
        c3 = hearts.Card("Rank 3", "Suit A", test_card_suits, test_card_ranks)
        c4 = hearts.Card("Rank 1", "Suit B", test_card_suits, test_card_ranks)
        c5 = hearts.Card("Rank 1", "Suit C", test_card_suits, test_card_ranks)
        c6 = hearts.Card("Rank 2", "Suit A", test_card_suits, test_card_ranks)
        p1.receive_cards([c1, c2, c3])
        p2.receive_cards([c4, c5, c6])
        players = [p1, p2]
        hearts.Utils.sort_player_cards(players, test_card_suits, test_card_ranks)
        self.assertEqual([c3, c1, c2], p1.cards)
        self.assertEqual([c6, c4, c5], p2.cards)

    def test_card_sort_by_suit(self):
        c = hearts.Card("Rank 2", "Suit C", test_card_suits, test_card_ranks)
        self.assertEqual(2, hearts.Utils.card_sort_by_suit(c, test_card_suits))

    def test_card_sort_by_rank(self):
        c = hearts.Card("Rank 1", "Suit B", test_card_suits, test_card_ranks)
        self.assertEqual(0, hearts.Utils.card_sort_by_rank(c, test_card_ranks))

    def test_ordinal_1(self):
        self.assertEqual("1st", hearts.Utils.ordinal(1))
        self.assertEqual("2nd", hearts.Utils.ordinal(2))
        self.assertEqual("3rd", hearts.Utils.ordinal(3))
        self.assertEqual("4th", hearts.Utils.ordinal(4))

    def test_ordinal_2(self):
        with self.assertRaises(ValueError):
            hearts.Utils.ordinal(5)

    def test_ordinal_3(self):
        with self.assertRaises(ValueError):
            hearts.Utils.ordinal(0)

    def test_ordinal_4(self):
        with self.assertRaises(ValueError):
            hearts.Utils.ordinal(-1)


class TestGame(unittest.TestCase):

    def test_init(self):
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        self.assertEqual(test_starting_card, g.starting_card)
        self.assertEqual([], g.players)
        self.assertEqual(test_card_suits, g.card_suits)
        self.assertEqual(test_card_ranks, g.card_ranks)
        self.assertEqual(hearts.Deck(test_card_suits, test_card_ranks), g.deck)

    def test_add_players(self):
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        g.add_players(test_player_names)
        self.assertEqual(len(test_player_names), len(g.players))
        self.assertTrue(all(p.name in test_player_names for p in g.players))

    def test_shuffle_players(self):
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        g.add_players(test_player_names)
        g.shuffle_players()
        self.assertEqual(len(test_player_names), len(g.players))
        self.assertTrue(all(p.name in test_player_names for p in g.players))

    def test_player_count(self):
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        g.add_players(test_player_names)
        self.assertEqual(len(test_player_names), g.player_count())

    def test_shuffle_deck(self):
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        g.shuffle_deck()
        self.assertEqual(test_card_count, g.deck.count())
        self.assertTrue(all(c.rank in test_card_ranks and c.suit in test_card_suits for c in g.deck.cards))

    def test_deal_cards(self):
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        g.add_players(test_player_names)
        g.deal_cards()
        self.assertEqual(0, g.deck.count())
        self.assertTrue(
            all(c.rank in test_card_ranks and c.suit in test_card_suits for p in g.players for c in p.cards))
        cards_per_player = test_card_count / len(test_player_names)
        self.assertTrue(all(cards_per_player == len(p.cards) for p in g.players))

    def test_pass_three_cards(self):
        hand = 1
        g = hearts.Game(test_starting_card_rank, test_starting_card_suit, test_card_suits, test_card_ranks)
        g.add_players(test_player_names)
        g.deal_cards()
        card_passes = g.pass_three_cards(hand)
        player_count = len(test_player_names)
        cards_per_player = test_card_count / player_count
        self.assertTrue(all(cards_per_player == len(p.cards) for p in g.players))
        self.assertEqual(4, len([k for k in card_passes.keys() for p in g.players if p == k[0]]))
        self.assertEqual(4, len([k for k in card_passes.keys() for p in g.players if p == k[1]]))
        self.assertTrue(all(len(cards) == 3 for (_, __), cards in card_passes.items()))
        self.assertEqual(player_count, len(card_passes))
