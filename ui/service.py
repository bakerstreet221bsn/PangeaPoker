from utils.settings import Settings
from utils.errors import PangeaException, PangaeaErrorCodes
from messaging import PangeaMessage
import random
import logging
from dealer import DealerEvents

default_names = ["Anna", "Alex", "Carl", "Cathy", "John", "Jack"]


class UiService(object):

    def __init__(self, dealer_client, ui_client):
        self.logger = logging.getLogger(__name__)
        self.dealer_client = dealer_client
        self.ui_client = ui_client
        self.settings = Settings()

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

    def leave_table(self):
        self.logger.debug("leave_table")
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.leave_table(table_id, player_id)

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
        response = self.dealer_client.get_table_status(table_id, player_id, last_check, log_messages=True)

        ui_message = PangeaMessage(seats=[], chat=[], player={"sitting": 0})

        if response.table:
            if "seats" in response.table:
                for item in response.table["seats"]:
                    self.logger.debug("Processing seat: {0}".format(item))

                    seat_player_id = item.get("player_id")
                    if seat_player_id == player_id:
                        is_player = 1
                        ui_message.player = self.ui_client.create_player(
                            sitting=1,
                            hole_cards=item.get("hole_cards"),
                            stack=item.get("stack"),
                            seat_number=item.get("seat_number")
                        )
                    else:
                        is_player = 0

                    seat = self.ui_client.create_seat_item(
                        seat_number=item.get("seat_number"),
                        stack=item.get("stack"),
                        player=is_player,
                        playing=1,
                        empty=0,
                        player_cards=item.get("hole_cards"),
                        bet=item.get("bet"),
                        name=item.get("username")
                    )
                    ui_message.seats.append(seat)

        if response.events:
            for event in response.events:
                event_name = event.get("event_name", "")
                seat = self.get_matching_seat(ui_message.seats, event["seat_number"])

                if seat is None:
                    seat = self.ui_client.create_seat_item(seat_number=event["seat_number"])
                #    ui_message.seats.append(seat)

                if event_name == DealerEvents.PLAYER_JOIN_TABLE:
                    seat["empty"] = 0
                elif event_name == DealerEvents.PLAYER_LEAVE_TABLE:
                    seat["empty"] = 1

                    if seat.get("player_id", None) == player_id:
                        ui_message.player["sitting"] = 0
                elif event_name == DealerEvents.PLAYER_BET:
                    seat["bet"] = event["bet"]
                    seat["action"] = "<span>Bet<br/>{0}</span>".format(event["bet"])

        if response.chats:
            for chat in response.chats:
                chat_message = self.ui_client.create_chat(chat.message)
                ui_message.chat.append(chat_message)

        self.ui_client.send_message(ui_message)
        self.logger.debug("table_status complete")

    def bet(self, amount):
        self.logger.debug("bet, amount: {0}", amount)
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.player_bet(table_id, player_id, amount)

    def fold(self):
        self.logger.debug("fold")
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.player_fold(table_id, player_id)

    def chat(self, chat_message):
        self.logger.debug("chat: {0}".format(chat_message))
        table_id = self.auto_create_table()
        player_id = self.auto_create_player()

        response = self.dealer_client.create_chat(table_id, player_id, chat_message)

    def reset(self):
        self.logger.debug("reset")
        # Clear the table/lobby
        self.settings.set("default_lobby_id", None)
        self.settings.set("default_table_id", None)
        self.settings.temp_player_id = None

        # This should automatically create a new player/table and refresh the ui
        self.table_status(None)

    def auto_create_table(self):
        default_lobby_id = self.settings.get("default_lobby_id")
        default_table_id = self.settings.get("default_table_id")

        if default_lobby_id is None:
            self.logger.debug("No default_lobby_id found in settings. Automatically creating a default lobby")
            response = self.dealer_client.create_lobby("Default lobby")
            default_lobby_id = response.lobby["id"]
            self.settings.set("default_lobby_id", default_lobby_id)

        if default_table_id is None:
            self.logger.debug("No default_table_id found in settings. Automatically creating a default table")
            response = self.dealer_client.create_table(default_lobby_id, "Default table")
            default_table_id = response.table["id"]
            self.settings.set("default_table_id", default_table_id)

        return default_table_id

    def auto_create_player(self):
        # This works different to auto_create_table. Here we create a new player
        # every time the application starts up
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