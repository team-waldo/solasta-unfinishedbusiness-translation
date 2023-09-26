from collections import defaultdict, namedtuple
import csv
from dataclasses import dataclass
import glob
import os
from pathlib import Path
import subprocess
from translation_storage import TranslationFile, TranslationEntry, load_translation

from config import *


# def update_mod_repo():
#     if not os.path.exists(MOD_REPO_NAME):
#         subprocess.call(["git", "clone", MOD_REPO_URL])
    
#     subprocess.call(["git", "pull", "origin", "dev"], cwd=os.path.realpath(MOD_REPO_NAME))

@dataclass
class TxtItem:
    key: str
    value: str

def read_txt(path: str) -> list[TxtItem]:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    result = []
    for line in lines:
        k, v = line.split("=", maxsplit=1)
        result.append(TxtItem(k, v[:-1]))
    
    return result


def save_txt(path: str, data: list[TxtItem]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"{item.key}={item.value}\n")


def main():
    os.makedirs(os.path.join(TRANSLATION_DIRECTORY, LANGCODE), exist_ok=True)

    # update_mod_repo()

    # templates = generate_templates()

    translation_data = load_translation(os.path.join(TRANSLATION_DIRECTORY, LANGCODE))

    for value in translation_data.values():
        value.target = value.target.replace("\n", "\\n")
        value.source = value.source.replace("\n", "\\n")

    translations_dir = Path(MOD_REPO_NAME, MOD_REPO_NAME, "Translations")

    english_dir = translations_dir / "en"
    output_dir = translations_dir / LANGCODE
    
    input_dir = output_dir # english_dir

    for txt_path in input_dir.glob("**/*.txt"):
        relpath = txt_path.relative_to(input_dir)
        print(relpath)

        txt = read_txt(str(txt_path))

        for item in txt:
            if (tr := translation_data.get(item.key, None)) and tr.target:
                item.value = tr.target
        
        output_path = output_dir / str(relpath).replace("-en", f"-{LANGCODE}")
        os.makedirs(output_path.parent, exist_ok=True)

        save_txt(str(output_path), txt)


if __name__ == '__main__':
    main()