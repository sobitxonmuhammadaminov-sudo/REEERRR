import os

def fix_extensions():
    count = 0
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py.txt") or file.endswith(".env.txt"):
                old_path = os.path.join(root, file)
                new_path = old_path.replace(".txt", "")
                os.rename(old_path, new_path)
                print(f"Tuzatildi: {file} -> {new_path.replace('./', '')}")
                count += 1
    if count == 0:
        print("✅ Barcha fayllar already to'g'ri kengaytmaga ega!")
    else:
        print(f"✅ Jami {count} ta fayl muvaffaqiyatli tuzatildi!")

if __name__ == "__main__":
    fix_extensions()