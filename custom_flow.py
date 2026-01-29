import customtkinter as ctk
import json 
import os
import sys
import requests
import threading
import webbrowser
from datetime import datetime, timedelta
from tkinter import messagebox
import ctypes


# --- WINDOWS TASKBAR ICON FIX ---
try:
    # Use a unique string for your app
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("UniversalStacker.CustomFlow.1.0")
except:
    pass
# --- CONFIGURATION ---
DATA_FILE = "owl_data.json"
VERSION = "1.0.0" # Set to 1.0.0 for your first official release
VERSION_URL = "https://raw.githubusercontent.com/UniversalStacker/CustomFlow/main/version.txt"
RELEASE_URL = "https://github.com/UniversalStacker/CustomFlow/releases"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_current_time_str():
    return datetime.now().strftime("%I:%M %p")

def save_data(tasks, start_time, end_time):
    data = {"tasks": tasks, "start_time": start_time, "end_time": end_time}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"tasks": [], "start_time": "02:00 PM", "end_time": "04:00 AM"}

def time_to_int(time_str):
    return datetime.strptime(time_str, "%I:%M %p").hour

def get_logical_day(start_h, end_h):
    now = datetime.now()
    current_h = now.hour
    display_date = now - timedelta(days=1) if (end_h < start_h and current_h < end_h) else now
    return display_date.strftime("%A, %B %d")

class NightOwlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Centering Logic
        width, height = 600, 750
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.title(f"CustomFlow To-Do v{VERSION}")
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(550, 650) 
        ctk.set_appearance_mode("dark")
        
        # Load Icon
        try:
            self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        except:
            pass

        self.is_loading = True 
        data = load_data()
        self.saved_tasks = data["tasks"]
        self.purple_accent, self.success_green, self.danger_red = "#6A5ACD", "#2cc985", "#FF4C4C"

        s_parts = data.get("start_time", "02:00 PM").replace(":00", "").split(" ")
        e_parts = data.get("end_time", "04:00 AM").replace(":00", "").split(" ")
        self.last_start_h, self.last_start_p = s_parts[0], s_parts[1]
        self.last_end_h, self.last_end_p = e_parts[0], e_parts[1]

        # UI
        self.date_label = ctk.CTkLabel(self, text="", font=("Arial Bold", 26), text_color=self.purple_accent)
        self.date_label.pack(pady=(20, 5))
        self.clock_label = ctk.CTkLabel(self, text="", font=("Courier New", 18), text_color="gray70")
        self.clock_label.pack(pady=(0, 10))

        # Settings
        self.settings_frame = ctk.CTkFrame(self, fg_color="#252538")
        self.settings_frame.pack(pady=10, padx=20, fill="x")
        self.settings_frame.columnconfigure(0, weight=1); self.settings_frame.columnconfigure(1, weight=1)

        HOURS, PERIODS = [f"{i:02d}" for i in range(1, 13)], ["AM", "PM"]
        self.start_h_var = ctk.StringVar(value=self.last_start_h)
        self.start_p_var = ctk.StringVar(value=self.last_start_p)
        self.end_h_var = ctk.StringVar(value=self.last_end_h)
        self.end_p_var = ctk.StringVar(value=self.last_end_p)

        s_grp = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        s_grp.grid(row=0, column=0, pady=10)
        ctk.CTkLabel(s_grp, text="Start:").pack(side="left", padx=2)
        ctk.CTkOptionMenu(s_grp, values=HOURS, variable=self.start_h_var, width=65, command=lambda _: self.update_logic()).pack(side="left", padx=2)
        ctk.CTkOptionMenu(s_grp, values=PERIODS, variable=self.start_p_var, width=65, command=lambda _: self.update_logic()).pack(side="left", padx=2)

        e_grp = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        e_grp.grid(row=0, column=1, pady=10)
        ctk.CTkLabel(e_grp, text="End:").pack(side="left", padx=2)
        ctk.CTkOptionMenu(e_grp, values=HOURS, variable=self.end_h_var, width=65, command=lambda _: self.update_logic()).pack(side="left", padx=2)
        ctk.CTkOptionMenu(e_grp, values=PERIODS, variable=self.end_p_var, width=65, command=lambda _: self.update_logic()).pack(side="left", padx=2)

        self.save_settings_btn = ctk.CTkButton(self.settings_frame, text="Apply Changes", fg_color=self.success_green, text_color="black", height=24, command=self.apply_new_times)

        # Input
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=15, fill="x", padx=40)
        self.task_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Plan your time...")
        self.task_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        self.add_button = ctk.CTkButton(self.input_frame, text="+ Add", width=80, fg_color=self.purple_accent, command=self.add_task)
        self.add_button.pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1E1E2E")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=10)
        self.ontop_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.controls_frame, text="Always on Top", variable=self.ontop_var, command=self.toggle_ontop).pack(side="left", padx=10)
        self.theme_switch = ctk.CTkSegmentedButton(self.controls_frame, values=["Purple", "Midnight"], command=self.change_theme, selected_color=self.purple_accent)
        self.theme_switch.set("Purple"); self.theme_switch.pack(side="left", padx=10)

        self.clear_button = ctk.CTkButton(self, text="Clear All Tasks", fg_color="transparent", border_width=1, border_color=self.danger_red, text_color=self.danger_red, command=self.clear_all)
        self.clear_button.pack(pady=(0, 10))
        self.update_btn = ctk.CTkButton(self, text="", fg_color="#4B0082", height=30, command=self.open_release_page)

        self.refresh_ui(); self.update_clock()
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        self.is_loading = False 

    def toggle_ontop(self): self.attributes("-topmost", self.ontop_var.get())

    def change_theme(self, choice):
        self.purple_accent = "#6A5ACD" if choice == "Purple" else "#1f538d"
        self.date_label.configure(text_color=self.purple_accent)
        self.add_button.configure(fg_color=self.purple_accent)
        self.theme_switch.configure(selected_color=self.purple_accent)

    def update_logic(self):
        if self.is_loading: return
        changed = (self.start_h_var.get() != self.last_start_h or self.start_p_var.get() != self.last_start_p or
                   self.end_h_var.get() != self.last_end_h or self.end_p_var.get() != self.last_end_p)
        if changed: self.save_settings_btn.grid(row=1, column=0, columnspan=2, pady=10)
        else: self.save_settings_btn.grid_forget()

    def apply_new_times(self):
        if messagebox.askyesno("Confirm", "Update cycle times?"):
            self.last_start_h, self.last_start_p = self.start_h_var.get(), self.start_p_var.get()
            self.last_end_h, self.last_end_p = self.end_h_var.get(), self.end_p_var.get()
            self.persist(); self.refresh_ui()
        self.save_settings_btn.grid_forget()

    def check_for_updates(self):
        try:
            res = requests.get(VERSION_URL, timeout=5)
            if res.status_code == 200 and res.text.strip() != VERSION:
                self.after(0, lambda: self.show_update_notice(res.text.strip()))
        except: pass

    def show_update_notice(self, ver): self.update_btn.configure(text=f"✨ Update v{ver} Available"); self.update_btn.pack(pady=10, side="bottom")

    def open_release_page(self): webbrowser.open(RELEASE_URL)

    def update_clock(self):
        now = datetime.now()
        self.clock_label.configure(text=now.strftime("%I:%M:%S %p"))
        if now.second == 0: self.refresh_ui()
        self.after(1000, self.update_clock)

    def add_task(self):
        text = self.task_entry.get().strip()
        if text:
            self.saved_tasks.append({"text": text, "done": False, "day": self.date_label.cget("text"), "created_at": get_current_time_str(), "completed_at": None})
            self.task_entry.delete(0, 'end'); self.persist(); self.refresh_ui()

    def draw_single_task(self, index, task):
        f = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        f.pack(fill="x", pady=5); f.columnconfigure(0, weight=1)
        cb = ctk.CTkCheckBox(f, text=task["text"], command=lambda: self.toggle_task(index))
        cb.grid(row=0, column=0, sticky="w", padx=10)
        if task.get("done"):
            t, col = f"Done {task.get('completed_at', '---')}", self.success_green
            cb.select(); cb.configure(text_color="gray40")
        else:
            t, col = f"In {task.get('created_at', 'Today')}", "gray60"
        ctk.CTkLabel(f, text=t, font=("Arial", 11, "italic"), text_color=col, width=140, anchor="e").grid(row=0, column=1, padx=5)
        ctk.CTkButton(f, text="🗑", width=35, fg_color="transparent", text_color="#777777", command=lambda: self.delete_task(index)).grid(row=0, column=2, padx=5)

    def toggle_task(self, index):
        self.saved_tasks[index]["done"] = not self.saved_tasks[index]["done"]
        self.saved_tasks[index]["completed_at"] = get_current_time_str() if self.saved_tasks[index]["done"] else None
        self.persist(); self.refresh_ui()

    def delete_task(self, index): self.saved_tasks.pop(index); self.persist(); self.refresh_ui()

    def clear_all(self): self.saved_tasks = []; self.persist(); self.refresh_ui()

    def persist(self):
        save_data(self.saved_tasks, f"{self.start_h_var.get()}:00 {self.start_p_var.get()}", f"{self.end_h_var.get()}:00 {self.end_p_var.get()}")

    def refresh_ui(self):
        try:
            s, e = time_to_int(f"{self.start_h_var.get()}:00 {self.start_p_var.get()}"), time_to_int(f"{self.end_h_var.get()}:00 {self.end_p_var.get()}")
            day = get_logical_day(s, e); self.date_label.configure(text=day)
            filtered = [t for t in self.saved_tasks if t.get("day") == day]
            for w in self.scroll_frame.winfo_children(): w.destroy()
            for t in filtered: self.draw_single_task(self.saved_tasks.index(t), t)
        except: pass

if __name__ == "__main__":
    app = NightOwlApp(); app.mainloop()