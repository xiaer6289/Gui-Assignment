import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
from datetime import datetime
import json
import os
import re
import webbrowser
from PIL import Image, ImageTk

# ===================================================================
#                         NOTE CLASSES
# ===================================================================
class Note:
    def __init__(self, title, content, tags="", category="Uncategorized"):
        self.__title = title
        self.__content = content
        self.__tags = tags
        self.__category = category
        self.__last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_title(self):
        return self.__title

    def set_title(self, title):
        self.__title = title

    def get_content(self):
        return self.__content

    def set_content(self, content):
        self.__content = content

    def get_tags(self):
        return self.__tags

    def set_tags(self, tags):
        self.__tags = tags

    def get_category(self):
        return self.__category

    def set_category(self, category):
        self.__category = category

    def get_last_modified(self):
        return self.__last_modified

    def set_last_modified(self):
        self.__last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # convert note to dictionary for saving to JSON
    def to_dict(self):
        return {
            "type": self.__class__.__name__,  # automatically saves the class name (e.g., TextNote or ImageNote) so we know the note type when loading
            "title": self.get_title(),
            "content": self.get_content(),
            "tags": self.get_tags(),
            "category": self.get_category(),
            "last_modified": self.get_last_modified()
    }

    # convert dictionary from JSON back to note
    @staticmethod
    def from_dict_to_note(data):
        note_type = data.get("type", "TextNote")

        if note_type == "ImageNote":
            note = ImageNote(
                data.get("title", ""),
                data.get("content", ""),
                data.get("image_path", ""),
                data.get("tags", ""),
                data.get("category", "Uncategorized")
            )
        else:
            note = TextNote(
                data.get("title", ""),
                data.get("content", ""),
                data.get("tags", ""),
                data.get("category", "Uncategorized")
            )
        
        # set last_modified from saved data instead of using setter, 
        # so it keeps original time
        note._Note__last_modified = data.get("last_modified", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return note


class TextNote(Note):
    # no extra fields, just inherits everything from note
    pass

class ImageNote(Note):
    # inherits from note class
    def __init__(self, title, content, image_path="", tags="", category="Uncategorized"):
        super().__init__(title, content, tags, category)
        self.__image_path = image_path

    def get_image_path(self):
        return self.__image_path

    def set_image_path(self, path):
        self.__image_path = path

    def to_dict(self):
        data = super().to_dict()
        data["image_path"] = self.__image_path
        return data


# ===================================================================
#                         APP CLASS
# ===================================================================
class Note_Organizer:
    def __init__(self, root):
        """Initialize the NoteApp"""  
        self.root = root
        root.title("Note Organizer 📝")

        menubar = tk.Menu(self.root)
        self.root.config(menu = menubar)

        exitMenu = tk.Menu(menubar, tearoff = 0)
        exitMenu.add_command(label = "Return", command = self.return_to_main)
        exitMenu.add_command(label = "Quit", command = self.root.destroy)
        menubar.add_cascade(label = "Exit", menu = exitMenu)

        app_width, app_height = 700, 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (app_width // 2)
        y = (screen_height // 2) - (app_height // 2)
        root.geometry(f"{app_width}x{app_height}+{x}+{y}")
        
        self.notes = []
        self.selected_note_index = None
        self.categories = ["Uncategorized"] # default category

        self.image_window = None

        self.setup_ui()
        self.read_file()

    # ==============================
    # UI SETUP
    # ==============================
    def setup_ui(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # create a paned window (split container) for left and right sections
        paned = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ---------- Left Panel ----------
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="All Notes", font=('Arial', 12, 'bold')).pack(pady=5)

        # Search bar
        search_frame = ttk.Frame(left)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar() # bind to search entry
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X, padx=(5, 0))
        self.search_var.trace('w', self.refresh_list) # when search_var changes, call refresh_list function

        # Category filter
        filter_frame = ttk.Frame(left)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT)
        self.filter_category_var = tk.StringVar(value="All")
        self.filter_dropdown = ttk.OptionMenu(filter_frame, self.filter_category_var, "All")
        self.filter_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_category_var.trace("w", self.refresh_list)

        # Notes list
        listbox_frame = ttk.Frame(left)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=('Arial', 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.load_note)

        ttk.Button(left, text="New Note", command=self.new_note).pack(fill=tk.X, padx=5, pady=5)

        # ---------- Right Panel ----------
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        editor = ttk.LabelFrame(right, text="Note Editor", padding="10")
        editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        editor.columnconfigure(1, weight=1)
        editor.rowconfigure(1, weight=1)

        # Title
        ttk.Label(editor, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title = ttk.Entry(editor, width=50)
        self.title.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)

        # Content
        ttk.Label(editor, text="Content:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=2)
        self.content = scrolledtext.ScrolledText(editor, width=50, height=15, wrap=tk.WORD)
        self.content.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=2)
        # Detect links when typing
        self.content.bind("<KeyRelease>", lambda e: self.make_links_clickable(self.content.get("1.0", tk.END)))

        # Tags
        ttk.Label(editor, text="Tags:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tags = ttk.Entry(editor, width=50)
        self.tags.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)

        # Category dropdown
        ttk.Label(editor, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.OptionMenu(editor, self.category_var, None)
        self.category_dropdown.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.update_category_dropdown()

        # Image path + Browse
        img_row = ttk.Frame(editor)
        img_row.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(6, 2))
        ttk.Label(editor, text="Image Path :").grid(row=4, column=0, sticky=tk.W, pady=(6, 2))
        self.image_entry = ttk.Entry(img_row)
        self.image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(img_row, text="Browse…", command=self.browse_image).pack(side=tk.LEFT, padx=6)
        ttk.Button(img_row, text="Open Image", command=self.open_image).pack(side=tk.LEFT, padx=6)

        # Action buttons frame
        button_frame = ttk.Frame(editor)
        button_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        button_frame.columnconfigure(0, weight=1) 
        button_frame.columnconfigure(1, weight=0)
        button_frame.columnconfigure(2, weight=0)

        # Last Modified label
        self.last_modified_label = ttk.Label(button_frame, text="Last Modified: -")
        self.last_modified_label.grid(row=0, column=0, sticky="w")

        # Save Note button
        self.save_button = tk.Button(button_frame, text="💾Save Note", 
                             command=self.save_note, 
                             bg="#4CAF50", fg="white", 
                             activebackground="#45a049") 
        self.save_button.grid(row=0, column=1, padx=5, sticky="e")

        # Delete Note button
        self.delete_button = tk.Button(button_frame, text="❌Delete Note", 
                               command=self.delete_note, 
                               bg="#f44336", fg="white", 
                               activebackground="#e53935") 
        self.delete_button.grid(row=0, column=2, padx=5, sticky="e")

    # ===================================================================
    # FILE HANDLING
    # ===================================================================
    
    # read notes from JSON file
    def read_file(self):
        try:
            if os.path.exists("notes.json") and os.path.getsize("notes.json") > 0:
                with open("notes.json", "r", encoding="utf-8") as f:
                    data = json.load(f) # load the JSON file
                    self.notes = [Note.from_dict_to_note(note) for note in data]
            
            else:
                self.notes = []


            # collect all categories from existing notes 
            category = set(note.get_category() for note in self.notes)
            self.categories = ["Uncategorized"] + sorted(category)

            # refresh the ui elements for categories and notes list(left panel)
            self.update_category_dropdown()
            self.refresh_list()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read notes: {e}")

    # write notes to JSON file
    def write_notes_to_file(self):
        try:
            with open("notes.json", "w", encoding="utf-8") as f:
                json.dump([note.to_dict() for note in self.notes], f, indent=4, ensure_ascii=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notes: {e}")

    # ===================================================================
    # CATEGORY MANAGEMENT
    # ===================================================================
    def update_category_dropdown(self):
        # refresh category dropdown menu
        menu = self.category_dropdown["menu"]
        menu.delete(0, "end")

        menu.add_command(label="➕ Add Category", command=self.add_category)

        for category in sorted(set(self.categories)):
             # using lambda to let system remember this category
             # so system knows which one is clicked
            menu.add_command(label=category, command=lambda value=category: self.category_var.set(value))

        if self.categories:
            # set default category as the fisrt value which is uncategorized
            self.category_var.set(self.categories[0])


        # update filter dropdown (left panel)
        filter_menu = self.filter_dropdown["menu"]
        filter_menu.delete(0, "end") 
        filter_menu.add_command(label="All", command=lambda: self.filter_category_var.set("All"))
        # list other categories
        for category in sorted(set(self.categories)):
            filter_menu.add_command(label=category, command=lambda value=category: self.filter_category_var.set(value))

    def add_category(self):
        new_cat = simpledialog.askstring(" ", "Enter new category:")
        if new_cat and new_cat not in self.categories:
            self.categories.append(new_cat)
            self.update_category_dropdown()
            self.category_var.set(new_cat)

    # ===================================================================
    # NOTE CRUD
    # ===================================================================
    def save_note(self):
        title = self.title.get().strip()
        content = self.content.get("1.0", tk.END).strip()
        tags = self.tags.get().strip()
        category = self.category_var.get().strip()
        image_path = self.image_entry.get().strip()

        if not title.strip() or not content.strip():
            messagebox.showwarning("Warning", "Title and content cannot be empty.")
            return

        # check for duplicate title
        for i, note in enumerate(self.notes):
            if note.get_title() == title and i != self.selected_note_index:
                messagebox.showwarning("Warning", f"Title '{title}' already exists!")
                return
            
        if image_path:
            new_note = ImageNote(title, content, image_path, tags, category)
        else:
            new_note = TextNote(title, content, tags, category)

        new_note.set_last_modified()

        # update existing note
        if self.selected_note_index is not None:
            # update categories list if added new category
            if category not in self.categories:
                self.categories.append(category)

            # replace existing note with changed note
            self.notes[self.selected_note_index] = new_note

            self.write_notes_to_file()
            self.update_category_dropdown()
            self.refresh_list()

            messagebox.showinfo("Success", "Note updated successfully!")
        
        # add new note
        else:
            if category not in self.categories:
                self.categories.append(category)
            self.notes.append(new_note)
            self.write_notes_to_file()
            self.update_category_dropdown()
            self.clear_editor()
            self.refresh_list()
            messagebox.showinfo("Success", "Note added successfully!")

    # refresh left panel including note list with search filter
    def refresh_list(self, *args):
        self.clear_editor()
        
        search = self.search_var.get().lower()
        filter_cat = self.filter_category_var.get()
        self.listbox.delete(0, tk.END)

        # check if the note matches the search keyword and category
        # 1. not search - True if search box is empty
        # 2. any(...) - True if the keyword is found in title or tags
        for note in self.notes:
            fields = [note.get_title(), note.get_tags()]

            match_search = (not search or any(search in (field or "").lower() for field in fields))
            
            # check if the note matches the selected category
            # if filter_cat is all, show everything
            match_category = (filter_cat == "All" or note.get_category() == filter_cat)

            if match_search and match_category:
                self.listbox.insert(tk.END, note.get_title())

    # get matching note indices after searching
    def search_note_indices(self):
        keyword = self.search_var.get().lower()
        filter_cat = self.filter_category_var.get()
        
        matching_indices = []

        for i, note in enumerate(self.notes):
            fields = [note.get_title(), note.get_tags()]
            match_search = (not keyword or any(keyword in (field or "").lower() for field in fields))
            match_category = (filter_cat == "All" or note.get_category() == filter_cat)

            if match_search and match_category:
                matching_indices.append(i)

        return matching_indices
    
    # load selected note into editor
    def load_note(self, event=None):
        selected_items = self.listbox.curselection()   
        if not selected_items:
            return

        visible_idx = selected_items[0] # index in the visible filtered list
        mapping = self.search_note_indices() # get the actual indices of notes after filtering
        if visible_idx >= len(mapping):
            return  # exit if the selected index is out of range
        i = mapping[visible_idx] # map back to actual index in self.notes

        self.selected_note_index = i
        note = self.notes[i]

        self.title.delete(0, tk.END)
        self.title.insert(0, note.get_title())

        self.content.delete(1.0, tk.END)
        self.content.insert(1.0, note.get_content())
        self.make_links_clickable(note.get_content())

        self.tags.delete(0, tk.END)
        self.tags.insert(0, note.get_tags())

        self.category_var.set(note.get_category())

        if isinstance(note, ImageNote):
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, note.get_image_path())
        else:
            self.image_entry.delete(0, tk.END)

        self.last_modified_label.config(text=f"Last Modified: {note.get_last_modified()}")

    def new_note(self):
        self.selected_note_index = None
        self.clear_editor()
        self.title.focus()

    def clear_editor(self):
        self.title.delete(0, tk.END)
        self.content.delete(1.0, tk.END)
        self.tags.delete(0, tk.END)
        if self.categories:
            self.category_var.set(self.categories[0])
        self.image_entry.delete(0, tk.END)
        self.last_modified_label.config(text="Last Modified: -")
        
    def delete_note(self):
        if self.selected_note_index is not None:
            title = self.notes[self.selected_note_index].get_title()
            del self.notes[self.selected_note_index]
            self.selected_note_index = None
            self.write_notes_to_file()
            self.clear_editor()
            self.refresh_list()
            messagebox.showinfo("Success", f"Note deleted: {title}")

    # ===================================================================
    # LINK HANDLING
    # ===================================================================
    
    # detect URL and make them clickable
    def make_links_clickable(self, content_text):
        for tag in self.content.tag_names():
            if tag.startswith("link_"):
                self.content.tag_delete(tag)

        url_pattern = r"https?://[^\s)>\]}\"']+"

        # finditer returns the place where the pattern matches
        for m in re.finditer(url_pattern, content_text):
            start_idx = f"1.0+{m.start()}c" # start position of the URL in Text widget (Tkinter needs "line.char" format)
            end_idx = f"1.0+{m.end()}c" # end position of the URL
            tag = f"link_{m.start()}" # unique tag for each link

            self.content.tag_add(tag, start_idx, end_idx)

            self.content.tag_config(tag, foreground="blue", underline=1)
            url = m.group() 

            # open the URL when clicked
            self.content.tag_bind(tag, "<Button-1>", lambda e, u=url: webbrowser.open(u))
            # change cursor to hand when hovering
            self.content.tag_bind(tag, "<Enter>", lambda e: self.content.config(cursor="hand2"))
            # reset cursor back to text when leaving
            self.content.tag_bind(tag, "<Leave>", lambda e: self.content.config(cursor="xterm"))

    # ===================================================================
    # IMAGE FILE PICKER
    # ===================================================================
    
    # open file dialog to pick image
    def browse_image(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.path.join(os.path.expanduser("~"), "Pictures"),
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )

        # if user cancel to insert image, show warning
        if not filepath:
            messagebox.showwarning("No file", "No image selected!")
            return

        if filepath:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filepath)

    # open and display the image in a new window
    def open_image(self):
        filepath = self.image_entry.get().strip()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Invalid image path!")
            return

        try:
            # create new window
            self.image_window = tk.Toplevel(self.root)
            self.image_window.title("Image Viewer")

            self.image_window.grab_set() # make the window modal
            self.image_window.transient(self.root) 
            img = Image.open(filepath)
            img.thumbnail((700, 500))  
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(self.image_window, image=photo)
            lbl.image = photo # keep a reference to avoid garbage collection
            lbl.pack() # display image

            ttk.Button(self.image_window, text="Close", command=self.image_window.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")

    # ===================================================================
    def return_to_main(self):
        self.hasEnded = True
        for widget in self.root.winfo_children():
            widget.destroy()

        # rebuild main menu
        from Main_Menu import Main_Menu
        Main_Menu(self.root)