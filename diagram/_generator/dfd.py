"""Spesifikasi DFD konteks, level 1, dan level 2 DayaMuda."""
from diagen import Diagram

OUT = "/home/claude/diagram/src"
EW, EH = 150, 52          # ukuran entitas luar
SW, SH = 200, 44          # ukuran penyimpanan


def ent(d, nid, x, y, label):
    return d.node(nid, "rect", x, y, EW, EH, label, bold=True, fill="#f7f9fb")


def proc(d, nid, cx, cy, label, r=62):
    return d.node(nid, "circle", cx - r, cy - r, 2 * r, 2 * r, label, size=13, bold=True, fill="#eef4ff",
                  stroke="#3b6fd6")


def store(d, nid, x, y, label):
    return d.node(nid, "store", x, y, SW, SH, label, size=12.5)


# ---------------------------------------------------------------- konteks
def konteks():
    d = Diagram("DFD konteks", 860, 520, "Gambar 4.4 DFD konteks: satu proses, empat entitas luar")
    ent(d, "pem", 20, 80, "Pemuda")
    ent(d, "sel", 20, 430, "Selektor")
    ent(d, "ins", 690, 80, "Instruktur")
    ent(d, "pen", 690, 430, "Pengurus inti")
    proc(d, "p0", 430, 300, "0\nSistem\nDayaMuda", r=78)
    d.edge("pem", "p0", "Data pendaftaran\nPermintaan pengunduran diri", sp=(110, 132), pts=[(110, 300)], t=0.35, loff=(-18, 0))
    d.edge("p0", "pem", "Status seleksi dan alasan\nRiwayat presensi\nNilai dan status kelulusan\nSurat Keterangan Hasil Pelatihan",
           pts=[(260, 106)], dp=(170, 106), t=0.55, loff=(0, 16))
    d.edge("sel", "p0", "Data pendaftaran dibantu\nKeputusan seleksi dan alasan", sp=(170, 448), pts=[(300, 448)], t=0.3, loff=(46, 24))
    d.edge("p0", "sel", "Antrean pendaftar", pts=[(110, 360)], dp=(110, 430), t=0.4, loff=(0, -14))
    d.edge("ins", "p0", "Presensi sesi\nNilai uji praktik", sp=(690, 98), pts=[(580, 98)], t=0.3, loff=(0, -24))
    d.edge("p0", "ins", "Daftar peserta dan jadwal sesi", pts=[(765, 270)], dp=(765, 132), t=0.45, loff=(10, 0))
    d.edge("pen", "p0", "Data kelas dan jadwal\nPengesahan kelulusan", sp=(690, 448), pts=[(560, 448)], t=0.3, loff=(0, 22))
    d.edge("p0", "pen", "Informasi kuota\nRekap evaluasi kelulusan\nLaporan ringkas kegiatan", pts=[(765, 330)],
           dp=(765, 430), t=0.38, loff=(0, 0))
    d.save(OUT, "dfd-0-konteks")


# ---------------------------------------------------------------- level 1 (dua bagian)
# Pola tiap baris: entitas luar di kiri, proses di tengah, penyimpanan di kanan.
# Entitas/penyimpanan yang sama digambar ulang per baris (salinan) agar garis tidak bersilangan.

LX, PX, SX = 20, 440, 660
R = 60


