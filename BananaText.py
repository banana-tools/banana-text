#!/usr/bin/env python3
"""
BananaText - A Rich Terminal Text Editor Themed After Bananas
"""

import signal
import curses
import sys
import os
from typing import List, Optional, Tuple


# Disable Ctrl+C from killing the app
signal.signal(signal.SIGINT, signal.SIG_IGN)


class BananaTheme:
    """Banana-themed color scheme"""
    PAIR_DEFAULT = 1
    PAIR_KEYWORD = 2
    PAIR_STRING = 3
    PAIR_COMMENT = 4
    PAIR_NUMBER = 5
    PAIR_FUNCTION = 6
    PAIR_STATUS = 7
    PAIR_MENU = 8
    PAIR_SELECTION = 9
    PAIR_LINE_NUM = 10
    PAIR_DIR = 11
    PAIR_FILE = 12
    PAIR_HELP = 13
    
    COLOR_BANANA_YELLOW = 11
    COLOR_BANANA_GOLD = 12
    COLOR_BANANA_BROWN = 13
    COLOR_BANANA_CREAM = 14
    COLOR_BANANA_GREEN = 15
    COLOR_DARK_BROWN = 16
    
    @classmethod
    def init_colors(cls):
        curses.start_color()
        curses.use_default_colors()
        
        curses.init_color(cls.COLOR_BANANA_YELLOW, 1000, 1000, 0)
        curses.init_color(cls.COLOR_BANANA_GOLD, 1000, 800, 200)
        curses.init_color(cls.COLOR_BANANA_BROWN, 600, 400, 200)
        curses.init_color(cls.COLOR_BANANA_CREAM, 900, 900, 800)
        curses.init_color(cls.COLOR_BANANA_GREEN, 200, 800, 300)
        curses.init_color(cls.COLOR_DARK_BROWN, 200, 100, 50)
        
        curses.init_pair(cls.PAIR_DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_KEYWORD, cls.COLOR_BANANA_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_STRING, cls.COLOR_BANANA_CREAM, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_COMMENT, cls.COLOR_BANANA_BROWN, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_NUMBER, cls.COLOR_BANANA_GOLD, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_FUNCTION, cls.COLOR_BANANA_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_STATUS, cls.COLOR_BANANA_CREAM, cls.COLOR_DARK_BROWN)
        curses.init_pair(cls.PAIR_MENU, cls.COLOR_BANANA_YELLOW, cls.COLOR_DARK_BROWN)
        curses.init_pair(cls.PAIR_SELECTION, cls.COLOR_DARK_BROWN, cls.COLOR_BANANA_YELLOW)
        curses.init_pair(cls.PAIR_LINE_NUM, 8, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_DIR, cls.COLOR_BANANA_GREEN, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_FILE, cls.COLOR_BANANA_CREAM, curses.COLOR_BLACK)
        curses.init_pair(cls.PAIR_HELP, 8, 234)


HELP_BAR_HEIGHT = 2

EDITOR_HELP = [
    "Arrows:move | Shift+Arrows:select | Enter:newline | Backspace:delete | Del:delete",
    "Ctrl+S:save | Ctrl+N:new | Ctrl+O:pick | Ctrl+F:view | Ctrl+Q:quit | F1:copy | F2:paste | F5:help"
]

VIEWER_HELP = [
    "Arrows/PgUp/PgDn:move | Home/End:line | F3:pick file | q:quit | F5:help"
]


