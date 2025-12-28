from model.user import User
from controller.filemenager import FileReader, FileWriter
from controller.admin_controller import AdminController
from controller.customer_controller import CustomerController
from PyQt5.QtWidgets import QMessageBox
from view.login import LoginWindow
from view.admin import AdminWindow
from view.user import UserWindow

class LoginController:
    def __init__(self, view):
        self.view = view 
        # LoginController.__init__ içinde
        self.user_file = LoginWindow.resource_path("data/users.json")
        self.view.btn_login.clicked.connect(self.handle_login)
        self.view.btn_register.clicked.connect(self.handle_register)

    def handle_login(self):
        username = self.view.entry_username.text()
        password = self.view.entry_password.text()

        if not username or not password:
            QMessageBox.warning(self.view, "Eksik Bilgi","Sisteme erişebilmek için lütfen kullanıcı adı ve şifre alanlarının tamamını doldurunuz.")
            return
        
        reader = FileReader(self.user_file)
        data = reader.readFile()

        if data and "kullanicilar" in data:
            users = data["kullanicilar"]
            if username in users:
                if str(users[username]["sifre"]) == password:
                    is_admin = users[username]["admin_mi"]
                    self.redirect_user(is_admin, username)
                else:
                    QMessageBox.critical(self.view, "Giriş Başarısız","Girdiğiniz şifre hatalıdır. Lütfen bilgilerinizi kontrol edip tekrar deneyiniz.")
            else:
               QMessageBox.warning(self.view, "Kayıt Mevcut Değil","Belirttiğiniz kullanıcı adına sahip bir hesap bulunamadı. Lütfen kullanıcı adınızı kontrol edin veya yeni bir hesap oluşturun.")

    def handle_register(self):
        username = self.view.entry_username.text()
        password = self.view.entry_password.text()
        
        reader = FileReader(self.user_file)
        data = reader.readFile()
        
        users = data.get("kullanicilar", {}) if data else {}

        if not username or not password:
            QMessageBox.warning(self.view, "Kayıt İşlemi Durduruldu","Yeni bir hesap oluşturabilmek için kullanıcı adı ve şifre belirlenmesi zorunludur.")
            return
        if username in users:
            QMessageBox.critical(self.view, "Kayıt Hatası",f"'{username}' kullanıcı adı zaten sisteme kayıtlıdır. Lütfen farklı bir kullanıcı adı seçiniz.")
            return
        else:
            new_user = User(username, password, False)
            writer = FileWriter(self.user_file)
            writer.writeFile(new_user.to_dict())
            QMessageBox.information(self.view, "İşlem Başarılı", f"'{username}' sisteme başarıyla kaydedilmiştir. Artık giriş bilgilerinizle oturum açabilirsiniz.")

    def redirect_user(self, is_admin, username):
        if is_admin:
            print(f"Admin Paneli Açılıyor: {username}")
            self.admin_window = AdminWindow() 
            self.admin_ctrl = AdminController(self.admin_window)
            self.admin_window.show()
        else:
            print(f"Müşteri Paneli Açılıyor: {username}")
            self.user_window = UserWindow() 
            self.user_ctrl = CustomerController(self.user_window, username)
            self.user_window.show()
        
        
        self.view.close()