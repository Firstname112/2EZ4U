"""Benchmark M3: tabel n vs perbandingan (insertion vs merge) + linear vs binary search.

Jalankan dari akar repo:   python benchmark/benchmark_m3.py
Keluaran: tabel Markdown siap tempel ke README, dan grafik docs/m3_grafik.png
(grafik hanya dibuat bila matplotlib terpasang:  pip install matplotlib).
"""
import os
import sys
import time

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AKAR)

from backend.m1_pesanan import muat_csv
from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort,
                                linear_search, binary_search)

UKURAN_SORT = [500, 1000, 2000, 4000, 8000, 16000]
UKURAN_MERGE_SAJA = [50000, 100000, 200000]
TARGET_CARI = ["O-000001", "O-050000", "O-100000", "O-137442", "O-199999", "O-999999"]


def ribuan(n):
    s = "%d" % n
    hasil = ""
    for i in range(len(s)):
        if i > 0 and (len(s) - i) % 3 == 0:
            hasil += "."
        hasil += s[i]
    return hasil


def ambil(arr, n):
    hasil = []
    for i in range(min(n, len(arr))):
        hasil.append(arr.get(i))
    return hasil


def jalan(fungsi, data, kunci):
    salinan = list(data)
    pc = Pencacah()
    t0 = time.perf_counter()
    fungsi(salinan, kunci, pc)
    return pc, (time.perf_counter() - t0) * 1000


def main():
    path = os.path.join(AKAR, "data", "pesanan.csv")
    arr, _ = muat_csv(path)
    print("Data: %s baris, kunci sort = harga\n" % ribuan(len(arr)))

    print("### Insertion sort vs merge sort\n")
    print("| n | insertion: perbandingan | insertion: ms | merge: perbandingan | merge: ms |")
    print("|---:|---:|---:|---:|---:|")
    titik = []
    for n in UKURAN_SORT:
        data = ambil(arr, n)
        pi, ti = jalan(insertion_sort, data, "harga")
        pm, tm = jalan(merge_sort, data, "harga")
        titik.append((n, pi.perbandingan, pm.perbandingan))
        print("| %s | %s | %.2f | %s | %.2f |" % (ribuan(n), ribuan(pi.perbandingan), ti,
                                                  ribuan(pm.perbandingan), tm))
    for n in UKURAN_MERGE_SAJA:
        if n > len(arr):
            continue
        data = ambil(arr, n)
        pm, tm = jalan(merge_sort, data, "harga")
        print("| %s | ditolak (> 20.000) | - | %s | %.2f |" % (ribuan(n), ribuan(pm.perbandingan), tm))

    print("\n### Rasio saat n dilipatduakan\n")
    print("| n -> 2n | insertion | merge |")
    print("|---|---:|---:|")
    for i in range(1, len(titik)):
        print("| %s -> %s | x%.2f | x%.2f |" % (ribuan(titik[i - 1][0]), ribuan(titik[i][0]),
                                               titik[i][1] / titik[i - 1][1],
                                               titik[i][2] / titik[i - 1][2]))

    print("\n### Linear search vs binary search (oid)\n")
    semua = ambil(arr, len(arr))
    terurut = list(semua)
    pb = Pencacah()
    t0 = time.perf_counter()
    merge_sort(terurut, "oid", pb)
    ms_bangun = (time.perf_counter() - t0) * 1000
    print("Biaya membangun daftar terurut oid (sekali, merge sort): %.2f ms, %s perbandingan\n" %
          (ms_bangun, ribuan(pb.perbandingan)))
    print("| target | linear: perbandingan | linear: ms | binary: perbandingan | binary: ms |")
    print("|---|---:|---:|---:|---:|")
    for target in TARGET_CARI:
        pl = Pencacah()
        t0 = time.perf_counter()
        linear_search(semua, target, "oid", pl)
        tl = (time.perf_counter() - t0) * 1000
        pbn = Pencacah()
        t0 = time.perf_counter()
        binary_search(terurut, target, "oid", pbn)
        tb = (time.perf_counter() - t0) * 1000
        print("| %s | %s | %.2f | %s | %.3f |" % (target, ribuan(pl.perbandingan), tl,
                                                  ribuan(pbn.perbandingan), tb))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib tidak ada, grafik dilewati. Install: pip install matplotlib)")
        return
    xs = []
    yi = []
    ym = []
    for t in titik:
        xs.append(t[0])
        yi.append(t[1])
        ym.append(t[2])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(xs, yi, "o-", label="insertion sort  O(n^2)")
    ax[0].plot(xs, ym, "s-", label="merge sort  O(n log n)")
    ax[0].set_xlabel("n (jumlah pesanan)")
    ax[0].set_ylabel("jumlah perbandingan")
    ax[0].set_title("Skala linear")
    ax[0].legend()
    ax[0].grid(alpha=0.3)
    ax[1].loglog(xs, yi, "o-", label="insertion sort")
    ax[1].loglog(xs, ym, "s-", label="merge sort")
    ax[1].set_xlabel("n (log)")
    ax[1].set_ylabel("perbandingan (log)")
    ax[1].set_title("Skala log-log (kemiringan = pangkat n)")
    ax[1].legend()
    ax[1].grid(alpha=0.3, which="both")
    fig.tight_layout()
    keluar = os.path.join(AKAR, "docs", "m3_grafik.png")
    os.makedirs(os.path.dirname(keluar), exist_ok=True)
    fig.savefig(keluar, dpi=130)
    print("\nGrafik disimpan: docs/m3_grafik.png")


if __name__ == "__main__":
    main()
