# Array dasar
class Array:
    def __init__(self, kapasitas=4):
        self._data = [None] * kapasitas
        self._n = 0

    def ukuran(self):
        return self._n

    def kapasitas(self):
        return len(self._data)

    def get(self, i):
        if i < 0 or i >= self._n:
            raise IndexError("indeks di luar batas")
        return self._data[i]

    def ubah(self, i, v):
        if i < 0 or i >= self._n:
            raise IndexError("indeks di luar batas")
        self._data[i] = v

    def append(self, v):
        if self._n == len(self._data):          
            baru = [None] * (len(self._data) * 2)
            for i in range(self._n):
                baru[i] = self._data[i]
            self._data = baru
        self._data[self._n] = v
        self._n += 1

    def pop_last(self):
        if self._n == 0:
            raise IndexError("array kosong")
        self._n -= 1
        v = self._data[self._n]
        self._data[self._n] = None
        return v

    def ke_list(self):
        hasil = []
        for i in range(self._n):
            hasil.append(self._data[i])
        return hasil


# =====================================================================
# Stack
# =====================================================================
class Stack:
    def __init__(self):
        self._arr = Array()

    def push(self, x):
        self._arr.append(x)

    def pop(self):
        if self._arr.ukuran() == 0:
            raise IndexError("stack kosong")
        return self._arr.pop_last()

    def peek(self):
        if self._arr.ukuran() == 0:
            raise IndexError("stack kosong")
        return self._arr.get(self._arr.ukuran() - 1)

    def kosong(self):
        return self._arr.ukuran() == 0

    def ukuran(self):
        return self._arr.ukuran()

    def isi(self):
        return self._arr.ke_list()

    def kosongkan(self):
        while self._arr.ukuran() > 0:
            self._arr.pop_last()


# =====================================================================
# Bagian A (1): kasir, infix -> postfix -> total
# =====================================================================
def tokenisasi(teks):
    token = Array()
    angka = ""
    for ch in teks:
        if ch in "0123456789.":
            angka = angka + ch
            continue
        if angka != "":
            token.append(angka)
            angka = ""
        if ch in "+-*/()":
            token.append(ch)
        elif ch in " \t\n":
            pass
        else:
            raise ValueError("karakter tidak dikenal: " + ch)
    if angka != "":
        token.append(angka)
    return token.ke_list()


def _operator(t):
    return t == "+" or t == "-" or t == "*" or t == "/"


def _prioritas(op):
    if op == "*" or op == "/":
        return 2
    return 1


def _gabung(daftar):
    s = ""
    for i in range(len(daftar)):
        if i > 0:
            s = s + " "
        s = s + str(daftar[i])
    return s


def _tampil_stack(st):
    if st.kosong():
        return "kosong"
    return _gabung(st.isi())


def ke_postfix_langkah(ekspresi):
    token = tokenisasi(ekspresi)
    st = Stack()
    out = Array()
    baris = Array()
    n = 0
    for t in token:
        n += 1
        no = "1." + str(n)
        if t == "(":
            st.push(t)
            tindakan = "push ( ke stack"
        elif t == ")":
            while not st.kosong() and st.peek() != "(":
                out.append(st.pop())
            if st.kosong():
                raise ValueError("kurung tutup tanpa pasangan")
            st.pop()                                   # buang '('
            tindakan = "pop sampai (, lalu buang ("
        elif _operator(t):
            tindakan = "push " + t
            if not st.kosong() and st.peek() != "(" and _prioritas(st.peek()) >= _prioritas(t):
                ket = ""
                while (not st.kosong() and st.peek() != "("
                       and _prioritas(st.peek()) >= _prioritas(t)):
                    atas = st.pop()
                    out.append(atas)
                    ket = ket + atas + " "
                tindakan = "pop " + ket.strip() + " (lebih/sama kuat), push " + t
            st.push(t)
        else:
            out.append(t)
            tindakan = "angka, langsung keluar"
        baris.append((no, t, tindakan, _tampil_stack(st), _gabung(out.ke_list())))
    while not st.kosong():
        atas = st.pop()
        if atas == "(":
            raise ValueError("kurung buka tanpa pasangan")
        out.append(atas)
    baris.append(("1.akhir", "-", "pop sisa stack", "kosong", _gabung(out.ke_list())))
    return out.ke_list(), baris.ke_list()


def ke_postfix(ekspresi):
    postfix, _ = ke_postfix_langkah(ekspresi)
    return postfix


def _angka(s):
    if "." in s:
        return float(s)
    return int(s)