class FilePicker:
    def __init__(self, stdscr, start_dir: str = None):
        self.stdscr = stdscr
        self.current_dir = start_dir or os.getcwd()
        self.selected_idx = 0
        self.scroll = 0
        self.files: List[Tuple[str, bool]] = []
        self.height = 0
        self.width = 0
    
    def refresh_list(self):
        self.files = []
        try:
            if self.current_dir != "/":
                self.files.append(("..", True))
            for name in sorted(os.listdir(self.current_dir)):
                path = os.path.join(self.current_dir, name)
                is_dir = os.path.isdir(path)
                self.files.append((name, is_dir))
        except:
            self.files = []
    
    def draw(self, h: int, w: int):
        self.height = h - 4
        self.width = w - 2
        
        self.stdscr.addstr(0, 1, f" 📂 {self.current_dir}".ljust(w - 2), 
            curses.color_pair(BananaTheme.PAIR_MENU) | curses.A_REVERSE)
        
        visible = self.files[self.scroll:self.scroll + self.height]
        
        for i, (name, is_dir) in enumerate(visible):
            y = i + 1
            if y >= self.height:
                break
            
            prefix = "📁 " if is_dir else "📄 "
            if i + self.scroll == self.selected_idx:
                attr = curses.color_pair(BananaTheme.PAIR_SELECTION) | curses.A_REVERSE
            elif is_dir:
                attr = curses.color_pair(BananaTheme.PAIR_DIR)
            else:
                attr = curses.color_pair(BananaTheme.PAIR_FILE)
            
            try:
                self.stdscr.addstr(y, 1, prefix + name.ljust(self.width - 4), attr)
            except:
                pass
    
    def handle_key(self, ch: int) -> Optional[str]:
        if ch in (27,):
            return None
        elif ch in (curses.KEY_ENTER, 10, 13):
            if self.files:
                name, is_dir = self.files[self.selected_idx]
                if is_dir:
                    if name == "..":
                        self.current_dir = os.path.dirname(self.current_dir)
                    else:
                        self.current_dir = os.path.join(self.current_dir, name)
                    self.selected_idx = 0
                    self.scroll = 0
                    self.refresh_list()
                else:
                    return os.path.join(self.current_dir, name)
        elif ch == curses.KEY_UP:
            self.selected_idx = max(0, self.selected_idx - 1)
        elif ch == curses.KEY_DOWN:
            self.selected_idx = min(len(self.files) - 1, self.selected_idx + 1)
        elif ch == curses.KEY_PPAGE:
            self.selected_idx = max(0, self.selected_idx - self.height)
        elif ch == curses.KEY_NPAGE:
            self.selected_idx = min(len(self.files) - 1, self.selected_idx + self.height)
        
        if self.selected_idx < self.scroll:
            self.scroll = self.selected_idx
        elif self.selected_idx >= self.scroll + self.height:
            self.scroll = self.selected_idx - self.height + 1
        
        return None
    
    def open_picker(self) -> Optional[str]:
        self.refresh_list()
        
        while True:
            h, w = self.stdscr.getmaxyx()
            self.stdscr.erase()
            self.draw(h, w)
            self.stdscr.addstr(h - 3, 1, " ↑↓ navigate | Enter:open | Esc:quit ", 
                curses.color_pair(BananaTheme.PAIR_STATUS))
            self.stdscr.refresh()
            
            ch = self.stdscr.getch()
            result = self.handle_key(ch)
            if result:
                return result
            elif result == None and ch in (27,):
                return None


