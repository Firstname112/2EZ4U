"""M3: Sort & Search.

Empat algoritma, masing-masing melaporkan jumlah perbandingan lewat Pencacah:
  - insertion_sort : di tempat, stabil, O(n^2)
  - merge_sort     : stabil, O(n log n)
  - linear_search  : O(n), data boleh acak
  - binary_search  : O(log n), data HARUS terurut menurut kunci yang dicari

Hanya memakai list sebagai larik primitif. Tidak ada sorted(), .sort(), dict, set,
heapq, bisect, maupun collections.

Definisi hitungan:
  perbandingan : satu kali membandingkan dua kunci.
  pemindahan   : satu kali menulis elemen ke slot larik.
                 insertion sort = jumlah geseran + satu penempatan per elemen.
                 merge sort     = jumlah elemen yang ditulis saat penggabungan.
"""

BATAS_INSERTION = 20000          # insertion sort menolak data lebih besar dari ini
BELUM_SELESAI = 10 ** 9          # pesanan tanpa waktu selesai diurutkan paling akhir
KUNCI_SORT = ("oid", "harga", "selesai")

_TAK_ADA = object()


class Pencacah:
    """Pencacah sederhana yang dititipkan ke algoritma."""

    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0

    def reset(self):
        self.perbandingan = 0
        self.pemindahan = 0


# ---------------------------------------------------------------- kunci
def _ambil(p, nama_nama):
    for nama in nama_nama:
        v = getattr(p, nama, _TAK_ADA)
        if v is not _TAK_ADA:
            return v
    raise AttributeError("Pesanan tidak punya atribut %s" % (nama_nama,))


def kunci_oid(p):
    return _ambil(p, ("oid",))


def kunci_harga(p):
    return int(_ambil(p, ("harga",)))


def kunci_selesai(p):
    v = _ambil(p, ("selesai", "t_selesai", "t_selesai_detik", "selesai_detik"))
    if v is None or v == "":
        return BELUM_SELESAI
    return int(v)


def pembuat_kunci(kunci):
    """kunci boleh berupa nama ("oid", "harga", "selesai") atau fungsi pengambil kunci."""
    if callable(kunci):
        return kunci
    if kunci == "oid":
        return kunci_oid
    if kunci == "harga":
        return kunci_harga
    if kunci == "selesai":
        return kunci_selesai
    raise ValueError("kunci tidak dikenal: %s (pilih oid, harga, atau selesai)" % kunci)


# ---------------------------------------------------------------- sort
def insertion_sort(A, kunci, pencacah=None):
    """Mengurutkan A di tempat. Stabil: geser hanya bila kunci kiri LEBIH BESAR (>)."""
    fk = pembuat_kunci(kunci)
    n = len(A)
    D = []
    for x in A:
        D.append((fk(x), x))        # kunci dihitung sekali per elemen

    banding = 0
    geser = 0
    i = 1
    while i < n:
        x = D[i]
        kx = x[0]
        j = i - 1
        while j >= 0:
            banding += 1
            if D[j][0] > kx:        # strict >, bukan >=  -> stabil
                D[j + 1] = D[j]
                geser += 1
                j -= 1
            else:
                break
        D[j + 1] = x
        i += 1

    i = 0
    while i < n:
        A[i] = D[i][1]
        i += 1
    if pencacah is not None:
        pencacah.perbandingan += banding
        pencacah.pemindahan += geser + (n - 1 if n > 0 else 0)
    return A


def _gabung(D, aux, lo, mid, hi, pencacah):
    i = lo
    j = mid + 1
    k = lo
    banding = 0
    while i <= mid and j <= hi:
        banding += 1
        if D[i][0] <= D[j][0]:      # <=  -> elemen bagian kiri didahulukan -> stabil
            aux[k] = D[i]
            i += 1
        else:
            aux[k] = D[j]
            j += 1
        k += 1
    while i <= mid:                 # sisa bagian kiri
        aux[k] = D[i]
        i += 1
        k += 1
    while j <= hi:                  # sisa bagian kanan
        aux[k] = D[j]
        j += 1
        k += 1
    t = lo
    while t <= hi:
        D[t] = aux[t]
        t += 1
    pencacah.perbandingan += banding
    pencacah.pemindahan += hi - lo + 1


def _merge_sort_rekursif(D, aux, lo, hi, pencacah):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    _merge_sort_rekursif(D, aux, lo, mid, pencacah)
    _merge_sort_rekursif(D, aux, mid + 1, hi, pencacah)
    _gabung(D, aux, lo, mid, hi, pencacah)


def merge_sort(A, kunci, pencacah=None):
    """Mengurutkan A (hasil ditulis kembali ke A dan dikembalikan). Stabil, O(n log n)."""
    n = len(A)
    if n < 2:
        return A
    fk = pembuat_kunci(kunci)
    if pencacah is None:
        pencacah = Pencacah()
    D = []
    for x in A:
        D.append((fk(x), x))
    aux = [None] * n
    _merge_sort_rekursif(D, aux, 0, n - 1, pencacah)
    i = 0
    while i < n:
        A[i] = D[i][1]
        i += 1
    return A


# ---------------------------------------------------------------- search
def linear_search(A, target, kunci="oid", pencacah=None):
    """Telusuri dari depan. Kembalikan indeks, atau -1 bila tidak ada."""
    fk = pembuat_kunci(kunci)
    banding = 0
    hasil = -1
    i = 0
    n = len(A)
    while i < n:
        banding += 1
        if fk(A[i]) == target:
            hasil = i
            break
        i += 1
    if pencacah is not None:
        pencacah.perbandingan += banding
    return hasil


def binary_search(A, target, kunci="oid", pencacah=None):
    """A WAJIB terurut menurut kunci yang sama. Kembalikan indeks, atau -1 bila tidak ada."""
    fk = pembuat_kunci(kunci)
    lo = 0
    hi = len(A) - 1
    banding = 0
    hasil = -1
    while lo <= hi:                 # <= , bukan <
        mid = (lo + hi) // 2
        banding += 1
        k = fk(A[mid])
        if k == target:
            hasil = mid
            break
        if k < target:
            lo = mid + 1
        else:
            hi = mid - 1
    if pencacah is not None:
        pencacah.perbandingan += banding
    return hasil