def hitung_langkah(postfix):
    st = Stack()
    baris = Array()
    n = 0
    for t in postfix:
        n += 1
        no = "2." + str(n)
        if _operator(t):
            if st.ukuran() < 2:
                raise ValueError("ekspresi tidak valid (operand kurang)")
            b = st.pop()            # yang keluar PERTAMA = operand kanan
            a = st.pop()
            if t == "+":
                r = a + b
            elif t == "-":
                r = a - b
            elif t == "*":
                r = a * b
            else:
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                if a % b == 0:
                    r = a // b
                else:
                    r = a / b
            st.push(r)
            tindakan = "pop " + str(b) + " dan " + str(a) + " -> " + str(a) + t + str(b) + " = " + str(r)
        else:
            st.push(_angka(t))
            tindakan = "operand, push " + t
        baris.append((no, t, tindakan, _tampil_stack(st), ""))
    if st.ukuran() != 1:
        raise ValueError("ekspresi tidak valid")
    return st.pop(), baris.ke_list()


def hitung(postfix):
    total, _ = hitung_langkah(postfix)
    return total


def format_rupiah(n):
    """48000 -> 'Rp 48.000' (tanpa locale)."""
    negatif = n < 0
    s = str(int(abs(n)))
    hasil = ""
    cnt = 0
    for i in range(len(s) - 1, -1, -1):
        if cnt == 3:
            hasil = "." + hasil
            cnt = 0
        hasil = s[i] + hasil
        cnt += 1
    return ("-" if negatif else "") + "Rp " + hasil


def stack_postfix(ekspresi):
    """Satu tabel langkah (konversi + evaluasi). Kembalikan (teks_postfix, total, baris)."""
    postfix, b1 = ke_postfix_langkah(ekspresi)
    total, b2 = hitung_langkah(postfix)
    semua = Array()
    for r in b1:
        semua.append(r)
    for r in b2:
        semua.append(r)
    return _gabung(postfix), total, semua.ke_list()


# =====================================================================
# Bagian B: dua versi antrean
# =====================================================================
class AntreanNaif:
    """Larik biasa; dequeue mengambil indeks 0 lalu menggeser sisa ke kiri -> O(n)."""

    def __init__(self):
        self._arr = Array()
        self.total_geser = 0
        self.geser_terakhir = 0

    def __len__(self):
        return self._arr.ukuran()

    def enqueue(self, x):
        self._arr.append(x)                     # O(1) amortized

    def dequeue(self):
        n = self._arr.ukuran()
        if n == 0:
            return None
        data = self._arr._data
        depan = data[0]
        for i in range(1, n):                   # geser satu langkah ke kiri
            data[i - 1] = data[i]
        data[n - 1] = None
        self._arr._n = n - 1
        self.geser_terakhir = n - 1
        self.total_geser += n - 1
        return depan

    def dequeue_many(self, k):
        hasil = []
        geser = 0
        for _ in range(k):
            if len(self) == 0:
                break
            hasil.append(self.dequeue())
            geser += self.geser_terakhir
        self.geser_terakhir = geser
        return hasil

    def pop_back(self):
        if self._arr.ukuran() == 0:
            return None
        return self._arr.pop_last()

    def push_front_many(self, items):
        """Kembalikan items (urutan asli) ke DEPAN antrean."""
        k = len(items)
        n = self._arr.ukuran()
        for _ in range(k):
            self._arr.append(None)              # tambah ruang
        data = self._arr._data
        for i in range(n - 1, -1, -1):          # geser isi ke kanan sebanyak k
            data[i + k] = data[i]
        for j in range(k):
            data[j] = items[j]

    def kapasitas(self):
        return self._arr.kapasitas()

    def ke_list(self):
        return self._arr.ke_list()


