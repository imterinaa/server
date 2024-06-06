import json
import xml.etree.ElementTree as ET
import codecs
from crud import init_db, Note
from dateutil.parser import parse
from datetime import date

def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    result = {}
    lastnames = root.findall('.//lastname')
    for lastname_element in lastnames:
        try:
            encoded_lastname = codecs.encode(lastname_element.text, 'cp857').decode('cp866')
        except UnicodeEncodeError:
            print(f"Cannot encode '{lastname_element.text}' in utf-8")
    firstnames = root.findall('.//firstname')
    for firstname_element in firstnames:
        try:
            encoded_firstname = codecs.encode(lastname_element.text, 'cp857').decode('cp866')
        except UnicodeEncodeError:
            print(f"Cannot encode '{lastname_element.text}' in utf-8")        
    birthdate_element = root.find('.//birthdate')
    if birthdate_element is not None:
        birthdate_value = format_date_of_birth(birthdate_element.text)
    else:
        print("Элемент birthdate не найден.")

    date_element = root.find('.//date')
    if date_element is not None:
        date_value = format_date_of_birth(date_element.text)
    else:
        print("Элемент date не найден.")
        
    for channel in root.findall('.//channel'):
        samplecount = channel.find('samplecount')
        if samplecount is not None and samplecount.text == '5000':
            name = channel.find('name')
            data = channel.find('data')
            
            if name is not None and data is not None:
                result[name.text] = data.text

    birthdate_datetime = parse(birthdate_value)
    date_of_birth = birthdate_datetime.date()
    date_of_upload = parse(date_value)
    date_of_upload = date_of_upload.date()

    Note.create_note(date_of_birth, date_of_upload, encoded_firstname, encoded_lastname,result)

    return result
    
def format_date_of_birth(date_string):
    if len(date_string)!= 8 or not date_string.isdigit():
        raise ValueError("Неверный формат даты рождения.")
    year = date_string[:4]
    month = date_string[4:6]
    day = date_string[6:]
    
    formatted_date = f"{day}.{month}.{year}"
    return formatted_date
