import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, font
import shutil

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def disable_maximize(root):
    if sys.platform == "win32":
        import ctypes
        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 0x00010000

        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style = style & ~WS_MAXIMIZEBOX
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)

class UITronApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UITron - Electron App Builder")
        self.root.geometry("500x300")
        self.root.resizable(False, True)  # Fixed width, vertical resize only
        self.root.configure(bg="#2b2b2b")

        disable_maximize(self.root)

        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=11)
        self.entry_font = font.Font(family="Segoe UI", size=11)
        self.button_font = font.Font(family="Segoe UI", size=12, weight="bold")

        title_lbl = tk.Label(root, text="UITron - Electron App Builder", fg="#f0f0f0", bg="#2b2b2b", font=self.title_font)
        title_lbl.pack(pady=(15, 10))

        input_frame = tk.Frame(root, bg="#3c3f41")
        input_frame.pack(padx=20, pady=10, fill="x")

        app_folder_lbl = tk.Label(input_frame, text="App Folder Name:", fg="#e1e1e1", bg="#3c3f41", font=self.label_font)
        app_folder_lbl.grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.app_folder_entry = tk.Entry(input_frame, font=self.entry_font, width=35, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.app_folder_entry.grid(row=0, column=1, padx=10, pady=8)

        exe_name_lbl = tk.Label(input_frame, text="EXE Name (without .exe):", fg="#e1e1e1", bg="#3c3f41", font=self.label_font)
        exe_name_lbl.grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.exe_name_entry = tk.Entry(input_frame, font=self.entry_font, width=35, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.exe_name_entry.grid(row=1, column=1, padx=10, pady=8)

        self.select_folder_btn = tk.Button(root, text="Select Folder with Files", font=self.button_font, bg="#007acc", fg="#ffffff", activebackground="#005f9e", activeforeground="#ffffff", command=self.select_folder)
        self.select_folder_btn.pack(pady=(15, 5), ipadx=10, ipady=6)

        self.selected_folder_lbl = tk.Label(root, text="No folder selected", fg="#d3d3d3", bg="#2b2b2b", font=self.label_font, wraplength=460)
        self.selected_folder_lbl.pack(pady=(0, 15))

        self.create_app_btn = tk.Button(root, text="Create Electron App", font=self.button_font, bg="#28a745", fg="#ffffff", activebackground="#1e7e34", activeforeground="#ffffff", command=self.create_app)
        self.create_app_btn.pack(ipadx=10, ipady=8)

        self.selected_folder = None

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Your Files")
        if folder:
            self.selected_folder = folder
            display_text = f"Selected folder:\n{folder}"
            self.selected_folder_lbl.config(text=display_text, fg="#b0d6ff")
            self.update_height()

    def update_height(self):
        self.root.update_idletasks()
        new_height = self.selected_folder_lbl.winfo_y() + self.selected_folder_lbl.winfo_height() + 70
        width = self.root.winfo_width()
        self.root.geometry(f"{width}x{new_height}")

    def create_app(self):
        app_folder = self.app_folder_entry.get().strip()
        exe_name = self.exe_name_entry.get().strip()

        if not app_folder:
            messagebox.showerror("Error", "Please enter an app folder name.")
            return
        if not exe_name:
            messagebox.showerror("Error", "Please enter an EXE name.")
            return
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder containing your files.")
            return

        template_dir = resource_path("template")
        if not os.path.exists(template_dir):
            messagebox.showerror("Error", f"Template folder not found:\n{template_dir}")
            return

        app_dir = os.path.join(os.getcwd(), "apps", app_folder)
        try:
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)
            shutil.copytree(template_dir, app_dir)

            dest_resources_app = os.path.join(app_dir, "resources", "app")
            os.makedirs(dest_resources_app, exist_ok=True)

            for item in os.listdir(self.selected_folder):
                s = os.path.join(self.selected_folder, item)
                d = os.path.join(dest_resources_app, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            old_exe = os.path.join(app_dir, "App.exe")
            new_exe = os.path.join(app_dir, f"{exe_name}.exe")
            if os.path.exists(old_exe):
                os.rename(old_exe, new_exe)

            messagebox.showinfo("Success", f"Electron app '{app_folder}' created successfully in:\n{app_dir}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create app:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UITronApp(root)
    root.mainloop()