class BananaText:
    def __init__(self, stdscr, view_only=False):
        self.stdscr = stdscr
        self.view_only = view_only
        self.filename: Optional[str] = None
        self.lines: List[str] = [""]
        self.modified = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.height = 0
        self.width = 0
        
        # Selection
        self.selecting = False
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        self.clipboard: List[str] = []
        
        self.keywords = {'def', 'class', 'if', 'elif', 'else', 'for', 'while', 
                    'return', 'import', 'from', 'as', 'try', 'except', 
                    'finally', 'with', 'async', 'await', 'yield', 'lambda',
                    'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'}
        
        self.init_editor()
    
    def init_editor(self):
        curses.curs_set(1)
        self.stdscr.keypad(1)
        BananaTheme.init_colors()
        self.resize()
    
    def resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.editor_height = self.height - HELP_BAR_HEIGHT - 2
        self.editor_width = self.width - 6
    
    def load_file(self, filename: str):
        try:
            with open(filename, 'r') as f:
                self.lines = f.read().splitlines()
            if not self.lines:
                self.lines = [""]
            self.filename = filename
            self.modified = False
        except Exception as e:
            self.show_message(f"Error loading file: {e}")
    
    def save_file(self, filename: Optional[str] = None):
        if filename:
            self.filename = filename
        if not self.filename:
            self.filename = self.show_input_dialog("Save as:", "")
        if self.filename:
            try:
                with open(self.filename, 'w') as f:
                    f.write('\n'.join(self.lines))
                self.modified = False
                self.show_message(f"Saved: {self.filename}")
            except Exception as e:
                self.show_message(f"Error saving file: {e}")
    
    def new_file(self):
        self.lines = [""]
        self.filename = None
        self.modified = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.clear_selection()
    
    def show_message(self, message: str):
        self.draw_status(f"🍌 {message}")
        self.stdscr.refresh()
        self.stdscr.getch()
    
    def show_input_dialog(self, prompt: str, default: str = "") -> Optional[str]:
        h, w = self.stdscr.getmaxyx()
        dialog_h = 3
        dialog_w = min(50, w-4)
        dialog_y = max(1, h//2 - dialog_h//2)
        dialog_x = max(1, (w - dialog_w) // 2)
        
        overlay = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
        overlay.bkgd(' ', curses.color_pair(BananaTheme.PAIR_MENU))
        overlay.box()
        overlay.addstr(1, 2, prompt, curses.color_pair(BananaTheme.PAIR_MENU))
        curses.curs_set(1)
        overlay.keypad(1)
        
        text = default
        pos = len(prompt) + 3
        
        while True:
            overlay.clear()
            overlay.box()
            overlay.addstr(1, 2, prompt, curses.color_pair(BananaTheme.PAIR_MENU))
            overlay.addstr(1, len(prompt) + 3, text[:dialog_w - len(prompt) - 5], curses.color_pair(BananaTheme.PAIR_DEFAULT))
            overlay.move(1, pos)
            ch = overlay.getch()
            
            if ch in (curses.KEY_ENTER, 10, 13):
                break
            elif ch in (27,):
                return None
            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                if text:
                    text = text[:-1]
                    pos = max(len(prompt) + 3, len(prompt) + 3 + len(text))
            elif 32 <= ch <= 126:
                text += chr(ch)
                pos += 1
            
            overlay.refresh()
        
        curses.curs_set(1)
        return text if text else None
    
    def get_selection_text(self) -> str:
        if not self.selection_start or not self.selection_end:
            return ""
        
        sy, sx = self.selection_start
        ey, ex = self.selection_end
        
        if sy > ey or (sy == ey and sx > ex):
            sy, sx, ey, ex = ey, ex, sy, sx
        
        if sy == ey:
            if sx < len(self.lines[sy]):
                return self.lines[sy][sx:min(ex+1, len(self.lines[sy]))]
            return ""
        
        result = []
        if sx < len(self.lines[sy]):
            result.append(self.lines[sy][sx:])
        for i in range(sy + 1, ey):
            result.append(self.lines[i])
        if ex < len(self.lines[ey]):
            result.append(self.lines[ey][:ex+1])
        
        return '\n'.join(result)
    
    def clear_selection(self):
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
    
    def copy_selection(self):
        text = self.get_selection_text()
        if text:
            self.clipboard = text.split('\n')
            self.clear_selection()
            self.show_message("Copied!")
        else:
            self.show_message("Nothing selected")
    
    def paste(self):
        if not self.clipboard:
            self.show_message("Nothing to paste")
            return
        
        if len(self.clipboard) == 1:
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[:self.cursor_x] + self.clipboard[0] + line[self.cursor_x:]
            self.cursor_x += len(self.clipboard[0])
        else:
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[:self.cursor_x] + self.clipboard[0]
            for i in range(1, len(self.clipboard)):
                self.lines.insert(self.cursor_y + i, self.clipboard[i])
            self.cursor_y += len(self.clipboard) - 1
            self.cursor_x = len(self.clipboard[-1])
        
        self.modified = True
        self.show_message("Pasted!")
    
    def show_help(self):
        help_h = 7
        help_w = min(75, self.width - 4)
        help_y = 2
        help_x = (self.width - help_w) // 2
        
        overlay = curses.newwin(help_h, help_w, help_y, help_x)
        overlay.bkgd(' ', curses.color_pair(BananaTheme.PAIR_MENU))
        overlay.box()
        
        title = " 🍌 BananaText Shortcuts "
        overlay.addstr(0, (help_w - len(title)) // 2, title, curses.color_pair(BananaTheme.PAIR_MENU))
        
        shortcuts = [
            "Arrows   : Move cursor",
            "Shift+Arrows : Select text", 
            "Enter   : New line",
            "Backspace: Delete character left",
            "Del     : Delete character at cursor",
            "Ctrl+C  : Copy selected text",
            "Ctrl+V  : Paste clipboard",
            "Ctrl+S  : Save file",
            "Ctrl+N  : New file",
            "Ctrl+O  : Open file picker",
            "Ctrl+Q  : Quit editor"
        ]
        
        for i, s in enumerate(shortcuts[:help_h - 2], 1):
            overlay.addstr(i, 2, s.ljust(help_w - 4), curses.color_pair(BananaTheme.PAIR_DEFAULT))
        
        overlay.addstr(help_h - 1, help_w - 15, " Esc or q to close ", curses.color_pair(BananaTheme.PAIR_HELP))
        
        while True:
            overlay.refresh()
            ch = overlay.getch()
            if ch in (27, 113, ord('q')):
                break
    
    def draw(self):
        self.stdscr.erase()
        
        self.draw_menu()
        self.draw_editor()
        self.draw_status()
        self.draw_help_bar()
        
        self.update_cursor()
        self.stdscr.refresh()
    
    def update_cursor(self):
        screen_y = self.cursor_y - self.scroll_y + 1
        screen_x = self.cursor_x - self.scroll_x + 5
        screen_y = max(1, min(screen_y, self.height - HELP_BAR_HEIGHT - 1))
        screen_x = max(0, min(screen_x, self.width - 1))
        try:
            self.stdscr.move(screen_y, screen_x)
            curses.setsyx(screen_y, screen_x)
        except:
            pass
    
    def draw_menu(self):
        mode = "📖 VIEW" if self.view_only else "🍌 BananaText"
        if self.filename:
            mode += f" - {os.path.basename(self.filename)}"
        if self.modified:
            mode += " [Modified]"
        
        self.stdscr.addstr(0, 0, mode.ljust(self.width), 
            curses.color_pair(BananaTheme.PAIR_MENU) | curses.A_REVERSE)
    
    def draw_editor(self):
        for i in range(self.editor_height):
            line_num = i + self.scroll_y
            if line_num >= len(self.lines):
                break
            
            line_str = f"{line_num + 1:4} │"
            try:
                self.stdscr.addstr(i + 1, 0, line_str, 
                    curses.color_pair(BananaTheme.PAIR_LINE_NUM))
            except:
                pass
            
            self.draw_line_with_selection(self.lines[line_num], i + 1, 5, line_num)
    
    def draw_line_with_selection(self, line: str, y: int, x: int, line_idx: int):
        if not line:
            try:
                attr = curses.color_pair(BananaTheme.PAIR_DEFAULT)
                self.stdscr.addstr(y, x, " ", attr)
            except:
                return
            return
        
        if self.selection_start and self.selection_end:
            self.draw_line_chunks(line, y, x, line_idx)
        else:
            attr = curses.color_pair(BananaTheme.PAIR_DEFAULT)
            try:
                visible = line[x - 5:x - 5 + self.editor_width]
                self.stdscr.addstr(y, x, visible, attr)
            except:
                pass
    
    def draw_line_chunks(self, line: str, y: int, x: int, line_idx: int):
        if not line:
            return
        
        sy = self.selection_start[0]
        sx = self.selection_start[1]
        ey = self.selection_end[0]
        ex = self.selection_end[1]
        
        if sy > ey or (sy == ey and sx > ex):
            sx, sy, ex, ey = ex, ey, sx, sy
        
        pos = x
        i = 0
        while i < len(line) and pos < self.width:
            ch = line[i]
            
            in_sel = False
            if line_idx == sy and line_idx == ey:
                in_sel = sx <= i <= ex
            elif line_idx == sy:
                in_sel = sx <= i
            elif line_idx == ey:
                in_sel = i <= ex
            elif sy < line_idx < ey:
                in_sel = True
            
            if in_sel:
                attr = curses.color_pair(BananaTheme.PAIR_SELECTION) | curses.A_REVERSE
            else:
                attr = curses.color_pair(BananaTheme.PAIR_DEFAULT)
            
            try:
                self.stdscr.addstr(y, pos, ch, attr)
            except:
                pass
            pos += 1
            i += 1
    
    def draw_status(self, message: Optional[str] = None):
        if message is None:
            path = self.filename or "Untitled"
            lineno = self.cursor_y + 1
            colno = self.cursor_x + 1
            message = f" {path} | Ln {lineno}, Col {colno} "
        
        status_y = self.height - HELP_BAR_HEIGHT - 1
        message = message[:self.width-1]
        try:
            self.stdscr.addstr(status_y, 0, message.ljust(self.width), 
                curses.color_pair(BananaTheme.PAIR_STATUS))
        except:
            pass
    
    def draw_help_bar(self):
        help_y = self.height - HELP_BAR_HEIGHT
        
        if self.view_only:
            help_lines = VIEWER_HELP
        else:
            help_lines = EDITOR_HELP
        
        for i, line in enumerate(help_lines):
            try:
                self.stdscr.addstr(help_y + i, 0, line.ljust(self.width), 
                    curses.color_pair(BananaTheme.PAIR_HELP))
            except:
                pass
    
    def handle_key(self, ch: int) -> bool:
        if self.view_only:
            return self.handle_viewer_key(ch)
        return self.handle_editor_key(ch)
    
    def handle_viewer_key(self, ch: int) -> bool:
        # F5 - help (keycode 269)
        if ch == 269:
            self.show_help()
            return True
        # F3 - file picker (keycode 267)
        if ch == 267:
            picker = FilePicker(self.stdscr)
            filename = picker.open_picker()
            if filename:
                self.load_file(filename)
            return True
        if ch in (27, 113):
            return False
        
        if ch == curses.KEY_UP:
            self.cursor_y = max(0, self.cursor_y - 1)
        elif ch == curses.KEY_DOWN:
            self.cursor_y = min(len(self.lines) - 1, self.cursor_y + 1)
        elif ch == curses.KEY_LEFT:
            self.cursor_x = max(0, self.cursor_x - 1)
        elif ch == curses.KEY_RIGHT:
            self.cursor_x = min(len(self.lines[self.cursor_y]), self.cursor_x + 1)
        elif ch == curses.KEY_HOME:
            self.cursor_x = 0
        elif ch == curses.KEY_END:
            self.cursor_x = len(self.lines[self.cursor_y])
        elif ch == curses.KEY_PPAGE:
            self.cursor_y = max(0, self.cursor_y - self.editor_height)
        elif ch == curses.KEY_NPAGE:
            self.cursor_y = min(len(self.lines) - 1, self.cursor_y + self.editor_height)
        
        self.update_scroll()
        return True
    
    def handle_editor_key(self, ch: int) -> bool:
        # Ctrl+C - copy
        if ch == 3:
            if self.selecting:
                self.copy_selection()
            else:
                self.show_message("Shift+arrows to select, then Ctrl+C or F1 to copy")
            return True
        
        # F1 - copy (keycode 265)
        if ch == 265:
            if self.selecting:
                self.copy_selection()
            else:
                self.show_message("Shift+arrows to select, then Ctrl+C or F1 to copy")
            return True
        
        # F2 - paste (keycode 266)
        if ch == 266:
            self.paste()
            return True
        
        # F5 - help (keycode 269)
        if ch == 269:
            self.show_help()
            return True
        
        # Shift+arrow for selection
        if ch == curses.KEY_SR:
            if not self.selecting:
                self.selecting = True
                self.selection_start = (self.cursor_y, self.cursor_x)
            self.cursor_y = max(0, self.cursor_y - 1)
            self.selection_end = (self.cursor_y, self.cursor_x)
            return True
        elif ch == curses.KEY_SF:
            if not self.selecting:
                self.selecting = True
                self.selection_start = (self.cursor_y, self.cursor_x)
            self.cursor_y = min(len(self.lines) - 1, self.cursor_y + 1)
            self.selection_end = (self.cursor_y, self.cursor_x)
            return True
        elif ch == curses.KEY_SLEFT:
            if not self.selecting:
                self.selecting = True
                self.selection_start = (self.cursor_y, self.cursor_x)
            self.cursor_x = max(0, self.cursor_x - 1)
            self.selection_end = (self.cursor_y, self.cursor_x)
            return True
        elif ch == curses.KEY_SRIGHT:
            if not self.selecting:
                self.selecting = True
                self.selection_start = (self.cursor_y, self.cursor_x)
            self.cursor_x = min(len(self.lines[self.cursor_y]), self.cursor_x + 1)
            self.selection_end = (self.cursor_y, self.cursor_x)
            return True
        
        # Escape - cancel selection
        if ch in (27,):
            self.clear_selection()
        
        # Ctrl+S (save)
        if ch == 19:
            self.save_file()
            return True
        
        # Ctrl+N (new)
        if ch == 14:
            self.new_file()
            return True
        
        # Ctrl+O - open file picker
        if ch == 15:
            picker = FilePicker(self.stdscr)
            filename = picker.open_picker()
            if filename:
                self.load_file(filename)
            return True
        
        # Ctrl+F - open as viewer
        if ch == 6:
            picker = FilePicker(self.stdscr)
            filename = picker.open_picker()
            if filename:
                viewer = BananaText(self.stdscr, view_only=True)
                viewer.load_file(filename)
                viewer.run()
                self.resize()
            return True
        
        # Ctrl+Q - quit
        if ch == 17:
            if self.modified:
                if self.confirm_discard():
                    return False
            return False
        
        # Arrow keys (no selection mode)
        if ch == curses.KEY_UP:
            self.clear_selection()
            self.cursor_y = max(0, self.cursor_y - 1)
        elif ch == curses.KEY_DOWN:
            self.clear_selection()
            self.cursor_y = min(len(self.lines) - 1, self.cursor_y + 1)
        elif ch == curses.KEY_LEFT:
            self.clear_selection()
            self.cursor_x = max(0, self.cursor_x - 1)
        elif ch == curses.KEY_RIGHT:
            self.clear_selection()
            self.cursor_x = min(len(self.lines[self.cursor_y]), self.cursor_x + 1)
        elif ch == curses.KEY_HOME:
            self.clear_selection()
            self.cursor_x = 0
        elif ch == curses.KEY_END:
            self.clear_selection()
            self.cursor_x = len(self.lines[self.cursor_y])
        elif ch == curses.KEY_PPAGE:
            self.clear_selection()
            self.cursor_y = max(0, self.cursor_y - self.editor_height)
        elif ch == curses.KEY_NPAGE:
            self.clear_selection()
            self.cursor_y = min(len(self.lines) - 1, self.cursor_y + self.editor_height)
        
        # Backspace
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if self.selecting:
                self.copy_selection()
                self.delete_selection()
            elif self.cursor_x > 0:
                line = self.lines[self.cursor_y]
                self.lines[self.cursor_y] = line[:self.cursor_x-1] + line[self.cursor_x:]
                self.cursor_x -= 1
                self.modified = True
            elif self.cursor_y > 0:
                self.cursor_x = len(self.lines[self.cursor_y - 1])
                self.lines[self.cursor_y - 1] += self.lines[self.cursor_y]
                del self.lines[self.cursor_y]
                self.cursor_y -= 1
                self.modified = True
        
        # Delete key
        elif ch == curses.KEY_DC:
            if self.selecting:
                self.copy_selection()
                self.delete_selection()
            else:
                line = self.lines[self.cursor_y]
                if self.cursor_x < len(line):
                    self.lines[self.cursor_y] = line[:self.cursor_x] + line[self.cursor_x+1:]
                    self.modified = True
        
        # Enter
        elif ch in (curses.KEY_ENTER, 10, 13):
            self.clear_selection()
            line = self.lines[self.cursor_y]
            new_line = line[self.cursor_x:]
            self.lines[self.cursor_y] = line[:self.cursor_x]
            self.lines.insert(self.cursor_y + 1, new_line)
            self.cursor_y += 1
            self.cursor_x = 0
            self.modified = True
        
        # Regular characters (printable)
        elif 32 <= ch <= 126:
            if self.selecting:
                self.delete_selection()
            char = chr(ch)
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x:]
            self.cursor_x += 1
            self.modified = True
        
        self.update_scroll()
        return True
    
    def delete_selection(self):
        text = self.get_selection_text()
        if not text:
            self.clear_selection()
            return
        
        sy, sx = self.selection_start
        ey, ex = self.selection_end
        
        if sy > ey or (sy == ey and sx > ex):
            sy, sx, ey, ex = ey, ex, sy, sx
        
        if sy == ey:
            line = self.lines[sy]
            if sx < len(line):
                self.lines[sy] = line[:sx] + line[ex+1:]
                self.cursor_x = sx
        else:
            first_line = self.lines[sy][:sx]
            last_line = self.lines[ey][ex+1:] if ex < len(self.lines[ey]) else ""
            self.lines[sy] = first_line + last_line
            del self.lines[sy+1:ey+1]
            self.cursor_y = sy
            self.cursor_x = len(first_line)
        
        self.clear_selection()
        self.modified = True
    
    def update_scroll(self):
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        elif self.cursor_y >= self.scroll_y + self.editor_height:
            self.scroll_y = self.cursor_y - self.editor_height + 1
        
        if self.cursor_x < self.scroll_x:
            self.scroll_x = self.cursor_x
        elif self.cursor_x >= self.scroll_x + self.editor_width:
            self.scroll_x = self.cursor_x - self.editor_width + 1
    
    def confirm_discard(self) -> bool:
        h, w = self.stdscr.getmaxyx()
        overlay = curses.newwin(5, 50, h//2-2, w//2-25)
        overlay.bkgd(' ', curses.color_pair(BananaTheme.PAIR_MENU))
        overlay.box()
        overlay.addstr(1, 2, " Unsaved changes! Quit anyway? (y/n): ", 
            curses.color_pair(BananaTheme.PAIR_MENU))
        
        while True:
            ch = overlay.getch()
            if ch in (121, 89):
                return True
            elif ch in (110, 78, 27):
                return False
    
    def run(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == '-v' or sys.argv[1] == '--view':
                if len(sys.argv) > 2:
                    self.view_only = True
                    self.load_file(sys.argv[2])
            else:
                self.load_file(sys.argv[1])
        
        while True:
            self.draw()
            ch = self.stdscr.getch()
            
            if not self.handle_key(ch):
                break


def main(stdscr):
    editor = BananaText(stdscr)
    editor.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass