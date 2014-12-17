from messaging import PangeaMessage

UI_MESSAGE_TYPE_PLACE_REQ = "ui_place_bet_req"


class UiModule(object):

    def __init__(self):
        pass


class UiMessages(object):

    # Requests
    @staticmethod
    def place_bet_req(table_id, player_id, amount):
        return PangeaMessage(message_type="", table_id=table_id, player_id=player_id, amount=amount)

    @staticmethod
    def dealer_shuffle_cards_req(table_id, dealer_id, players, cards):
        return PangeaMessage(message_type="", table_id=table_id, dealer_id=dealer_id,
                             players=players, cards=cards)

    @staticmethod
    def shuffle_cards_req(table_id, player_id, cards):
        return PangeaMessage(message_type="", table_id=table_id, player_id=player_id, cards=cards)

    # Responses
    @staticmethod
    def dealer_shuffle_cards_resp(table_id, dealer_id, cards):
        return PangeaMessage(message_type="", table_id=table_id, dealer_id=dealer_id,
                             shuffled_cards=cards)

    @staticmethod
    def shuffle_cards_resp(table_id, dealer_id, player_id, shuffled_cards):
        return PangeaMessage(message_type="", table_id=table_id, dealer_id=dealer_id,
                             player_id=player_id, shuffled_cards=shuffled_cards)