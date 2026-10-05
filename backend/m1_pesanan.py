import csv


# data
def fmt_waktu(detik):
    """Detik sejak 00:00 -> 'hh:mm:ss'. None -> '-'."""
    if detik is None:
        return "-"
    d = detik % 86400
    return "%02d:%02d:%02d" % (d // 3600, (d % 3600) // 60, d % 60)


NAMA_PRIORITAS_1 = "VIP"
NAMA_PRIORITAS_2 = "PRIORITAS"
NAMA_PRIORITAS_3 = "REGULER"


def nama_prioritas(p):
    if p == 1:
        return NAMA_PRIORITAS_1
    if p == 2:
        return NAMA_PRIORITAS_2
    return NAMA_PRIORITAS_3


class Pesanan:
    __slots__ = ("oid", "pelanggan", "resto", "menu", "harga",
                 "prioritas", "t_masuk", "t_selesai", "status")

    def __init__(self, oid, pelanggan, resto, menu, harga,
                 prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas
        self.t_masuk = t_masuk
        self.t_selesai = t_selesai
        self.status = status

    def ke_baris(self):
        """Daftar pasangan (kolom, isi) untuk ditampilkan di antarmuka."""
        return [
            ("oid", self.oid),
            ("pelanggan", self.pelanggan),
            ("resto", self.resto),
            ("menu", self.menu),
            ("harga", "%d" % self.harga),
            ("prioritas", "%d (%s)" % (self.prioritas, nama_prioritas(self.prioritas))),
            ("masuk", fmt_waktu(self.t_masuk)),
            ("selesai", fmt_waktu(self.t_selesai)),
            ("status", self.status),
        ]


# aturan tiga jenis
class _AturanPesanan:
    """Tiga letak penyisipan; sama persis untuk Array dan LinkList."""

    def tambah_reguler(self, v):
        self.append(v)
        return len(self) - 1

    def tambah_prioritas(self, v):
        i = len(self) // 2
        self.insert(i, v)
        return i

    def tambah_vip(self, v):
        self.insert(0, v)
        return 0


# Array
class Array(_AturanPesanan):
    """Array dinamis: kapasitas digandakan ketika penuh (amortized O(1))."""

    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self._cap = kapasitas
        self._data = [None] * kapasitas
        self._n = 0
        self.langkah_terakhir = 0   
        self.total_geser = 0        
        self.total_salin = 0        
        self.jumlah_tumbuh = 0      

    def __len__(self):
        return self._n

    @property
    def kapasitas(self):
        return self._cap

    def _tumbuh(self):
        baru = [None] * (self._cap * 2)
        i = 0
        while i < self._n:
            baru[i] = self._data[i]
            i += 1
        self.total_salin += self._n
        self.jumlah_tumbuh += 1
        self._data = baru
        self._cap = self._cap * 2

    def _cek(self, i, batas):
        if i < 0 or i >= batas:
            raise IndexError("indeks %d di luar jangkauan (panjang %d)" % (i, self._n))

    def get(self, i):
        self._cek(i, self._n)
        self.langkah_terakhir = 0
        return self._data[i]

    def append(self, v):
        if self._n == self._cap:
            self._tumbuh()
        self._data[self._n] = v
        self._n += 1
        self.langkah_terakhir = 0

    def insert(self, i, v):
        self._cek(i, self._n + 1)
        if self._n == self._cap:
            self._tumbuh()
        j = self._n
        geser = 0
        while j > i:
            self._data[j] = self._data[j - 1]
            j -= 1
            geser += 1
        self._data[i] = v
        self._n += 1
        self.langkah_terakhir = geser
        self.total_geser += geser

    def remove_at(self, i):
        self._cek(i, self._n)
        v = self._data[i]
        j = i
        geser = 0
        while j < self._n - 1:
            self._data[j] = self._data[j + 1]
            j += 1
            geser += 1
        self._data[self._n - 1] = None
        self._n -= 1
        self.langkah_terakhir = geser
        self.total_geser += geser
        return v

    def to_list(self):
        hasil = []
        i = 0
        while i < self._n:
            hasil.append(self._data[i])
            i += 1
        return hasil

    def stats(self):
        return [
            ("array_len", self._n),
            ("array_capacity", self._cap),
            ("array_tumbuh", self.jumlah_tumbuh),
            ("array_total_salin", self.total_salin),
            ("array_total_geser", self.total_geser),
        ]


# LinkList
class _Simpul:
    __slots__ = ("nilai", "next")

    def __init__(self, nilai):
        self.nilai = nilai
        self.next = None


class LinkList(_AturanPesanan):
    """Singly linked list dengan penunjuk head dan tail."""

    def __init__(self):
        self.head = None
        self.tail = None
        self._n = 0
        self.langkah_terakhir = 0   
        self.total_telusur = 0

    def __len__(self):
        return self._n

    def _cek(self, i, batas):
        if i < 0 or i >= batas:
            raise IndexError("indeks %d di luar jangkauan (panjang %d)" % (i, self._n))

    def _catat(self, langkah):
        self.langkah_terakhir = langkah
        self.total_telusur += langkah

    def get(self, i):
        self._cek(i, self._n)
        cur = self.head
        langkah = 0
        while langkah < i:
            cur = cur.next
            langkah += 1
        self._catat(langkah)
        return cur.nilai

    def append(self, v):
        s = _Simpul(v)
        if self.tail is None:
            self.head = s
            self.tail = s
        else:
            self.tail.next = s
            self.tail = s
        self._n += 1
        self._catat(0)

    def prepend(self, v):
        s = _Simpul(v)
        s.next = self.head
        self.head = s
        if self.tail is None:
            self.tail = s
        self._n += 1
        self._catat(0)

    def insert(self, i, v):
        self._cek(i, self._n + 1)
        if i == 0:
            self.prepend(v)
            return
        if i == self._n:
            self.append(v)
            return
        cur = self.head
        langkah = 0
        while langkah < i - 1:      
            cur = cur.next
            langkah += 1
        s = _Simpul(v)
        s.next = cur.next
        cur.next = s
        self._n += 1
        self._catat(langkah)

    def remove_at(self, i):
        self._cek(i, self._n)
        if i == 0:
            s = self.head
            self.head = s.next
            if self.head is None:
                self.tail = None
            self._n -= 1
            self._catat(0)
            return s.nilai
        cur = self.head
        langkah = 0
        while langkah < i - 1:
            cur = cur.next
            langkah += 1
        s = cur.next
        cur.next = s.next
        if s is self.tail:
            self.tail = cur
        self._n -= 1
        self._catat(langkah)
        return s.nilai

    def to_list(self):
        hasil = []
        cur = self.head
        while cur is not None:
            hasil.append(cur.nilai)
            cur = cur.next
        return hasil

    def stats(self):
        return [
            ("linkedlist_len", self._n),
            ("linkedlist_total_telusur", self.total_telusur),
        ]


# loader
def muat_csv(path, batas=None):
    """Baca pesanan.csv sekali, isi Array dan LinkList dengan data yang sama."""
    arr = Array()
    ll = LinkList()
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        pembaca = csv.reader(f)
        next(pembaca, None)  
        for b in pembaca:
            if len(b) < 9:
                continue
            if batas is not None and n >= batas:
                break
            t_selesai = None
            if b[7] != "":
                t_selesai = int(b[7])
            p = Pesanan(b[0], b[1], b[2], b[3], int(b[4]),
                        int(b[5]), int(b[6]), t_selesai, b[8])
            arr.append(p)
            ll.append(p)
            n += 1
    return arr, ll
