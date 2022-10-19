import random
from itertools import cycle
from flask import Flask, render_template

clubs_suit = "\033[38;2;0;128;0m\N{Black Club Suit}\033[0m"
diamonds_suit = "\033[38;2;255;0;255m\N{Black Diamond Suit}\033[0m"
spades_suit = "\033[38;2;128;128;255m\N{Black Spade Suit}\033[0m"
hearts_suit = "\033[38;2;255;0;0m\N{Black Heart Suit}\033[0m"
card_suits = [clubs_suit, diamonds_suit, spades_suit, hearts_suit]
card_ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
starting_card_rank = "2"
starting_card_suit = clubs_suit
player_names = ["Bob", "Alice", "John", "Sandy"]
ordinals = ["1st", "2nd", "3rd", "4th"]
max_points = 100


class Card:

    def __init__(self, rank, suit, _card_suits, _card_ranks):
        if not (suit in _card_suits):
            raise ValueError(f"Invalid card suit {suit}")
        if not (rank in _card_ranks):
            raise ValueError(f"Invalid card rank: {rank}")
        self.rank = rank
        self.suit = suit
        self.suit_symbol_html = \
            "&#9830;" if self.suit == diamonds_suit else \
                "&#9824;" if self.suit == spades_suit else \
                    "&#9827;" if self.suit == clubs_suit else \
                        "&#9829;" if self.suit == hearts_suit else ""
        self.suit_color_html = \
            "#00ff00" if self.rank == "2" and self.suit == clubs_suit else \
                "#ffff00" if self.rank == "Q" and self.suit == spades_suit else \
                    "#ff00ff" if self.suit == diamonds_suit else \
                        "#8080ff" if self.suit == spades_suit else \
                            "#006500" if self.suit == clubs_suit else \
                                "#ff0000" if self.suit == hearts_suit else "#000000"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return NotImplemented

    def encode(self):
        return {'rank': self.rank, 'suit_html': self.suit_symbol_html, 'suit_color': self.suit_color_html}

    def __str__(self):
        return "[Q\033[38;2;255;255;0m\N{Black Spade Suit}\033[0m]" if self.rank == "Q" and self.suit == spades_suit \
            else ("[2\033[38;2;0;255;0m\N{Black Club Suit}\033[0m]" if (self.rank == "2" and self.suit == clubs_suit)
                  else f"[{self.rank}{self.suit}]")


