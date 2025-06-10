import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime
import json
import tkinter.filedialog as filedialog

class Console:
    def __init__(self, parent):
        # Console frame
        self.frame = tk.Frame(parent, bg="#333")
        self.frame.pack(fill=tk.X, padx=10, pady=5)
        self.logs = []  # Initialize logs as an empty list

        # Desired initial console height
        initial_slider_value = 8
        font_size = 10  # Default font size for calculation
        line_height = font_size * 1.5
        initial_height = int(line_height * initial_slider_value)

        # Create a frame specifically for the console with the smaller size
        self.console_frame = tk.Frame(self.frame, height=initial_height, width=600)
        self.console_frame.pack_propagate(False)
        self.console_frame.pack(fill=tk.BOTH, expand=True)

        # Console text area inside the frame
        self.console = scrolledtext.ScrolledText(
            self.console_frame, 
            wrap=tk.WORD, 
            height=8, 
            bg="#1e1e1e", 
            fg="white", 
            font=("Segoe UI", 10), 
            state="disabled"
        )
        self.console.pack(fill=tk.BOTH, expand=True)

        # Tag configurations for different log levels
        self.console.tag_config("debug", foreground="gray")
        self.console.tag_config("info", foreground="lightgreen")
        self.console.tag_config("success", foreground="lightblue")
        self.console.tag_config("warning", foreground="yellow")
        self.console.tag_config("error", foreground="orange")
        self.console.tag_config("critical", foreground="red")

        # Toolbar with console buttons and inputs
        self.toolbar = tk.Frame(self.frame, bg="#333")
        self.toolbar.pack(fill=tk.X, pady=5)

        # Buttons and inputs in the toolbar (all aligned side by side)
        self.clear_button = tk.Button(self.toolbar, text="Clear", command=self.clear, bg="#444", fg="white")
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.export_button = tk.Button(self.toolbar, text="Export Logs", command=self.export_logs, bg="#444", fg="white")
        self.export_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.filter_label = tk.Label(self.toolbar, text="Filter:", bg="#333", fg="white")
        self.filter_label.pack(side=tk.LEFT, padx=5)

        self.log_level = tk.StringVar(value="All")
        self.filter_menu = tk.OptionMenu(self.toolbar, self.log_level, "All", "Debug", "Info", "Success", "Warning", "Error", "Critical", command=self.apply_filter)
        self.filter_menu.config(bg="#444", fg="white", width=10)
        self.filter_menu.pack(side=tk.LEFT, padx=5)

        self.search_label = tk.Label(self.toolbar, text="Search:", bg="#333", fg="white")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.toolbar, bg="#555", fg="white", width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.search)

        # Message input and send button side by side in the same row
        self.message_input = tk.Entry(self.toolbar, bg="#555", fg="white", width=40)
        self.message_input.pack(side=tk.LEFT, padx=5)

        self.send_button = tk.Button(self.toolbar, text="Send Message", command=self.send_message, bg="#444", fg="white")
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Dark/Light mode toggle button
        self.theme_toggle_button = tk.Button(self.toolbar, text="Toggle Theme", command=self.toggle_theme, bg="#444", fg="white")
        self.theme_toggle_button.pack(side=tk.LEFT, padx=5)

        # Font size slider
        self.font_size_slider = tk.Scale(self.toolbar, from_=8, to=20, orient=tk.HORIZONTAL, label="Font Size", command=self.change_font_size, bg="#444", fg="white")
        self.font_size_slider.set(10)  # Set default font size
        self.font_size_slider.pack(side=tk.LEFT, padx=5)

        # Console height slider
        self.console_height_slider = tk.Scale(self.toolbar, from_=8, to=20, orient=tk.HORIZONTAL, label="Console Height", command=self.change_console_height, bg="#444", fg="white")
        self.console_height_slider.set(8)  # Set default height
        self.console_height_slider.pack(side=tk.LEFT, padx=5)

        # Load previous session logs
        self.load_button = tk.Button(self.toolbar, text="Load Last Session", command=self.load_last_session, bg="#444", fg="white")
        self.load_button.pack(side=tk.LEFT, padx=5)

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        current_bg = self.frame.cget("bg")
        if current_bg == "#333":  # Switch to light theme
            self.frame.config(bg="#f5f5f5")
            self.console.config(bg="#ffffff", fg="#000000")
            self.toolbar.config(bg="#f5f5f5")
            self.clear_button.config(bg="#ddd", fg="black")
            self.export_button.config(bg="#ddd", fg="black")
            self.filter_menu.config(bg="#ddd", fg="black")
            self.search_entry.config(bg="#ddd", fg="black")
            self.message_input.config(bg="#ddd", fg="black")
            self.send_button.config(bg="#ddd", fg="black")
            self.theme_toggle_button.config(bg="#ddd", fg="black")
            self.font_size_slider.config(bg="#ddd", fg="black")
            self.console_height_slider.config(bg="#ddd", fg="black")
            self.load_button.config(bg="#ddd", fg="black")

            # Update text tag colors for light theme
            self.console.tag_config("debug", foreground="darkgray")
            self.console.tag_config("info", foreground="darkgreen")
            self.console.tag_config("success", foreground="blue")
            self.console.tag_config("warning", foreground="darkorange")
            self.console.tag_config("error", foreground="red")
            self.console.tag_config("critical", foreground="darkred")
        else:  # Switch back to dark theme
            self.frame.config(bg="#333")
            self.console.config(bg="#1e1e1e", fg="white")
            self.toolbar.config(bg="#333")
            self.clear_button.config(bg="#444", fg="white")
            self.export_button.config(bg="#444", fg="white")
            self.filter_menu.config(bg="#444", fg="white")
            self.search_entry.config(bg="#555", fg="white")
            self.message_input.config(bg="#555", fg="white")
            self.send_button.config(bg="#444", fg="white")
            self.theme_toggle_button.config(bg="#444", fg="white")
            self.font_size_slider.config(bg="#444", fg="white")
            self.console_height_slider.config(bg="#444", fg="white")
            self.load_button.config(bg="#444", fg="white")

            # Restore text tag colors for dark theme
            self.console.tag_config("debug", foreground="gray")
            self.console.tag_config("info", foreground="lightgreen")
            self.console.tag_config("success", foreground="lightblue")
            self.console.tag_config("warning", foreground="yellow")
            self.console.tag_config("error", foreground="orange")
            self.console.tag_config("critical", foreground="red")


    def change_font_size(self, event=None):
        """Change the font size of the console text."""
        new_font_size = self.font_size_slider.get()
        self.console.config(font=("Segoe UI", new_font_size))

    def change_console_height(self, event=None):
        """Change the height of the console screen."""
        new_height = self.console_height_slider.get()
        
        # Calculate pixel height based on font size
        font_size = self.font_size_slider.get()
        line_height = font_size * 1.5  # Approximate line height
        total_height = int(line_height * new_height)
        
        # Resize console frame
        self.console_frame.config(height=total_height)

    def load_last_session(self):
        """Load the last session's logs from a file."""
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                logs = file.read()
                self.console.config(state="normal")
                self.console.insert(tk.END, logs)
                self.console.config(state="disabled")
            self.log("Logs loaded successfully.", level="success")

    def send_message(self):
        """Send a message typed in the input box to the console."""
        message = self.message_input.get().strip()
        if message:
            level = self.log_level.get().lower()
            self.log(message, level)
            self.message_input.delete(0, tk.END)  # Clear the input field

    def log(self, message, level="info"):
        """Logs a message with a specified level."""
        self.console.config(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}\n"
        self.console.insert(tk.END, formatted_message, level)
        self.console.yview(tk.END)
        self.console.config(state="disabled")
        
        # Store the log message in self.logs
        self.logs.append((timestamp, level, message))

    def clear(self):
        """Clears the console."""
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.config(state="disabled")

    def export_logs(self):
        """Exports console logs to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                logs = self.console.get("1.0", tk.END).strip()
                file.write(logs)
            self.log("Logs exported successfully.", level="success")

    def apply_filter(self, event=None):
        """Applies a filter to show only selected log levels."""
        level = self.log_level.get().lower()
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)

        for line in self.logs:
            timestamp, log_level, message = line
            if level == "all" or log_level == level:
                tag = log_level
                formatted_message = f"[{timestamp}] [{log_level.upper()}] {message}\n"
                self.console.insert(tk.END, formatted_message, tag)

        self.console.config(state="disabled")
        self.console.yview(tk.END)

    def search(self, event=None):
        """Searches the console logs for a query."""
        query = self.search_entry.get().strip().lower()
        if query:
            self.console.tag_remove("highlight", "1.0", tk.END)
            start_pos = "1.0"
            while True:
                start_pos = self.console.search(query, start_pos, stopindex=tk.END, nocase=True)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(query)}c"
                self.console.tag_add("highlight", start_pos, end_pos)
                start_pos = end_pos
            self.console.tag_config("highlight", background="yellow", foreground="black")


