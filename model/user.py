from model.BaseModel import BaseModel

class User(BaseModel):
    def __init__(self,kullanici_adi,sifre,admin_mi):
        self.__kullanici_adi=kullanici_adi
        self.__sifre=sifre
        self.__admin_mi=admin_mi
        
    
    @property
    def kullanici_adi(self):
        return self.__kullanici_adi
    @property
    def sifre(self):
        return self.__sifre
    @property
    def admin_mi(self):
        return self.__admin_mi
    
    def to_dict(self):
        return {
            "kullanicilar": {
                self.__kullanici_adi:{
                    "sifre":self.__sifre,
                    "admin_mi":self.__admin_mi  
                }
            }
        }
    
    @classmethod
    def from_dict(cls,kullanici_adi,data):
        return cls(
            kullanici_adi=kullanici_adi,
            sifre=data.get("sifre"),
            admin_mi=data.get("admin_mi")
        )
    def __repr__(self):
        return f"User(ad={(self.__kullanici_adi)},admin_mi={self.__admin_mi})"