# Save this as game.py
import random

color = ('RED', 'GREEN', 'BLUE', 'YELLOW')
rank = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw2', 'Draw4', 'Wild')
ctype = {'0': 'number', '1': 'number', '2': 'number', '3': 'number', '4': 'number', '5': 'number',
         '6': 'number', '7': 'number', '8': 'number', '9': 'number', 'Skip': 'action', 'Reverse': 'action',
         'Draw2': 'action', 'Draw4': 'action_nocolor', 'Wild': 'action_nocolor'}


class Card:
    """
    Represents a single card in the UNO deck.

    Attributes:
        color (str): The color of the card (e.g., RED, GREEN, etc.).
        rank (str): The rank of the card (e.g., 0, 1, Skip, etc.).
        cardtype (str): The type of the card (number, action, or action_nocolor).
    """

    def __init__(self, color, rank):
        self.rank = rank
        if ctype[rank] == 'number':
            self.color = color
            self.cardtype = 'number'
        elif ctype[rank] == 'action':
            self.color = color
            self.cardtype = 'action'
        else:
            self.color = None
            self.cardtype = 'action_nocolor'

    def __str__(self):
        if self.color == None:
            return self.rank
        else:
            return self.color + " " + self.rank


class Deck:
    """
    Represents the deck of cards used in the game.

    Attributes:
        deck (list): The list of Card objects in the deck.
    """

    def __init__(self):
        self.deck = []
        self.build()

    def __str__(self):
        deck_comp = ''
        for card in self.deck:
            deck_comp += '\n' + card.__str__()
        return 'The deck has ' + deck_comp

    def build(self):
        """
        Builds the deck by adding cards of all colors and ranks.
        """
        self.deck = []
        for clr in color:
            for ran in rank:
                # Add two of each card, except for action_nocolor
                if ctype[ran] != 'action_nocolor':
                    self.deck.append(Card(clr, ran))
                    self.deck.append(Card(clr, ran))
                else:
                    # Add four of each action_nocolor card (Wild, Draw4)
                    # Note: Original UNO has 4 of each, not 1 per color
                    pass

        # Add the 4 Wild and 4 Draw4 cards
        for _ in range(4):
            self.deck.append(Card(None, 'Wild'))
            self.deck.append(Card(None, 'Draw4'))

    def shuffle(self):
        """
        Shuffles the deck to randomize the order of cards.
        """
        random.shuffle(self.deck)

    def deal(self):
        """
        Deals a card from the deck. Rebuilds and reshuffles if the deck is empty.

        Returns:
            Card: The card dealt from the deck.
        """
        if len(self.deck) == 0:
            print("Deck is empty! Rebuilding and shuffling...")
            self.build()
            self.shuffle()
            # A real game would use the discard pile, but this is simpler
        return self.deck.pop()


class Hand:
    """
    Represents a player's hand of cards.

    Attributes:
        cards (list): The list of Card objects in the player's hand.
    """

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """
        Adds a card to the player's hand.

        Args:
            card (Card): The card to add.
        """
        self.cards.append(card)

    def remove_card(self, place):
        """
        Removes a card from the player's hand.

        Args:
            place (int): The 1-indexed position of the card to remove.

        Returns:
            Card: The removed card.
        """
        # 'place' is 1-indexed for user-friendliness
        return self.cards.pop(place - 1)

    def get_card(self, place):
        """
        Retrieves a card from the player's hand without removing it.

        Args:
            place (int): The 1-indexed position of the card to retrieve.

        Returns:
            Card: The retrieved card.
        """
        # 'place' is 1-indexed
        return self.cards[place - 1]

    def no_of_cards(self):
        """
        Returns the number of cards in the player's hand.

        Returns:
            int: The number of cards in the hand.
        """
        return len(self.cards)

    def get_hand_str(self):
        """
        Returns a string representation of the player's hand.

        Returns:
            str: The string representation of the hand.
        """
        hand_str = ""
        for i in range(len(self.cards)):
            hand_str += f' {i + 1}.{str(self.cards[i])}\n'
        return hand_str


def single_card_check(top_card, card):
    """
    Checks if a card can be played on top of the current top card.

    Args:
        top_card (Card): The current top card on the pile.
        card (Card): The card to check.

    Returns:
        bool: True if the card can be played, False otherwise.
    """
    return card.color == top_card.color or top_card.rank == card.rank or card.cardtype == 'action_nocolor'