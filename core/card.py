
def create_deck():
    cards = []

    for i in range(52):
        card = Card()
        cards.append(card)

    return card

class Card(object):

    def __init__(self):
        pass