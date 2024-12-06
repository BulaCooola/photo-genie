import tkinter as tk
from tkinter import messagebox, Scrollbar, ttk


class ThemesTab:
    def __init__(self, notebook, gemini, dbfuncs):
        self.gemini = gemini
        self.dbfuncs = dbfuncs

        self.frame = tk.Frame(notebook)

        # Label for Title
        label = ttk.Label(
            self.frame,
            text="Generate Photography Theme",
            font=("Helvetica", 14),
        )
        label.pack(pady=10)

        # Canvas setup
        self.theme_canvas = tk.Canvas(self.frame)
        self.theme_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.theme_inner_frame = tk.Frame(self.theme_canvas)

        # Add a vertical scrollbar
        theme_scrollbar = Scrollbar(self.theme_inner_frame, orient="vertical")
        self.theme_canvas.config(yscrollcommand=theme_scrollbar.set)
        theme_scrollbar.config(command=self.theme_canvas.yview)
        theme_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.theme_canvas.pack(side=tk.LEFT)
        self.theme_canvas.create_window(
            0, 0, window=self.theme_inner_frame, anchor="nw"
        )
        self.theme_inner_frame.bind(
            "<Configure>",
            lambda e: self.theme_canvas.configure(
                scrollregion=self.theme_canvas.bbox("all")
            ),
        )

        # Button to generate theme
        self.theme_button = ttk.Button(
            self.theme_canvas,
            text="Generate Theme",
            command=self.process_generate_theme,
        )
        self.theme_button.pack(pady=5)

        # Frame where generated themes will go
        self.theme_container = tk.Frame(self.theme_inner_frame)
        self.theme_container.pack(fill=tk.BOTH, expand=True)

        # Add a button to load saved themes
        self.load_button = tk.Button(
            self.theme_canvas,
            text="Load Saved Themes",
            command=self.load_saved_themes,
        )
        self.load_button.pack(pady=5)

        # Frame where saved themes go
        self.saved_themes_frame = tk.Frame(self.theme_inner_frame)
        self.saved_themes_frame.pack(fill=tk.BOTH, expand=True, pady=60)

    def process_generate_theme(self):
        """
        Generate a photography theme using the provided function
        and display it in the output text widget.
        """
        # Clear the existing theme frame (if any)
        for widget in self.theme_container.winfo_children():
            widget.destroy()

        try:
            # Call gemimi function to generate themes
            themes = self.gemini.generate_theme()

            # Validate themes and type
            if themes and isinstance(themes, dict):
                # Iterate through all themes
                for key, theme in themes.items():
                    if key != "critique_date":
                        # Create frame for each theme
                        theme_frame = tk.Frame(self.theme_container)
                        theme_frame.pack(fill=tk.X, pady=5)

                        # Display theme text
                        theme_label = tk.Label(
                            theme_frame,
                            text=f"{key}: {theme}",
                            wraplength=400,
                            justify=tk.LEFT,
                        )
                        theme_label.pack(side=tk.LEFT, padx=10)

                        # Save button for theme
                        save_button = tk.Button(theme_frame, text="Save Theme")
                        save_button.config(
                            command=lambda b=save_button, k=key, t=theme: self.save_theme_to_db(
                                b, k, t
                            )
                        )
                        save_button.pack(side=tk.RIGHT)

        except Exception as e:
            print(f"Error generating themes: {e}")
            messagebox.showerror("Error", "An error occurred while generating themes.")

    def load_saved_themes(self):
        """
        Load saved themes from database and display them
        """
        # Clear frame
        for widget in self.saved_themes_frame.winfo_children():
            widget.destroy()

        try:
            saved_themes = self.dbfuncs.getAllThemes()
            if not saved_themes:
                messagebox.showinfo("Info", "No saved themes found")
                return

            # Title for saved themes section
            saved_themes_label = tk.Label(
                self.saved_themes_frame,
                text="Saved Themes",
                font=("Ariel", 14, "bold"),
                pady=5,
            )
            saved_themes_label.pack()

            # Add each theme
            for theme in saved_themes:
                # Make another frame to house both theme name and description separately
                theme_row_frame = tk.Frame(self.saved_themes_frame)
                theme_row_frame.pack(fill=tk.BOTH, pady=5)

                # Theme name label
                theme_name_label = tk.Label(
                    theme_row_frame,
                    text=theme["theme_name"],
                    font=("Arial", 10, "bold"),
                    anchor="w",
                    width=20,
                )
                theme_name_label.pack(side=tk.LEFT, padx=10)

                # Description label
                description_label = tk.Label(
                    theme_row_frame,
                    text=theme["description"],
                    anchor="w",  # Align text to the left
                    wraplength=400,  # Allow text wrapping
                )
                description_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        except Exception as e:
            print(f"Error loading saved themes: {e}")
            messagebox.showerror("Error", f"Error loading saved themes: {e}")

    def save_theme_to_db(self, button, theme_name, theme_description):
        """
        Save the selected theme to the database.

        :param button: button widget for respective theme
        :type button: Button
        :param theme_name: The name of the theme
        :type theme_name: str
        :param theme_description: Description of what the theme is
        :type theme_description: str
        """
        try:
            # Call your database save function (adjust as needed)
            self.dbfuncs.add_theme(theme_name, theme_description)
            button.config(state=tk.DISABLED)  # Disable the button after saving
            messagebox.showinfo("Success", f"Theme saved: {theme_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme: {e}")
