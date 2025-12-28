from model.RentalAgreement import RentalAgreement
from model.user import User
from model.car import Car
from controller.filemenager import FileReader, FileWriter
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import json
from datetime import datetime
from view.user import UserWindow

class CustomerController:
    def __init__(self, view, current_username):
        self.view = view
        self.username = current_username
        self.car_file = UserWindow.resource_path("data/cars.json")
        self.rental_file = UserWindow.resource_path("data/rentalAgreements.json")
        self.view.btn_rent.clicked.connect(self.handle_rental)
        self.view.btn_logout_customer.clicked.connect(self.logout)
        from PyQt5.QtCore import QDate # İmportlara eklemeyi unutmayın


        bugun = QDate.currentDate()
        self.view.entry_start.setMinimumDate(bugun)
        self.view.entry_end.setMinimumDate(bugun)


        self.view.entry_start.dateChanged.connect(lambda d: self.view.entry_end.setMinimumDate(d))
        
        if hasattr(self.view, 'btn_return_vehicle'):
            self.view.btn_return_vehicle.clicked.connect(self.return_car)
            
        self.load_available_cars()

    def load_available_cars(self):
        from PyQt5.QtGui import QColor

        self.deep_sync_files()
        start_dt = self.view.entry_start.date().toPyDate()
        end_dt = self.view.entry_end.date().toPyDate()

        cars_data = FileReader(self.car_file).readFile()
        rental_data = FileReader(self.rental_file).readFile()
        if not isinstance(rental_data, dict): rental_data = {}
        
        self.view.table_available_cars.setRowCount(0)
        fmt = "%d.%m.%Y"

        if cars_data and "arabalar" in cars_data:
            for plaka, info in cars_data["arabalar"].items():
                if info["durum"].lower() == "bakımda": 
                    continue
                
                cakisma_var = False
                sozlesmeler = rental_data.get("sozlesmeler", {})
                
                for r_id, r_info in sozlesmeler.items():
                    if r_info["plaka"] == plaka:
                        try:
                            r_start = datetime.strptime(r_info["baslangic_tarihi"], fmt).date()
                            r_end = datetime.strptime(r_info["bitis_tarihi"], fmt).date()
                            if start_dt <= r_end and end_dt >= r_start:
                                cakisma_var = True
                                break
                        except: continue

                row = self.view.table_available_cars.rowCount()
                self.view.table_available_cars.insertRow(row)
                
                items = [
                    QTableWidgetItem(plaka),
                    QTableWidgetItem(info["marka"]),
                    QTableWidgetItem(info["model"]),
                    QTableWidgetItem(str(info["gunlukUcret"])),
                    QTableWidgetItem("Müsait" if not cakisma_var else "Kirada")
                ]

                for item in items:
                    if cakisma_var:
                        item.setBackground(QColor(255, 200, 200)) 
                        item.setForeground(QColor(150, 0, 0))     
                    self.view.table_available_cars.setItem(row, items.index(item), item)

        self.view.table_available_cars.setVisible(True)
        self.view.label_no_cars.setVisible(False)

    def deep_sync_files(self):
        try:
            # 1. Dosyaları Oku
            car_reader = FileReader(self.car_file)
            rental_reader = FileReader(self.rental_file)

            car_data = car_reader.readFile()
            rental_data = rental_reader.readFile()

            arabalar = car_data.get("arabalar", {})
            sozlesmeler = rental_data.get("sozlesmeler", {})

            changes_made = False

            # --- SENARYO A: cars.json'da 'müsait' olan aracın kiralama kaydını sil ---
            for plaka, info in arabalar.items():
                if info.get("durum") == "müsait":
                    # Eğer araç müsaitse ama sözleşmelerde hala duruyorsa, sözleşmeyi sil
                    for aid in list(sozlesmeler.keys()):
                        if sozlesmeler[aid]["plaka"] == plaka:
                            del sozlesmeler[aid]
                            changes_made = True
                            print(f"Sistem Temizliği: {plaka} müsait olduğu için sözleşmesi silindi.")

            # --- SENARYO B: rentalagreement.json'da kaydı olan aracı 'kirada' yap ---
            active_rented_plakas = [s["plaka"] for s in sozlesmeler.values()]
            for plaka, info in arabalar.items():
                if plaka in active_rented_plakas and info.get("durum") != "kirada":
                    arabalar[plaka]["durum"] = "kirada"
                    changes_made = True
                    print(f"Sistem Düzeltme: {plaka} sözleşmesi olduğu için 'kirada' yapıldı.")

            # 2. Eğer bir değişiklik yapıldıysa dosyaları güncelle
            if changes_made:
                with open(self.car_file, 'w', encoding='utf-8') as f:
                    json.dump({"arabalar": arabalar}, f, ensure_ascii=False, indent=4)
                with open(self.rental_file, 'w', encoding='utf-8') as f:
                    json.dump({"sozlesmeler": sozlesmeler}, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Senkronizasyon Hatası: {e}")
    def handle_rental(self):
        try:
            selected_row = self.view.table_available_cars.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self.view, "Seçim Yapılmadı", "Lütfen bir araç seçiniz.")
                return

            # Verileri al
            plaka = self.view.table_available_cars.item(selected_row, 0).text()
            gunluk_ucret = int(self.view.table_available_cars.item(selected_row, 3).text())
            
            # Tarihleri al ve hesapla
            start_date_str = self.view.entry_start.date().toString("dd.MM.yyyy")
            end_date_str = self.view.entry_end.date().toString("dd.MM.yyyy")
            fmt = "%d.%m.%Y"
            
            start_dt = datetime.strptime(start_date_str, fmt).date()
            end_dt = datetime.strptime(end_date_str, fmt).date()

            gun_sayisi = (end_dt - start_dt).days
            if gun_sayisi <= 0: gun_sayisi = 1
            toplam_ucret = gun_sayisi * gunluk_ucret

            # 1. DOSYAYI OKU (Hata almamak için en başta tanımlıyoruz)
            reader = FileReader(self.rental_file)
            current_data = reader.readFile()
            if not isinstance(current_data, dict): 
                current_data = {"sozlesmeler": {}}
            
            if "sozlesmeler" not in current_data:
                current_data["sozlesmeler"] = {}

            # 2. ÇAKIŞMA KONTROLÜ
            sozlesmeler = current_data["sozlesmeler"]
            for r_info in sozlesmeler.values():
                if r_info["plaka"] == plaka:
                    r_start = datetime.strptime(r_info["baslangic_tarihi"], fmt).date()
                    r_end = datetime.strptime(r_info["bitis_tarihi"], fmt).date()
                    if start_dt <= r_end and end_dt >= r_start:
                        QMessageBox.warning(self.view, "Tarih Çakışması", "Bu araç seçili tarihlerde dolu.")
                        return

            # 3. ONAY VE KAYIT
            onay = QMessageBox.question(self.view, "Kiralama Onayı", 
                                        f"Ücret: {toplam_ucret}₺\nSüre: {gun_sayisi} Gün\nOnaylıyor musunuz?",
                                        QMessageBox.Yes | QMessageBox.No)

            if onay == QMessageBox.Yes:
                car_obj = Car(plaka, "", "", gunluk_ucret, "kirada")
                user_obj = User(self.username, "", False)

                agreement = RentalAgreement(
                    agreement_id=f"RENT-{plaka}-{datetime.now().strftime('%H%M%S')}",
                    user=user_obj,
                    car=car_obj,
                    baslangic_tarihi=start_date_str,
                    bitis_tarihi=end_date_str
                )

                # Veriyi sözlüğe ekle ve yaz
                current_data["sozlesmeler"].update(agreement.to_dict()["sozlesmeler"])

                with open(self.rental_file, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=4)

                self.update_car_status(plaka, "kirada")
                QMessageBox.information(self.view, "Başarılı", "Kiralama işlemi tamamlandı.")
                self.load_available_cars()

        except Exception as e:
            # Programın kapanmasını engeller ve hatayı gösterir
            QMessageBox.critical(self.view, "Hata", f"İşlem sırasında bir hata oluştu: {str(e)}")

    def return_car(self):
        try:
            # 1. Seçim kontrolü: Kullanıcı tablodan bir araca tıkladı mı?
            selected_row = self.view.table_available_cars.currentRow()

            if selected_row < 0:
                QMessageBox.warning(self.view, "Seçim Yapılmadı",
                                    "Lütfen iade etmek istediğiniz aracı aşağıdaki listeden seçiniz.")
                return

            # 2. Seçili satırdan plakayı al
            plaka_item = self.view.table_available_cars.item(selected_row, 0)
            if not plaka_item:
                return

            plaka_to_return = plaka_item.text()

            # 3. Dosyayı oku
            reader = FileReader(self.rental_file)
            data = reader.readFile()

            if not data or "sozlesmeler" not in data:
                QMessageBox.warning(self.view, "Kayıt Yok", "Sistemde aktif kiralama bulunamadı.")
                return

            # 4. DOĞRU ARACI BULMA (Kritik Nokta)
            # Sadece kullanıcı adı eşleşen ilk kaydı değil,
            # HEM kullanıcı adı HEM plakası eşleşen kaydı arıyoruz.
            found_aid = None
            for aid, info in data["sozlesmeler"].items():
                if info["kiralayan"] == self.username and info["plaka"] == plaka_to_return:
                    found_aid = aid
                    break

            # 5. İade İşlemini Gerçekleştir
            if found_aid:
                # Sözleşmeyi sil
                del data["sozlesmeler"][found_aid]

                with open(self.rental_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                # Aracın durumunu dosyada 'müsait' yap
                self.update_car_status(plaka_to_return, "müsait")

                QMessageBox.information(self.view, "Başarılı",
                                        f"'{plaka_to_return}' plakalı araç iade edildi.")

                # Tabloyu yenile (Kırmızıdan normale dönecek)
                self.load_available_cars()
            else:
                # Eğer araç listede kırmızı ama kiralayan bu kullanıcı değilse
                QMessageBox.warning(self.view, "Yetki Hatası",
                                    "Bu araç sizin tarafınızdan kiralanmamış. Başkasının aracını iade edemezsiniz.")

        except Exception as e:
            QMessageBox.critical(self.view, "Hata", f"İade sırasında bir hata oluştu: {str(e)}")
    def update_car_status(self, plaka, status):
        reader = FileReader(self.car_file)
        data = reader.readFile()
        if data and "arabalar" in data and plaka in data["arabalar"]:
            data["arabalar"][plaka]["durum"] = status
            with open(self.car_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def logout(self):
        from view.login import LoginWindow
        from controller.login_controller import LoginController
        self.lv = LoginWindow()
        self.lc = LoginController(self.lv)
        self.lv.show()
        self.view.close()