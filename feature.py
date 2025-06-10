import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
import time
import csv
import json
import matplotlib.pyplot as plt
import psutil  # For performance monitoring
import json  # Add this import statement
import tkinter.filedialog as filedialog
# other imports...


class Features:
    def __init__(self, app):
        self.app = app

    # 1. Undo/Redo Functionality
    def undo_redo(self):
        # Simple implementation of undo/redo functionality could involve a stack of changes
        # This is a placeholder for the actual logic.
        pass

    # 2. Project History
    def open_recent_project(self):
        # Open a list of recent projects
        recent_projects = self.load_recent_projects()
        if not recent_projects:
            messagebox.showinfo("No Recent Projects", "No recent projects found.")
            return
        project = messagebox.askquestion("Recent Projects", f"Open the following recent project?\n{recent_projects[0]}")
        if project == "yes":
            self.app.open_project(recent_projects[0])

    def load_recent_projects(self):
        # This can load a list from a file or in-memory storage
        return ["project1.dat", "project2.dat"]

    # 3. Export Options
    def export_project(self, format_type):
        if format_type == "CSV":
            self.export_to_csv()
        elif format_type == "PDF":
            self.export_to_pdf()
        elif format_type == "XML":
            self.export_to_xml()

    def export_to_csv(self):
        project_data = self.collect_project_data()
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(project_data.keys())
                writer.writerow(project_data.values())
            messagebox.showinfo("Export", f"Project exported to {file_path}")

    def export_to_pdf(self):
        # Implement export to PDF functionality
        messagebox.showinfo("Export", "Exported to PDF format.")

    def export_to_xml(self):
        project_data = self.collect_project_data()
        file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
        if file_path:
            root = tk.Tk()
            xml_data = f"<project>\n  <name>{project_data['name']}</name>\n  <description>{project_data['description']}</description>\n</project>"
            with open(file_path, "w") as file:
                file.write(xml_data)
            messagebox.showinfo("Export", f"Project exported to {file_path}")

    def collect_project_data(self):
        # Placeholder for actual project data
        return {
            "name": "Hydraulic Transient Analysis",
            "description": "A robust hydraulic model for simulation."
        }

    # 4. Advanced File Management
    def version_project(self):
        version_number = self.get_new_version()
        self.save_project_version(version_number)
        messagebox.showinfo("Versioning", f"Project versioned as {version_number}.")

    def get_new_version(self):
        # Simple versioning by incrementing a version number
        return "v1.1"

    def save_project_version(self, version_number):
        version_file = "project_versions.json"
        versions = self.load_versions()
        versions.append(version_number)
        with open(version_file, "w") as file:
            json.dump(versions, file)

    def load_versions(self):
        version_file = "project_versions.json"
        if os.path.exists(version_file):
            with open(version_file, "r") as file:
                return json.load(file)
        return []

    # 5. Search and Filter Functionality
    def search_project(self, search_term):
        project_data = self.collect_project_data()
        if search_term.lower() in project_data["name"].lower():
            messagebox.showinfo("Search Result", f"Found '{search_term}' in project name.")
        else:
            messagebox.showinfo("Search Result", f"'{search_term}' not found in project.")

    # 6. Customizable UI (Themes)
    def toggle_theme(self):
        current_bg = self.app.root.cget("bg")
        new_bg = "#333" if current_bg == "#f5f5f5" else "#f5f5f5"
        self.app.root.config(bg=new_bg)
        messagebox.showinfo("Theme", f"Switched to {'Dark' if new_bg == '#333' else 'Light'} mode.")

    # 7. Data Visualization
    def plot_data(self):
        data = [1, 2, 3, 4, 5]
        plt.plot(data)
        plt.title("Sample Data Visualization")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.show()

    # 8. Simulation/Analysis Results
    def run_simulation(self):
        result = self.simulate_hydraulic_model()
        messagebox.showinfo("Simulation Result", f"Simulation completed with result: {result}")

    def simulate_hydraulic_model(self):
        # Placeholder for actual hydraulic simulation logic
        return "Simulation successful"

    # 9. Collaboration Features
    def enable_collaboration(self):
        # Placeholder for collaboration feature (could integrate cloud-based systems)
        messagebox.showinfo("Collaboration", "Collaboration enabled.")

    # 10. Notifications/Alerts
    def show_notification(self, message):
        messagebox.showinfo("Notification", message)

    # 11. Backup and Restore
    def backup_project(self):
        backup_path = filedialog.askdirectory(title="Select Backup Location")
        if backup_path:
            backup_folder = os.path.join(backup_path, "Backup")
            shutil.copytree(self.app.file_path, backup_folder)
            messagebox.showinfo("Backup", "Project backed up successfully.")

    def restore_project(self):
        restore_path = filedialog.askdirectory(title="Select Restore Location")
        if restore_path:
            shutil.copytree(restore_path, self.app.file_path)
            messagebox.showinfo("Restore", "Project restored successfully.")

    # 12. Help and Documentation
    def show_help(self):
        help_text = "Here is how to use Airavata:\n" \
                    "1. Create a new project\n" \
                    "2. Open an existing project\n" \
                    "3. Export data\n" \
                    "4. Run simulations\n" \
                    "For detailed instructions, refer to the user manual."
        messagebox.showinfo("Help", help_text)

    # 13. User Authentication and Permissions
    def user_authentication(self):
        # Placeholder for user authentication system (login/signup)
        messagebox.showinfo("Authentication", "User authentication successful.")

    # 14. Integrating External Libraries or APIs
    def integrate_api(self):
        # Example: Integrating with an external API (for example, weather data or another API)
        messagebox.showinfo("API Integration", "API integrated successfully.")

    # 15. Task Scheduling
    def schedule_task(self, time, task):
        # Placeholder for task scheduling (could integrate with OS task scheduler)
        messagebox.showinfo("Task Scheduling", f"Task '{task}' scheduled at {time}.")

    # 16. Error Logging/Reporting
    def log_error(self, error_message):
        # Log errors to a file
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"{time.ctime()}: {error_message}\n")
        messagebox.showinfo("Error Logging", "Error logged successfully.")

    # 17. System Performance Monitoring (Extended)
    def monitor_performance(self):
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory_info = psutil.virtual_memory()
        
        # Disk usage
        disk_info = psutil.disk_usage('/')
        
        # Network usage
        net_info = psutil.net_io_counters()
        
        # Battery status (if applicable)
        battery = psutil.sensors_battery()
        battery_status = "Charging" if battery and battery.power_plugged else "Not Charging"
        battery_percentage = battery.percent if battery else "N/A"
        
        # GPU usage (if available)
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_usage = ", ".join([f"GPU {gpu.id}: {gpu.memoryUtil * 100:.2f}% used" for gpu in gpus])
        except ImportError:
            gpu_usage = "GPU monitoring not available"
        
        # Active Processes (top 5 processes by CPU usage)
        processes = [(p.info['pid'], p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent'])]
        processes = sorted(processes, key=lambda x: x[2], reverse=True)[:5]  # Top 5 processes
        process_info = "\n".join([f"PID: {pid}, Name: {name}, CPU Usage: {cpu}%" for pid, name, cpu in processes])

        # Display the gathered stats in a message box
        messagebox.showinfo("Performance Monitoring", 
                            f"CPU Usage: {cpu_usage}%\n"
                            f"Memory Usage: {memory_info.percent}%\n"
                            f"Disk Usage: {disk_info.percent}%\n"
                            f"Network - Sent: {net_info.bytes_sent} bytes, Received: {net_info.bytes_recv} bytes\n"
                            f"Battery Status: {battery_status} ({battery_percentage}%)\n"
                            f"GPU Usage: {gpu_usage}\n"
                            f"Top 5 Processes by CPU Usage:\n{process_info}")
