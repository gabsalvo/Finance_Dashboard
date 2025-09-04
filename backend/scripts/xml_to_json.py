import xmltodict
import json
import re
import sys
import os

def remove_namespaces(xml_content):
  xml_content = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', xml_content, flags=re.MULTILINE)
  xml_content = re.sub(r'<(/?)[a-zA-Z0-9]+:', r'<\1', xml_content)
  return xml_content

def xml_to_json(xml_path, json_path):
  try:
    with open(xml_path, 'r', encoding='utf-8') as f:
      xml_content = f.read()
    xml_content = remove_namespaces(xml_content)
    data_dict = xmltodict.parse(xml_content, process_namespaces=False)
    with open(json_path, 'w', encoding='utf-8') as f:
      json.dump(data_dict, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON salvato come: {json_path}")
  except FileNotFoundError:
    print(f"❌ File non trovato: {xml_path}")
  except Exception as e:
    print(f"❌ Errore: {e}")

if __name__ == "__main__":
  xml_file = input("Nome file XML da convertire (es: IT01879020517A2025_eS0wN.xml): ").strip()
  if not os.path.isfile(xml_file):
    print(f"❌ Il file '{xml_file}' non esiste nella cartella corrente.")
    sys.exit(1)
  json_file = xml_file.rsplit('.', 1)[0] + '.json'
  xml_to_json(xml_file, json_file)