class Deck:

    def __init__(self, _card_suits, _card_ranks):
        self.cards = []
        for s in _card_suits:
            for r in _card_ranks:
                self.cards.append(Card(r, s, _card_suits, _card_ranks))

    def count(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def take(self):
        return self.cards.pop()

    def encode(self):
        return [card.encode() for card in self.cards]

    def __eq__(self, other):
        if isinstance(other, Deck):
            return self.cards == other.cards
        return NotImplemented

    def __str__(self):
        return '\n'.join([str(c) for c in self.cards])


class Trick:
    def __init__(self, index, starting_card, _card_suits, _card_ranks):
        self.index = index
        self.starting_card = starting_card
        self.card_suits = _card_suits
        self.card_ranks = _card_ranks
        self.cards_by_player = {}
        self.suit = ""
        self.card_index = 0

    def add(self, player, card):
        if self.empty():
            self.suit = card.suit
        self.card_index += 1
        self.cards_by_player[(self.card_index, player)] = card
        return self

    def first(self):
        return self.index == 1

    def empty(self):
        return len(self.cards_by_player) == 0

    def point_cards(self):
        return sorted([card for card in self.cards_by_player.values() if
                       card.suit == hearts_suit or (card.rank == "Q" and card.suit == spades_suit)], key=lambda x: (
            Utils.card_sort_by_suit(x, self.card_suits, reverse=True),
            Utils.card_sort_by_rank(x, self.card_ranks)), reverse=True)

    def points(self):
        return sum(1 if x.suit == hearts_suit else 13 for x in self.point_cards())

    def suit(self):
        return self.suit

    def winning_card(self):
        return next((c for c in self.cards_by_player.values() if c.suit == self.suit and c.rank == self.card_ranks[
            max(list(
                self.card_ranks.index(x.rank) for x in self.cards_by_player.values() if x.suit == self.suit))]),
                    None)

    def winning_player(self):
        winning_card = self.winning_card()
        return next((player for (i, player), card in self.cards_by_player.items() if card == winning_card), None)

    def card_action_word(self, card):
        index = next(i for (i, _), c in self.cards_by_player.items() if c == card)
        queen = card.rank == "Q" and card.suit == spades_suit
        leading = index == 1
        if leading and queen:
            return " LED THE QUEEN!"
        elif queen:
            return " DROPPED THE QUEEN!"
        elif leading:
            return " led."
        elif card.suit != self.suit and card.suit != hearts_suit:
            return " sloughed."
        elif card.suit != self.suit and card.suit == hearts_suit:
            return " painted."
        elif card.suit == self.suit:
            return " followed."

    def __str__(self):
        return f"Trick {self.index}:\n\n{chr(10).join([str(card) + ' ' + player.name + self.card_action_word(card) for (i, player), card in self.cards_by_player.items()])}\nTrick winner: {next((player.name for (i, player), card in self.cards_by_player.items() if card == self.winning_card()), None)}{' (+' + str(self.points()) + ')' if self.points() > 0 else ''} {' '.join(list(map(str, self.point_cards())))}"


class Player:

    def __init__(self, name):
        self.name = name
        self.cards = []
        self.hand_points = {}

    def receive_card(self, card):
        self.cards.append(card)

    def receive_cards(self, cards):
        [self.receive_card(card) for card in cards]

    def has_cards(self):
        return len(self.cards) > 0

    def has_card(self, card):
        return self.has_card_with(card.rank, card.suit)

    def has_all_cards_of(self, cards):
        return all(self.has_card(card) for card in cards)

    def has_any_cards_of(self, cards):
        return any(self.has_card(card) for card in cards)

    def has_card_with(self, card_rank, card_suit):
        return any(c.rank == card_rank and c.suit == card_suit for c in self.cards)

    def has_card_with_suit(self, card_suit):
        return any(c.suit == card_suit for c in self.cards)

    def get_card_with(self, card_rank, card_suit):
        return next(c for c in self.cards if c.rank == card_rank and c.suit == card_suit)

    def pass_three_cards_to(self, player):
        passed_cards = []
        [passed_cards.append(self.cards.pop(random.randint(0, len(self.cards) - 1))) for _ in range(3)]
        player.receive_cards(passed_cards)
        return passed_cards

    def sort_cards(self, _card_suits, _card_ranks):
        self.cards = sorted(self.cards,
                            key=lambda x: (
                                Utils.card_sort_by_suit(x, _card_suits), Utils.card_sort_by_rank(x, _card_ranks)))

    def add_points(self, points, hand):
        self.hand_points[hand] = points

    def points(self, hand):
        return self.hand_points[hand]

    def total_points(self):
        return sum(self.hand_points.values())

    # TODO Implement
    @staticmethod
    def should_shoot_the_moon():
        return False

    def play(self, trick):
        if trick.first() and trick.empty():
            index = self.cards.index(trick.starting_card)
            card = self.cards[index]
            self.cards.remove(card)
            trick.add(self, card)
            return trick
        card = next((c for c in random.sample(self.cards, len(self.cards)) if c.suit == trick.suit),
                    self.cards[random.randint(0, len(self.cards) - 1)])
        self.cards.remove(card)
        trick.add(self, card)
        return trick

        # Follow suit if possible
        # if (self.has_card_with_suit(trick.suit))

        # One possible path:
        # If not possible to follow trick suit, check if trick is full
        # If trick is full, check if trick has points
        # If trick has points, check if player is shooting-the-moon
        # If player is shooting-the-moon, check if player has non-trump / non-point suit
        # If player has non-trump / non-point suit, play lowest rank (keep higher ranked cards for shooting-the-moon)
        # If player is not shooting-the-moon, check if first trick
        # If is first trick, check if player has non-point suit
        # If player has non-point suit, play highest ranked card
        # If player does not have non-point suit, paint the trick with highest ranked point card
        # If is not first trick, paint the trick with highest ranked point card

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self):
        return self.name + ': ' + ' '.join([str(c) for c in self.cards])


