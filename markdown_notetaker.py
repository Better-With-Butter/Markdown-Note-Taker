import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import json
from datetime import datetime

# --- CONFIGURATION & COLORS ---
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "note_taker_config.json")
LAST_DIR_KEY = "last_save_directory"
LAST_FILENAME_KEY = "last_filename" # NEW: Key for storing the last used filename

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
        self.root.geometry("600x450")
        self.root.configure(bg=COLOR_BG)
        
        self.root.minsize(400, 350) 
        
        # Load the last saved directory
        self.last_save_directory = self._load_config(LAST_DIR_KEY)
        if not self.last_save_directory:
             self.last_save_directory = os.path.expanduser("~")

        # Load the last filename
        self.last_filename = self._load_config(LAST_FILENAME_KEY)
        
        # --- Variables ---
        self.filename_var = tk.StringVar(root)
        self.note_content_var = tk.StringVar(root)
        self.dir_display_var = tk.StringVar(root, value=f"Saving to: {self.last_save_directory}")

        # --- UI Setup ---

        # 1. Filename Input
        tk.Label(root, text="📝 Filename:", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG).pack(pady=(15, 5), padx=20, anchor="w")
        
        # Use stored filename or default date format if none is stored
        default_filename = self.last_filename if self.last_filename else datetime.now().strftime("%Y-%m-%d-Note")
        self.filename_var.set(default_filename)
        
        self.filename_entry = tk.Entry(root, textvariable=self.filename_var, 
                                     font=("Segoe UI", 12), 
                                     bg=COLOR_INPUT_BG, fg=COLOR_FG, 
                                     insertbackground="white", relief="flat", highlightthickness=1, 
                                     highlightbackground="#555555", highlightcolor=COLOR_ACCENT)
        self.filename_entry.pack(fill=tk.X, padx=20, pady=5)
        
        # 2. Save Button
        self.save_btn = tk.Button(root, text="💾 Save Note as Markdown", 
                                  font=("Segoe UI", 14, "bold"), 
                                  bg=COLOR_ACCENT, fg="white", 
                                  activebackground=COLOR_ACCENT, activeforeground="white",
                                  relief="flat", width=25, height=1, cursor="hand2",
                                  command=self.save_note)
        self.save_btn.pack(pady=(15, 5)) 

        # 3. Change Directory Button
        self.change_dir_btn = tk.Button(root, text="Change Save Folder", 
                                  font=("Segoe UI", 9), 
                                  bg=COLOR_SECONDARY_BTN, fg="white", 
                                  activebackground=COLOR_BUTTON_ACTIVE, activeforeground="white",
                                  relief="flat", cursor="hand2",
                                  command=self.set_save_directory)
        self.change_dir_btn.pack(pady=(5, 10)) 

        # 4. Directory Display
        self.dir_label = tk.Label(root, textvariable=self.dir_display_var, 
                 font=("Segoe UI", 8, "italic"), bg=COLOR_BG, fg="#888888")
        self.dir_label.pack(pady=(0, 5))
        
        # 5. Note Content Frame 
        self.content_frame = tk.Frame(root, bg=COLOR_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5) 
        
        # Note Label
        tk.Label(self.content_frame, text="✍️ Note Content:", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG).pack(pady=(5, 5), anchor="w")

        # Text Area
        self.note_text_area = tk.Text(self.content_frame, 
                                      font=("Segoe UI", 11), 
                                      bg=COLOR_TEXT_BG, fg=COLOR_FG, 
                                      insertbackground="white", relief="flat", 
                                      selectbackground=COLOR_ACCENT,
                                      padx=10, pady=10)
        self.note_text_area.pack(fill=tk.BOTH, expand=True) 

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
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
            
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

    def save_note(self):
        """
        Saves the note directly to the remembered folder.
        Appends content if the file exists and saves the new filename.
        """
        # 1. Input Validation
        filename_base = self.filename_var.get().strip()
        content = self.note_text_area.get("1.0", tk.END).strip()
        
        if not filename_base:
            messagebox.showerror("Error", "Please enter a filename.")
            return

        if not content:
            messagebox.showerror("Error", "Note content cannot be empty.")
            return
            
        # Ensure directory is valid before proceeding
        if not os.path.isdir(self.last_save_directory):
            messagebox.showerror("Error", "Invalid save directory. Please use the 'Change Save Folder' button to select a valid location.")
            return

        # 2. Add .md extension and save filename for next time
        filename_with_ext = filename_base
        if not filename_base.lower().endswith(".md"):
            filename_with_ext += ".md"
            
        # Store the filename (without extension) for next time
        self._save_config(LAST_FILENAME_KEY, filename_base)

        # 3. Construct the full file path and prepare data
        filepath = os.path.join(self.last_save_directory, filename_with_ext)
        file_exists = os.path.exists(filepath)
        
        # Format the requested date wikilink
        date_link = f"[[{datetime.now().strftime('%m-%d-%y')}]]"
        
        # Prepare the full text to be written/appended
        appended_text = f"\n{content} {date_link}"
        
        try:
            if file_exists:
                # 4a. File exists: Append the new content seamlessly
                with open(filepath, "a", encoding="utf-8") as f: 
                    f.write(appended_text)
                
            else:
                # 4b. File does not exist: Create a new file (write mode)
                
                title = filename_base.replace("-", " ").title()
                
                with open(filepath, "w", encoding="utf-8") as f: 
                    # Start the file with the title, then the first note content + date link
                    f.write(f"# {title}\n")
                    f.write(appended_text) 
            
            # 5. Clear the text area after successful save
            self.note_text_area.delete("1.0", tk.END)
            
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save or append to file:\n{e}")

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownNoteTakerApp(root)
    root.mainloop()