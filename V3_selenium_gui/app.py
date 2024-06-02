# app.py

import tkinter as tk
from models import SurveyModel
from views import SurveyView
from controllers import SurveyController

if __name__ == "__main__":
    root = tk.Tk()
    model = SurveyModel()
    initial_link = model.get_survey_link()
    view = SurveyView(root, initial_link)
    controller = SurveyController(model, view)
    root.mainloop()


