# Night-Owl-Todo
A minimalist To-Do app with a customizable Day Reset Time.
🦉 Night Owl To-Do
Night Owl To-Do is a minimalist task manager designed specifically for people whose "today" doesn't end at midnight. Whether you're a night shift worker, a student pulling an all-nighter, or just a late-night coder, this app ensures your to-do list stays with you until you actually go to sleep.

✨ Key Features
Custom Day Reset: Set your own "start" and "end" times (e.g., 3:00 AM) so your list doesn't vanish in the middle of your productivity flow.

Automatic Cleanup: Tasks from the previous "logical day" are cleared automatically based on your settings.

Minimalist Design: A dark, moon-lit aesthetic that’s easy on the eyes during late-night sessions.

Subtle Updates: A non-intrusive notification appears only when a new version is available.

Privacy First: All data is saved locally on your computer in a simple JSON file. No cloud, no tracking.

🚀 How to Install
For Regular Users (Windows)
Go to the Releases page.

Download the latest NightOwl_vX.X.X.exe.

Double-click to run! (Windows may show a "SmartScreen" warning since it's an unrecognized app; just click More Info -> Run Anyway).

For Developers (Python)
If you want to run the source code directly:

Clone this repository:

Bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
Install the required libraries:

Bash
pip install customtkinter requests
Run the app:

Bash
python night_owl.py
🛠️ How to Update
When a new version is released, a ✨ Update Available button will appear at the bottom of the app. Clicking it will take you back to the download page to grab the latest .exe.

⚙️ Configuration
Start Time: When your "productivity day" begins.

End Time: The "cutoff" point. If it's 2:00 AM and your cutoff is 4:00 AM, the app still considers it "today."

📄 License
This project is open-source and available under the MIT License.
