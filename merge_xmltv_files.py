import logging
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom


def _parse_xmltv_file(file, required):
    try:
        root = ET.parse(file).getroot()
        if root.tag != 'tv':
            raise ValueError(f'unexpected root element: {root.tag}')
        return root
    except (OSError, ET.ParseError, ValueError) as error:
        message = f'Unable to read XMLTV file {file}: {error}'
        if required:
            raise RuntimeError(message) from error
        logging.warning('Skipping optional %s', message)
        return None


def merge_xmltv_files(file_list, output_file, required_files=None):
    required_files = set(required_files or ())
    roots = []
    for file in file_list:
        root = _parse_xmltv_file(file, file in required_files)
        if root is not None:
            roots.append(root)

    if not roots:
        raise RuntimeError('No valid XMLTV files were available to merge')

    tv = ET.Element('tv')
    for root in roots:
        for channel in root.findall('channel'):
            tv.append(channel)
    for root in roots:
        for programme in root.findall('programme'):
            tv.append(programme)

    xml_str = ET.tostring(tv, encoding='utf-8', method='xml').decode()
    formatted_xml = minidom.parseString(xml_str).toprettyxml(indent='  ')
    formatted_xml_cleaned = re.sub(r'\n\s*\n', '\n', formatted_xml)

    temporary_output = f'{output_file}.tmp'
    try:
        with open(temporary_output, 'w', encoding='utf-8') as output:
            output.write(formatted_xml_cleaned)
        os.replace(temporary_output, output_file)
    finally:
        if os.path.exists(temporary_output):
            os.remove(temporary_output)


if __name__ == '__main__':
    merge_xmltv_files(
        ['all.xml', 'epg0.xml', 'gmcc_epg.xml'],
        'EPG.xml',
        required_files={'epg0.xml'},
    )
