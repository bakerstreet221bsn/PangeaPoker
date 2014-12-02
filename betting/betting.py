class Betting(object):

    def __init__(self, supernet):
        self.__supernet = supernet

    def bet(self, table, player, amount):
        return self.__supernet.send_bet_message(table, player, amount)