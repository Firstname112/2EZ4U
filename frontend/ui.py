import os
import time
import tkinter as tk
from tkinter import ttk, messagebox

from backend.m1_pesanan import Pesanan, muat_csv, fmt_waktu
from backend.m2_antrean import ManajerAntrean, stack_postfix, format_rupiah
from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort, linear_search,
                                binary_search, KUNCI_SORT, BATAS_INSERTION)

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PESANAN = os.path.join(AKAR, "data", "pesanan.csv")

# (label menu, struktur, aksi)
MENU_M1 = [
    ("ARRAY - LIHAT PESANAN", "array", "lihat"),
    ("ARRAY - TAMBAH PESANAN REGULER", "array", "reguler"),
    ("ARRAY - TAMBAH PESANAN PRIORITAS", "array", "prioritas"),
    ("ARRAY - TAMBAH PESANAN VIP", "array", "vip"),
    ("ARRAY - HAPUS PESANAN", "array", "hapus"),
    ("LINKEDLIST - LIHAT PESANAN", "linkedlist", "lihat"),
    ("LINKEDLIST - TAMBAH PESANAN REGULER", "linkedlist", "reguler"),
    ("LINKEDLIST - TAMBAH PESANAN PRIORITAS", "linkedlist", "prioritas"),
    ("LINKEDLIST - TAMBAH PESANAN VIP", "linkedlist", "vip"),
    ("LINKEDLIST - HAPUS PESANAN", "linkedlist", "hapus"),
]

MENU_M2 = [
    ("STACK - POSTFIX (MESIN KASIR)", "m2", "postfix"),
    ("STACK - UNDO", "m2", "undo"),
    ("STACK - REDO", "m2", "redo"),
    ("QUEUE - ENQUEUE", "m2", "enqueue"),
    ("QUEUE - DEQUEUE NAIF", "m2", "dequeue_naif"),
    ("QUEUE - DEQUEUE CIRCULAR", "m2", "dequeue_circular"),
]

MENU_M3 = [
    ("SORT - INSERTION SORT", "m3", "insertion_sort"),
    ("SORT - MERGE SORT", "m3", "merge_sort"),
    ("SEARCH - LINEAR SEARCH", "m3", "linear_search"),
    ("SEARCH - BINARY SEARCH", "m3", "binary_search"),
]

MENU_SEMUA = MENU_M1 + MENU_M2 + MENU_M3

KETERANGAN = [
    ("postfix", "Struk infix diubah ke postfix (stack operator), lalu dihitung (stack angka). Baris 1.x konversi, 2.x evaluasi."),
    ("undo", "Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya. Aksi terakhir dibatalkan lebih dulu."),
    ("redo", "Mengerjakan ulang aksi aslinya (bukan kebalikannya). Aksi baru apa pun mengosongkan tumpukan redo."),
    ("enqueue", "Menambah pesanan di ujung belakang KEDUA antrean (naif dan circular). O(1) di keduanya."),
    ("dequeue_naif", "Mengambil indeks 0 lalu menggeser seluruh sisa isi ke kiri: O(n) setiap dequeue."),
    ("dequeue_circular", "Hanya penunjuk front yang maju, isi larik tidak digeser: O(1)."),
    ("insertion_sort", "Setiap elemen digeser mundur sampai menemukan tempatnya. Stabil, tetapi kerjanya tumbuh kuadratik O(n^2). Dibatasi 20.000 baris."),
    ("merge_sort", "Larik dibelah dua terus-menerus, lalu potongan yang sudah terurut disatukan kembali. Stabil, O(n log n)."),
    ("linear_search", "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut. Kasus terburuk menyentuh seluruh data: O(n)."),
    ("binary_search", "Membuang separuh sisa daftar pada setiap perbandingan: O(log n). Menuntut daftar yang SUDAH terurut menurut oid; daftar itu dibangun sekali dengan merge sort."),
    ("lihat", "Membuka detail satu pesanan berdasarkan indeks (0-based)."),
    ("reguler", "Pesanan REGULER (3) masuk paling belakang."),
    ("prioritas", "Pesanan PRIORITAS (2) menyerobot ke tengah barisan (indeks n/2)."),
    ("vip", "Pesanan VIP (1) langsung ke urutan pertama."),
    ("hapus", "Mencabut pesanan ke-i dari barisan (indeks 0-based)."),
]

