import customtkinter as ctk
import json 
import os
import requests
import threading
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DATA_FILE = "owl_data.json"
VERSION = "1.0.0"
# Replace 'YOUR_USERNAME' and 'YOUR_REPO' with your actual GitHub details after uploading
VERSION_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/version.txt"

# --- HELPERS ---
def get_current_time_str():
    return datetime.now().strftime("%I:%M %p")

def save_data(tasks, start_time, end_time):
    clean_tasks = []
    for t in tasks:
        clean_tasks.append({
            "text": t.get("text", ""),
            "done": t.get("done", False),
            "day": t.get("day", ""),
            "created_at": t.get("created_at", ""),
            "completed_at": t.get("completed_at", None)
        })
    data = {"tasks": clean_tasks, "start_time": start_time, "end_time": end_time}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"tasks": [], "start_time": "2:00 PM", "end_time": "4:00 AM"}

def time_to_int(time_str):
    return datetime.strptime(time_str, "%I:%M %p").hour

def get_logical_day(start_h, end_h):
    now = datetime.now()
    current_h = now.hour
    if end_h < start_h and current_h < end_h:
        display_date = now - timedelta(days=1)
    else:
        display_date = now
    return display_date.strftime("%A, %B %d")

# --- MAIN APP ---
class NightOwlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        data = load_data()
        self.saved_tasks = data["tasks"]

        self.title(f"Night Owl To-Do v{VERSION}")
        self.geometry("620x750") 
        ctk.set_appearance_mode("dark")

        # Define Custom Colors
        self.purple_accent = "#6A5ACD"
        self.deep_bg = "#1A1A2E"
        self.success_green = "#2cc985"
        self.danger_red = "#FF4C4C"

        # UI Components
        self.date_label = ctk.CTkLabel(self, text="", font=("Arial Bold", 26), text_color=self.purple_accent)
        self.date_label.pack(pady=(20, 5))
        
        self.clock_label = ctk.CTkLabel(self, text="", font=("Courier New", 18), text_color="gray70")
        self.clock_label.pack(pady=(0, 20))

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self, fg_color="#252538")
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        HOURS = [str(i) for i in range(1, 13)]
        PERIODS = ["AM", "PM"]
        s_parts = data.get("start_time", "2:00 PM").replace(":00", "").split(" ")
        e_parts = data.get("end_time", "4:00 AM").replace(":00", "").split(" ")

        ctk.CTkLabel(self.settings_frame, text="Start Time:").grid(row=0, column=0, padx=10, pady=10)
        self.start_h_var = ctk.StringVar(value=s_parts[0])
        self.start_p_var = ctk.StringVar(value=s_parts[1])
        ctk.CTkOptionMenu(self.settings_frame, values=HOURS, variable=self.start_h_var, width=65, fg_color=self.purple_accent).grid(row=0, column=1)
        ctk.CTkOptionMenu(self.settings_frame, values=PERIODS, variable=self.start_p_var, width=75, fg_color=self.purple_accent).grid(row=0, column=2, padx=5)

        ctk.CTkLabel(self.settings_frame, text="End Time:").grid(row=0, column=3, padx=10)
        self.end_h_var = ctk.StringVar(value=e_parts[0])
        self.end_p_var = ctk.StringVar(value=e_parts[1])
        ctk.CTkOptionMenu(self.settings_frame, values=HOURS, variable=self.end_h_var, width=65, fg_color=self.purple_accent).grid(row=0, column=4)
        ctk.CTkOptionMenu(self.settings_frame, values=PERIODS, variable=self.end_p_var, width=75, fg_color=self.purple_accent).grid(row=0, column=5, padx=5)

        # Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=15)
        self.task_entry = ctk.CTkEntry(self.input_frame, placeholder_text="What's on the moon-lit agenda?", width=320, border_color=self.purple_accent)
        self.task_entry.pack(side="left", padx=10)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        self.add_button = ctk.CTkButton(self.input_frame, text="+ Add", width=80, fg_color=self.purple_accent, command=self.add_task)
        self.add_button.pack(side="left")

        # Scrollable List
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=580, height=350, fg_color="#1E1E2E")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.clear_button = ctk.CTkButton(self, text="Clear All Tasks", fg_color="transparent", border_width=1, border_color=self.danger_red, text_color=self.danger_red, command=self.clear_all)
        self.clear_button.pack(pady=15)

        # Initialize State
        self.refresh_ui()
        self.update_clock()
        
        # Start background update check
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def check_for_updates(self):
        try:
            response = requests.get(VERSION_URL, timeout=5)
            if response.status_code == 200:
                latest_version = response.text.strip()
                if latest_version != VERSION:
                    self.after(0, lambda: self.show_update_notice(latest_version))
        except Exception as e:
            print(f"Update check failed: {e}")

    def show_update_notice(self, new_ver):
        # This creates a simple top-level popup window
        popup = ctk.CTkToplevel(self)
        popup.title("Update Available")
        popup.geometry("300x150")
        popup.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(popup, text=f"New version {new_ver} is out!", pady=20)
        lbl.pack()
        
        btn = ctk.CTkButton(popup, text="Close", fg_color=self.purple_accent, command=popup.destroy)
        btn.pack()

    def update_clock(self):
        now = datetime.now()
        self.clock_label.configure(text=now.strftime("%I:%M:%S %p"))
        if now.second == 0:
            self.refresh_ui()
        self.after(1000, self.update_clock)

    def add_task(self):
        text = self.task_entry.get().strip()
        if text:
            task_dict = {"text": text, "done": False, "day": self.date_label.cget("text"), 
                         "created_at": get_current_time_str(), "completed_at": None}
            self.saved_tasks.append(task_dict)
            self.task_entry.delete(0, 'end')
            self.persist()
            self.refresh_ui()

    def draw_single_task(self, index, task):
        item_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)
        item_frame.columnconfigure(0, weight=1)

        cb = ctk.CTkCheckBox(item_frame, text=task["text"], command=lambda: self.toggle_task(index))
        cb.grid(row=0, column=0, sticky="w", padx=10)

        if task.get("done"):
            t_val = task.get('completed_at') or "---"
            display_time, label_color = f"Done {t_val}", self.success_green 
            cb.select()
            cb.configure(text_color="gray40")
        else:
            t_val = task.get('created_at') or "Today"
            display_time, label_color = f"In {t_val}", "gray60"

        ctk.CTkLabel(item_frame, text=display_time, font=("Arial", 11, "italic"), text_color=label_color, width=140, anchor="e").grid(row=0, column=1, padx=5)
        ctk.CTkButton(item_frame, text="🗑", width=35, fg_color="transparent", text_color="#777777", command=lambda: self.delete_task(index)).grid(row=0, column=2, padx=5)

    def toggle_task(self, index):
        self.saved_tasks[index]["done"] = not self.saved_tasks[index]["done"]
        self.saved_tasks[index]["completed_at"] = get_current_time_str() if self.saved_tasks[index]["done"] else None
        self.persist()
        self.refresh_ui()

    def delete_task(self, index):
        self.saved_tasks.pop(index)
        self.persist()
        self.refresh_ui()

    def clear_all(self):
        self.saved_tasks = []
        self.persist()
        self.refresh_ui()

    def persist(self):
        s_str = f"{self.start_h_var.get()}:00 {self.start_p_var.get()}"
        e_str = f"{self.end_h_var.get()}:00 {self.end_p_var.get()}"
        save_data(self.saved_tasks, s_str, e_str)

    def refresh_ui(self):
        try:
            s = time_to_int(f"{self.start_h_var.get()}:00 {self.start_p_var.get()}")
            e = time_to_int(f"{self.end_h_var.get()}:00 {self.end_p_var.get()}")
            current_day = get_logical_day(s, e)
            self.date_label.configure(text=current_day)
            self.saved_tasks = [t for t in self.saved_tasks if t.get("day") == current_day]
        except: pass
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        for i, task in enumerate(self.saved_tasks):
            self.draw_single_task(i, task)

    def on_closing(self):
        self.persist()
        self.destroy()

if __name__ == "__main__":
    app = NightOwlApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()