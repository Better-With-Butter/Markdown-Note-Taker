import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import json
from datetime import datetime

# --- CONFIGURATION & CONSTANTS ---
# File to store the last used directory and filename
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "note_taker_config.json")
LAST_DIR_KEY = "last_save_directory"
LAST_FILENAME_KEY = "last_filename" 

# Modern Dark Theme Palette
COLOR_BG = "#1e1e1e"        
COLOR_FG = "#ffffff"        
COLOR_ACCENT = "#007acc"    
COLOR_INPUT_BG = "#3c3c3c"  
COLOR_BUTTON_ACTIVE = "#5a5a5a" 
COLOR_TEXT_BG = "#2d2d30"
COLOR_SECONDARY_BTN = "#555555" 

class MarkdownNoteTakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Markdown Note Taker")
        # Set a wider initial geometry for the split view
        self.root.geometry("1000x650") 
        self.root.configure(bg=COLOR_BG)
        self.root.minsize(700, 450) 
        
        # Load configurations
        self.last_save_directory = self._load_config(LAST_DIR_KEY) or os.path.expanduser("~")
        self.last_filename = self._load_config(LAST_FILENAME_KEY) or datetime.now().strftime("%Y-%m-%d-Note")
        
        # --- Variables ---
        self.filename_var = tk.StringVar(root, value=self.last_filename)
        self.dir_display_var = tk.StringVar(root, value=f"Saving to: {self.last_save_directory}")

        # --- UI SETUP ---
        self._setup_top_controls()
        self._setup_split_content_area()
        
        # Initial file content load
        self.root.after(100, self.update_preview)

    def _setup_top_controls(self):
        """Sets up the Filename input, Save buttons, and directory display."""
        
        # 1. Filename Input
        tk.Label(self.root, text="📝 Filename:", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG).pack(pady=(15, 5), padx=20, anchor="w")
        
        self.filename_entry = tk.Entry(self.root, textvariable=self.filename_var, 
                                     font=("Segoe UI", 12), 
                                     bg=COLOR_INPUT_BG, fg=COLOR_FG, 
                                     insertbackground="white", relief="flat", highlightthickness=1, 
                                     highlightbackground="#555555", highlightcolor=COLOR_ACCENT)
        self.filename_entry.pack(fill=tk.X, padx=20, pady=5)
        
        # Bindings for preview update on filename change
        self.filename_entry.bind('<Return>', self.update_preview) 
        self.filename_entry.bind('<FocusOut>', self.update_preview)

        # 2. Save Button (Clears the whole box)
        self.save_btn = tk.Button(self.root, text="💾 Save All (Click to Clear)", 
                                  font=("Segoe UI", 14, "bold"), 
                                  bg=COLOR_ACCENT, fg="white", 
                                  activebackground=COLOR_ACCENT, activeforeground="white",
                                  relief="flat", width=35, height=1, cursor="hand2",
                                  command=lambda: self.save_note(clear_after_save=True)) 
        self.save_btn.pack(pady=(15, 5)) 

        # 3. Change Directory Button
        self.change_dir_btn = tk.Button(self.root, text="Change Save Folder", 
                                  font=("Segoe UI", 9), 
                                  bg=COLOR_SECONDARY_BTN, fg="white", 
                                  activebackground=COLOR_BUTTON_ACTIVE, activeforeground="white",
                                  relief="flat", cursor="hand2",
                                  command=self.set_save_directory)
        self.change_dir_btn.pack(pady=(5, 10)) 

        # 4. Directory Display
        self.dir_label = tk.Label(self.root, textvariable=self.dir_display_var, 
                 font=("Segoe UI", 8, "italic"), bg=COLOR_BG, fg="#888888")
        self.dir_label.pack(pady=(0, 5))

    def _setup_split_content_area(self):
        """Sets up the PanedWindow with read-only preview and new input."""

        self.content_panedwindow = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.content_panedwindow.pack(fill=tk.BOTH, expand=True, padx=20, pady=5) 
        
        # --- LEFT PANEL: READ-ONLY FILE PREVIEW ---
        self.read_panel_frame = tk.Frame(self.content_panedwindow, bg=COLOR_BG)
        self.content_panedwindow.add(self.read_panel_frame, weight=1) 
        
        tk.Label(self.read_panel_frame, text="📖 Current File Contents (Read-Only):", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG).pack(pady=(5, 5), anchor="w")

        self.preview_text_area = tk.Text(self.read_panel_frame, 
                                      font=("Segoe UI", 11), bg=COLOR_TEXT_BG, fg=COLOR_FG, 
                                      relief="flat", padx=10, pady=10, state=tk.DISABLED)
        self.preview_text_area.pack(fill=tk.BOTH, expand=True)
        
        # --- RIGHT PANEL: NEW NOTE INPUT ---
        self.write_panel_frame = tk.Frame(self.content_panedwindow, bg=COLOR_BG)
        self.content_panedwindow.add(self.write_panel_frame, weight=1)

        tk.Label(self.write_panel_frame, text="✍️ New Note Content (Press Enter to Save Line):", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG).pack(pady=(5, 5), anchor="w")

        self.note_text_area = tk.Text(self.write_panel_frame, 
                                      font=("Segoe UI", 11), bg=COLOR_TEXT_BG, fg=COLOR_FG, 
                                      insertbackground="white", relief="flat", 
                                      selectbackground=COLOR_ACCENT, padx=10, pady=10)
        self.note_text_area.pack(fill=tk.BOTH, expand=True)
        
        # Bind the Enter key within the text input area to the save function
        self.note_text_area.bind('<Return>', lambda event: self.save_note(event, clear_after_save=False)) 

    # ----------------------------------------------------------------------
    # --- CONFIGURATION METHODS ---
    # ----------------------------------------------------------------------

    def _load_config(self, key):
        """Loads configuration from a JSON file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f).get(key, "")
            except: 
                return ""
        return ""

    def _save_config(self, key, value):
        """Saves configuration to a JSON file."""
        data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
            except: 
                pass
        
        data[key] = value
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
             pass # Fail silently if we can't write config

    # ----------------------------------------------------------------------
    # --- LOGIC METHODS ---
    # ----------------------------------------------------------------------

    def set_save_directory(self):
        """Opens the file dialog to change the permanent save location."""
        new_dir = filedialog.askdirectory(
            title="Select New Permanent Save Folder",
            initialdir=self.last_save_directory 
        )
        
        if new_dir:
            self.last_save_directory = new_dir
            self._save_config(LAST_DIR_KEY, new_dir)
            self.dir_display_var.set(f"Saving to: {new_dir}")
            messagebox.showinfo("Folder Changed", f"Notes will now be saved to:\n{new_dir}") 
            self.update_preview() 

    def get_current_filepath(self, filename_base=None):
        """Helper to construct the full filepath based on current input."""
        if filename_base is None:
            filename_base = self.filename_var.get().strip()
            
        if not filename_base:
            return None
        
        filename_with_ext = filename_base
        if not filename_base.lower().endswith(".md"):
            filename_with_ext += ".md"
            
        return os.path.join(self.last_save_directory, filename_with_ext)


    def update_preview(self, event=None):
        """
        Loads the content of the file specified in the filename field 
        and updates the read-only preview panel.
        """
        filepath = self.get_current_filepath()
        content = ""
        
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"--- ERROR READING FILE ---\n{e}"
        elif filepath:
             content = f"File does not exist yet:\n{os.path.basename(filepath)}"
        else:
             content = "Enter a filename to begin..."

        # Temporarily enable the widget to modify its content
        self.preview_text_area.config(state=tk.NORMAL)
        self.preview_text_area.delete("1.0", tk.END)
        self.preview_text_area.insert(tk.END, content)
        # Scroll to the bottom to show the latest entry
        self.preview_text_area.see(tk.END)
        # Restore read-only state
        self.preview_text_area.config(state=tk.DISABLED)


    def save_note(self, event=None, clear_after_save=True):
        """
        Saves the note. Handles both button click (full save/clear) and Enter key (single line save).
        """
        filename_base = self.filename_var.get().strip()

        if not filename_base:
            messagebox.showerror("Error", "Please enter a filename.")
            return

        if not os.path.isdir(self.last_save_directory):
            messagebox.showerror("Error", "Invalid save directory. Please use the 'Change Save Folder' button to select a valid location.")
            return

        # --- DETERMINE CONTENT TO SAVE AND WHETHER TO CLEAR ---
        if event and event.keysym == 'Return':
            # Enter Key Logic: Grab the line just typed (before the newline)
            try:
                # Grab content of the line before the cursor's current position (where Enter lands)
                content_to_save = self.note_text_area.get("insert -1c linestart", "insert -1c").strip()
            except tk.TclError:
                # This can happen if the text area is empty or cursor is at the very beginning
                content_to_save = ""
            
            if not content_to_save:
                # If Enter was pressed on an empty line, just consume the event.
                return "break"
            
            # Delete the line just saved + the newline it created
            try:
                self.note_text_area.delete("insert -1c linestart", "insert")
            except:
                pass 
            
            clear_after_save = False # Don't clear the whole box
            
        else:
            # Button Click Logic: Grab all content
            content_to_save = self.note_text_area.get("1.0", tk.END).strip()
            
            if not content_to_save:
                messagebox.showerror("Error", "Note content cannot be empty.")
                return 
        
        # If content is still empty (e.g., if content was whitespace), stop.
        if not content_to_save:
             return "break" if event and event.keysym == 'Return' else None
        
        # --- SAVE CONFIG & FILE ---
        
        # 1. Update persisted filename
        self._save_config(LAST_FILENAME_KEY, filename_base)
        
        # 2. Prepare file path
        filepath = self.get_current_filepath(filename_base)
        file_exists = os.path.exists(filepath)
        
        # 3. Prepare text
        date_link = f"[[{datetime.now().strftime('%m-%d-%y')}]]"
        appended_text = f"\n\n{content_to_save} {date_link}"
        
        try:
            if file_exists:
                with open(filepath, "a", encoding="utf-8") as f: 
                    f.write(appended_text)
            else:
                title = filename_base.replace("-", " ").title()
                with open(filepath, "w", encoding="utf-8") as f: 
                    f.write(f"# {title}\n")
                    f.write(appended_text) 
            
            # 4. Cleanup
            if clear_after_save:
                self.note_text_area.delete("1.0", tk.END)
            
            self.update_preview()

            # For the Enter key binding, return "break" to suppress default behavior
            if event and event.keysym == 'Return':
                return "break"
            
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save or append to file:\n{e}")
            if event and event.keysym == 'Return':
                return "break"


# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownNoteTakerApp(root)
    root.mainloop()
