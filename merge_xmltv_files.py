import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging


def merge_xmltv_files(file_list, output_file):
    tv = ET.Element('tv')
    for file in file_list:
        try:
            tree = ET.parse(file)
        except FileNotFoundError as e:
            logging.warning(e)
        else:
            root = tree.getroot()
            for channel in root.findall('channel'):
                tv.append(channel)
    for file in file_list:
        try:
            tree = ET.parse(file)
        except FileNotFoundError as e:
            logging.warning(e)
        else:
            root = tree.getroot()
            for programme in root.findall('programme'):
                tv.append(programme)
    xml_str = ET.tostring(tv, encoding='utf-8', method='xml').decode()
    formatted_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    formatted_xml_cleaned = re.sub(r'\n\s*\n', '\n', formatted_xml)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_xml_cleaned)


if __name__ == '__main__':
    merge_xmltv_files(['all.xml', 'epg.xml', 'epg0.xml'], 'EPG.xml')
