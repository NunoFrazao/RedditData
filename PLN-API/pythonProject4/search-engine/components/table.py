import customtkinter

class TableFrameData(customtkinter.CTkScrollableFrame):
    def __init__(self, master, progressbar, **kwargs):
        super().__init__(master, **kwargs)
        self.progressbar = progressbar

    def setRedditData(self, data):
        size = len(data.titles)
        self.progressbar.setSteps(2 + size*2)
        self.progressbar.beginning()

        # HEADERS TABLE
        widths = [200, 800]
        headers = ["Reddit", "Text"]
        for col, header in enumerate(headers):
            headers = customtkinter.CTkLabel(master=self, wraplength=widths[col], text=header, font=("Roboto", 12, "bold"))
            headers.grid(row=1, column=col, padx=10, pady=5)

            self.progressbar.customStep()
            self.update_idletasks()

        # ROWS TABLE
        for row, (title, selftext) in enumerate(zip(data.titles, data.selftexts), start=2):
            row_label = customtkinter.CTkLabel(self, width=widths[0], wraplength=widths[0], font=("Roboto", 12), text=title.strip(), bg_color=("#333333", "#333333"))
            row_label.grid(row=row, column=0, padx=10, pady=5)

            row_label2 = customtkinter.CTkLabel(self, width=widths[1], wraplength=widths[1], font=("Roboto", 12), text=selftext.strip(), bg_color=("#333333", "#333333"))
            row_label2.grid(row=row, column=1, padx=10, pady=5)

            self.progressbar.customStep()
            self.update_idletasks()

        self.progressbar.done()

        return size


class TableFrame(customtkinter.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        progressbar = ProgressBar(master=self, orientation="horizontal")
        progressbar.set(0)

        self.data_frame = TableFrameData(master=self, progressbar=progressbar, width=1000, height=400)
        self.data_frame.pack(side="top", fill="none")

        progressbar.pack(side="top", fill="x")

        self.label_size = customtkinter.CTkLabel(master=self, text="POSTS")
        self.label_size.pack(pady=12, padx=10, side="top", anchor="w")


    def update_size(self, size):
        self.label_size.configure(text= f"{size} posts")



class ProgressBar(customtkinter.CTkProgressBar):

    # https://stackoverflow.com/questions/74686881/how-to-add-progress-bar-on-customtkinter
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.steps = 0
        self.iter_step: float = 0
        self.progress_step: float = 0

    def setSteps(self, steps):
        self.steps = steps
        self.iter_step = 1 / steps
        self.progress_step = 0

    def customStep(self, times=1):
        self.progress_step += self.iter_step*times
        self.set(self.progress_step)

    def done(self):
        self.set(1)

    def beginning(self):
        self.set(0)
