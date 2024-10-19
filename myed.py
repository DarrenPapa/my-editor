import tkinter as tk
from os.path import isfile, join, isdir
from os import name as system_name, getenv, mkdir
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
from tkinter import filedialog as fd
import json
import re
import webbrowser as wb
from __main__ import __builtins__ as _builtins

# Default configuration for syntax highlighter
default_config = {
    "tags": {
        "notes": {
            "title": {
                "config":{
                    "font":["tkDefaultFont", 25, "bold"]
                },
                "regex":"(\\n<.*?>|^\\n<.*?>)"
            },"section": {
                "config":{
                    "font":["tkDefaultFont", 17]
                },
                "regex":"\\n%[^\\n]+"
            },
            "quotes": {
                "config":{
                    "foreground":"green"
                },
                "regex":"\"[^\"]+?\""
            },
            "links": {
                "config":{
                    "foreground":"blue"
                },
                "regex":"\\[[^\\]]+\\]",
                "on_click":"webbrowser.open(self[1:-1])"
            }
        },
        "python":{
            "comments":{
                "config":{
                    "foreground":"grey"
                },
                "regex":"\\#[^\\n]+"
            },
            "keywords":{
                "config":{
                    "foreground":"blue"
                },
                "regex":"\\b(for|import|def|in|if|while|return|else|try|lambda|assert|match|case|finally|except|None|True|False|class|raise)\\b"
            },
            "strings":{
                "config":{
                    "foreground":"green"
                },
                "regex":"f?(\"[^\"\\n]*?\"|'[^'\\n]*?')"
            },
            "numbers":{
                "config":{
                    "foreground":"orange"
                },
                "regex":"-?\\d+(\\.\\d+)?"
            },
            "builtins_functions":{
                "config":{
                    "foreground":"grey"
                },
                "regex":"\\b(print|input|exit|sum|type|hash|map|filter|max|min|any)\\b"
            },
            "decorators":{
                "config":{
                    "foreground":"magenta"
                },
                "regex":"@[\\w\\.]+"
            },
            "objects":{
                "config":{
                    "foreground":"purple"
                },
                "regex":"\\b(int|float|object|str|bool|complex|Exception|BaseException|self|cls)\\b"
            },
            "exceptions":{
                "config":{
                    "font":["monospace", 11, "italic"],
                    "foreground":"purple"
                },
                "regex":"\\b(Runtime|ZeroDivision|FloatingPoint|Lookup|Index|Key|FileNotFound|IO|Assertion|Memory|OS|Permission|FileExists|Overflow|Recusion|Import|Type|Value|EOF|)Error|(KeyboardInterrupt|StopIteration|SystemExit)\\b"
            }
        }
    },
    "line_numbers":False,
    "defauult_syntax":"notes"
}

home = f"C:\\Users\\{getenv('USERNAME')}" if system_name == "nt" else "~\\.config"
if not isdir(home) and system_name != "nt":
    mkdir(home)
setup_file = join(home, "myed_config.json")

def save_config():
    with open(setup_file, "w") as f:
        f.write(json.dumps(config, indent=4))

def load_config():
    if not isfile(setup_file):
        with open(setup_file, "w") as f:
            f.write(json.dumps(default_config, indent=4))
    with open(setup_file, "r") as f:
        data = json.loads(f.read())
    return data

config = load_config()

app = tk.Tk()
app.title("My editor [0]")

def hash_file(filepath):
    if filepath is None or not isfile(filepath):
        return "---"
    with open(filepath, 'r') as f:
        return hash(f.read() + '\n')

def hash_text(text):
    return hash(text)

def convert_bytes(byte):
    """Convert bytes to appropriate units"""
    if byte < 1e3:
        return byte, "B"
    elif byte < 1e6:
        return byte * 1e-3, "KB"
    elif byte < 1e9:
        return byte * 1e-6, "MB"
    elif byte < 1e12:
        return byte * 1e-9, "GB"
    elif byte < 1e15:
        return byte * 1e-12, "TB"
    else:
        return byte * 1e-15, "PB"

