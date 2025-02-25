import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog

class GapBuffer:
    def __init__(self, initial_text=""):
        self.gap_size = 50  # initial extra space for insertions
        # Our buffer is a list of characters. The gap is an unused area.
        self.buffer = list(initial_text) + [""] * self.gap_size
        self.gap_start = len(initial_text)
        self.gap_end = len(initial_text) + self.gap_size
        # Build a simple line index from the initial text.
        self.line_index = [0]
        for i, ch in enumerate(initial_text):
            if ch == "\n":
                self.line_index.append(i + 1)

    def get_text(self):
        # Return the logical text (skipping the gap)
        return "".join(self.buffer[:self.gap_start] + self.buffer[self.gap_end:])

    def length(self):
        return len(self.buffer) - (self.gap_end - self.gap_start)
    def move_gap(self, pos):
        # Move the gap so that gap_start equals pos (logical position)
        if pos < self.gap_start:
            # Move gap left: copy characters from before the gap into the end of the gap.
            while self.gap_start > pos:
                self.gap_start -= 1
                self.gap_end -= 1
                self.buffer[self.gap_end] = self.buffer[self.gap_start]
                self.buffer[self.gap_start] = ""
        elif pos > self.gap_start:
            # Move gap right: copy characters from after the gap into the gap.
            while self.gap_start < pos:
                self.buffer[self.gap_start] = self.buffer[self.gap_end]
                self.buffer[self.gap_end] = ""
                self.gap_start += 1
                self.gap_end += 1

    def expand_gap(self):
        print("Expanding gap...")
        # Called when the gap is 0. Adds gap_size gap to buffer at gap_start
        extra = [""] * self.gap_size
        self.buffer[self.gap_end:self.gap_end] = extra
        self.gap_end += self.gap_size

    def insert(self, char, pos):
        if self.gap_start == self.gap_end:
            self.expand_gap()
        self.move_gap(pos)
        self.buffer[self.gap_start] = char
        self.gap_start += 1
        # If a newline is inserted, rebuild the line index.
        if char == "\n":
            self.rebuild_line_index()
            return
        for i in range(len(self.line_index)):
            if self.line_index[i] > pos:
                self.line_index[i] += 1


    def delete_backward(self, pos):
        if pos == 0:
            return
        # To delete the character immediately before pos, move the gap there.
        self.move_gap(pos)
        self.gap_start -= 1
        deleted = self.buffer[self.gap_start]
        self.buffer[self.gap_start] = ""    # Not necessary but useful for clarity
        if deleted == "\n":
            self.rebuild_line_index()
            return
        for i in range(len(self.line_index)):   # shift line index when new line is above
            if self.line_index[i] >= pos:
                self.line_index[i] -= 1

    def delete_forward(self, pos):
        if pos >= self.length():
            return
        self.move_gap(pos)
        deleted = self.buffer[self.gap_end]
        self.buffer[self.gap_end] = "" # Not necessary but useful for clarity
        self.gap_end += 1
        if deleted == "\n":
            self.rebuild_line_index()
            return
        for i in range(len(self.line_index)):
            if self.line_index[i] > pos:
                self.line_index[i] -= 1

    def rebuild_line_index(self):
        # For simplicity, rebuild the entire line index.
        text = self.get_text()
        self.line_index = [0]
        for i, ch in enumerate(text):
            if ch == "\n":
                self.line_index.append(i + 1)

    def get_line(self, line_number):
        # Returns the specified line’s text.
        text = self.get_text()
        if line_number < len(self.line_index):
            start = self.line_index[line_number]
            if line_number + 1 < len(self.line_index):
                end = self.line_index[line_number + 1]  
            else:
                end = len(text)
            line = text[start:end]
            # if line.endswith("\n"):
            #     line = line[:-1]
            return line
        else:
            return ""


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(self.root, width=900, height=600, bg="white")

        self.frm_buttons = tk.Frame(self.root, relief=tk.RAISED, bd=2)

        btn_open = tk.Button(self.frm_buttons, text="Open", command=self.open_file)
        btn_save = tk.Button(self.frm_buttons, text="Save As...", command=self.save_file)

        self.root.rowconfigure(0, minsize=800, weight=1)
        self.root.columnconfigure(1, minsize=800, weight=1)
        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_save.grid(row=1, column=0, sticky="ew", padx=5)
        self.frm_buttons.grid(row=0, column=0, sticky="ns")
        self.canvas.grid(row=0, column=1, sticky="nsew") 

        self.buffer = GapBuffer("")
        self.cursor_line = 0
        self.cursor_col = 0


        self.font = ("Courier New", 12)
        self.char_width = 10
        font_obj = tkFont.Font(family=self.font[0], size=self.font[1])
        self.line_height = font_obj.metrics("linespace")
        self.root.bind("<Key>", self.on_key_press)
        self.redraw()

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        self.canvas.delete("all")
        with open(filepath, "r", encoding="utf-8") as input_file:
            text = input_file.read()
            self.buffer = GapBuffer(text)
            self.cursor_line = 0
            self.cursor_col = 0
            self.redraw()
        self.root.title(f"Text Editor - {filepath}")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        with open(filepath, "w", encoding="utf-8") as output_file:
            output_file.write(self.buffer.get_text())
        self.root.title(f"Text Editor - {filepath}")

    def get_abs_pos(self):
        # Compute the logical (absolute) position from cursor_line and cursor_col.
        # We use the line index stored in the gap buffer.
        if self.cursor_line < len(self.buffer.line_index):
            return self.buffer.line_index[self.cursor_line] + self.cursor_col
        else:
            return self.buffer.length()

    def on_key_press(self, event):
        if event.char and event.char.isprintable():
            self.insert_char(event.char)
        elif event.keysym == "BackSpace":
            self.delete_backward()
        elif event.keysym == "Delete":
            self.delete_forward()
        elif event.keysym == "Left":
            self.move_cursor(-1, 0)
            print(self.buffer.buffer)
        elif event.keysym == "Right":
            self.move_cursor(1, 0)
            print(self.buffer.buffer)
        elif event.keysym == "Up":
            self.move_cursor(0, -1)
            print(self.buffer.buffer)
        elif event.keysym == "Down":
            self.move_cursor(0, 1)
            print(self.buffer.buffer)
        elif event.keysym == "Return":
            self.new_line()
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        # Get the full text and split into lines.
        text_body = self.buffer.get_text()
        y = 0
        self.canvas.create_text(
            10, y,
            text=text_body,
            anchor="nw",
            font=self.font
        )

        # Draw the cursor based on our stored line and column.
        cursor_x = 10 + self.cursor_col * self.char_width
        cursor_y = self.cursor_line * self.line_height
        self.canvas.create_line(
            cursor_x, cursor_y,
            cursor_x, cursor_y + self.line_height,
            fill="black", width=2
        )

    def new_line(self):
        pos = self.get_abs_pos()
        # Insert a newline character at the current position.
        self.buffer.insert("\n", pos)
        self.cursor_line += 1
        self.cursor_col = 0

    def insert_char(self, char):
        pos = self.get_abs_pos()
        self.buffer.insert(char, pos)
        self.cursor_col += 1

    def delete_backward(self):
        if self.cursor_col > 0:
            pos = self.get_abs_pos()
            self.buffer.delete_backward(pos)
            self.cursor_col -= 1
        elif self.cursor_line > 0:
            # When at the beginning of a line, delete the newline to merge lines.
            original_prev_line_length = len(self.buffer.get_line(self.cursor_line - 1))
            pos = self.get_abs_pos()
            self.buffer.delete_backward(pos)
            self.cursor_line -= 1
            # Set cursor_col to the end of the previous line.
            self.cursor_col = original_prev_line_length - 1 #ignore new line

    def delete_forward(self):    
        pos = self.get_abs_pos()
        self.buffer.delete_forward(pos)

    def move_cursor(self, dx, dy):
        # make sure the new line is within bounds
        new_line = self.cursor_line + dy 
        new_line = max(0, min(new_line, len(self.buffer.line_index) - 1)) 
        
        if dx < 0:          #if cursor is moving left
            if self.cursor_col > 0:      # and cursor is not at the beginning of the line
                new_col = self.cursor_col - 1
            else:                        # and cursor is at the beginning of the line
                if self.cursor_line > 0:  # if cursor is not at first line then go to end of previous line
                    new_line -= 1
                    new_col = len(self.buffer.get_line(new_line)) -1
                else:
                    new_col = 0
        elif dx > 0 : 
            line_text = self.buffer.get_line(new_line)
            if self.cursor_col < len(line_text) - 1: # if cursor is not at the end of the line
                new_col = self.cursor_col + 1
            else: # if cursor is at the end of the line
                if self.cursor_line < len(self.buffer.line_index) - 1: # if cursor is not at the last line then go to beginning of next line
                    new_line += 1
                    new_col = 0
                else:
                    if self.cursor_line == len(self.buffer.line_index) - 1:    # needed because last line doesn't have newline char
                        new_col = len(line_text)
                    else:
                        new_col = len(line_text) - 1
                
        else:
            if new_line == len(self.buffer.line_index) - 1:
                new_col = min(self.cursor_col, len(self.buffer.get_line(new_line)))  # needed because last line doesnt have \n 
            else:
                new_col = min(self.cursor_col, len(self.buffer.get_line(new_line)) - 1)

        self.cursor_line = new_line
        self.cursor_col = new_col

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Text Editor")
    editor = TextEditor(root)
    root.mainloop()