PRIORITAS_ANGKA = [("reguler", 3), ("prioritas", 2), ("vip", 1)]


class Ditolak(Exception):
    """Permintaan ditolak dengan pesan (bukan galat input)."""
    pass


def cari(daftar, kunci):
    for k, v in daftar:
        if k == kunci:
            return v
    return None


def status_pesanan(p):
    s = getattr(p, "status", None)
    if s is None:
        s = cari(p.ke_baris(), "status")
    return s


def ribuan(n):
    s = "%d" % n
    hasil = ""
    hitung = 0
    i = len(s) - 1
    while i >= 0:
        if hitung > 0 and hitung % 3 == 0:
            hasil = "." + hasil
        hasil = s[i] + hasil
        hitung += 1
        i -= 1
    return hasil


class Aplikasi(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("2EZ4U Food Delivery")
        self.geometry("1100x780")
        self.arr = None
        self.ll = None
        self.m2 = None
        self.idx_oid = None          # daftar terurut oid (untuk binary search)
        self.ms_idx_oid = 0.0
        self.next_id = 1
        self.menu_aktif = -1
        self.entries = []
        self._bangun()

    # layout
    def _bangun(self):
        judul = tk.Label(self, text="2EZ4U Food Delivery", bg="#2c3e5a", fg="white",
                         font=("Helvetica", 14, "bold"), anchor="w", padx=10, pady=8)
        judul.pack(fill="x")

        tengah = tk.Frame(self)
        tengah.pack(fill="both", expand=True)

        # panel menu kiri dibuat bisa di-scroll supaya semua menu (M1 + M2) selalu terjangkau
        wadah = tk.Frame(tengah, width=300)
        wadah.pack(side="left", fill="y", padx=6, pady=6)
        wadah.pack_propagate(False)
        kanvas = tk.Canvas(wadah, highlightthickness=0)
        sbk = ttk.Scrollbar(wadah, orient="vertical", command=kanvas.yview)
        kanvas.configure(yscrollcommand=sbk.set)
        sbk.pack(side="right", fill="y")
        kanvas.pack(side="left", fill="both", expand=True)
        kiri = tk.Frame(kanvas)
        jendela = kanvas.create_window((0, 0), window=kiri, anchor="nw")
        kiri.bind("<Configure>", lambda e: kanvas.configure(scrollregion=kanvas.bbox("all")))
        kanvas.bind("<Configure>", lambda e: kanvas.itemconfigure(jendela, width=e.width))

        def roda(e):
            if e.num == 4:
                d = -1
            elif e.num == 5:
                d = 1
            else:
                d = -1 if e.delta > 0 else 1
            kanvas.yview_scroll(d, "units")

        def aktif(e):
            self.bind_all("<MouseWheel>", roda)
            self.bind_all("<Button-4>", roda)
            self.bind_all("<Button-5>", roda)

        def nonaktif(e):
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")

        wadah.bind("<Enter>", aktif)
        wadah.bind("<Leave>", nonaktif)

        self._header(kiri, "DATA")
        tk.Button(kiri, text="Load", anchor="w", command=self._muat).pack(fill="x", pady=1)
        self._header(kiri, "M1 - DATA PESANAN")
        i = 0
        while i < len(MENU_SEMUA):
            if i == len(MENU_M1):
                self._header(kiri, "M2 - STACK DAN QUEUE")
            elif i == len(MENU_M1) + len(MENU_M2):
                self._header(kiri, "M3 - SORT DAN SEARCH")
            tk.Button(kiri, text=MENU_SEMUA[i][0], anchor="w",
                      command=lambda k=i: self._pilih(k)).pack(fill="x", pady=1)
            i += 1

        kanan = tk.Frame(tengah)
        kanan.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        self.lbl_judul = tk.Label(kanan, text="Pilih menu di kiri", anchor="w",
                                  font=("Helvetica", 12, "bold"))
        self.lbl_judul.pack(fill="x")
        self.lbl_ket = tk.Label(kanan, text="Klik Load dulu untuk memuat 200.000 pesanan.",
                                anchor="w", fg="#666666", wraplength=620, justify="left")
        self.lbl_ket.pack(fill="x", pady=(0, 6))

        self.frm_form = tk.Frame(kanan)
        self.frm_form.pack(fill="x")
        self.btn_jalan = tk.Button(kanan, text="JALANKAN", bg="#2c3e5a", fg="white",
                                   command=self._jalankan, state="disabled")
        self.btn_jalan.pack(anchor="w", pady=6)

        self.lbl_hasil = tk.Label(kanan, text="", anchor="w", justify="left", wraplength=620)
        self.lbl_hasil.pack(fill="x")

        frm_tab = tk.Frame(kanan)
        frm_tab.pack(fill="both", expand=True, pady=4)
        sb = ttk.Scrollbar(frm_tab, orient="vertical")
        self.tabel = ttk.Treeview(frm_tab, columns=("kolom", "isi"), show="headings", height=10,
                                  yscrollcommand=sb.set)
        sb.config(command=self.tabel.yview)
        sb.pack(side="right", fill="y")
        self.tabel.pack(side="left", fill="both", expand=True)
        self._atur_tabel(("kolom", "isi"), (140, 420))

        tk.Label(kanan, text="COMMAND", anchor="w", font=("Helvetica", 9, "bold")).pack(fill="x")
        self.log = tk.Text(kanan, height=6, font=("Courier", 9))
        self.log.pack(fill="x")

        self.status = tk.Label(self, text="[siap]", anchor="w", bg="#2c3e5a", fg="white",
                               font=("Courier", 9), padx=8)
        self.status.pack(fill="x", side="bottom")

    def _header(self, induk, teks):
        tk.Label(induk, text=teks, anchor="w", fg="#2c3e5a",
                 font=("Helvetica", 8, "bold")).pack(fill="x", pady=(8, 0))

    # aksi
    def _catat(self, perintah, modul, ms):
        self.log.insert("1.0", "%-26s -> %-14s %.2f ms\n" % (perintah, modul, ms))
        self.status.config(text="[%s] %.2f ms" % (modul, ms))

    def _muat(self):
        if not os.path.exists(CSV_PESANAN):
            messagebox.showerror("Data tidak ada",
                                 "File data/pesanan.csv tidak ditemukan.\n"
                                 "Letakkan data dari dosen, atau jalankan: python data/buat_data.py")
            return
        t0 = time.perf_counter()
        self.arr, self.ll = muat_csv(CSV_PESANAN)
        ms = (time.perf_counter() - t0) * 1000
        self.next_id = len(self.arr) + 1
        self.idx_oid = None
        self._catat("load", "M1 - larik+rantai", ms)
        t1 = time.perf_counter()
        self.m2 = ManajerAntrean()
        antre = []
        for j in range(len(self.arr)):
            p = self.arr.get(j)
            if status_pesanan(p) == "ANTRE":
                antre.append(p)
        self.m2.isi_awal(antre)
        ms2 = (time.perf_counter() - t1) * 1000
        self._catat("load_antrean", "M2 - antrean", ms2)
        self.lbl_hasil.config(text="%s pesanan dimuat ke Array dan LinkList (kapasitas array %s).\n"
                                   "%s pesanan berstatus ANTRE masuk ke KEDUA antrean (naif & circular)." %
                              (ribuan(len(self.arr)), ribuan(self.arr.kapasitas), ribuan(len(antre))))
        self._kosongkan_tabel()
        self.btn_jalan.config(state="normal")

    def _pilih(self, k):
        self.menu_aktif = k
        label, struktur, aksi = MENU_SEMUA[k]
        self.lbl_judul.config(text=label)
        self.lbl_ket.config(text=cari(KETERANGAN, aksi))
        for w in self.frm_form.winfo_children():
            w.destroy()
        self.entries = []
        if struktur == "m2":
            self._form_m2(aksi)
        elif struktur == "m3":
            self._form_m3(aksi)
        elif aksi == "lihat" or aksi == "hapus":
            self._isian("Indeks ke-i (0-based)", "0")
        else:
            self._isian("Nama pelanggan", "Pelanggan Baru")
            self._isian("Resto", "kafe-teknik")
            self._isian("Menu", "roti-bakar")
            self._isian("Harga", "12000")
        self.lbl_hasil.config(text="")
        self._kosongkan_tabel()
        if aksi == "postfix":
            self.btn_jalan.config(state="normal")      # kasir tidak butuh Load
        elif self.arr is None:
            self.btn_jalan.config(state="disabled")

    def _form_m2(self, aksi):
        if aksi == "postfix":
            self._isian("Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        elif aksi == "enqueue":
            self._isian("Nama pelanggan", "Pelanggan Baru")
        elif aksi == "dequeue_naif" or aksi == "dequeue_circular":
            self._isian("Berapa kali dequeue", "1")

    def _form_m3(self, aksi):
        if aksi == "insertion_sort":
            self._isian("Jumlah baris diurutkan", "10")
            self._pilihan("Diurutkan menurut", KUNCI_SORT, "harga")
        elif aksi == "merge_sort":
            self._isian("Jumlah baris diurutkan", "4000")
            self._pilihan("Diurutkan menurut", KUNCI_SORT, "oid")
        else:
            self._isian("Nomor pesanan (oid)", "O-137442")

    def _pilihan(self, label, nilai, awal):
        baris = tk.Frame(self.frm_form)
        baris.pack(fill="x", pady=1)
        tk.Label(baris, text=label, width=22, anchor="w").pack(side="left")
        c = ttk.Combobox(baris, values=list(nilai), state="readonly", width=27)
        c.set(awal)
        c.pack(side="left")
        self.entries.append(c)

    def _isian(self, label, awal):
        baris = tk.Frame(self.frm_form)
        baris.pack(fill="x", pady=1)
        tk.Label(baris, text=label, width=22, anchor="w").pack(side="left")
        e = tk.Entry(baris, width=30)
        e.insert(0, awal)
        e.pack(side="left")
        self.entries.append(e)

    def _atur_tabel(self, kolom, lebar):
        self.tabel.configure(columns=kolom)
        for j in range(len(kolom)):
            self.tabel.heading(kolom[j], text=kolom[j])
            self.tabel.column(kolom[j], width=lebar[j], anchor="w")

    def _kosongkan_tabel(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)
        self._atur_tabel(("kolom", "isi"), (140, 420))

    def _tabel_langkah(self, baris):
        self._kosongkan_tabel()
        self._atur_tabel(("langkah", "token", "tindakan", "stack", "output"),
                         (60, 50, 250, 110, 150))
        for r in baris:
            self.tabel.insert("", "end", values=r)

    def _tabel_pesanan(self, items):
        self._kosongkan_tabel()
        self._atur_tabel(("#", "oid", "pelanggan", "resto", "menu", "masuk"),
                         (50, 90, 160, 110, 100, 80))
        for j in range(min(len(items), 200)):          # batasi tampilan agar tidak membeku
            br = items[j].ke_baris()
            self.tabel.insert("", "end", values=(j + 1, cari(br, "oid"), cari(br, "pelanggan"),
                                                 cari(br, "resto"), cari(br, "menu"),
                                                 cari(br, "masuk")))

    def _tabel_sort(self, items):
        self._kosongkan_tabel()
        self._atur_tabel(("#", "oid", "harga", "selesai", "resto", "menu"),
                         (50, 90, 80, 80, 110, 110))
        for j in range(min(len(items), 200)):          # batasi tampilan agar tidak membeku
            br = items[j].ke_baris()
            self.tabel.insert("", "end", values=(j + 1, cari(br, "oid"), cari(br, "harga"),
                                                 cari(br, "selesai"), cari(br, "resto"),
                                                 cari(br, "menu")))

    def _salin_arr(self, n=None):
        """Salin n pesanan pertama dari Array M1 ke larik biasa (M1 tidak diubah)."""
        total = len(self.arr)
        if n is None or n > total:
            n = total
        hasil = []
        for j in range(n):
            hasil.append(self.arr.get(j))
        return hasil

    def _normalisasi_oid(self, teks):
        t = teks.strip().upper()
        if t == "":
            raise ValueError("nomor pesanan tidak boleh kosong")
        if t.isdigit():
            t = "O-%06d" % int(t)
        return t

    def _jalankan_m3(self, aksi):
        """Kembalikan (ms, modul, perintah). Setiap menu melaporkan jumlah perbandingan."""
        if aksi == "insertion_sort" or aksi == "merge_sort":
            n = int(self.entries[0].get().strip())
            kunci = self.entries[1].get()
            if n < 1:
                raise ValueError("jumlah baris minimal 1")
            insertion = aksi == "insertion_sort"
            if insertion and n > BATAS_INSERTION:
                raise Ditolak("batasnya %s baris, pakai merge sort untuk data penuh" %
                              ribuan(BATAS_INSERTION))
            data = self._salin_arr(n)
            pc = Pencacah()
            t0 = time.perf_counter()
            if insertion:
                insertion_sort(data, kunci, pc)
            else:
                merge_sort(data, kunci, pc)
            ms = (time.perf_counter() - t0) * 1000
            self.lbl_hasil.config(text="%s pesanan diurutkan menurut %s.\n%s perbandingan, %s pemindahan." %
                                  (ribuan(len(data)), kunci, ribuan(pc.perbandingan),
                                   ribuan(pc.pemindahan)))
            if len(data) > 200:
                self.lbl_hasil.config(text=self.lbl_hasil.cget("text") +
                                      "\n(tabel menampilkan 200 pesanan pertama)")
            self._tabel_sort(data)
            if insertion:
                return ms, "M3 - insertion sort", "insertion_sort"
            return ms, "M3 - merge sort", "merge_sort"

        oid = self._normalisasi_oid(self.entries[0].get())
        if aksi == "linear_search":
            data = self._salin_arr()
            pc = Pencacah()
            t0 = time.perf_counter()
            idx = linear_search(data, oid, "oid", pc)
            ms = (time.perf_counter() - t0) * 1000
            if idx < 0:
                self.lbl_hasil.config(text="%s tidak ditemukan setelah memeriksa %s baris.\n%s perbandingan." %
                                      (oid, ribuan(len(data)), ribuan(pc.perbandingan)))
                self._kosongkan_tabel()
            else:
                self.lbl_hasil.config(text="Ditemukan pada indeks %s.\n%s perbandingan." %
                                      (ribuan(idx), ribuan(pc.perbandingan)))
                self._isi_tabel(data[idx])
            return ms, "M3 - linear search", "linear_search"

        # binary search: butuh daftar terurut menurut oid, dibangun sekali (merge sort)
        if self.idx_oid is None:
            data = self._salin_arr()
            pb = Pencacah()
            t0 = time.perf_counter()
            merge_sort(data, "oid", pb)
            self.ms_idx_oid = (time.perf_counter() - t0) * 1000
            self.idx_oid = data
            self._catat("bangun_indeks_oid", "M3 - merge sort", self.ms_idx_oid)
            baris1 = "Daftar terurut oid dibangun sekali dengan merge sort, %.2f ms." % self.ms_idx_oid
        else:
            baris1 = "Memakai daftar terurut oid yang sudah ada (dibangun %.2f ms)." % self.ms_idx_oid
        pc = Pencacah()
        t0 = time.perf_counter()
        idx = binary_search(self.idx_oid, oid, "oid", pc)
        ms = (time.perf_counter() - t0) * 1000
        if idx < 0:
            self.lbl_hasil.config(text="%s\n%s tidak ditemukan.\n%s perbandingan, bandingkan dengan linear search." %
                                  (baris1, oid, ribuan(pc.perbandingan)))
            self._kosongkan_tabel()
        else:
            self.lbl_hasil.config(
                text="%s\nDitemukan pada baris ke-%s dari %s baris.\n%s perbandingan, bandingkan dengan linear search." %
                (baris1, ribuan(idx + 1), ribuan(len(self.idx_oid)), ribuan(pc.perbandingan)))
            self._isi_tabel(self.idx_oid[idx])
        return ms, "M3 - binary search", "binary_search"

    def _info_antrean(self):
        st = self.m2.stats()
        return ("Panjang antrean: naif %s, circular %s. Tumpukan undo %d, redo %d." %
                (ribuan(st.queue_len_naif), ribuan(st.queue_len_circular),
                 st.undo_depth, st.redo_depth))

    def _jalankan_m2(self, aksi):
        """Kembalikan (ms, modul, perintah)."""
        if aksi == "postfix":
            ekspresi = self.entries[0].get().strip()
            t0 = time.perf_counter()
            postfix, total, baris = stack_postfix(ekspresi)
            ms = (time.perf_counter() - t0) * 1000
            self.lbl_hasil.config(text="Struk  : %s\nPostfix: %s\nTOTAL  : %s" %
                                  (ekspresi, postfix, format_rupiah(total)))
            self._tabel_langkah(baris)
            return ms, "M2 - stack", "stack_postfix"

        if aksi == "undo" or aksi == "redo":
            t0 = time.perf_counter()
            a = self.m2.undo_last() if aksi == "undo" else self.m2.redo_last()
            ms = (time.perf_counter() - t0) * 1000
            if a is None:
                self.lbl_hasil.config(text="Tidak ada aksi untuk %s." %
                                      ("dibatalkan (tumpukan undo kosong)" if aksi == "undo"
                                       else "diulang (tumpukan redo kosong)"))
                self._kosongkan_tabel()
                return ms, "M2 - stack", "stack_" + aksi
            if a.jenis == "ENQUEUE":
                if aksi == "undo":
                    kal = "Pembatalan enqueue: %s dikeluarkan lagi dari belakang." % a.data.oid
                else:
                    kal = "Enqueue dikerjakan lagi: %s masuk kembali ke belakang." % a.data.oid
                self._isi_tabel(a.data)
            elif a.jenis == "DEQUEUE":
                if aksi == "undo":
                    kal = "Pembatalan dequeue: %s pesanan dikembalikan ke DEPAN antrean %s." % (
                        ribuan(len(a.data)), a.target)
                else:
                    kal = "Dequeue dikerjakan lagi: %s pesanan keluar lagi dari antrean %s." % (
                        ribuan(len(a.data)), a.target)
                self._tabel_pesanan(a.data)
            else:
                kal = "Aksi %s %s." % (a.jenis, "dibatalkan" if aksi == "undo" else "diulang")
                self._kosongkan_tabel()
            self.lbl_hasil.config(text=kal + "\n" + self._info_antrean())
            return ms, "M2 - stack", "stack_" + aksi

        if aksi == "enqueue":
            pelanggan = self.entries[0].get().strip()
            if pelanggan == "":
                raise ValueError("nama pelanggan tidak boleh kosong")
            lt = time.localtime()
            masuk = lt.tm_hour * 3600 + lt.tm_min * 60 + lt.tm_sec
            p = Pesanan("O-%06d" % self.next_id, pelanggan, "kafe-teknik", "roti-bakar",
                        12000, 3, masuk, None, "ANTRE")
            self.next_id += 1
            t0 = time.perf_counter()
            self.m2.enqueue(p)
            ms = (time.perf_counter() - t0) * 1000
            self.lbl_hasil.config(text="%s masuk ke barisan paling belakang pada KEDUA antrean.\n%s" %
                                  (p.oid, self._info_antrean()))
            self._isi_tabel(p)
            return ms, "M2 - queue", "queue_enqueue"

        # dequeue naif / circular
        k = int(self.entries[0].get().strip())
        if k < 1:
            raise ValueError("jumlah dequeue minimal 1")
        naif = aksi == "dequeue_naif"
        if naif and k > 1000:
            raise ValueError("dequeue naif dibatasi 1.000 per klik (O(n) tiap dequeue, bisa membeku)")
        t0 = time.perf_counter()
        if naif:
            items, geser = self.m2.dequeue_naif(k)
        else:
            items, geser = self.m2.dequeue_circular(k)
        ms = (time.perf_counter() - t0) * 1000
        if len(items) == 0:
            self.lbl_hasil.config(text="Antrean kosong, tidak ada pesanan yang keluar.")
            self._kosongkan_tabel()
        else:
            if naif:
                kal = ("%s pesanan keluar dari depan antrean naif.\n"
                       "Total %s elemen digeser, rata-rata %s geseran per dequeue.\n"
                       "Sisa antrean naif %s." %
                       (ribuan(len(items)), ribuan(geser), ribuan(geser // len(items)),
                        ribuan(len(self.m2.naif))))
            else:
                q = self.m2.melingkar
                kal = ("%s pesanan keluar dari depan antrean circular.\n"
                       "Tidak ada elemen yang digeser. front sekarang %s, rear %s, kapasitas %s.\n"
                       "Sisa antrean circular %s." %
                       (ribuan(len(items)), ribuan(q.front), ribuan(q.rear),
                        ribuan(q.kapasitas()), ribuan(len(q))))
            if len(items) > 200:
                kal += "\n(tabel menampilkan 200 pesanan pertama)"
            self.lbl_hasil.config(text=kal)
            self._tabel_pesanan(items)
        if naif:
            return ms, "M2 - queue naif", "queue_dequeue_naive"
        return ms, "M2 - queue circular", "queue_dequeue_circular"

    def _isi_tabel(self, p):
        self._kosongkan_tabel()
        for kolom, isi in p.ke_baris():
            self.tabel.insert("", "end", values=(kolom, isi))

    def _jalankan(self):
        if self.menu_aktif < 0:
            messagebox.showinfo("Pilih menu", "Pilih salah satu menu di kiri.")
            return
        label, nama_struktur, aksi = MENU_SEMUA[self.menu_aktif]
        if self.arr is None and aksi != "postfix":
            messagebox.showinfo("Belum dimuat", "Klik Load dulu.")
            return
        struktur = self.arr if nama_struktur == "array" else self.ll
        modul = "M1 - " + nama_struktur
        satuan = "elemen digeser" if nama_struktur == "array" else "simpul ditelusuri"
        perintah = nama_struktur + "_" + aksi
        try:
            if nama_struktur == "m2":
                ms, modul, perintah = self._jalankan_m2(aksi)
            elif nama_struktur == "m3":
                ms, modul, perintah = self._jalankan_m3(aksi)
            elif aksi == "lihat" or aksi == "hapus":
                i = int(self.entries[0].get().strip())
                t0 = time.perf_counter()
                if aksi == "lihat":
                    p = struktur.get(i)
                else:
                    p = struktur.remove_at(i)
                ms = (time.perf_counter() - t0) * 1000
                kata = "dibuka" if aksi == "lihat" else "dihapus"
                if aksi == "hapus":
                    # struktur lain disamakan agar tetap konsisten
                    lain = self.ll if nama_struktur == "array" else self.arr
                    lain.remove_at(i)
                self.lbl_hasil.config(
                    text="Pesanan %s indeks %d %s | %s %s | panjang sekarang %s" %
                    (p.oid, i, kata, ribuan(struktur.langkah_terakhir), satuan,
                     ribuan(len(struktur))))
                self._isi_tabel(p)
            else:
                pelanggan = self.entries[0].get().strip()
                resto = self.entries[1].get().strip()
                menu = self.entries[2].get().strip()
                harga = int(self.entries[3].get().strip())
                if pelanggan == "" or resto == "" or menu == "":
                    raise ValueError("nama, resto, dan menu tidak boleh kosong")
                prioritas = cari(PRIORITAS_ANGKA, aksi)
                lt = time.localtime()
                masuk = lt.tm_hour * 3600 + lt.tm_min * 60 + lt.tm_sec
                p = Pesanan("O-%06d" % self.next_id, pelanggan, resto, menu, harga,
                            prioritas, masuk, None, "ANTRE")
                self.next_id += 1
                t0 = time.perf_counter()
                if aksi == "reguler":
                    pos = struktur.tambah_reguler(p)
                elif aksi == "prioritas":
                    pos = struktur.tambah_prioritas(p)
                else:
                    pos = struktur.tambah_vip(p)
                ms = (time.perf_counter() - t0) * 1000
                # struktur lain ikut diisi supaya data tetap sama
                lain = self.ll if nama_struktur == "array" else self.arr
                if aksi == "reguler":
                    lain.tambah_reguler(p)
                elif aksi == "prioritas":
                    lain.tambah_prioritas(p)
                else:
                    lain.tambah_vip(p)
                self.lbl_hasil.config(
                    text="%s masuk di posisi %s dari %s | %s %s | kapasitas array %s" %
                    (p.oid, ribuan(pos), ribuan(len(struktur)),
                     ribuan(struktur.langkah_terakhir), satuan, ribuan(self.arr.kapasitas)))
                self._isi_tabel(p)
        except IndexError as e:
            self.lbl_hasil.config(text="Gagal: %s" % e)
            return
        except Ditolak as e:
            self.lbl_hasil.config(text="DITOLAK: %s" % e)
            self._kosongkan_tabel()
            return
        except ValueError as e:
            messagebox.showerror("Input tidak valid", str(e))
            return
        if (nama_struktur == "array" or nama_struktur == "linkedlist") and aksi != "lihat":
            self.idx_oid = None        # data M1 berubah -> daftar terurut oid harus dibangun ulang
        self._catat(perintah, modul, ms)


def jalankan():
    Aplikasi().mainloop()