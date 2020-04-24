# Packages
import numpy as np
import os
from shutil import copyfile
import sys

# Card definitions by module
SETS = {
    "NAMES": {
        "BASE_SET": "Base",
        "HIDDEN_SIGNS": "Hidden Signs",
        "SECRETS_AND_LIES": "Secrets and Lies",
        "HIDDEN_MOTIVES": "Hidden Motives",
    },
    "BASE_SET": {
        "character_cards": [str(card) for card in range(1, 19)],
        "location_cards": [str(card) for card in range(19, 37)],
        "object_cards": [str(card) for card in range(37, 55)],
        "vision_cards": [str(card) for card in range(1, 85)],
    },
    "HIDDEN_SIGNS": {
        "character_cards": ["HS" + str(card) for card in range(1, 7)],
        "location_cards": ["HS" + str(card) for card in range(7, 13)],
        "object_cards": ["HS" + str(card) for card in range(13, 19)],
        "vision_cards": ["HS" + str(card) for card in range(1, 43)],
    },
    "SECRETS_AND_LIES": {
        "character_cards": ["SL" + str(card) for card in range(1, 7)],
        "location_cards": ["SL" + str(card) for card in range(7, 13)],
        "object_cards": ["SL" + str(card) for card in range(13, 19)],
        "story_cards": ["SL" + str(card) for card in range(19, 37)],
        "vision_cards": ["SL" + str(card) for card in range(1, 43)],
    },
    "HIDDEN_MOTIVES": {
        "motive_cards": [
            "Hearth and Home",
            "Honor",
            "Love",
            "Lunacy",
            "Marriage",
            "Sex",
            "Wealth",
        ]
    },
}

# Set-up Rules
SETUP = {
    "PLAYERS": [str(number) for number in range(2, 8)],
    "DIFFICULTY": {
        "easy": {"2": 4, "3": 5, "4": 5, "5": 6, "6": 6, "7": 7,},
        "medium": {"2": 5, "3": 6, "4": 6, "5": 7, "6": 8, "7": 8,},
        "hard": {"2": 6, "3": 7, "4": 7, "5": 8, "6": 8, "7": 9,},
    },
    "CLARVOYANCY": {"2": 0, "3": 0, "4": 4, "5": 4, "6": 6, "7": 6,},
    "VISION_CARD_TOTAL": {"2": 7, "3": 7, "4": 7, "5": 7, "6": 7, "7": 7,},
}


class Settings:
    exit_queues = ["exit", "quit", "q", "-1", "continue"]

    def __init__(self, sets, setup):
        self.name = None
        self.number_of_players = None
        self.difficulty = None
        self.selected_sets = None
        self.number_setup_cards = None
        self.number_ghost_cards = None
        self.sets = sets
        self.setup = setup
        self.get_settings()

    def get_settings(self):
        while self.name is None:
            self.name = input("Please provide a name for this game. ")

        while self.number_of_players not in self.setup["PLAYERS"]:
            self.number_of_players = input(
                "How many players? (2 to 7 possible players) "
            )

        while self.difficulty not in self.setup["DIFFICULTY"]:
            self.difficulty = input(
                "What difficulty would you like to play? (easy, medium, or hard) "
            )

        selection, selected = 0, []
        prompt = [
            "[" + str(number) + "] " + list(SETS["NAMES"].items())[number][1]
            for number in range(len(SETS["NAMES"]))
        ]
        while selection not in self.exit_queues:
            print(
                "Current Selection: ",
                ", ".join([str(number) for number in selected]),
                "\n",
            )
            print(
                "Select sets to add for play. Enter 'continue' or 'exit' to continue "
            )
            selection = str(input("\n".join(prompt) + "\n"))
            if (
                selection in [str(number) for number in range(len(self.sets["NAMES"]))]
                and selection not in selected
            ):
                selected += selection
            elif selection.lower() == "r":
                selected = []
        self.selected_sets = [
            list(self.sets["NAMES"].keys())[int(key)] for key in selected
        ]
        self.number_setup_cards = self.setup["DIFFICULTY"][self.difficulty][
            self.number_of_players
        ]
        self.number_ghost_cards = self.setup["VISION_CARD_TOTAL"][
            self.number_of_players
        ]

    def show_settings(self):
        print("Number of Players: {}".format(self.number_of_players))
        print("Difficulty : {}".format(self.difficulty))
        print("Sets Included: {}".format(self.selected_sets))
        print("Number of Displayed Cards: {}".format(self.number_setup_cards))
        print("Total Ghost Cards in Hand: {}".format(self.number_ghost_cards))


