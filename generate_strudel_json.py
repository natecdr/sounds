from pathlib import Path

extensions = [".mp4", ".MP4", ".wav", ".WAV"]

files_found = []
for ext in extensions:
    files_found.extend(Path(".").rglob(f"*{ext}"))

# res_dict = {
#     _base: "https://raw.githubusercontent.com/natecdr/"
# }

# print(files_found)