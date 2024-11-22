# survey_model.py

import os

class SurveyModel:
    def __init__(self, file_path="survey_link.txt"):
        self.file_path = file_path
        self.survey_link = self.load_link_from_file()

    def set_survey_link(self, link):
        self.survey_link = link
        self.save_link_to_file(link)

    def get_survey_link(self):
        return self.survey_link

    def load_link_from_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return file.read().strip()
        return ""

    def save_link_to_file(self, link):
        with open(self.file_path, "w") as file:
            file.write(link)


