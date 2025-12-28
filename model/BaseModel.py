from abc import ABC,abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def to_dict(self):
        pass
    @abstractmethod
    def from_dict(cls,key,data):
        pass
    @abstractmethod
    def __repr__(self):
        pass