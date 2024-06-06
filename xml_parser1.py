import json
import xml.etree.ElementTree as ET
import codecs
from dateutil.parser import parse
from datetime import date

def parse_xml_file(file_path):

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    result = {}
        
    for channel in root.findall('.//channel'):
        samplecount = channel.find('samplecount')
        if samplecount is not None and samplecount.text == '500':
            name = channel.find('name')
            data = channel.find('data')
            
            if name is not None and data is not None:
                result = data.text
                break

    return result