def _route(d, nid, pid, side, y_from, x_from, entry_off, jog, direction, label, above, both=False):
    """Garis siku: horizontal dari simbol, belok vertikal di x=jog, lalu horizontal masuk lingkaran."""
    import math
    cx, cy = d.center(d.nodes[pid])
    ye = cy + entry_off
    xe = cx - math.sqrt(R * R - entry_off ** 2) if side == "L" else cx + math.sqrt(R * R - entry_off ** 2)
    if abs(y_from - ye) < 1:
        pts = []
    else:
        pts = [(jog, y_from), (jog, ye)]
    seg1 = abs(jog - x_from) if pts else abs(xe - x_from)
    total = seg1 + (abs(ye - y_from) + abs(xe - jog) if pts else 0)
    loff = (0, -12 if above else 13)
    nlines = label.count("\n") + 1
    if nlines > 1:
        loff = (0, (-12 - 8 * (nlines - 1)) if above else (13 + 8 * (nlines - 1)))
    wlab = max(len(x) for x in label.split("\n")) * 12 * 0.53 + 8
    lx = x_from + (wlab / 2 + 6 if side == "L" else -(wlab / 2 + 6))
    lpos = (lx, y_from + loff[1])
    if direction == "in":
        t = (seg1 / 2) / total
        d.edge(nid, pid, label, sp=(x_from, y_from), dp=(xe, ye), pts=pts, t=t, loff=loff, both=both, lpos=lpos)
    else:
        rp = list(reversed(pts))
        t = 1 - (seg1 / 2) / total
        d.edge(pid, nid, label, sp=(xe, ye), dp=(x_from, y_from), pts=rp, t=t, loff=loff, both=both, lpos=lpos)


def row(d, y0, pid, plabel, lefts, rights, height):
    """lefts/rights: [(nid,label,[(dir,label)])]; dir 'in' = menuju proses, 'out' = keluar, 'both' = dua arah."""
    cy = y0 + height / 2
    proc(d, pid, PX, cy, plabel, r=R)
    for side, items in (("L", lefts), ("R", rights)):
        gap = height / len(items)
        flows = []
        for i, (nid, lab, fl) in enumerate(items):
            if side == "L":
                ey = y0 + gap * i + (gap - EH) / 2
                ent(d, nid, LX, ey, lab)
                yc, xf = ey + EH / 2, LX + EW
            else:
                ey = y0 + gap * i + (gap - SH) / 2
                store(d, nid, SX, ey, lab)
                yc, xf = ey + SH / 2, SX
            n = len(fl)
            for k, (dr, txt) in enumerate(fl):
                off = (k - (n - 1) / 2) * 24
                above = (k == 0) if n > 1 else True
                flows.append(dict(nid=nid, y=yc + off, x=xf, dr=dr, txt=txt, above=above))
        m = len(flows)
        spread = 40 if m < 6 else 75
        span = min(96, 22 * (m - 1))
        for j, f in enumerate(flows):
            f["entry"] = (j - (m - 1) / 2) * (span / (m - 1) if m > 1 else 0)
        # semakin jauh dari pusat, semakin dekat ke lingkaran belokannya
        order = sorted(range(m), key=lambda j: abs(flows[j]["y"] - (cy + flows[j]["entry"])))
        for rank, j in enumerate(order):
            f = flows[j]
            if side == "L":
                jog = PX - R - 70 + rank * (spread / max(1, m - 1))
            else:
                jog = PX + R + 70 - rank * (spread / max(1, m - 1))
            _route(d, f["nid"], pid, side, f["y"], f["x"], f["entry"], jog,
                   "in" if f["dr"] == "in" else "out", f["txt"], f["above"], both=(f["dr"] == "both"))


