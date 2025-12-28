from model.BaseModel import BaseModel

class Car(BaseModel):
    def __init__(self,plaka,marka,model,gunlukUcret,durum,kiralayan=None,baslangicTarihi=None,bitisTarihi=None):
        self.__plaka=plaka
        self.__marka=marka
        self.__model=model
        self.__gunlukUcret=gunlukUcret
        self.__durum=durum
        self.__kiralayan=kiralayan
        self.__baslangicTarihi=baslangicTarihi
        self.__bitisTarihi=bitisTarihi
    
    @property
    def plaka(self):
        return self.__plaka
    @property
    def marka(self):
        return self.__marka
    @property
    def model(self):
        return self.__model
    @property
    def gunlukUcret(self):
        return self.__gunlukUcret
    @property
    def durum(self):
        return self.__durum
    @property
    def kiralayan(self):
        return self.__kiralayan
    @property
    def baslangicTarihi(self):
        return self.__baslangicTarihi
    @property
    def bitisTarihi(self):
        return self.__bitisTarihi
    
    def update_durum(self,durum,kiralayan=None,baslangicTarihi=None,bitisTarihi=None):
        if(durum=="kirada"):
            if(kiralayan==None or baslangicTarihi==None or bitisTarihi==None):
                raise ValueError("HATA: Gerekli kiralama bilgileri eksik veya durum geçersiz.")
            self.__durum="kirada"
            self.__kiralayan=kiralayan
            self.__baslangicTarihi=baslangicTarihi
            self.__bitisTarihi=bitisTarihi
        elif(durum=="müsait"):
            self.__durum="müsait"
            self.__kiralayan=None
            self.__baslangicTarihi=None
            self.__bitisTarihi=None
        else:
            raise ValueError("HATA: Geçersiz durum değeri")
    def to_dict(self):
        return {
            "arabalar":{
                self.__plaka:{
                    "marka": self.__marka,
                    "model": self.__model,
                    "gunlukUcret": self.__gunlukUcret,
                    "durum": self.__durum,
                    "kiralayan": self.__kiralayan,
                    "baslangicTarihi": self.__baslangicTarihi,
                    "bitisTarihi": self.__bitisTarihi
                }
            }
        }
    
    @classmethod
    def from_dict(cls,plaka,car_dict):
        return cls(
            plaka=plaka,
            marka=car_dict.get('marka'),
            model=car_dict.get('model'),
            gunlukUcret=car_dict.get('gunlukUcret'),
            durum=car_dict.get('durum'),
            kiralayan=car_dict.get('kiralayan'),
            baslangicTarihi=car_dict.get('baslangicTarihi'),
            bitisTarihi=car_dict.get('bitisTarihi')
        )
    
    def __repr__(self):
        return f"Car(plaka={self.__plaka},model={self.__model},durum={self.__durum})"