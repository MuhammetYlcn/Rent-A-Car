from model.car import Car
from controller.filemenager import FileReader, FileWriter
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import json
from view.user import UserWindow

class AdminController:
    def __init__(self, view):
        self.view = view
        self.car_file = UserWindow.resource_path("data/cars.json")
        self.user_file = UserWindow.resource_path("data/users.json")
        self.view.btn_add_vehicle.clicked.connect(self.add_car)
        self.view.btn_save.clicked.connect(self.save_all_to_file)
        self.view.btn_delete.clicked.connect(self.delete_selected_car)
        self.view.btn_logout_admin.clicked.connect(self.logout)
        self.view.btn_users.clicked.connect(self.load_users_as_message)
        self.view.combo_durum.clear()
        self.view.combo_durum.addItems(["Müsait", "Bakımda"])
        self.load_cars_to_table()

    def load_cars_to_table(self):
        reader = FileReader(self.car_file)
        data = reader.readFile()
        self.view.table_vehicles.setRowCount(0)
        if data and "arabalar" in data:
            for plaka, info in data["arabalar"].items():
                row = self.view.table_vehicles.rowCount()
                self.view.table_vehicles.insertRow(row)
                self.view.table_vehicles.setItem(row, 0, QTableWidgetItem(plaka))
                self.view.table_vehicles.setItem(row, 1, QTableWidgetItem(info["marka"]))
                self.view.table_vehicles.setItem(row, 2, QTableWidgetItem(info["model"]))
                self.view.table_vehicles.setItem(row, 3, QTableWidgetItem(str(info["gunlukUcret"])))
                self.view.table_vehicles.setItem(row, 4, QTableWidgetItem(info["durum"]))

    def load_users_as_message(self):
        reader = FileReader(self.user_file)
        data = reader.readFile()
        
        if data and "kullanicilar" in data:
            liste = ""
            for name, info in data["kullanicilar"].items():
                rol = "Yönetici" if info["admin_mi"] else "Müşteri"
                liste += f"👤 {name} ({rol})\n"
            
            QMessageBox.information(self.view, "Kayıtlı Kullanıcılar", liste)
        else:
            QMessageBox.warning(self.view, "Uyarı", "Kullanıcı verisi bulunamadı!")

    def add_car(self):
        plaka = self.view.entry_plaka.text()
        marka = self.view.entry_marka.text()
        model = self.view.entry_model.text()
        ucret = self.view.entry_ucret.text()
        durum = self.view.combo_durum.currentText().lower()

        if not all([plaka, marka, model, ucret]):
            QMessageBox.warning(self.view, "Hata", "Lütfen tüm alanları doldurun!")
            return

        try:
            yeni_arac = Car(plaka, marka, model, int(ucret), durum)
            writer = FileWriter(self.car_file)
            writer.writeFile(yeni_arac.to_dict())
            QMessageBox.information(self.view, "Başarılı", f"{plaka} plakalı araç eklendi.")
            self.load_cars_to_table()
        except ValueError:
            QMessageBox.critical(self.view, "Hata", "Ücret sayı olmalıdır!")

    def delete_selected_car(self):
        selected_row = self.view.table_vehicles.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.view, "Uyarı", "Silinecek aracı tablodan seçin!")
            return
            
        plaka = self.view.table_vehicles.item(selected_row, 0).text()
        if QMessageBox.question(self.view, "Onay", f"{plaka} silinsin mi?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            reader = FileReader(self.car_file)
            data = reader.readFile()
            if data and "arabalar" in data and plaka in data["arabalar"]:
                del data["arabalar"][plaka]
                with open(self.car_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                self.load_cars_to_table()

    def save_all_to_file(self):
        QMessageBox.information(self.view, "Kaydet", "Tüm değişiklikler başarıyla kaydedildi.")

    def logout(self):
        from view.login import LoginWindow
        from controller.login_controller import LoginController
        self.login_v = LoginWindow()
        self.login_c = LoginController(self.login_v)
        self.login_v.show()
        self.view.close()