class myApp:
    def __init__(self, root):
        self.syntax = True
        self.root = root
        self.frame = tk.Frame(root)
        self.current_edit = 0
        self.show_line_numbers = config["line_numbers"]  # Toggle flag
        self.line_numbers = tk.Text(self.frame, width=4, padx=3, takefocus=0, border=0, background='lightgray', state='disabled', wrap='none', bg="silver")
        self.immortal_label = tk.Label(self.frame, text="[New file]", bg="silver", fg="black")
        self.line_numbers.tag_configure("right", justify="right")
        self.texts = []
        self.push_new_text()
        self.texts[0]["text"].insert("1.0", """< This is MyEd (My Editor) >

% This is a simple editor

    and yes this is a custom markup language.
    My github is here [https://github.com/DarrenPapa/]

% How to use
    
    The keybinds might bug the text!

    ctrl-o = Open a file
    ctrl-s = Save a file
    strl-shift-s= Save as
    ctrl-x = Close the current window, if its the last one it will clear it.
    ctrl-n = New window.
    ctrl-l = Goto the next window.
    ctrl-k = Goto the previous window.
    ctrl-shift-k = Reload config and syntax highlighting.
    ctrl-shift-alt-s = Toggle syntax highlighting. (After renable configs must be reloaded)
    ctrl-t = Set the title of the current window.
    ctrl-shift-l = List all the windows.
    ctrl-g = Go to a specific line.
    ctrl-n = Toggle line numbers.

% Info

    Find the config either in C:\\Users\\(your username)\\myed_config.json""")
        self.highlight_syntax()

        self.frame.pack(fill=tk.BOTH, expand=True)
        self.immortal_label.config(text=self.texts[self.current_edit]["label"])
        if config["line_numbers"]:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.info_widgets = [self.immortal_label]

        # Bindings
        self.root.bind("<Control-k>", self.l_switch)
        self.root.bind("<Control-l>", self.r_switch)
        self.root.bind("<Control-n>", self.push_new_text)
        self.root.bind("<Control-t>", self.set_title)
        self.root.bind("<Control-s>", self.save)
        self.root.bind("<Control-p>", self.run_code)
        self.root.bind("<Control-S>", self.save_as)
        self.root.bind("<Control-o>", self.open)
        self.root.bind("<Control-x>", self.pop)
        self.root.bind("<Control-Shift-L>", self.list)
        self.root.bind("<Control-Shift-N>", self.toggle_line_numbers)
        self.root.bind("<Control-Shift-K>", self.refresh)
        self.root.bind("<Control-Shift-S>", self.save_as)
        self.root.bind("<Control-Alt-Shift-S>", self.toggle_syntax)
        self.root.bind("<Control-Alt-s>", self.set_syntax)
        self.root.bind("<Control-Alt-r>", self.display)
        self.root.bind("<Control-r>", self.read_only)
        def what(event):
            global config
            config = default_config
            save_config()
        self.root.bind("<Control-Alt-r>", what)
        self.root.bind("<Control-R>", self.disable_read_only)
        self.root.bind("<Control-g>", self.goto_line)
        self.update()

        self.texts[0]["text"].config(state="disabled")

    def run_code(self, _=None):
        code = self.texts[self.current_edit]["text"].get("1.0", tk.END)
        window = tk.Toplevel(self.root)
        output = tk.Text(window)
        output.pack(fill=tk.X, expand=True)
        builtins = _builtins.__dict__.copy()
        def this(*_, **__):
            "Replacement for unimplemented or blocked features."
            raise RuntimeError("This feature may not be used!")
        builtins["open"] = builtins["__import__"] = this
        builtins["exit"] = window.destroy
        def my_print(*text, end="\n", sep=" "):
            output.insert("1.0", f"{sep.join(map(str, text))}{end}")
        def my_input(prompt=""):
            return sd.askstring("Input", str(prompt)) or ""
        try:
            exec(
                compile(code, self.texts[self.current_edit]['label'] or "<script>", "exec"), {
                    "_editor":self,
                    "_window":window,
                    "_output":output,
                    "print":my_print,
                    "input":my_input,
                    "__builtins__":builtins
                }
            )
            window.destroy()
        except Exception as e:
            mb.showerror("Oh no!", repr(e))
            window.destroy()

    def toggle_syntax(self, _=None):
        self.syntax = not self.syntax

    def set_syntax(self, _=None):
        while True:
            text = sd.askstring("Syntax", f"Available:\n{chr(10).join(config['tags'].keys())}\n\nSyntax Name")
            if text == None:
                break
            if text not in config["tags"]:
                mb.showwarning("Not found", "Couldnt find syntax!")
            else:
                break
        self.texts[self.current_edit]["syntax"] = text

    def refresh(self, _=None):
        global config
        config = load_config()
        self.hide(self.current_edit)
        self.load(self.current_edit)
        self.highlight_syntax()

    def load(self, index):
        self.line_numbers.pack_forget()
        self.immortal_label.config(text=self.texts[index]["label"] if self.texts[index]["label"] is not None else "[New file]")
        self.immortal_label.pack(fill=tk.X)
        self.texts[index]["text"].pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.texts[index]["text"].focus_set()
        if self.show_line_numbers:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        # Highlight syntax in the text widget
        self.highlight_syntax()

    def hide(self, index):
        self.immortal_label.pack_forget()
        self.texts[index]["text"].config(state="normal")
        self.texts[index]["text"].pack_forget()
        self.line_numbers.pack_forget()

    def switch(self, index):
        self.hide(self.current_edit)
        self.current_edit = index
        self.load(self.current_edit)

    def list(self, _=None):
        temp = []
        maxc = len(str(max(map(len, map(lambda x: x["label"] or "", self.texts)))))
        for pos, i in enumerate(self.texts):
            content_preview = i['text'].get("1.0", "1.30").strip().replace("\n", " ")
            temp.append(f"({(i['label'] or '[New file]').rjust(maxc)}) : {content_preview}...")
        mb.showinfo("Windows:", f"{len(self.texts)} Windows\nCurrent Index: {self.current_edit}", detail="\n".join(temp))

    def l_switch(self, _=None):
        if self.current_edit <= 0:
            return
        self.switch(self.current_edit - 1)

    def r_switch(self, _=None):
        if self.current_edit >= len(self.texts) - 1:
            return
        self.switch(self.current_edit + 1)

    def display(self, _, file=None):
        if file is None:
            file = fd.askopenfilename()
        if not isfile(file):
            mb.showerror("Error!", "Invalid file!")
            return
        with open(file) as f:
            self.push_new_text()
            self.texts[self.current_edit]['text'].insert("1.0", f.read())
            self.texts[self.current_edit]['text'].config(state="disabled")
            self.highlight_syntax(self.texts[self.current_edit]['text'])  # Highlight syntax after loading

    def read_only(self, _=None):
        self.texts[self.current_edit]['text'].config(state="disabled")

    def disable_read_only(self, _=None):
        self.texts[self.current_edit]['text'].config(state="normal")

    def open(self, _=None):
        file = fd.askopenfile()
        if file is None:
            return
        self.push_new_text()
        with file as f:
            self.texts[self.current_edit]["text"].delete("1.0", tk.END)
            self.texts[self.current_edit]["text"].insert("1.0", f.read())
            self.texts[self.current_edit]["label"] = f.name
            self.immortal_label.config(text=f.name)
            self.highlight_syntax(self.texts[self.current_edit]["text"])  # Highlight syntax after opening

    def save(self, _=None):
        title = self.texts[self.current_edit]["label"]
        if title is None:
            self.save_as()
            return
        text = self.texts[self.current_edit]["text"].get("1.0", tk.END).strip()
        if title and title != "New file":
            with open(title, "w") as f:
                f.write(text)

    def save_as(self, _=None):
        path = fd.asksaveasfilename(title="Choose a file name to save as")
        if path:
            self.texts[self.current_edit]["label"] = path
            self.immortal_label.config(text=path)
            text = self.texts[self.current_edit]["text"].get("1.0", tk.END).strip()
            with open(path, "w") as f:
                f.write(text)

    def toggle_line_numbers(self, _=None):
        """Toggle the line number visibility."""
        self.show_line_numbers = not self.show_line_numbers
        if self.show_line_numbers:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.line_numbers.pack_forget()

    def push_new_text(self, _=None):
        self.texts.append({
            "label": None,
            "text": tk.Text(self.frame, wrap="none", undo=True, fg="black"),
            "syntax": config.get("defauult_syntax")
        })
        self.switch(len(self.texts) - 1)

    def pop(self, _=None):
        self.hide(self.current_edit)
        if len(self.texts) <= 1:
            self.load(self.current_edit)
            self.texts[self.current_edit]["label"] = None
            self.texts[self.current_edit]["text"].delete("1.0", tk.END)
            self.texts[self.current_edit]["syntax"] = "Notes"
            return
        self.texts.pop(self.current_edit)
        self.current_edit = min(self.current_edit, len(self.texts) - 1)
        self.refresh()

    def set_title(self, _=None):
        title = sd.askstring("Title", "New title:")
        if title is not None and title.strip():
            self.texts[self.current_edit]["label"] = title.strip()
            self.immortal_label.config(text=title.strip())

    def highlight_syntax(self, _=None):
        """Highlight syntax based on the current text widget's configuration."""
        # Clear previous tags
        if self.texts[self.current_edit]["syntax"] is None:
            return
        state = self.texts[self.current_edit]["text"].cget("state")
        if state == "disabled":
            self.texts[self.current_edit]["text"].config(state="normal")
        text_widget = self.texts[self.current_edit]["text"]
        for tag in text_widget.tag_names():
            text_widget.tag_remove(tag, "1.0", tk.END)

        # Get the current syntax configuration
        syntax_config = config["tags"][self.texts[self.current_edit]["syntax"]]

        # Apply new syntax highlighting
        for tag_name, settings in syntax_config.items():
            if (temp_regex:=settings["regex"]):
                pattern = re.compile(settings["regex"])
                for match in pattern.finditer(text_widget.get("1.0", tk.END)):
                    start_index = f"1.0 + {match.start()} chars"
                    end_index = f"1.0 + {match.end()} chars"
                    text_widget.tag_add(str(match.group()), start_index, end_index)
                    text_widget.tag_config(str(match.group()), **settings["config"])
                    text_widget.tag_bind(str(match.group()), "<Button-1>", lambda _: exec(settings.get("on_click", ""), {**globals(), **locals(), "self":match.group(), "webbrowser":wb}))
        if state == "disabled":
            self.texts[self.current_edit]["text"].config(state=state)
        if self.syntax:
            self.root.after(100, self.highlight_syntax)

    def goto_line(self, _=None):
        line = sd.askinteger("Goto Line", "Line number:", initialvalue=self.texts[self.current_edit]['text'].index(tk.INSERT).split('.', 1)[0])
        if line is not None:
            self.texts[self.current_edit]["text"].mark_set("insert", f"{line}.0")

    def update(self):
        """Update loop."""
        if self.show_line_numbers:
            text_widget = self.texts[self.current_edit]["text"]
            line_count = int(text_widget.index('end-1c').split('.')[0])
            if line_count >= 10_000:
                return
            line_number_content = "\n".join(str(i) for i in range(1, line_count + 1))

            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', tk.END)
            self.line_numbers.insert('1.0', line_number_content, "right")
            self.line_numbers.yview_moveto(float(self.texts[self.current_edit]["text"].yview()[0]))
            self.line_numbers.config(state='disabled')


        saved = "Saved" if hash_file(self.texts[self.current_edit]['label']) == hash_text(self.texts[self.current_edit]['text'].get("1.0", tk.END)) else "Unsaved"
        size = convert_bytes(len(self.texts[self.current_edit]['text'].get("1.0", tk.END)))
        self.root.title(f"My editor [{self.current_edit}] {saved} | {self.texts[self.current_edit]['text'].cget("state")} : {self.texts[self.current_edit]['label'] or '<'+self.texts[self.current_edit]['text'].get('1.0', '1.30')+'>' or '???'} - {size[0]:,.2f}{size[1]}")

        self.root.after(10, self.update)

app_instance = myApp(app)
app.mainloop()
