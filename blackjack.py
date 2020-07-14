from random import randint
import pickle
import os
from copy import deepcopy
import argparse

# command line argument parsing
parser = argparse.ArgumentParser(description="simulate games of blackjack")
parser.add_argument('outfile')
parser.add_argument('--hands', help="write each step of the game (hand) as its own row",
                    action="store_true")
parser.add_argument('--games', help="number of games to simulate; default 1000",
                    default=1000)
parser.add_argument('--gen_probs', help="generate probabilities of final dealer values given observed cards",
                    action="store_true")
args = parser.parse_args()



# globals setup
starting_deck = ['A']*4+['2']*4+['3']*4+['4']*4+['5']*4+['6']*4+['7']*4+['8']*4\
                    +['9']*4+['10']*16#+['J']*4+['Q']*4+['K']*4

starting_deck_vals = {'A':4,'2':4,'3':4,'4':4,'5':4,'6':4,'7':4,'8':4,'9':4,'10':16}

deck = deepcopy(starting_deck)

if os.path.isfile(args.outfile):
    pickle_in = open(args.outfile,"rb")
    cached_dealer_probs = pickle.load(pickle_in)
    pickle_in.close()
else:
    cached_dealer_probs = {}



def deal(deck, deck_vals):
    # draw a card for the dealer
    house_card_1 = draw(deck, deck_vals)
    house_card_2 = draw(deck, deck_vals)
    # draw two cards for the player
    player_card_1 = draw(deck, deck_vals)
    player_card_2 = draw(deck, deck_vals)
    return [house_card_1, house_card_2], [player_card_1, player_card_2]

def draw(deck, deck_vals):
    # get a random card
    i = randint(0,len(deck)-1)
    card = deck[i]
    # remove that card from the deck
    deck.pop(i)

    return card

def reshuffle():
    return deepcopy(starting_deck)

def value(hand):
    val = 0
    aces = 0
    soft = False
    for card in hand:
        if card is 'A':
            val += 1
            aces += 1
        elif card is 'J' or card is 'Q' or card is 'K': val += 10
        else: val += int(card)
    if aces > 0 and val <= 11:
        val += 10
        soft = True
    return val, soft

def random_policy(house_cards, player_cards):
    return bool(randint(0,1))

def dealer_probs(dealer_cards, deck_vals):
    dealer_value, dealer_soft = value(dealer_cards)
    # check cache
    global cached_dealer_probs
    if (dealer_value, dealer_soft, tuple(deck_vals.items())) in cached_dealer_probs:
        print("cache hit!")
        return cached_dealer_probs[(dealer_value, dealer_soft, tuple(deck_vals.items()))]

    # calculate probabilities based on all possible draws given remaining deck
    probs = {17:0, 18:0, 19:0, 20:0, 21:0, 22:0}
    deck_size = sum(deck_vals.values())
    # simulate each possible draw value
    for val in deck_vals.keys():
        new_dealer_cards = deepcopy(dealer_cards)
        new_dealer_cards.append(val)
        new_value, new_soft = value(new_dealer_cards)
        #print(new_dealer_cards)
        # if the new card causes the dealer to stop drawing,
        # then update the probability of the new value
        if new_value > 21:
            probs[22] += deck_vals[val] / deck_size
        elif new_value in probs:
            probs[new_value] += deck_vals[val] / deck_size
        # if the dealer will continue to draw cards,
        # then recur to find all possible ending values based on subsequent draws
        # update probabilities for those ending values accordingly
        else:
            # skip calculating too many low probability hands
            if len(dealer_cards) > 6: continue
            # remove the card drawn from the remaining deck
            new_deck_vals = deepcopy(deck_vals)
            new_deck_vals[val] -= 1
            if new_deck_vals[val] == 0: del new_deck_vals[val]
            # recur with set of dealer cards and new remaining deck
            probs_given_val = dealer_probs(new_dealer_cards, new_deck_vals)
            # update probabilities
            for key in probs:
                probs[key] += probs_given_val[key] * (deck_vals[val] / deck_size)
    # add to cache
    if not (dealer_value, dealer_soft, tuple(deck_vals.items())) in cached_dealer_probs:
        cached_dealer_probs[(dealer_value, dealer_soft, tuple(deck_vals.items()))] = probs
    return probs

