import json
import os

class FileReader:
    
    def __init__(self,file_name):
        self.file_name=file_name   
     
    def readFile(self):
        if not os.path.exists(self.file_name) or os.stat(self.file_name).st_size == 0:
            return {}
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                data=json.load(file)
                return data
        except FileNotFoundError:
            print("file not found")
            return None
        except json.JSONDecodeError:
            print("The file content is not in a valid JSON format.")
            return None
        except Exception as e:
            print("An unexpected error occurred",e)
            return None

class FileWriter:
    
    def __init__(self,file_name):
        self.file_name=file_name
    
    def writeFile(self,data):
        try:
            reader=FileReader(self.file_name)
            current_data=reader.readFile()
            if(current_data==None):
                current_data={}
            for key,value in data.items():
                if key in current_data:
                    current_data[key].update(value)
                else:
                    current_data[key]=value
            with open(self.file_name, 'w', encoding='utf-8') as file:
                json.dump(current_data, file, indent=4, ensure_ascii=False)
                print("Data successfully saved")              
        except TypeError:
            print("type error")
            return None
        except Exception as e:
            print("An unexpected error occurred",e)
            return None 