def level1():
    a = Diagram("DFD level 1 bagian A", 880, 880, "Gambar 4.5a DFD Level 1 (P-1, P-2, P-5)")
    y = 50
    row(a, y, "p1", "P-1\nKelola\nPendaftaran\ndan Seleksi",
        [("a_pem", "Pemuda", [("in", "Data pendaftaran;\npermintaan mundur"), ("out", "Status seleksi\ndan alasan")]),
         ("a_sel", "Selektor", [("in", "Data pendaftaran dibantu;\nkeputusan dan alasan"), ("out", "Antrean pendaftar")]),
         ("a_pen", "Pengurus inti", [("out", "Informasi kuota")])],
        [("a_d1", "D1 Data Peserta", [("both", "Data peserta")]),
         ("a_d2", "D2 Data Pendaftaran", [("both", "Data pendaftaran")]),
         ("a_d3", "D3 Data Kelas dan Sesi", [("in", "Status dan kuota kelas"), ("out", "Status KUOTA_PENUH")]),
         ("a_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 330)
    a.node("sep1", "line", 20, y + 340, 840, 0, "")
    y += 350
    row(a, y, "p2", "P-2\nCatat\nPresensi",
        [("b_ins", "Instruktur", [("in", "Presensi sesi"), ("out", "Daftar peserta\ndan jadwal sesi")]),
         ("b_pem", "Pemuda", [("out", "Riwayat presensi")])],
        [("b_d2", "D2 Data Pendaftaran", [("in", "Peserta disetujui")]),
         ("b_d3", "D3 Data Kelas dan Sesi", [("in", "Jadwal sesi")]),
         ("b_d4", "D4 Data Presensi", [("out", "Rekam presensi")]),
         ("b_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 260)
    a.node("sep2", "line", 20, y + 270, 840, 0, "")
    y += 280
    row(a, y, "p5", "P-5\nKelola Kelas\ndan Jadwal",
        [("e_pen", "Pengurus inti", [("in", "Data kelas\ndan jadwal")])],
        [("e_d8", "D8 Data Pengguna Staf", [("in", "Daftar instruktur")]),
         ("e_d3", "D3 Data Kelas dan Sesi", [("out", "Kelas dan sesi")]),
         ("e_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 190)
    a.save(OUT, "dfd-1-level1-a")

    b = Diagram("DFD level 1 bagian B", 880, 840, "Gambar 4.5b DFD Level 1 (P-3, P-4)")
    y = 50
    row(b, y, "p3", "P-3\nEvaluasi\nKelulusan",
        [("c_ins", "Instruktur", [("in", "Nilai uji praktik")]),
         ("c_pen", "Pengurus inti", [("in", "Pengesahan kelulusan"), ("out", "Rekap evaluasi\nkelulusan")]),
         ("c_pem", "Pemuda", [("out", "Nilai dan status\nkelulusan")])],
        [("c_d2", "D2 Data Pendaftaran", [("in", "Peserta disetujui")]),
         ("c_d4", "D4 Data Presensi", [("in", "Data presensi")]),
         ("c_d5", "D5 Data Evaluasi", [("both", "Nilai dan status")]),
         ("c_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 290)
    b.node("sep3", "line", 20, y + 300, 840, 0, "")
    y += 310
    row(b, y, "p4", "P-4\nTerbitkan\nSurat dan\nLaporan",
        [("d_pem", "Pemuda", [("out", "Surat Keterangan\nHasil Pelatihan")]),
         ("d_pen", "Pengurus inti", [("out", "Laporan ringkas\nkegiatan")])],
        [("d_d1", "D1 Data Peserta", [("in", "Identitas peserta")]),
         ("d_d2", "D2 Data Pendaftaran", [("in", "Data pendaftaran")]),
         ("d_d3", "D3 Data Kelas dan Sesi", [("in", "Kelas dan durasi JP")]),
         ("d_d4", "D4 Data Presensi", [("in", "Rekap kehadiran")]),
         ("d_d5", "D5 Data Evaluasi", [("in", "Status lulus disahkan")]),
         ("d_d6", "D6 Data Surat", [("out", "Arsip surat")]),
         ("d_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 470)
    b.save(OUT, "dfd-1-level1-b")


# ---------------------------------------------------------------- level 2 P-1
def level2_p1():
    d = Diagram("DFD level 2 P-1", 880, 1000, "Gambar 4.6 DFD Level 2 P-1 Kelola Pendaftaran dan Seleksi")
    y = 50
    row(d, y, "p11", "P-1.1\nTerima dan\nValidasi\nPendaftaran",
        [("a_pem", "Pemuda", [("in", "Data pendaftaran"), ("out", "Status seleksi dan alasan\n(tanda terima / galat)")]),
         ("a_sel", "Selektor", [("in", "Data pendaftaran\ndibantu")])],
        [("a_d3", "D3 Data Kelas dan Sesi", [("in", "Status kelas")]),
         ("a_d1", "D1 Data Peserta", [("both", "Data peserta")]),
         ("a_d2", "D2 Data Pendaftaran", [("out", "Pendaftaran DIAJUKAN")]),
         ("a_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 280)
    d.node("s1", "line", 20, y + 290, 840, 0, "")
    y += 300
    row(d, y, "p12", "P-1.2\nVerifikasi\ndan Kunci\nKuota",
        [("b_sel", "Selektor", [("in", "Keputusan seleksi\ndan alasan"), ("out", "Antrean pendaftar")]),
         ("b_pem", "Pemuda", [("out", "Status seleksi\ndan alasan")]),
         ("b_pen", "Pengurus inti", [("out", "Informasi kuota")])],
        [("b_d3", "D3 Data Kelas dan Sesi", [("in", "Kuota maksimal"), ("out", "Status KUOTA_PENUH")]),
         ("b_d2", "D2 Data Pendaftaran", [("both", "Status pendaftaran")]),
         ("b_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 300)
    d.node("s2", "line", 20, y + 310, 840, 0, "")
    y += 320
    row(d, y, "p13", "P-1.3\nProses\nPengunduran\nDiri",
        [("c_pem", "Pemuda", [("in", "Permintaan\npengunduran diri"), ("out", "Status seleksi\ndan alasan")])],
        [("c_d2", "D2 Data Pendaftaran", [("both", "Status mundur")]),
         ("c_d7", "D7 Jejak Audit", [("out", "Catatan audit")])], 170)
    d.h = y + 180
    d.save(OUT, "dfd-2-level2-p1")


# ---------------------------------------------------------------- level 2 P-3
def level2_p3():
    d = Diagram("DFD level 2 P-3", 900, 780, "Gambar 4.7 DFD Level 2 P-3 Evaluasi Kelulusan")
    proc(d, "p31", 400, 150, "P-3.1\nHitung\nKehadiran", r=56)
    proc(d, "p32", 400, 380, "P-3.2\nRekam Nilai\nUji Praktik", r=56)
    proc(d, "p33", 640, 260, "P-3.3\nTentukan\nStatus\nKelulusan", r=60)
    proc(d, "p34", 640, 600, "P-3.4\nSahkan\nKelulusan", r=56)
    store(d, "d2", 20, 108, "D2 Data Pendaftaran")
    store(d, "d4", 20, 172, "D4 Data Presensi")
    ent(d, "ins", 20, 354, "Instruktur")
    store(d, "d7a", 20, 470, "D7 Jejak Audit")
    ent(d, "pen2", 20, 574, "Pengurus inti")
    ent(d, "pen", 730, 140, "Pengurus inti")
    store(d, "d5", 600, 430, "D5 Data Evaluasi")
    store(d, "d7b", 330, 700, "D7 Jejak Audit")
    ent(d, "pem", 730, 700, "Pemuda")
    d.edge("d2", "p31", "Peserta disetujui", sp=(220, 130), lpos=(282, 118))
    d.edge("d4", "p31", "Data presensi", sp=(220, 194), lpos=(282, 206))
    d.edge("p31", "p33", "Jumlah HADIR dan\nkelengkapan 10 sesi", lpos=(530, 172))
    d.edge("ins", "p32", "Nilai uji praktik", sp=(170, 380), lpos=(270, 368))
    d.edge("p32", "d7a", "Catatan audit", sp=(400, 436), pts=[(400, 492)], dp=(220, 492), lpos=(300, 480))
    d.edge("p32", "p33", "Nilai praktik", lpos=(535, 345))
    d.edge("p32", "d5", "Nilai praktik", sp=(452.6, 399), pts=[(560, 399), (560, 452)], dp=(600, 452), lpos=(505, 411))
    d.edge("p33", "d5", "Status kelulusan", sp=(660, 316.6), dp=(660, 430), lpos=(725, 372))
    d.edge("p33", "pen", "Rekap evaluasi\nkelulusan", dp=(730, 166), lpos=(735, 222))
    d.edge("pen2", "p34", "Pengesahan kelulusan", sp=(170, 600), lpos=(330, 588))
    d.edge("p34", "d5", "Status dan tanda\ndisahkan", sp=(640, 544), dp=(640, 474), both=True, lpos=(560, 512))
    d.edge("p34", "d7b", "Catatan audit", dp=(520, 700), lpos=(520, 668))
    d.edge("p34", "pem", "Nilai dan status\nkelulusan", dp=(780, 700), lpos=(800, 650))
    d.save(OUT, "dfd-2-level2-p3")


if __name__ == "__main__":
    konteks()
    level1()
    level2_p1()
    level2_p3()
