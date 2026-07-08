import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_frame import MainFrame
from src.gui.main_menu import MainMenu

def main():
    app = MainFrame()
    app.center_window()
    app.show_view(MainMenu)
    app.mainloop()

if __name__ == '__main__':
    main()