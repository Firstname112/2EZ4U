import os
import sys
import time

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AKAR)

from backend.m1_pesanan import Pesanan, muat_csv


def ukur(fn):
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000


def main():
    path = os.path.join(AKAR, "data", "pesanan.csv")
    t0 = time.perf_counter()
    arr, ll = muat_csv(path)
    print("muat %d baris ke Array+LinkList: %.0f ms (tumbuh %d kali, total salin %d)" %
          (len(arr), (time.perf_counter() - t0) * 1000, arr.jumlah_tumbuh, arr.total_salin))

    def baru(n):
        return Pesanan("O-%06d" % n, "Uji", "r", "m", 1000, 3, 0, None, "ANTRE")

    print("%-10s %12s %12s   %s" % ("jenis", "array(ms)", "linked(ms)", "geser / telusur"))
    for nama, fa, fl, n in [
        ("REGULER", arr.tambah_reguler, ll.tambah_reguler, 900001),
        ("PRIORITAS", arr.tambah_prioritas, ll.tambah_prioritas, 900002),
        ("VIP", arr.tambah_vip, ll.tambah_vip, 900003),
    ]:
        ta = ukur(lambda: fa(baru(n)))
        la = arr.langkah_terakhir
        tl = ukur(lambda: fl(baru(n)))
        ll_ = ll.langkah_terakhir
        print("%-10s %12.3f %12.3f   %d / %d" % (nama, ta, tl, la, ll_))

    mid = len(arr) // 2
    ta = ukur(lambda: arr.get(mid))
    tl = ukur(lambda: ll.get(mid))
    print("%-10s %12.3f %12.3f   %d / %d" % ("LIHAT mid", ta, tl,
                                               arr.langkah_terakhir, ll.langkah_terakhir))
    ta = ukur(lambda: arr.remove_at(mid))
    tl = ukur(lambda: ll.remove_at(mid))
    print("%-10s %12.3f %12.3f   %d / %d" % ("HAPUS mid", ta, tl,
                                               arr.langkah_terakhir, ll.langkah_terakhir))


if __name__ == "__main__":
    main()
