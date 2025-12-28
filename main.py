import sys
from PyQt5.QtWidgets import QApplication
from view.login import LoginWindow
from controller.login_controller import LoginController

def main():
    app = QApplication(sys.argv)
    login_view = LoginWindow()
    login_ctrl = LoginController(login_view)
    login_view.show()
    print("--- Araç Kiralama Sistemi Başlatıldı ---")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()