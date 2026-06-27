"""
Точка входа в приложение.
Запускает главное окно.
"""


from gui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()