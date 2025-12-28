from model.BaseModel import BaseModel
from datetime import datetime
from model.user import User
from model.car import Car

class RentalAgreement(BaseModel):
    def __init__(self, agreement_id, user: User, car: Car, baslangic_tarihi, bitis_tarihi):
        self.__agreement_id = agreement_id
        self.__user = user
        self.__car = car
        self.__baslangic_tarihi = baslangic_tarihi
        self.__bitis_tarihi = bitis_tarihi
        self.__gunluk_ucret = car.gunlukUcret
        self.__gun_sayisi = 0 # İlk değer ataması
        self.__toplam_ucret = self.hesapla_toplam_ucret()
    
    def hesapla_toplam_ucret(self):
        """Tarih farkını hesaplar, gun_sayisi niteliğini doldurur ve toplam ücreti döner."""
        try:
            fmt = "%d.%m.%Y" 
            d1 = datetime.strptime(self.__baslangic_tarihi, fmt)
            d2 = datetime.strptime(self.__bitis_tarihi, fmt)
            
            fark = (d2 - d1).days
            if fark < 0:
                raise ValueError("HATA: Başlangıç tarihi bitiş tarihinden sonra olamaz.")
            
            # Gün sayısını değişkene kaydediyoruz (Controller buraya erişecek)
            self.__gun_sayisi = max(fark, 1) 
            return self.__gun_sayisi * self.__gunluk_ucret
            
        except ValueError as hata:
            raise hata
        except Exception as e:
            raise Exception(f"Beklenmedik bir tarih hesaplama hatası: {e}")
    
    @property
    def agreement_id(self): 
        return self.__agreement_id

    @property
    def user(self): 
        return self.__user

    @property
    def car(self): 
        return self.__car

    @property
    def baslangic_tarihi(self): 
        return self.__baslangic_tarihi

    @property
    def bitis_tarihi(self): 
        return self.__bitis_tarihi
    
    @bitis_tarihi.setter
    def bitis_tarihi(self, yeni_tarih):
        self.__bitis_tarihi = yeni_tarih
        self.__toplam_ucret = self.hesapla_toplam_ucret()
    
    @property
    def toplam_ucret(self): 
        return self.__toplam_ucret

    @property
    def gun_sayisi(self):
        # Sonsuz döngü düzeltildi: self.gun_sayisi yerine self.__gun_sayisi dönüyor
        return self.__gun_sayisi
    
    def to_dict(self):
        """Sözleşme verilerini JSON yapısına uygun sözlüğe dönüştürür."""
        return {
            "sozlesmeler": {
                str(self.__agreement_id): {
                    "kiralayan": self.__user.kullanici_adi, 
                    "plaka": self.__car.plaka,
                    "baslangic_tarihi": self.__baslangic_tarihi,
                    "bitis_tarihi": self.__bitis_tarihi,
                    "gunluk_ucret": self.__gunluk_ucret,
                    "gun_sayisi": self.__gun_sayisi,
                    "toplam_ucret": self.__toplam_ucret
                }
            }
        }
    
    @classmethod
    def from_dict(cls, key, data):
        """Bağımlılıklar nedeniyle bu metodun içi boş bırakılmıştır; eşleştirme controller'da yapılmalıdır."""
        pass

    def __repr__(self):
        """Nesnenin konsol çıktısını özelleştirir."""
        return (f"RentalAgreement("
                f"ID='{self.__agreement_id}', "
                f"User='{self.__user.kullanici_adi}', "
                f"Car='{self.__car.plaka}', "
                f"Start='{self.__baslangic_tarihi}', "
                f"End='{self.__bitis_tarihi}', "
                f"Days={self.__gun_sayisi}, "
                f"TotalPrice={self.__toplam_ucret}₺)")