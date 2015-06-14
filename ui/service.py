import utils.settings
from utils.errors import PangeaException, PangaeaErrorCodes
from messaging import PangeaMessage
import random
import logging
from dealer import DealerEvents, PangaeaDealerErrorCodes
from ui.client import UiClient

default_names = [
    "Anna", "Alex", "Carl", "Cathy", "John", "Jack", "Kate", "Alexander",
    "Peter", "Sebastian", "Ned", "Emily", "Shirlene", "Lisa", "Sarah"
]


class UiService(object):

    def __init__(self, dealer_client, ui_client: UiClient):
        self.logger = logging.getLogger(__name__)
        self.dealer_client = dealer_client
        self.ui_client = ui_client
        self.settings = utils.settings.Settings()

    def handle_message(self, message):
        request = PangeaMessage().from_json(message)
        self.logger.debug("handle_message, {0}".format(message))

        if request.action:
            if "join" in request.action:
                self.join_table(request.action["join"])
            if "leave" in request.action:
                self.leave_table()
            if "bet" in request.action:
                self.bet(request.action["bet"])
            if "fold" in request.action:
                self.fold()
            if "check" in request.action:
                self.check()
            if "reset" in request.action:
                self.reset()

        if request.chat:
            self.chat(request.chat)

    def join_table(self, seat_number):
        self.logger.debug("join_table, seat_number: {0}".format(seat_number))
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        stack = 10000
        response = self.dealer_client.join_table(table_id, player_id, seat_number, stack)
        utils.settings.joined_table = True

        ui_message = self.create_empty_ui_message()
        if self.process_table_data(response, ui_message):
            self.ui_client.send_message(ui_message)

    def leave_table(self):
        self.logger.debug("leave_table")
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.leave_table(table_id, player_id)
        utils.settings.joined_table = False

        ui_message = self.create_empty_ui_message()
        if self.process_table_data(response, ui_message):
            self.ui_client.send_message(ui_message)

    def table_status(self, last_check):
        self.logger.debug("table_status")

        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        # TODO: The status here needs to do a few things
        # 1) Return the list of "seats", if changed since the last check
        # 2) Return the "game" state, if changed since the last check
        # 3) Return any new "chat" messages
        # 4) Return any pending actions/events

        # The fourth will be the most tricky. With events would only the latest events should be played out.
        # The thing that might work would be to simply display any events that happened since the last check
        # (using if-modified-since) was done. There is still the problem would recording these events. Can they
        # really be stored in the database?

        try:
            response = self.dealer_client.get_table_status(table_id, player_id, last_check, log_messages=True)
        except PangeaException as ex:
            if ex.error_code == PangaeaDealerErrorCodes.NotFoundError:
                # In case someone else resets the table
                table_id = self.auto_create_table(True)
                response = self.dealer_client.get_table_status(table_id, player_id, last_check, log_messages=True)
            else:
                raise

        ui_message = self.create_empty_ui_message()

        self.process_table_data(response, ui_message)
        self.process_event_data(response, ui_message)
        self.process_chat_data(response, ui_message)

        self.ui_client.send_message(ui_message)
        self.logger.debug("table_status complete")

    def bet(self, amount):
        self.logger.debug("bet, amount: {0}".format(amount))
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.bet(table_id, player_id, amount)

    def fold(self):
        self.logger.debug("fold")
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.fold(table_id, player_id)

    def check(self):
        self.logger.debug("fold")
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.check(table_id, player_id)

    def chat(self, chat_message):
        self.logger.debug("chat: {0}".format(chat_message))
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.create_chat(table_id, player_id, chat_message)

    def reset(self):
        self.logger.debug("reset")

        self.dealer_client.delete_default_table()
        self.settings.default_table_id = None
        self.settings.temp_player_id = None
        self.table_status(None)

    def auto_create_table(self, reset=False):
        if reset:
            default_table_id = None
        else:
            default_table_id = self.settings.default_table_id

        if default_table_id is None:
            self.logger.debug("No default_table_id found in settings. Automatically getting the default table")
            response = self.dealer_client.get_default_table()
            default_table_id = response.table["id"]
            self.settings.default_table_id = default_table_id

        return default_table_id

    def auto_create_player(self):
        player_id = self.settings.temp_player_id

        if not player_id:
            self.logger.debug("No player id set, automatically creating one")
            name = random.choice(default_names)
            response = self.dealer_client.create_player(name)
            player_id = response.player["id"]
            self.settings.temp_player_id = player_id

        self.logger.debug("Current player id: {0}".format(player_id))

        return player_id

    def get_matching_seat(self, seats, seat_number):
        if seats:
            for seat in seats:
                if seat.get("seat_number", None) == seat_number:
                    return seat
        return None

    def process_table_data(self, response, ui_message):
        if not response.table:
            return False

        player_id = self.auto_create_player()

        active_seat_number = response.table.get("active_seat_number")

        pot = []
        if response.table.get("pot"):
            pot.append(response.table.get("pot", 0))
        else:
            pot.append(0)

        my_turn = 0
        player_cards = None
        if response.player_seat:
            seat_number = response.player_seat.get("seat_number")
            my_turn = 1 if seat_number == active_seat_number else 0
            player_cards = response.player_seat.get("hole_cards")

            ui_message.player = self.ui_client.create_player(
                sitting=1,
                hole_cards=player_cards,
                stack=response.player_seat.get("stack"),
                seat_number=seat_number
            )
        else:
            ui_message.player = self.ui_client.create_player(sitting=0)

        ui_message.deal = self.ui_client.create_deal(
            dealer=response.table.get("dealer_seat_number", ""),
            #hole_cards=player_cards,
            board_cards=response.table.get("board_cards", [])
        )

        ui_message.game = self.ui_client.create_game(
            game_type="No Limit Hold em<br>Blinds: 10/20",
            timer=0,
            limit=100,
            pot=pot,
            big_blind=response.table.get("big_blind"),
            to_call=response.table.get("current_bet"),
            my_turn=my_turn)

        if "seats" in response.table:
            for item in response.table["seats"]:
                self.logger.debug("Processing seat: {0}".format(item))

                seat_player_id = item.get("player_id")
                #seat_number = item.get("seat_number")

                #if seat_player_id == player_id:
                    #if seat_number is not None and seat_number == active_seat_number:
                    #    ui_message.game["myturn"] = 1
                    #else:
                    #    ui_message.game["myturn"] = 0

                #    is_player = 1
                    #ui_message.player = self.ui_client.create_player(
                    #    sitting=1,
                    #    hole_cards=item.get("hole_cards"),
                    #    stack=item.get("stack"),
                    #    seat_number=item.get("seat_number"),
                    #)

                    #ui_message.deal["holecards"] = item.get("hole_cards")
                #else:
               #     is_player = 0

                if item.get("hole_cards", None):
                    pass

                seat = self.ui_client.create_seat(
                    seat_number=item.get("seat_number"),
                    stack=item.get("stack"),
                    #player=is_player,
                    player=seat_player_id == player_id,
                    playing=1,
                    empty=0,
                    player_cards=item.get("hole_cards"),
                    bet=item.get("bet"),
                    name=item.get("username"),
                    status=item.get("status", "")
                )

                ui_message.seats.append(seat)

        return True

    def process_event_data(self, response, ui_message):
        if not response.events:
            return False

        player_id = self.auto_create_player()

        for event in response.events:
            event_name = event.get("event_name", "")
            seat_number = event.get("seat_number", "-1")
            seat = self.get_matching_seat(ui_message.seats, seat_number)

            if seat is None:
                seat = self.ui_client.create_seat(seat_number=seat_number)
            #    ui_message.seats.append(seat)

            if event_name == DealerEvents.PLAYER_JOIN_TABLE:
                seat["empty"] = 0
            elif event_name == DealerEvents.PLAYER_LEAVE_TABLE:
                seat["empty"] = 1
                if seat.get("player_id", None) == player_id:
                    ui_message.player["sitting"] = 0
            #elif event_name == DealerEvents.PLAYER_BET:
            #    seat["bet"] = event.get("bet", "0")
                #seat["action"] = "<span>Bet<br/>{0}</span>".format(seat.get("bet"))
            #elif event_name == DealerEvents.PLAYER_CHECK:
                #seat["action"] = "<span>Check</span>"
            elif event_name == DealerEvents.PLAYER_FOLD:
                ui_message.action = self.ui_client.create_return_player_cards(seat_number)
               # seat["action"] = "<span>Fold</span>"
            #elif event_name == DealerEvents.PLAYER_CALL:
            #    seat["bet"] = event.get("bet", 0)
                #seat["action"] = "<span>Call</span>"
            #elif event_name == DealerEvents.PLAYER_RAISE:
           #     seat["bet"] = event.get("bet", 0)
                #seat["action"] = "<span>Raise<br/>{0}</span>".format(seat.get("bet"))
            elif event_name == DealerEvents.HAND_COMPLETE:
                ui_message.action = self.ui_client.create_chips_to_pot()

        return True

    def process_chat_data(self, response, ui_message):
        if not response.chats:
            return False

        for chat in response.chats:
            chat_message = self.ui_client.create_chat(chat.get("message"))
            ui_message.chat.append(chat_message)

        return True

    def create_empty_ui_message(self):
        return PangeaMessage(seats=[], chat=[], player={"sitting": 0})