class Utils:
    @staticmethod
    def sort_player_cards(players, _card_suits, _card_ranks):
        [p.sort_cards(_card_suits, _card_ranks) for p in players]

    @staticmethod
    def card_sort_by_suit(card, _card_suits, reverse=False):
        return _card_suits.index(card.suit) if not reverse else len(_card_suits) - _card_suits.index(card.suit) - 1

    @staticmethod
    def card_sort_by_rank(card, _card_ranks, reverse=False):
        return _card_ranks.index(card.rank) if not reverse else len(_card_ranks) - _card_ranks.index(card.rank) - 1

    @staticmethod
    def cycle_players_to(_first_player, rotation):
        while (player := next(rotation)) != _first_player: pass
        return player

    @staticmethod
    def get_point_cards_for(tricks, _card_suits, _card_ranks):
        return sorted([card for trick in tricks for card in trick.point_cards()], key=lambda x: (
            Utils.card_sort_by_suit(x, _card_suits), Utils.card_sort_by_rank(x, _card_ranks)))

    @staticmethod
    def get_points_for(tricks, shot_the_moon):
        points = sum(trick.points() for trick in tricks)
        return points if not shot_the_moon else points + 26 if points < 26 else 0

    @staticmethod
    def shot_the_moon(tricks_by_player):
        return any(sum(trick.points() for trick in tricks) == 26 for player, tricks in tricks_by_player.items())

    @staticmethod
    def get_hand_winner(players, hand, shot_the_moon):
        return next((p for p in players if p.points(hand) == 0), None) if shot_the_moon else \
            min(players, key=lambda x: x.points(hand))

    @staticmethod
    def get_game_winner(players):
        return min(players, key=lambda x: x.total_points())

    @staticmethod
    def get_players_sorted_by_total_points(players):
        return sorted(players, key=lambda x: x.total_points())

    @staticmethod
    def get_three_card_pass_type_description(hand):
        pass_type = hand % 4
        if pass_type == 1:
            return "Left / Clockwise"
        elif pass_type == 2:
            return "Right / Counter-Clockwise"
        elif pass_type == 3:
            return "Across"
        else:
            return "None / Keep"

    @staticmethod
    def ordinal(n):
        if n not in range(1, 5):
            raise ValueError(f"Ordinal is out of range: {n}")
        return ordinals[n - 1]


