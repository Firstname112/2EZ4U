"""Generator data contoh: data/pesanan.csv (200.000 baris).

Hanya dipakai bila data asli dari dosen belum ada.
    python data/buat_data.py
"""
import csv
import os
import random

JUMLAH = 200000

DEPAN = ["Rahmi", "Cici", "Malika", "Oskar", "Ratna", "Raina", "Usyi", "Radika",
         "Ani", "Rafid", "Ami", "Oliva", "Gada", "Budi", "Sari", "Dewi", "Agus",
         "Putri", "Eko", "Lina"]
BELAKANG = ["Simanjuntak", "Handayani", "Dubukke", "Puspita", "Susanti",
            "Firmansyah", "Dongoran", "Tampubolon", "Hartati", "Usamah",
            "Pangestu", "Maryat", "Irawan", "Santoso", "Wijaya", "Lestari"]
RESTO = ["kafe-teknik", "kedai-kopi", "warung-bu-ida", "bakso-pak-yon",
         "kantin-asrama", "kantin-pusat"]
MENU = [("roti-bakar", 12000), ("bubur-ayam", 11000), ("mie-goreng", 13000),
        ("nasi-padang", 25000), ("nasi-campur", 20000), ("ayam-geprek", 19000),
        ("kentang-goreng", 14000), ("iga-penyet", 27000), ("sate-ayam", 24000),
        ("gado-gado", 16000), ("kopi-susu", 18000)]


def pilih(daftar, r):
    return daftar[int(r.random() * len(daftar))]


def main():
    r = random.Random(2026)
    tujuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pesanan.csv")
    with open(tujuan, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["oid", "pelanggan", "resto", "menu", "harga", "prioritas",
                    "t_masuk_detik", "t_selesai_detik", "status"])
        for i in range(1, JUMLAH + 1):
            nama = pilih(DEPAN, r) + " " + pilih(BELAKANG, r)
            menu, harga = pilih(MENU, r)
            x = r.random()
            if x < 0.1:
                prioritas = 1
            elif x < 0.3:
                prioritas = 2
            else:
                prioritas = 3
            masuk = int(r.random() * 86400)
            y = r.random()
            if y < 0.0993:
                status, selesai = "ANTRE", ""
            elif y < 0.2:
                status, selesai = "CANCEL", ""
            else:
                status = "DONE"
                selesai = masuk + 600 + int(r.random() * 3000)
            w.writerow(["O-%06d" % i, nama, pilih(RESTO, r), menu, harga,
                        prioritas, masuk, selesai, status])
    print("selesai:", tujuan)


if __name__ == "__main__":
    main()
