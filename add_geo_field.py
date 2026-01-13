import json
import os

file_ops = 'c:/desarrollo/logias/logias.json'

try:
    with open(file_ops, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = False
    for logia in data:
        if 'ubicacion_geografica' not in logia:
            logia['ubicacion_geografica'] = None
            updated = True

    if updated:
        with open(file_ops, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated logias.json with ubicacion_geografica field.")
    else:
        print("No updates needed.")

except Exception as e:
    print(f"Error: {e}")
