import os

# İstemediğimiz klasörleri (Sanal ortamlar, Git dosyaları vb.) filtreliyoruz
IGNORE_DIRS = ['venv', '.venv', '.git', '__pycache__', '.idea', '.vscode', 'node_modules']
# Sadece raporlamak istediğimiz kod ve ayar dosyalarının uzantıları
ALLOWED_EXTENSIONS = ('.py', '.html', '.css', '.js', '.yml', 'Dockerfile', '.env.example', '.md')

output_file = "TUM_PROJE_KODLARI.txt"

with open(output_file, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk("."):
        # İstemediğimiz klasörleri atla
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(ALLOWED_EXTENSIONS) or file == "Dockerfile":
                filepath = os.path.join(root, file)
                
                # Dosya yolunu başlık olarak ekle
                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"DOSYA YOLU: {filepath}\n")
                outfile.write(f"{'='*60}\n\n")
                
                # Dosyanın içeriğini oku ve yaz
                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read() + "\n")
                except Exception as e:
                    outfile.write(f"--- Bu dosya okunamadi: {e} ---\n")

print(f"İşlem tamam! Tüm proje kodları '{output_file}' dosyasına aktarıldı.")