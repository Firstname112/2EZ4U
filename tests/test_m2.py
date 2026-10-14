import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from m2_antrean import *

def total(e): return hitung(ke_postfix(e))

# --- postfix: 4 jenis ekspresi + sampel dosen
assert " ".join(ke_postfix("3 + 4 * 2")) == "3 4 2 * +"                # tanpa kurung
assert " ".join(ke_postfix("( 3 + 4 ) * 2")) == "3 4 + 2 *"            # berkurung
assert " ".join(ke_postfix("10 - 3 - 2")) == "10 3 - 2 -"              # '-' beruntun
assert " ".join(ke_postfix("( ( 1 + 2 ) * ( 3 - 4 ) ) / 3")) == "1 2 + 3 4 - * 3 /"  # bersarang
sampel = "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"
assert " ".join(ke_postfix(sampel)) == "3 12000 * 2 8500 * + 5000 -"
assert total(sampel) == 48000
assert format_rupiah(48000) == "Rp 48.000"
assert tokenisasi("3*12000+5") == ["3", "*", "12000", "+", "5"]       # multi-digit
# --- urutan pop (- dan /)
assert total("10 - 3 - 2") == 5 and total("8 / 4 / 2") == 1 and total("20 / 4 - 1") == 4
assert total("( ( 1 + 2 ) * ( 3 - 4 ) ) / 3") == -1
for bad in ["( 1 + 2", "1 + 2 )", "1 +", "4 / ( 2 - 2 )"]:
    try: total(bad); assert False, bad
    except ValueError: pass
_, tot, baris = stack_postfix(sampel)
assert tot == 48000 and baris[4][0] == "1.5" and "(" not in baris[4][4].split()

# --- antrean melingkar K=4: masuk 3, keluar 2, masuk 3 -> pointer berputar
q = AntreanMelingkar(4)
for x in "abc": q.enqueue(x)
assert q.dequeue_many(2) == ["a", "b"]
for x in "def": q.enqueue(x)
assert q.ke_list() == ["c", "d", "e", "f"] and q.rear == q.front   # penuh: front==rear tapi count=4
assert not q.is_empty() and q.is_full()
q.enqueue("g")                                                     # tumbuh saat penuh
assert q.ke_list() == list("cdefg") and q.kapasitas() == 8
assert q.dequeue_many(10) == list("cdefg") and q.dequeue() is None and q.is_empty()

# --- naif vs melingkar hasil identik + geseran
data = [("O-%06d" % i,) for i in range(1, 201)]
m = ManajerAntrean(); m.isi_awal(data)
a, ga = m.dequeue_naif(3); b, gb = m.dequeue_circular(3)
assert a == b == data[:3] and gb == 0 and ga == 199 + 198 + 197
assert m.naif.ke_list() == m.melingkar.ke_list()

# --- undo/redo (skenario dosen)
m = ManajerAntrean(); m.isi_awal(data)
m.enqueue(("NEW",)); assert m.stats().queue_len_circular == 201
m.undo_last(); assert m.stats().queue_len_circular == 200 and m.stats().undo_depth == 0
m.redo_last(); assert m.stats().queue_len_naif == 201 and m.stats().undo_depth == 1
items, _ = m.dequeue_circular(100)
assert m.melingkar.ke_list()[0] == data[100]
m.undo_last(); assert m.melingkar.ke_list()[:100] == items        # kembali ke DEPAN
m.redo_last(); assert len(m.melingkar) == 101
m.undo_last(); m.enqueue(("Pencabang",))                           # aksi baru -> redo kosong
assert m.stats().redo_depth == 0 and m.redo_last() is None
assert m.history()[-1] == ("ENQUEUE", ("Pencabang",))
# undo DEQUEUE naif
m = ManajerAntrean(); m.isi_awal(data); m.dequeue_naif(5); m.undo_last()
assert m.naif.ke_list() == data
print("SEMUA TES M2 LULUS")
