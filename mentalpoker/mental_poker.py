
class MentalPoker(object):

    def __init__(self):
        pass

    def shuffle(self, cards):
        return cards

    def show_cards(self, cards):

        unmasked_cards = []

        for card in cards:
            unmasked = tmcg.unmask_card(card)
            unmasked_cards.append(unmasked)

        return unmasked_cards