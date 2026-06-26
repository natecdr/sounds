from pathlib import Path
import json

extensions = [".mp4", ".wav"]

files_found = []
for ext in extensions:
    files_found.extend(Path(".").rglob(f"*{ext}"))

res_dict = {
    "_base": "https://raw.githubusercontent.com/natecdr/sounds/main/"
}

for file in files_found:
    print(files_found)
    parent = file.parent.stem
    if parent not in res_dict:
        res_dict[parent] = []
        
    res_dict[parent].append(file.name)
    
with open("./strudel.json", "w") as f:
    json.dump(res_dict, f, indent=4)