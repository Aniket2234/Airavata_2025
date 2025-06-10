import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk


class Dashboard:
    def __init__(self, root, go_to_main_callback):
        self.root = root
        self.go_to_main_callback = go_to_main_callback

        # Dashboard window setup
        self.root.title("Welcome to Airavata")
        self.root.geometry("1200x800")
        self.root.config(bg="#2c3e50")

        # Create toolbar frame
        self.toolbar_frame = tk.Frame(self.root, bg="#34495e")
        self.toolbar_frame.pack(fill=tk.X, side=tk.TOP)

        # Toolbar buttons with hover effect
        def on_enter(e, btn):
            btn['bg'] = "#2ecc71"

        def on_leave(e, btn):
            btn['bg'] = "#34495e"

        icon_paths = [
            "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/app-development.png",
            "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/cloud-services.png",
            "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/ai.png"
        ]
        for path in icon_paths:
            try:
                icon_img = Image.open(path).resize((32, 32), Image.Resampling.LANCZOS)
                icon_img = ImageTk.PhotoImage(icon_img)
                icon_button = tk.Button(self.toolbar_frame, image=icon_img, bg="#34495e", command=self.on_icon_click)
                icon_button.image = icon_img
                icon_button.pack(side=tk.LEFT, padx=5)
                icon_button.bind("<Enter>", lambda e, b=icon_button: on_enter(e, b))
                icon_button.bind("<Leave>", lambda e, b=icon_button: on_leave(e, b))
            except Exception as e:
                print(f"Error loading toolbar icon: {e}")

        # Header frame
        self.header_frame = tk.Frame(self.root, bg="#34495e", pady=20)
        self.header_frame.pack(fill=tk.X)

        # Logo or title
        self.title_label = tk.Label(self.header_frame, text="Airavata Hydraulic Simulation",
                                    font=("Segoe UI", 24, 'bold'), fg="#ecf0f1", bg="#34495e")
        self.title_label.pack()

        # Main content frame
        self.main_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Button to go to main application
        self.main_app_button = tk.Button(self.main_frame, text="Go to Main Application",
                                         command=self.go_to_main_callback, font=("Segoe UI", 14),
                                         bg="#3498db", fg="white", height=2, width=20)
        self.main_app_button.pack(pady=20)

        # Add Recent Projects section
        self.add_recent_projects()

    def add_recent_projects(self):
        recent_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        recent_label = tk.Label(recent_frame, text="Recent Projects", font=("Segoe UI", 18, 'bold'), bg="#ecf0f1")
        recent_label.pack(pady=10)

        # Scrollable Frame for Recent Projects
        scroll_canvas = tk.Canvas(recent_frame, bg="#ecf0f1", highlightthickness=0)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=scroll_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        project_frame = tk.Frame(scroll_canvas, bg="#ecf0f1")
        scroll_canvas.create_window((0, 0), window=project_frame, anchor="nw")

        # Add project cards
        projects = [
            {"name": "Project A", "description": "AI-powered analytics system.", "status": "In Progress"},
            {"name": "Project B", "description": "Cloud-based backup solution.", "status": "Completed"},
            {"name": "Project C", "description": "Mobile app for task tracking.", "status": "On Hold"},
            {"name": "Project D", "description": "E-commerce website development.", "status": "In Progress"}
        ]

        for project in projects:
            self.add_project_card(project_frame, project)

        # Configure scroll region
        project_frame.update_idletasks()
        scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))

    def add_project_card(self, parent, project):
        card_frame = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=2)
        card_frame.pack(pady=10, padx=20, fill=tk.X)

        # Project Name
        project_name = tk.Label(card_frame, text=project["name"], font=("Segoe UI", 14, 'bold'), bg="#ffffff")
        project_name.pack(anchor="w", padx=10, pady=5)

        # Project Description
        project_desc = tk.Label(card_frame, text=project["description"], font=("Segoe UI", 12), bg="#ffffff", wraplength=800)
        project_desc.pack(anchor="w", padx=10, pady=5)

        # Status and Action Button
        bottom_frame = tk.Frame(card_frame, bg="#ffffff")
        bottom_frame.pack(fill=tk.X, pady=10)

        project_status = tk.Label(bottom_frame, text=f"Status: {project['status']}", font=("Segoe UI", 10, 'italic'), bg="#ffffff", fg="#7f8c8d")
        project_status.pack(side=tk.LEFT, padx=10)

        action_button = tk.Button(bottom_frame, text="View Details", bg="#3498db", fg="white", font=("Segoe UI", 10),
                                  command=lambda: self.on_view_details(project["name"]))
        action_button.pack(side=tk.RIGHT, padx=10)

    def on_icon_click(self):
        # Placeholder for icon click functionality
        messagebox.showinfo("Toolbar Icon", "Toolbar icon clicked!")

    def on_view_details(self, project_name):
        # Placeholder for viewing project details
        messagebox.showinfo("Project Details", f"Viewing details for {project_name}")


def go_to_main_app():
    messagebox.showinfo("Main Application", "Navigating to the main application...")


if __name__ == "__main__":
    root = tk.Tk()
    dashboard = Dashboard(root, go_to_main_app)
    root.mainloop()
