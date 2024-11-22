# survey_view.py

import tkinter as tk

class SurveyView:
    def __init__(self, root, initial_link=""):
        self.root = root
        self.root.title("问卷分析器")

        # 创建一个frame用于包含label、entry和button
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10)

        self.link_label = tk.Label(self.top_frame, text="问卷链接:")
        self.link_label.pack(side=tk.LEFT)

        self.link_entry = tk.Entry(self.top_frame, width=50)
        self.link_entry.pack(side=tk.LEFT, padx=5)
        self.link_entry.insert(0, initial_link)  # 设置初始链接

        self.analyze_button = tk.Button(self.top_frame, text="分析问卷")
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.result_text = tk.Text(root, height=20, width=80)
        self.result_text.pack(pady=10)

    def set_analyze_command(self, command):
        self.analyze_button.config(command=command)

    def get_survey_link(self):
        return self.link_entry.get()

    def display_results(self, results):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, results)
