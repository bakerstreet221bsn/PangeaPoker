import yaml
import os
import logging
import traceback

joined_table = False

class Settings(object):

    logger = logging.getLogger(__name__)
    file_name = "settings.yaml"
    temp_player_id = None
    default_table_id = None

    def get(self, name, default_value=None):
        settings = self.load_settings()
        return settings.get(name, default_value)

    def set(self, name, value):
        settings = self.load_settings()
        settings[name] = value
        self.save_settings(settings)

    def load_settings(self):
        if not os.path.isfile(self.file_name):
            return {}

        with open(self.file_name, "r") as f:
            try:
                result = yaml.load(f)
                return result if result else {}
            except yaml.YAMLError as exc:
                error_message = "Unable to load settings.yaml. Empty settings returned. "

                if hasattr(exc, "problem_mark"):
                    mark = exc.problem_mark
                    error_message += "Error position: ({0}:{1}, ".format(mark.line+1, mark.column+1)

                error_message += "Exception: {0}".format(traceback.print_exc())
                self.logger(error_message)
                return {}

    def save_settings(self, settings):
        with open(self.file_name, "w") as f:
            yaml.dump(settings, f)