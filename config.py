import os
import toml
import shutil


class Config:
    def get_path(self, name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def extract_config(self, file_name, template_name):
        config_file = self.get_path(file_name)
        if not os.path.isfile(config_file):
            shutil.copyfile(self.get_path(template_name), config_file)
        return config_file


class TomlConfig(Config):
    def __init__(self, file_name, template_name):
        config_file = self.extract_config(file_name, template_name)
        self.load_config(config_file)

    def load_config(self, config_file):
        config = toml.load(config_file)
        bot = config["bot"]
        self.bot = bot["bot"]
        self.token = bot["token"]
        self.json_data_base = os.path.join(os.path.dirname(os.path.realpath(__file__)), bot["json_data_base"])

        self.servers = config["servers"]


config = TomlConfig("config.toml", "config.template.toml")