#dealer_probs(['10'], starting_deck_vals)

def game(policy, deck, deck_vals):
    house_cards, player_cards = deal(deck, deck_vals)
    #print("\nhouse hand:")
    #print(house_cards)
    #print("\nplayer hand:")
    #print(player_cards)
    i=1
    algo_view = []
    # blackjack wins automatically
    if value(player_cards) is 21:
        algo_view.append([value([house_cards[0]]),value(player_cards[:-1]),1,value(player_cards[i]),1, int('A' in player_cards[:-1])])
        return algo_view
    # otherwise hit or stay according to given strategy
    #print("\nplayer drawing:")
    algo_view.append([value([house_cards[0]]),value(player_cards[:-1]),1,value(player_cards[i]),0, int('A' in player_cards[:-1])])
    while policy(house_cards, player_cards):
        i+=1
        player_cards.append(draw(deck, deck_vals))
        #print(player_cards)
        if value(player_cards) is 21: # blackjack
            algo_view.append([value([house_cards[0]]),value(player_cards[:-1]),1,value(player_cards[i]),1, int('A' in player_cards[:-1])])
            return algo_view
        elif value(player_cards) > 21:# player bust, house wins
            algo_view.append([value([house_cards[0]]),value(player_cards[:-1]),1,value(player_cards[i]),-1, int('A' in player_cards[:-1])])
            return algo_view
        else:
            algo_view.append([value([house_cards[0]]),value(player_cards[:-1]),1,value(player_cards[i]),0, int('A' in player_cards[:-1])])
    # draw for dealer
    #print("\nhouse drawing:")
    while value(house_cards) < 17 or value(house_cards) is 17 and 'A' in house_cards: # draw on soft 17
        house_cards.append(draw(deck, deck_vals))
        #print(house_cards)
        if value(house_cards) > 21:
            algo_view.append([value([house_cards[0]]),value(player_cards),0,0,1, int('A' in player_cards[:-1])])
            return algo_view # house bust, player wins
    if value(house_cards) > value(player_cards):
        algo_view.append([value([house_cards[0]]),value(player_cards),0,0,-1, int('A' in player_cards[:-1])])
        return algo_view
    else:
        algo_view.append([value([house_cards[0]]),value(player_cards),0,0,1, int('A' in player_cards[:-1])])
        return algo_view # push goes to player




if __name__ == '__main__':
    # [dealer_value, player_value, decision, added_value, result]
    #print(game(random_policy, deck))
    if args.gen_probs:
        for card in starting_deck_vals.keys():
            print(dealer_probs([card],starting_deck_vals))
            pickle_out = open(args.outfile,"wb")
            pickle.dump(cached_dealer_probs, pickle_out)
            pickle_out.close()
            for card in starting_deck_vals.keys():
                deck1 = deepcopy(starting_deck_vals)
                deck1[card] -= 1
                print(dealer_probs([card],starting_deck_vals))
                pickle_out = open(args.outfile,"wb")
                pickle.dump(cached_dealer_probs, pickle_out)
                pickle_out.close()
                for card in deck1.keys():
                    deck2 = deepcopy(deck1)
                    deck2[card] -= 1
                    for card in deck2.keys():
                        deck3 = deepcopy(deck2)
                        deck3[card] -= 1
                        for card in deck3.keys():
                            deck4 = deepcopy(deck3)
                            deck4[card] -= 1
                            if starting_deck_vals[card] < 1:
                                del deck4[card]
                            for card in deck4.keys():
                                deck5 = deepcopy(deck4)
                                deck5[card] -= 1
                                if starting_deck_vals[card] < 1:
                                    del deck5[card]
        exit()
    game_data = [game(random_policy,reshuffle(),deepcopy(starting_deck_vals)) for _ in range(int(args.games))]
    import csv
    with open(args.outfile, 'w') as myfile:
        wr = csv.writer(myfile,delimiter='\t')
        if args.hands:
            for game in game_data:
                for hand in game:
                    wr.writerow(hand)
        else:
            for game in game_data:
                wr.writerow([val for hand in game for val in hand])