class CardPool:
    def __init__(
        self, sets, settings, card_type, cards=None,
    ):
        self.sets = sets
        self.settings = settings
        self.card_type = card_type
        if cards is not None:
            self.cards = cards
        else:
            self.cards = []
        self.generate_pool()

    def generate_pool(self):
        try:
            for set in self.settings.selected_sets:
                self.cards += self.sets[set][self.card_type]
        except:
            print("{} of type {} failed to generate.".format(self, self.card_type))


class Hand(CardPool):
    def __init__(self, card_pool, name=None, cards=None, limit=0):
        self.card_pool = card_pool
        self.name = name
        self.cards = cards if cards is not None else []
        self.limit = limit
        self.draw_hand()

    def draw_card(self):
        if len(self.card_pool.cards) == 0:
            self.card_pool.generate_pool()
        else:
            card = np.random.choice(self.card_pool.cards, replace=False)
            self.card_pool.cards.pop(self.card_pool.cards.index(card))
            self.cards.append(card)

    def draw_hand(self):
        while len(self.cards) < self.limit:
            self.draw_card()

    def discard_card(self, card):
        self.cards.pop(self.cards.index(card))

    def discard_hand(self):
        while len(self.cards) > 0:
            self.discard_card(self.cards[0])

    def show_hand(self):
        print("{} : {}".format(self.name, self.cards))

    def use_raven(self):
        self.discard_hand()
        self.draw_hand()


class Game:
    def __init__(
        self, sets, setup, settings, card_pools=None, selected_cards=None,
    ):
        self.sets = sets
        self.setup = setup
        self.settings = settings
        if card_pools is not None:
            self.card_pools = card_pools
        else:
            self.card_pools = {
                "characters": CardPool(
                    sets=self.sets, settings=self.settings, card_type="character_cards"
                ),
                "locations": CardPool(
                    sets=self.sets, settings=self.settings, card_type="location_cards"
                ),
                "objects": CardPool(
                    sets=self.sets, settings=self.settings, card_type="object_cards"
                ),
                "visions": CardPool(
                    sets=self.sets, settings=self.settings, card_type="vision_cards"
                ),
            }
        if selected_cards is not None:
            self.selected_cards = selected_cards
        else:
            self.selected_cards = {
                "characters": Hand(
                    card_pool=self.card_pools["characters"],
                    name="Character Cards",
                    limit=self.settings.number_setup_cards,
                ),
                "locations": Hand(
                    card_pool=self.card_pools["locations"],
                    name="Location Cards",
                    limit=self.settings.number_setup_cards,
                ),
                "objects": Hand(
                    card_pool=self.card_pools["objects"],
                    name="Object Cards",
                    limit=self.settings.number_setup_cards,
                ),
                "visions": Hand(
                    card_pool=self.card_pools["visions"],
                    name="Vision Cards",
                    limit=self.settings.number_ghost_cards,
                ),
            }

    def make_game_folders(self):
        path = os.path.join(sys.path[0], self.settings.name)
        if not os.path.exists(path):
            os.mkdir(path)
        for pool in list(self.card_pools.keys()):
            path = os.path.join(
                sys.path[0], self.settings.name, self.card_pools[pool].card_type
            )
            if not os.path.exists(path):
                os.makedirs(path)

    def copy_hand(self, hand: Hand):
        for card in hand.cards:
            source = os.path.join(
                sys.path[0], "cards", hand.card_pool.card_type, card + ".jpg"
            )
            destination = os.path.join(
                sys.path[0], self.settings.name, hand.card_pool.card_type, card + ".jpg"
            )
            copyfile(source, destination)

    def copy_game_setup(self):
        for hand in list(self.selected_cards.keys()):
            self.copy_hand(self.selected_cards[hand])

    def empty_hand(self, hand: Hand):
        path = os.path.join(sys.path[0], self.settings.name, hand.card_pool.card_type)
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))

    def refresh_hand(self, hand: Hand):
        self.empty_hand(hand)
        self.copy_hand(hand)

    def setup_game(self):
        self.make_game_folders()
        self.copy_game_setup()

    def prompt(self):
        selection = 0
        while selection != -1:
            selection = input(
                """
                [1] Delete Current Hand
                [2] Restore Current Hand
                [3] Replenish Hand
                [4] Show Settings
                [q] Exit Game
                """
            )
            if selection == "1":
                self.empty_hand(self.selected_cards["visions"])
            elif selection == "2":
                self.refresh_hand(self.selected_cards["visions"])
            elif selection == "3":
                self.selected_cards["visions"].use_raven()
                self.refresh_hand(self.selected_cards["visions"])
            elif selection == "4":
                self.settings.show_settings()
            elif selection in self.settings.exit_queues:
                break


if __name__ == "__main__":
    settings = Settings(SETS, SETUP)
    game = Game(SETS, SETUP, settings)
    game.setup_game()
    game.prompt()
