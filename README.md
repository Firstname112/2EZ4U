# Proyek 2EZ4U APP

Engine backend layanan antar makanan mini (Struktur Data & Analisa Algoritma, EC234303).

## Status
- [x] M1 - Array vs Linked List (`backend/m1_pesanan.py`)
- [ ] M2 - Stack & Queue
- [ ] M3 - Sort & Search
- [ ] M4 - Hash table
- [ ] M5 - BST + MinHeap
- [ ] M6 - Graf + BFS + Dijkstra

## Cara menjalankan
```
python data/buat_data.py   # hanya bila data/pesanan.csv dari dosen belum ada
python app.py              # buka jendela Tkinter, klik Load, pilih menu M1
python -m unittest discover -s tests -v
```
Python 3.11+. Tanpa library eksternal.

## M1 - ringkasan desain
- `Array`: larik berukuran tetap (`[None] * kapasitas`). Saat penuh, kapasitas digandakan
  lalu isi disalin sekali, sehingga `append` amortized O(1).
- `LinkList`: simpul tunggal dengan penunjuk `head` dan `tail`; `append` dan `prepend` O(1),
  akses/sisip tengah/hapus menelusuri simpul O(n).
- Tiga jenis pesanan, aturan sama untuk kedua struktur:
  REGULER -> belakang, PRIORITAS -> indeks `n // 2`, VIP -> indeks 0.
- Setiap operasi mencatat `langkah_terakhir` (elemen digeser / simpul ditelusuri) agar
  perbandingan tidak hanya bergantung pada waktu mesin.

| Operasi | Array | Linked List |
|---|---|---|
| Lihat ke-i | O(1) | O(n) |
| Tambah REGULER | O(1) amortized | O(1) |
| Tambah PRIORITAS | O(n) geser | O(n) telusur |
| Tambah VIP | O(n) geser | O(1) |
| Hapus ke-i | O(n) geser | O(n) telusur |

> TODO sebelum submit: tempel screenshot, video demo, diagram, dan tabel hasil benchmark
> (jalankan `python tests/benchmark_m1.py`) di sini.
