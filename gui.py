"""
Reddit Persona Analyzer - Tkinter Desktop GUI.

A desktop GUI application for analyzing Reddit user profiles
using web scraping and AI-powered analysis.
"""

import os
import sys
import threading
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import RedditScraper
from src.analyzer import PersonaAnalyzer
from src.utils import extract_username_from_url, format_output, sanitize_filename
import config


class RedditPersonaAnalyzerGUI:
    """Main GUI class for Reddit Persona Analyzer application."""

    def __init__(self, root):
        """
        Initialize the Reddit Persona Analyzer GUI.

        Args:
            root: The tkinter root window instance.
        """
        self.root = root
        self.root.title("Reddit Persona Analyzer")
        self.root.geometry("900x700")

        # Set style
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        self.bg_color = "#f0f0f0"
        self.reddit_orange = "#FF4500"
        self.root.configure(bg=self.bg_color)

        # Variables
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to analyze")
        self.progress_var = tk.DoubleVar()

        # Create GUI
        self.create_widgets()
        self.check_api_keys()

    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        self._create_header()
        self._create_main_container()

    def _create_header(self):
        """Create the header section of the GUI."""
        header_frame = tk.Frame(self.root, bg=self.reddit_orange, height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🔍 Reddit Persona Analyzer",
            font=("Arial", 24, "bold"),
            bg=self.reddit_orange,
            fg="white",
        )
        title_label.pack(pady=20)

    def _create_main_container(self):
        """Create the main container with all functional widgets."""
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_input_section(main_container)
        self._create_progress_section(main_container)
        self._create_results_section(main_container)
        self._create_buttons_section(main_container)

    def _create_input_section(self, parent):
        """
        Create the input section for URL entry.

        Args:
            parent: The parent widget container.
        """
        input_frame = tk.LabelFrame(
            parent,
            text="Enter Reddit Profile URL",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            padx=20,
            pady=10,
        )
        input_frame.pack(fill="x", pady=(0, 10))

        # URL Entry
        self.url_entry = tk.Entry(
            input_frame, textvariable=self.url_var, font=("Arial", 12), width=50
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Analyze Button
        self.analyze_btn = tk.Button(
            input_frame,
            text="Analyze Profile",
            command=self.analyze_profile,
            bg=self.reddit_orange,
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5,
            cursor="hand2",
        )
        self.analyze_btn.pack(side="left")

        # Example Buttons
        self._create_example_buttons(input_frame)

    def _create_example_buttons(self, parent):
        """
        Create example username buttons.

        Args:
            parent: The parent widget container.
        """
        examples_frame = tk.Frame(parent, bg=self.bg_color)
        examples_frame.pack(fill="x", pady=(10, 0))

        tk.Label(
            examples_frame, text="Examples:", font=("Arial", 10), bg=self.bg_color
        ).pack(side="left", padx=(0, 10))

        example_usernames = ["kojied", "Hungry-Move-6603", "AutoModerator"]
        for username in example_usernames:
            tk.Button(
                examples_frame,
                text=f"u/{username}",
                command=lambda u=username: self.set_example_url(u),
                font=("Arial", 10),
                cursor="hand2",
            ).pack(side="left", padx=5)

    def _create_progress_section(self, parent):
        """
        Create the progress bar section.

        Args:
            parent: The parent widget container.
        """
        progress_frame = tk.Frame(parent, bg=self.bg_color)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100, length=400
        )
        self.progress_bar.pack(fill="x")

        self.status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg=self.bg_color,
        )
        self.status_label.pack(pady=(5, 0))

    def _create_results_section(self, parent):
        """
        Create the results display section.

        Args:
            parent: The parent widget container.
        """
        results_frame = tk.LabelFrame(
            parent,
            text="Analysis Results",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            padx=10,
            pady=10,
        )
        results_frame.pack(fill="both", expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, font=("Courier", 10), height=20
        )
        self.results_text.pack(fill="both", expand=True)

    def _create_buttons_section(self, parent):
        """
        Create the action buttons section.

        Args:
            parent: The parent widget container.
        """
        buttons_frame = tk.Frame(parent, bg=self.bg_color)
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Save Button
        self.save_btn = tk.Button(
            buttons_frame,
            text="💾 Save Analysis",
            command=self.save_analysis,
            font=("Arial", 10),
            state="disabled",
            cursor="hand2",
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        # Clear Button
        tk.Button(
            buttons_frame,
            text="🗑️ Clear",
            command=self.clear_results,
            font=("Arial", 10),
            cursor="hand2",
        ).pack(side="left", padx=(0, 10))

        # View Saved Button
        tk.Button(
            buttons_frame,
            text="📁 View Saved Analyses",
            command=self.view_saved_analyses,
            font=("Arial", 10),
            cursor="hand2",
        ).pack(side="left")

        # API Status (right side)
        self.api_status_label = tk.Label(
            buttons_frame, text="", font=("Arial", 10), bg=self.bg_color
        )
        self.api_status_label.pack(side="right")

    def check_api_keys(self):
        """Check if API keys are properly configured."""
        issues = []

        if (
            not config.REDDIT_CLIENT_ID
            or config.REDDIT_CLIENT_ID == "your_client_id_here"
        ):
            issues.append("Reddit Client ID")

        if (
            not config.REDDIT_CLIENT_SECRET
            or config.REDDIT_CLIENT_SECRET == "your_client_secret_here"
        ):
            issues.append("Reddit Client Secret")

        if (
            not config.OPENAI_API_KEY
            or config.OPENAI_API_KEY == "your_openai_api_key_here"
        ):
            issues.append("OpenAI API Key")

        if issues:
            self.api_status_label.config(
                text=f"⚠️ Missing: {', '.join(issues)}", fg="red"
            )
            messagebox.showwarning(
                "API Configuration",
                f"Missing API keys: {', '.join(issues)}\n\n"
                "Please configure them in the .env file before "
                "analyzing profiles.",
            )
        else:
            self.api_status_label.config(text="✅ All APIs configured", fg="green")

    def set_example_url(self, username):
        """
        Set example URL in the entry field.

        Args:
            username: The Reddit username to set as example.
        """
        self.url_var.set(f"https://www.reddit.com/user/{username}/")

    def analyze_profile(self):
        """Analyze Reddit profile in a separate thread."""
        url = self.url_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a Reddit profile URL")
            return

        username = extract_username_from_url(url)
        if not username:
            messagebox.showerror(
                "Error", "Invalid Reddit URL. Please enter a valid " "user profile URL."
            )
            return

        # Disable button during analysis
        self.analyze_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.results_text.delete(1.0, tk.END)

        # Start analysis in separate thread
        thread = threading.Thread(target=self._analyze_profile_thread, args=(username,))
        thread.daemon = True
        thread.start()

    def _analyze_profile_thread(self, username):
        """
        Perform analysis in separate thread.

        Args:
            username: The Reddit username to analyze.
        """
        try:
            # Update progress
            self.update_progress(10, "Initializing Reddit scraper...")
            scraper = RedditScraper()

            # Scrape user data
            self.update_progress(30, f"Scraping posts and comments for u/{username}...")
            user_data = scraper.scrape_user(username)

            # Show statistics
            stats = (
                f"Found {len(user_data['posts'])} posts and "
                f"{len(user_data['comments'])} comments\n"
            )
            self.update_progress(50, stats)

            # Analyze user data
            self.update_progress(70, "Analyzing user data with AI...")
            analyzer = PersonaAnalyzer()
            persona = analyzer.analyze_user(user_data)

            # Format output
            self.update_progress(90, "Formatting results...")
            output_text = format_output(username, persona)

            # Save to file
            filename = f"{sanitize_filename(username)}.txt"
            output_path = os.path.join(config.OUTPUT_DIR, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_text)

            # Display results
            self.update_progress(100, f"Analysis complete! Saved to {filename}")
            self.display_results(output_text)

            # Enable save button
            self.root.after(0, lambda: self.save_btn.config(state="normal"))

        except Exception as e:
            error_msg = str(e)
            self.update_progress(0, f"Error: {error_msg}")
            self.root.after(
                0, lambda msg=error_msg: messagebox.showerror("Analysis Error", msg)
            )
        finally:
            self.root.after(0, lambda: self.analyze_btn.config(state="normal"))

    def update_progress(self, value, message):
        """
        Update progress bar and status message.

        Args:
            value: Progress value (0-100).
            message: Status message to display.
        """
        self.root.after(0, lambda: self.progress_var.set(value))
        self.root.after(0, lambda: self.status_var.set(message))

    def display_results(self, text):
        """
        Display results in text area.

        Args:
            text: The text content to display.
        """
        self.root.after(0, lambda: self.results_text.insert(1.0, text))

    def save_analysis(self):
        """Save analysis to a custom location."""
        text = self.results_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No analysis to save")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="reddit_persona_analysis.txt",
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Success", f"Analysis saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def clear_results(self):
        """Clear all results from the display."""
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Ready to analyze")
        self.save_btn.config(state="disabled")

    def view_saved_analyses(self):
        """Open window to view previously saved analyses."""
        saved_window = tk.Toplevel(self.root)
        saved_window.title("Saved Analyses")
        saved_window.geometry("600x400")

        # List frame
        list_frame = tk.Frame(saved_window)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Listbox with scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, font=("Arial", 11), height=15
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        # Load saved files
        output_files = sorted(
            Path("output").glob("*.txt"), key=os.path.getmtime, reverse=True
        )

        file_paths = []
        for file_path in output_files:
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            display_text = (
                f"{file_path.stem} - " f"{mod_time.strftime('%Y-%m-%d %H:%M')}"
            )
            listbox.insert(tk.END, display_text)
            file_paths.append(file_path)

        # View button
        def view_selected():
            """View the selected saved analysis."""
            selection = listbox.curselection()
            if selection:
                file_path = file_paths[selection[0]]
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, content)
                self.save_btn.config(state="normal")
                saved_window.destroy()

        tk.Button(
            saved_window,
            text="View Selected",
            command=view_selected,
            font=("Arial", 11),
            bg=self.reddit_orange,
            fg="white",
            cursor="hand2",
        ).pack(pady=10)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    _ = RedditPersonaAnalyzerGUI(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