class Game:

    def __init__(self, _starting_card_rank, _starting_card_suit, _card_suits, _card_ranks):
        self.starting_card = Card(_starting_card_rank, _starting_card_suit, _card_suits, _card_ranks)
        self.players = []
        self.card_suits = _card_suits
        self.card_ranks = _card_ranks
        self.deck = Deck(_card_suits, _card_ranks)
        self.hand = 0
        self.card_passes = {}
        self.player_rotation = cycle(self.players)

    def add_players(self, _player_names):
        [self.players.append(Player(p)) for p in _player_names]

    def shuffle_players(self):
        random.shuffle(self.players)

    def player_count(self):
        return len(self.players)

    def shuffle_deck(self):
        self.deck.shuffle()

    def deal_cards(self):
        [self.players[i % len(self.players)].receive_card(self.deck.take()) for i in range(self.deck.count())]

    def pass_three_cards(self, hand):
        passes = {}
        pass_type = hand % 4
        if pass_type == 0: return passes
        player_rotation = cycle(reversed(self.players) if pass_type == 2 else self.players)
        p1 = self.players[0]
        for i in range(self.player_count()):
            while next(player_rotation) != p1: pass
            p2 = next(player_rotation)
            p3 = next(player_rotation) if pass_type == 3 else p2
            passes[(p1, p3)] = p1.pass_three_cards_to(p3)
            p1 = p2
        return passes

    def get_first_player(self):
        return next(player for player in self.players if player.has_card(self.starting_card))

    def set_player_rotation(self):
        self.player_rotation = cycle(self.players)

    def get_next_player(self):
        return next(self.player_rotation)

    def start(self):
        self.hand = 1
        self.add_players(player_names)
        self.shuffle_players()
        print("\nWelcome to Hearts!")
        while not any(p.total_points() >= max_points for p in self.players):
            print(f"\nHand {self.hand}")
            self.shuffle_deck()
            print("\nInitial deal:\n")
            self.deal_cards()
            Utils.sort_player_cards(self.players, self.card_suits, self.card_ranks)
            [print(f"{p}") for p in self.players]
            print(f"\n3 Card Pass ({Utils.get_three_card_pass_type_description(self.hand)}):\n")
            self.card_passes = self.pass_three_cards(self.hand)
            Utils.sort_player_cards(self.players, self.card_suits, self.card_ranks)
            [print(f"{p1.name} => {p2.name}: {' '.join(map(str, cards))}") for (p1, p2), cards in
             self.card_passes.items()]
            if len(self.card_passes) > 0: print()
            self.set_player_rotation()
            first_player = Utils.cycle_players_to(self.get_first_player(), self.player_rotation)
            print(f"{first_player.name} has the {self.starting_card}.\n\nOrder of play (Clockwise):\n")
            i = 1
            print(f"{Utils.ordinal(i)} - {first_player.name}")
            while (player := next(self.player_rotation)) != first_player:
                i += 1
                print(f"{Utils.ordinal(i)} - {player.name}")
            trick_index = 1
            tricks_by_player = {}
            while (Utils.cycle_players_to(first_player, self.player_rotation)).has_cards():
                trick = first_player.play(Trick(trick_index, self.starting_card, self.card_suits, self.card_ranks))
                while (player := next(self.player_rotation)) != first_player: trick = player.play(trick)
                print(f"\n{trick}")
                first_player = trick.winning_player()
                tricks_by_player[first_player] = tricks_by_player.get(first_player, []) + [trick]
                trick_index += 1
            shot_the_moon = Utils.shot_the_moon(tricks_by_player)
            [p.add_points(Utils.get_points_for(tricks_by_player.get(p, ''), shot_the_moon), self.hand) for p in
             self.players]
            print(f"\nHand {self.hand} Score:")
            hand_winner = Utils.get_hand_winner(self.players, self.hand, shot_the_moon)
            print(f"\n{hand_winner.name} shot the moon!!!\n" if shot_the_moon else "")
            [print(
                f"{Utils.ordinal(i)} - {player.name}: {player.total_points()} (+{player.points(self.hand)}) {' '.join(list(map(str, Utils.get_point_cards_for(tricks_by_player.get(player, ''), card_suits, card_ranks))))}")
                for
                i, player in enumerate(Utils.get_players_sorted_by_total_points(self.players), start=1)]
            self.hand += 1
            self.deck = Deck(self.card_suits, self.card_ranks)
        print(f"\n{Utils.get_game_winner(self.players).name} won the game!")


app = Flask(__name__, template_folder="../templates")


@app.route('/')
def cards():
    game = Game(starting_card_rank, starting_card_suit, card_suits, card_ranks)
    game.hand = 1
    # game.add_players(player_names)
    # game.shuffle_players()
    # game.shuffle_deck()
    # game.deal_cards()
    # Utils.sort_player_cards(game.players, card_suits, card_ranks)
    ordinals = ["1st", "2nd", "3rd", "4th"]
    max_points = 100
    # deck_json = json.dumps(deck, default=lambda x: x.encode())
    # return deck_json
    return render_template('index.html', game=game, player_names=player_names, utils=Utils)


if __name__ == "__main__":
    app.run(debug=True)

Game(starting_card_rank, starting_card_suit, card_suits, card_ranks).start()
