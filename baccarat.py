"""
    Author: all_in

    baccarat class implements the playing functionality of the game.
"""

import deck 

class baccarat:
    def __init__(self):
        """ Initializes dict of users in the room and a deck. """
        self.users = {}
        self.deck = deck.deck()

    def bet(self, user, betsize, beton):
        """ 
        Saves what user betted on and how much into the dict of users
        in the class.

        This allows the game room to keep track of the users and their bet.
        """
        self.users[user] = [betsize, beton]

    def bet_message(self):
        """ 
        Returns the bet message for baccarat and a list of available options 
        users can bet on.
        """
        return "Place your bets! \n" \
                    + "Bet on the banker by typing 'banker'\n" \
                    + "Bet on the player by typing 'player'\n" \
                    + "Bet on a tie by typing 'tie'\n", \
                    ['banker', 'player', 'tie']

    def getTotal(self, card1, card2):
        """
        Returns the total of two cards after converting the 10-A to its
        integer value
        """
        print card1, card2
        if card1 == 'A':
            card1 = 1
        elif card1 in set(['10','J', 'Q','K']):
            card1 = 0
        else:
            card1 = int(card1)
        if card2 == 'A':
            card2 = 1
        elif card2 in set(['10','J', 'Q','K']):
            card2 = 0
        else:
            card2 = int(card2)

        print card1, card2 

        print (card1 + card2)%10 

        return (card1 + card2)%10

    def banker_draw(self, banker_total, banker_cards):
        """
        Draws a card for the banker, calculates the new total, 
        and return the new set of cards and total.
        """
        banker_draw = self.deck.draw_card()
        banker_cards.append(banker_draw)
        return self.getTotal(banker_total, banker_draw[0]), banker_cards

    def play(self, msgs):
        """
        Plays the baccarat game. Banker and Player are dealt cards,
        with additional card delt according to the rules. 

        Winners are added to the winners list and losers to the losers list.

        Returns the list [winners, losers, result_msg]
        """
        winners = []
        losers = []

        banker_cards = [self.deck.draw_card(), self.deck.draw_card()]
        player_cards = [self.deck.draw_card(), self.deck.draw_card()]

        print "banker\n"
        banker_total = self.getTotal(banker_cards[0][0], banker_cards[1][0])
        print "player\n"
        player_total = self.getTotal(player_cards[0][0], player_cards[1][0])

        player_draw = ''

        # Player draws if total is 0-5
        if player_total < 6:
            player_draw = self.deck.draw_card()
            player_cards.append(player_draw)
            player_total = self.getTotal(player_total, player_draw[0])

        # If player stood, then banker follows players rules
        if player_draw == '':
            if banker_total < 6:
                banker_total, banker_cards = self.banker_draw(banker_total, 
                                                              banker_cards)

        # Else, banker follow rules based on player_draw
        elif banker_total <= 2:
            banker_total, banker_cards = self.banker_draw(banker_total, 
                                                          banker_cards)
        elif banker_total == 3 and player_draw != 8:
            banker_total, banker_cards = self.banker_draw(banker_total, 
                                                          banker_cards)
        elif banker_total == 4 and player_draw in range(2,8):
            banker_total, banker_cards = self.banker_draw(banker_total,
                                                          banker_cards)
        elif banker_total == 5 and player_draw in range(4,8):
            banker_total, banker_cards = self.banker_draw(banker_total,
                                                          banker_cards)
        elif banker_total == 6 and player_draw in range(6,8):
            banker_total, banker_cards = self.banker_draw(banker_total,
                                                          banker_cards)

        result = ''
        if banker_total == player_total:
            result = 'tie'
        elif banker_total > player_total:
            result = 'banker'
        else:
            result = 'player'

        for user, bet in self.users.iteritems():
            if bet[1] == result:
                if result == 'player':
                    winners.append((user, bet[0]*1))
                elif result == 'banker':
                    winners.append((user, bet[0]*1.95))
                else:
                    winners.append((user, bet[0]*8))
            else:
                losers.append((user, -bet[0]))

        result_msg = "Player hand was: "
        for card, suit in player_cards:
            result_msg += card + " " + suit + "   "
        result_msg += "\nBanker hand was: "
        for card,suit in banker_cards:
            result_msg += card + " " + suit + "   "
        result_msg += "\n Winner is " + result + "!" + "\n"

        return [winners, losers, result_msg]

    def reset(self):
        """ Resets the room to be empty."""
        self.users = {}


    