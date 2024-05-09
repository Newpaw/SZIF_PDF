import os
import shutil

# Cesta ke složce 'docs'
base_dir = 'docs'

# Projde všechny podsložky ve složce 'docs'
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    
    # Kontroluje, zda je položka složka
    if os.path.isdir(folder_path):
        # Projde všechny soubory v podsložce
        for file in os.listdir(folder_path):
            # Vytvoří nový název souboru, který zahrnuje název složky
            new_file_name = f"{folder}_{file}"
            # Původní cesta k souboru
            old_file_path = os.path.join(folder_path, file)
            # Nová cesta k souboru
            new_file_path = os.path.join(base_dir, new_file_name)
            
            # Přesune soubor do hlavní složky 'docs' s novým názvem
            shutil.move(old_file_path, new_file_path)

print("Soubory byly přesunuty a přejmenovány.")