class AntreanMelingkar:
    """data, front, rear, count. Penunjuk berputar dengan (i+1) % K. dequeue O(1)."""

    def __init__(self, kapasitas=4):
        self.K = kapasitas
        self.data = [None] * kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geser = 0                    # selalu 0: tidak ada elemen digeser
        self.geser_terakhir = 0

    def __len__(self):
        return self.count

    def is_empty(self):
        return self.count == 0                  # bukan front == rear

    def is_full(self):
        return self.count == self.K

    def _tumbuh(self, minimal=0):
        baru_k = self.K * 2
        while baru_k < minimal:
            baru_k *= 2
        baru = [None] * baru_k
        for i in range(self.count):             # salin berurutan mulai dari front
            baru[i] = self.data[(self.front + i) % self.K]
        self.data = baru
        self.K = baru_k
        self.front = 0
        self.rear = self.count % baru_k

    def enqueue(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.K
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.K
        self.count -= 1
        self.geser_terakhir = 0
        return x

    def dequeue_many(self, k):
        hasil = []
        for _ in range(k):
            if self.count == 0:
                break
            hasil.append(self.dequeue())
        self.geser_terakhir = 0
        return hasil

    def pop_back(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1 + self.K) % self.K
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def push_front_many(self, items):
        """Kembalikan items (urutan asli) ke DEPAN antrean."""
        k = len(items)
        if self.count + k > self.K:
            self._tumbuh(self.count + k)
        for j in range(k - 1, -1, -1):
            self.front = (self.front - 1 + self.K) % self.K
            self.data[self.front] = items[j]
            self.count += 1

    def kapasitas(self):
        return self.K

    def ke_list(self):
        hasil = []
        for i in range(self.count):
            hasil.append(self.data[(self.front + i) % self.K])
        return hasil


# =====================================================================
# Bagian A (2): undo / redo
# =====================================================================
class Aksi:
    """Satu catatan riwayat. `data` = yang dibutuhkan untuk MEMBALIKKAN (mis. daftar pesanan)."""

    def __init__(self, jenis, data, fn_undo, fn_redo, target=""):
        self.jenis = jenis          # "ORDER" / "ENQUEUE" / "DEQUEUE"
        self.data = data
        self.target = target        # "naif" / "circular" (dipakai UI untuk pesan undo/redo)
        self.fn_undo = fn_undo
        self.fn_redo = fn_redo


class RiwayatAksi:
    def __init__(self):
        self.undo = Stack()
        self.redo = Stack()

    def catat(self, aksi):
        """Aksi BARU: push ke undo, kosongkan redo."""
        self.undo.push(aksi)
        self.redo.kosongkan()

    def undo_last(self):
        if self.undo.kosong():
            return None
        a = self.undo.pop()
        a.fn_undo()                 # jalankan KEBALIKANNYA
        self.redo.push(a)
        return a

    def redo_last(self):
        if self.redo.kosong():
            return None
        a = self.redo.pop()
        a.fn_redo()                 # kerjakan lagi AKSI ASLINYA
        self.undo.push(a)
        return a

    def history(self):
        """Daftar aksi yang sedang berlaku, dari terlama ke terbaru: [(jenis, jumlah)]."""
        hasil = []
        for a in self.undo.isi():
            if a.jenis == "DEQUEUE":
                hasil.append((a.jenis, len(a.data)))
            else:
                hasil.append((a.jenis, a.data))
        return hasil


# =====================================================================
# Manajer: dua antrean + undo/redo
# =====================================================================
class ManajerAntrean:
    def __init__(self, kapasitas=4):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar(kapasitas)
        self.riwayat = RiwayatAksi()

    def isi_awal(self, daftar):
        """Isi kedua antrean dengan data yang SAMA persis (tidak masuk riwayat)."""
        for x in daftar:
            self.naif.enqueue(x)
            self.melingkar.enqueue(x)

    def enqueue(self, x):
        self.naif.enqueue(x)
        self.melingkar.enqueue(x)

        def undo():
            self.naif.pop_back()
            self.melingkar.pop_back()

        def redo():
            self.naif.enqueue(x)
            self.melingkar.enqueue(x)

        self.riwayat.catat(Aksi("ENQUEUE", x, undo, redo))

    def _dequeue(self, antrean, nama, k):
        items = antrean.dequeue_many(k)
        geser = antrean.geser_terakhir
        if len(items) > 0:
            def undo():
                antrean.push_front_many(items)      # kembali ke DEPAN, bukan belakang

            def redo():
                antrean.dequeue_many(len(items))

            self.riwayat.catat(Aksi("DEQUEUE", items, undo, redo, nama))
        return items, geser

    def dequeue_naif(self, k=1):
        return self._dequeue(self.naif, "naif", k)

    def dequeue_circular(self, k=1):
        return self._dequeue(self.melingkar, "circular", k)

    def catat_order(self, oid, fn_undo, fn_redo):
        """Kait untuk M1: aksi ORDER (tambah pesanan) agar bisa di-undo/redo."""
        self.riwayat.catat(Aksi("ORDER", oid, fn_undo, fn_redo))

    def undo_last(self):
        return self.riwayat.undo_last()

    def redo_last(self):
        return self.riwayat.redo_last()

    def history(self):
        return self.riwayat.history()

    def stats(self):
        """Kembalikan objek Stats (tanpa kamus): akses lewat atribut."""
        return Stats(len(self.naif), len(self.melingkar), self.melingkar.kapasitas(),
                     self.naif.total_geser, self.riwayat.undo.ukuran(),
                     self.riwayat.redo.ukuran())


class Stats:
    def __init__(self, len_naif, len_circular, capacity, total_geser, undo_depth, redo_depth):
        self.queue_len_naif = len_naif
        self.queue_len_circular = len_circular
        self.queue_capacity = capacity
        self.total_geser = total_geser
        self.undo_depth = undo_depth
        self.redo_depth = redo_depth


# =====================================================================
# Helper data: ambil pesanan berstatus ANTRE dari CSV
# =====================================================================
def muat_pesanan_antre(path_csv):
    import csv
    hasil = []
    with open(path_csv, newline="", encoding="utf-8") as f:
        pembaca = csv.reader(f)
        kepala = next(pembaca)
        i_status = 0
        for i in range(len(kepala)):
            if kepala[i] == "status":
                i_status = i
        for baris in pembaca:
            if len(baris) > i_status and baris[i_status] == "ANTRE":
                hasil.append(tuple(baris))
    return hasil
