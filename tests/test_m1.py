import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.m1_pesanan import Array, LinkList, Pesanan, muat_csv, fmt_waktu


def buat(n):
    return Pesanan("O-%06d" % n, "x", "r", "m", 1000, 3, 0, None, "ANTRE")


def oids(struktur):
    hasil = []
    for p in struktur.to_list():
        hasil.append(p.oid)
    return hasil


class TesArray(unittest.TestCase):
    def test_tumbuh_menggandakan_kapasitas(self):
        a = Array(4)
        for i in range(5):
            a.append(buat(i))
        self.assertEqual(a.kapasitas, 8)
        self.assertEqual(len(a), 5)
        self.assertEqual(a.jumlah_tumbuh, 1)
        self.assertEqual(a.total_salin, 4)

    def test_append_amortized_tidak_menyalin_tiap_kali(self):
        a = Array(4)
        for i in range(1000):
            a.append(buat(i))
        self.assertLess(a.total_salin, 2 * 1000)

    def test_vip_menggeser_semua(self):
        a = Array(4)
        for i in range(10):
            a.tambah_reguler(buat(i))
        pos = a.tambah_vip(buat(99))
        self.assertEqual(pos, 0)
        self.assertEqual(a.langkah_terakhir, 10)
        self.assertEqual(a.get(0).oid, "O-000099")

    def test_prioritas_di_tengah(self):
        a = Array(4)
        for i in range(10):
            a.tambah_reguler(buat(i))
        pos = a.tambah_prioritas(buat(99))
        self.assertEqual(pos, 5)
        self.assertEqual(a.langkah_terakhir, 5)

    def test_hapus_dan_batas(self):
        a = Array()
        for i in range(5):
            a.append(buat(i))
        p = a.remove_at(2)
        self.assertEqual(p.oid, "O-000002")
        self.assertEqual(len(a), 4)
        self.assertEqual(oids(a), ["O-000000", "O-000001", "O-000003", "O-000004"])
        with self.assertRaises(IndexError):
            a.get(4)
        with self.assertRaises(IndexError):
            a.remove_at(-1)
        with self.assertRaises(IndexError):
            a.insert(6, buat(1))


class TesLinkList(unittest.TestCase):
    def test_reguler_dan_vip_o1(self):
        ll = LinkList()
        for i in range(100):
            ll.tambah_reguler(buat(i))
        self.assertEqual(ll.langkah_terakhir, 0)
        ll.tambah_vip(buat(999))
        self.assertEqual(ll.langkah_terakhir, 0)
        self.assertEqual(ll.get(0).oid, "O-000999")

    def test_prioritas_menelusuri(self):
        ll = LinkList()
        for i in range(10):
            ll.tambah_reguler(buat(i))
        pos = ll.tambah_prioritas(buat(99))
        self.assertEqual(pos, 5)
        self.assertEqual(ll.langkah_terakhir, 4)  

    def test_tail_terjaga_saat_hapus_terakhir(self):
        ll = LinkList()
        for i in range(3):
            ll.append(buat(i))
        ll.remove_at(2)
        ll.append(buat(7))
        self.assertEqual(oids(ll), ["O-000000", "O-000001", "O-000007"])

    def test_hapus_sampai_kosong_lalu_isi(self):
        ll = LinkList()
        ll.append(buat(1))
        ll.remove_at(0)
        self.assertEqual(len(ll), 0)
        self.assertIsNone(ll.head)
        self.assertIsNone(ll.tail)
        ll.append(buat(2))
        self.assertEqual(oids(ll), ["O-000002"])

    def test_batas(self):
        ll = LinkList()
        with self.assertRaises(IndexError):
            ll.get(0)
        with self.assertRaises(IndexError):
            ll.remove_at(0)


class TesKesetaraan(unittest.TestCase):
    def test_operasi_acak_hasil_sama(self):
        r = random.Random(7)
        a = Array(2)
        ll = LinkList()
        nomor = 0
        for _ in range(3000):
            x = r.random()
            if x < 0.25:
                a.tambah_reguler(buat(nomor)); ll.tambah_reguler(buat(nomor)); nomor += 1
            elif x < 0.45:
                a.tambah_prioritas(buat(nomor)); ll.tambah_prioritas(buat(nomor)); nomor += 1
            elif x < 0.65:
                a.tambah_vip(buat(nomor)); ll.tambah_vip(buat(nomor)); nomor += 1
            elif len(a) > 0:
                i = int(r.random() * len(a))
                self.assertEqual(a.remove_at(i).oid, ll.remove_at(i).oid)
            self.assertEqual(len(a), len(ll))
        self.assertEqual(oids(a), oids(ll))


class TesLoader(unittest.TestCase):
    def test_muat_csv(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_mini.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("oid,pelanggan,resto,menu,harga,prioritas,t_masuk_detik,t_selesai_detik,status\n")
            f.write("O-000001,Rahmi,kafe-teknik,roti-bakar,12000,3,47985,,CANCEL\n")
            f.write("O-000002,Cici,kedai-kopi,bubur-ayam,11000,3,59780,62115,DONE\n")
        try:
            a, ll = muat_csv(path)
        finally:
            os.remove(path)
        self.assertEqual(len(a), 2)
        self.assertEqual(len(ll), 2)
        self.assertIsNone(a.get(0).t_selesai)
        self.assertEqual(a.get(1).t_selesai, 62115)
        self.assertEqual(ll.get(1).harga, 11000)

    def test_fmt_waktu(self):
        self.assertEqual(fmt_waktu(47985), "13:19:45")
        self.assertEqual(fmt_waktu(None), "-")


if __name__ == "__main__":
    unittest.main()
