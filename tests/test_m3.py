"""Tes M3. Jalankan dari akar repo:  python tests/test_m3.py   (atau pytest)."""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort, linear_search,
                                binary_search, pembuat_kunci, BELUM_SELESAI)


class P:
    """Pesanan tiruan untuk menguji algoritma tanpa bergantung pada M1."""
    def __init__(self, oid, harga, selesai, urut=0):
        self.oid = oid
        self.harga = harga
        self.selesai = selesai
        self.urut = urut


def ident(x):
    return x


def terurut(A):
    i = 1
    while i < len(A):
        if A[i - 1] > A[i]:
            return False
        i += 1
    return True


def acak(n, maks, seed=1):
    r = random.Random(seed)
    return [r.randint(0, maks) for _ in range(n)]


def test_sort_empat_pola():
    pola = [acak(300, 10 ** 6), list(range(300)), list(range(300, 0, -1)), acak(300, 5), [], [7]]
    for data in pola:
        for fungsi in (insertion_sort, merge_sort):
            a = list(data)
            fungsi(a, ident, Pencacah())
            assert len(a) == len(data) and terurut(a), fungsi.__name__
            assert sum(a) == sum(data)                   # tidak ada data hilang/ganda
            if fungsi is merge_sort:
                b = list(data)
                insertion_sort(b, ident, Pencacah())
                assert a == b                            # kedua sort identik


def test_merge_sort_tidak_kehilangan_data():
    # kasus ukuran ganjil memaksa sisa salah satu sisi disalin
    for n in (2, 3, 5, 7, 15, 17, 33):
        a = acak(n, 100, seed=n)
        merge_sort(a, ident, Pencacah())
        assert len(a) == n and terurut(a)


def test_stabil_dan_identik():
    r = random.Random(3)
    data = []
    for i in range(500):
        data.append(P("O-%06d" % (i + 1), r.randint(1, 8) * 1000, None, i))
    a = list(data)
    b = list(data)
    insertion_sort(a, "harga", Pencacah())
    merge_sort(b, "harga", Pencacah())
    for i in range(len(a)):
        assert a[i] is b[i]                              # identik baris per baris
    for i in range(1, len(a)):
        if a[i - 1].harga == a[i].harga:
            assert a[i - 1].urut < a[i].urut             # urutan masuk dipertahankan


def test_selesai_kosong_paling_akhir():
    data = [P("a", 1, None), P("b", 1, 500), P("c", 1, 100), P("d", 1, None)]
    merge_sort(data, "selesai", Pencacah())
    assert data[0].oid == "c" and data[1].oid == "b"
    assert pembuat_kunci("selesai")(data[2]) == BELUM_SELESAI


def test_binary_search_lima_kasus():
    A = [10, 20, 30, 40, 50, 60, 70]
    assert binary_search(A, 40, ident) == 3      # tengah
    assert binary_search(A, 10, ident) == 0      # kiri
    assert binary_search(A, 70, ident) == 6      # kanan
    assert binary_search(A, 35, ident) == -1     # tidak ada
    assert binary_search([], 5, ident) == -1     # larik kosong
    assert binary_search([5], 5, ident) == 0


def test_linear_search():
    A = [4, 9, 1, 7]
    pc = Pencacah()
    assert linear_search(A, 1, ident, pc) == 2 and pc.perbandingan == 3
    pc.reset()
    assert linear_search(A, 99, ident, pc) == -1 and pc.perbandingan == 4
    assert linear_search([], 1, ident) == -1


def test_binary_oid_pada_pesanan():
    data = [P("O-%06d" % i, 1000, None) for i in range(1, 2001)]
    pc = Pencacah()
    idx = binary_search(data, "O-001234", "oid", pc)
    assert idx == 1233 and pc.perbandingan <= 11


def test_pola_perbandingan():
    # n dilipatduakan: insertion ~4x, merge ~2x
    hasil = []
    for n in (1000, 2000):
        a = acak(n, 10 ** 6, seed=9)
        b = list(a)
        pi = Pencacah()
        pm = Pencacah()
        insertion_sort(a, ident, pi)
        merge_sort(b, ident, pm)
        hasil.append((pi.perbandingan, pm.perbandingan))
    rasio_ins = hasil[1][0] / hasil[0][0]
    rasio_mrg = hasil[1][1] / hasil[0][1]
    assert 3.5 < rasio_ins < 4.5, rasio_ins
    assert 1.9 < rasio_mrg < 2.3, rasio_mrg


def test_insertion_hampir_terurut_mendekati_linear():
    a = list(range(2000))
    pc = Pencacah()
    insertion_sort(a, ident, pc)
    assert pc.perbandingan == 1999


if __name__ == "__main__":
    nama = list(globals().keys())
    for k in nama:
        if k.startswith("test_"):
            globals()[k]()
            print("OK  ", k)
    print("semua tes M3 lulus")
