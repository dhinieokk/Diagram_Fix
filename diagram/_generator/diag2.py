"""Use case, Flow Map as-is/to-be, arsitektur, dan wireframe DayaMuda."""
from diagen import Diagram

OUT = "/home/claude/diagram/src"


# ---------------------------------------------------------------- use case
def usecase():
    d = Diagram("Use case", 880, 720, "Gambar 4.1 Diagram use case: 4 aktor, 10 use case")
    d.node("sys", "group", 220, 56, 440, 640, "Sistem DayaMuda")
    names = [("uc02", "UC-02 Mendaftar pelatihan"), ("uc08", "UC-08 Melihat status dan\nmengunduh surat"),
             ("uc10", "UC-10 Mengundurkan diri"), ("uc01", "UC-01 Melakukan autentikasi"),
             ("uc03", "UC-03 Memverifikasi pendaftar"), ("uc05", "UC-05 Mencatat presensi sesi"),
             ("uc06", "UC-06 Menginput nilai\nuji praktik"), ("uc04", "UC-04 Mengelola kelas\ndan jadwal"),
             ("uc07", "UC-07 Mengesahkan kelulusan"), ("uc09", "UC-09 Melihat laporan kegiatan")]
    for i, (nid, lab) in enumerate(names):
        d.node(nid, "ellipse", 310, 90 + i * 60, 260, 48, lab, size=12.5)
    d.node("pem", "actor", 40, 110, 110, 90, "Pemuda")
    d.node("sel", "actor", 40, 300, 110, 90, "Selektor")
    d.node("ins", "actor", 730, 330, 110, 90, "Instruktur")
    d.node("pen", "actor", 730, 560, 110, 90, "Pengurus inti")
    for a, ucs in (("pem", ["uc02", "uc08", "uc10", "uc01"]), ("sel", ["uc02", "uc01", "uc03"]),
                   ("ins", ["uc01", "uc05", "uc06"]), ("pen", ["uc01", "uc04", "uc07", "uc09"])):
        an = d.nodes[a]
        left = an["x"] < 300
        for u in ucs:
            un = d.nodes[u]
            sp = (an["x"] + (82 if left else 28), an["y"] + 38)
            dp = (un["x"] if left else un["x"] + un["w"], un["y"] + un["h"] / 2)
            d.edge(a, u, arrow=False, sp=sp, dp=dp)
    d.save(OUT, "usecase-dayamuda")


# ---------------------------------------------------------------- flow map
def flowmap(stem, title, lanes, steps, links, lane_w, row_h=66, box_w=None, assumed=()):
    box_w = box_w or lane_w - 26
    top = 60
    n_rows = max(s[1] for s in steps) + 1
    H = top + 34 + n_rows * row_h + 24
    W = 20 + lane_w * len(lanes) + 20
    d = Diagram(stem, W, H, title)
    for i, ln in enumerate(lanes):
        d.node(f"lane{i}", "lane", 20 + i * lane_w, top, lane_w, H - top - 12, ln)
    for sid, r, lane, text in steps:
        x = 20 + lane * lane_w + (lane_w - box_w) / 2
        y = top + 34 + r * row_h + 8
        d.node(sid, "round", x, y, box_w, row_h - 16, text, size=12, dashed=sid in assumed,
               fill="#eef4ff" if lanes[lane].startswith("Sistem") else "#ffffff")
    for a, b in links:
        na, nb = d.nodes[a], d.nodes[b]
        ax, ay = na["x"] + na["w"] / 2, na["y"] + na["h"]
        bx, by = nb["x"] + nb["w"] / 2, nb["y"]
        if abs(ax - bx) < 1:
            d.edge(a, b, sp=(ax, ay), dp=(bx, by))
        elif by > ay:
            my = by - 8
            d.edge(a, b, sp=(ax, ay), pts=[(ax, my), (bx, my)], dp=(bx, by))
        else:  # langkah pada baris yang sama: masuk dari samping
            side = 1 if bx > ax else -1
            sy = na["y"] + na["h"] / 2
            d.edge(a, b, sp=(na["x"] + (na["w"] if side > 0 else 0), sy),
                   dp=(nb["x"] + (0 if side > 0 else nb["w"]), sy))
    d.save(OUT, stem)


def flowmaps():
    lanes = ["Pemuda", "Panitia / Selektor", "Instruktur", "Pengurus inti\ndan perangkat desa"]
    steps = [("g1", 0, 3, "Rapat persiapan,\nmembagi seksi [W]"),
             ("s1", 1, 1, "Menyebar info lewat\ngrup WA dan lisan [W]"),
             ("p1", 2, 0, "Menyatakan minat lewat\nWA atau lisan [W] KD-16"),
             ("s2", 3, 1, "Mencatat di buku, kertas,\nGoogle Form; foto KTP di\nHP pribadi [W] KD-10, 12"),
             ("s3", 4, 1, "Menyeleksi menurut\nkebutuhan dan rekam\njejak [W] KD-11"),
             ("p2", 5, 0, "Menerima keputusan\nlewat WA [W]"),
             ("p3", 6, 0, "Mengikuti 10 sesi [A]"),
             ("i1", 6, 2, "Mencatat hadir di kertas;\nnilai praktik sesi 10\n[A] KD-15"),
             ("g2", 7, 3, "Merekap hadir dan nilai,\nmengetik surat manual\n[A] KD-15"),
             ("g3", 8, 3, "Evaluasi dan LPJ ke\nperangkat desa\n[W] KD-13, KD-14")]
    links = [("g1", "s1"), ("s1", "p1"), ("p1", "s2"), ("s2", "s3"), ("s3", "p2"), ("p2", "p3"),
             ("p3", "i1"), ("i1", "g2"), ("g2", "g3")]
    flowmap("flowmap-as-is", "Gambar 4.2 Flow Map as-is: data berpindah dari WA ke kertas sampai LPJ",
            lanes, steps, links, 210, row_h=66, assumed={"p3", "i1", "g2"})

    lanes = ["Pemuda", "Selektor", "Sistem DayaMuda", "Instruktur", "Pengurus inti"]
    steps = [("g1", 0, 4, "Membuat kelas dan\n10 sesi, membuka kelas"),
             ("p1", 1, 0, "Mengisi formulir dan\nPIN (mandiri atau\ndibantu Selektor)"),
             ("y1", 2, 2, "Cek usia dan NIK;\nsimpan DIAJUKAN"),
             ("s1", 3, 1, "Memeriksa antrean urut\nwaktu; Setujui, atau\nTolak dengan alasan"),
             ("y2", 4, 2, "Kunci kuota; peserta\nke-30 menutup kelas,\nsisa ditolak otomatis"),
             ("p2", 5, 0, "Melihat status dan\nalasan (kode peserta\n+ PIN)"),
             ("p3", 6, 0, "Mengikuti 10 sesi"),
             ("i1", 6, 3, "Mencatat HADIR / IZIN\n/ ALFA tiap sesi,\njuga saat offline"),
             ("y3", 7, 2, "Menyimpan presensi di\nHP, mengirim saat ada\nsinyal tanpa dobel"),
             ("i2", 8, 3, "Mengisi nilai uji\npraktik di sesi 10"),
             ("y4", 9, 2, "Menghitung kelulusan:\nHADIR ≥ 8 dan\nnilai ≥ 75,00"),
             ("g2", 10, 4, "Meninjau rekap dan\nmengesahkan"),
             ("y5", 11, 2, "Menerbitkan PDF\nbernomor dengan\ntotal JP"),
             ("p4", 12, 0, "Mengunduh surat"),
             ("g3", 12, 4, "Meneruskan laporan\nringkas tanpa NIK\nke desa")]
    links = [("g1", "p1"), ("p1", "y1"), ("y1", "s1"), ("s1", "y2"), ("y2", "p2"), ("p2", "p3"), ("p3", "i1"),
             ("i1", "y3"), ("y3", "i2"), ("i2", "y4"), ("y4", "g2"), ("g2", "y5"), ("y5", "p4"), ("y5", "g3")]
    flowmap("flowmap-to-be", "Gambar 4.3 Flow Map to-be: sistem mengambil alih rekap, kuota, dan surat",
            lanes, steps, links, 168, row_h=62)


# ---------------------------------------------------------------- arsitektur
def arsitektur():
    d = Diagram("Arsitektur", 880, 640, "Gambar 5.1 Arsitektur klien-server: satu aplikasi web, satu basis data")
    d.node("g1", "group", 20, 52, 840, 158, "Lapisan presentasi: peramban HP atau laptop (PWA)")
    d.node("g2", "group", 20, 262, 840, 168, "Lapisan aplikasi: Node.js dengan Express (satu aplikasi)")
    d.node("g3", "group", 20, 482, 840, 140, "Lapisan data")
    d.node("ui", "round", 40, 90, 250, 100, "Halaman HTML, CSS, JS\nformulir, antrean,\npresensi, evaluasi\nREQ-F01–F11, REQ-N03", size=12.5)
    d.node("sw", "round", 315, 90, 250, 100, "Service Worker\nmenyimpan berkas aplikasi\nagar tetap terbuka offline\nREQ-N02, REQ-N04", size=12.5)
    d.node("idb", "round", 590, 90, 250, 100, "IndexedDB\nantrean presensi offline,\nnama tanpa NIK\nREQ-N02, REQ-N01", size=12.5)
    d.node("mw", "round", 40, 300, 250, 110, "Penjaga akses\ncookie sesi HttpOnly,\ncek peran, batas percobaan\nREQ-N01, REQ-F06", size=12.5)
    d.node("api", "round", 315, 300, 250, 110, "REST API /api/v1\npendaftaran, seleksi,\npresensi batch-sync, evaluasi\nREQ-F01–F04", size=12.5)
    d.node("svc", "round", 590, 300, 250, 110, "Aturan bisnis\nkuota atomik, kelulusan,\nsurat PDF, audit\nREQ-D01–D06", size=12.5)
    d.node("db", "round", 315, 520, 250, 86, "MariaDB\n9 tabel ERD, transaksi\nREQ-D01, REQ-D05", size=12.5, fill="#eef4ff", stroke="#3b6fd6")
    d.node("env", "round", 590, 520, 250, 86, "Berkas .env (tidak di repo)\nkunci enkripsi NIK, HMAC,\nsandi basis data", size=12.5)
    d.edge("ui", "sw", arrow=False, sp=(290, 140), dp=(315, 140))
    d.edge("sw", "idb", arrow=False, sp=(565, 140), dp=(590, 140))
    d.edge("ui", "mw", "HTTPS + JSON, cookie HttpOnly", sp=(165, 190), dp=(165, 300), both=True, lpos=(165, 236))
    d.edge("mw", "api", sp=(290, 355), dp=(315, 355))
    d.edge("api", "svc", sp=(565, 355), dp=(590, 355))
    d.edge("svc", "db", "query terparameter,\ntransaksi", sp=(640, 410), pts=[(640, 450), (440, 450)], dp=(440, 520),
           both=True, lpos=(520, 450))
    d.edge("env", "svc", "dibaca saat\nserver mulai", sp=(780, 520), dp=(780, 410), dashed=True, lpos=(800, 462))
    d.save(OUT, "arsitektur-dayamuda")


# ---------------------------------------------------------------- wireframe
def phone(d, x=20, y=50, h=690):
    d.node("frame", "frame", x, y, 360, h, "")
    return x + 16, y + 30


def note(d, i, x, y, text, px, py):
    """Penanda bernomor di layar + catatan di kolom kanan."""
    d.node(f"m{i}", "circle", px - 11, py - 11, 22, 22, str(i), size=12, bold=True, fill="#ffe8a3", stroke="#b7791f")
    d.node(f"mn{i}", "circle", x, y, 22, 22, str(i), size=12, bold=True, fill="#ffe8a3", stroke="#b7791f")
    d.node(f"t{i}", "text", x + 30, y - 6, 270, 34, text, size=12)


def wf_antrean():
    d = Diagram("Wireframe antrean", 720, 700, "Gambar 5.2 Layar 1: antrean dan verifikasi pendaftar (Selektor)")
    x, y = phone(d, h=630)
    d.node("hdr", "rect", x, y, 328, 74, "", fill="#f2f4f7", stroke="#cbd2d9")
    d.node("h1", "text", x + 10, y + 6, 300, 20, "DayaMuda · Selektor: Ani", size=13, bold=True)
    d.node("h2", "text", x + 10, y + 28, 300, 18, "Kelas: Perbengkelan Motor A1", size=12)
    d.node("bar", "box", x + 10, y + 50, 220, 12, "", fill="#ffffff")
    d.node("barf", "box", x + 10, y + 50, 176, 12, "", fill="#9fb3c8")
    d.node("h3", "text", x + 238, y + 47, 90, 18, "24 / 30", size=12, bold=True)
    d.node("tab1", "button", x, y + 86, 160, 34, "Antrean (12)", size=12, fill="#e8f0fe")
    d.node("tab2", "button", x + 168, y + 86, 160, 34, "Sudah diputuskan", size=12)
    rows = [("Budi Santoso", "Daftar 28 Okt 13.45", "NIK 3302xxxxxxxx0012"),
            ("Sari Astuti", "Daftar 28 Okt 13.52", "NIK 3302xxxxxxxx4103"),
            ("Rudi Hartono", "Daftar 28 Okt 14.10", "NIK 3302xxxxxxxx0277")]
    yy = y + 134
    for i, (nm, wk, nk) in enumerate(rows):
        hgt = 168 if i == 1 else 104
        d.node(f"r{i}", "box", x, yy, 328, hgt, "", fill="#ffffff")
        d.node(f"rn{i}", "text", x + 10, yy + 6, 300, 18, f"{i + 1}. {nm}", size=13, bold=True)
        d.node(f"rw{i}", "text", x + 10, yy + 26, 300, 16, wk, size=11.5, color="#52606d")
        d.node(f"rk{i}", "text", x + 10, yy + 44, 300, 16, nk, size=11.5, color="#52606d")
        d.node(f"bd{i}", "button", x + 10, yy + 64, 96, 30, "Lihat detail", size=11.5)
        d.node(f"bs{i}", "button", x + 114, yy + 64, 96, 30, "Setujui", size=11.5, fill="#e3f9e5")
        d.node(f"bt{i}", "button", x + 218, yy + 64, 96, 30, "Tolak", size=11.5, fill="#ffe3e3")
        if i == 1:
            d.node("al", "input", x + 10, yy + 102, 308, 30, "Alasan penolakan (wajib)", size=11.5)
            d.node("ak", "button", x + 218, yy + 136, 100, 26, "Kirim", size=11.5)
        yy += hgt + 10
    d.node("ft", "text", x + 4, yy + 4, 320, 30, "Saat kuota 30 tercapai, tombol Setujui mati\ndan sisa antrean ditolak otomatis.", size=11, color="#52606d")
    note(d, 1, 410, 120, "Kuota terisi dari 30;\nperingatan bila < 20 (REQ-F10)", x + 338, y + 56)
    note(d, 2, 410, 230, "Urut waktu daftar paling awal\n(REQ-F02)", x + 338, y + 160)
    note(d, 3, 410, 300, "NIK tersamar; NIK utuh hanya\ndi Lihat detail (REQ-N01)", x + 338, y + 186)
    note(d, 4, 410, 400, "Tolak membuka isian alasan\nwajib (REQ-F02)", x + 338, y + 362)
    note(d, 5, 410, 600, "Kuota atomik, tolak otomatis\n(REQ-D01)", x + 338, yy + 18)
    d.save(OUT, "wireframe-1-antrean")


def wf_presensi():
    d = Diagram("Wireframe presensi", 720, 680, "Gambar 5.3 Layar 2: presensi sesi yang tetap jalan offline (Instruktur)")
    x, y = phone(d, h=610)
    d.node("hdr", "rect", x, y, 328, 58, "", fill="#f2f4f7", stroke="#cbd2d9")
    d.node("h1", "text", x + 10, y + 6, 300, 20, "Presensi · Sesi 8 dari 10", size=13, bold=True)
    d.node("h2", "text", x + 10, y + 30, 300, 18, "Perbengkelan Motor A1 · 30 Okt", size=12)
    d.node("off", "box", x, y + 68, 328, 40, "", fill="#fff4d6")
    d.node("off1", "text", x + 10, y + 70, 310, 36, "● Offline · 6 data belum terkirim\n  tersimpan di HP ini", size=12, bold=True)
    people = [("Budi Santoso", 0), ("Sari Astuti", 1), ("Dewi Lestari", 2)]
    yy = y + 120
    for i, (nm, sel) in enumerate(people):
        d.node(f"c{i}", "box", x, yy, 328, 92, "", fill="#ffffff")
        d.node(f"cn{i}", "text", x + 10, yy + 6, 300, 18, nm, size=13, bold=True)
        for j, lab in enumerate(["Hadir", "Izin", "Alfa"]):
            fill = "#3b6fd6" if j == sel else "#ffffff"
            d.node(f"cb{i}{j}", "button", x + 10 + j * 104, yy + 32, 96, 50, lab, size=13,
                   fill="#c7dbff" if j == sel else "#ffffff")
        yy += 102
    d.node("more", "text", x + 10, yy, 300, 20, "… 27 peserta lain", size=11.5, color="#52606d")
    d.node("sync", "button", x, yy + 30, 328, 52, "Sinkronkan (6)", size=14, fill="#e8f0fe")
    d.node("last", "text", x + 4, yy + 88, 320, 18, "Terakhir terkirim: 29 Okt 10.42", size=11, color="#52606d")
    note(d, 1, 410, 150, "Status koneksi dan jumlah data\nyang masih di HP (REQ-N02)", x + 338, y + 88)
    note(d, 2, 410, 240, "Hanya nama, tanpa NIK\n(REQ-N01)", x + 338, y + 138)
    note(d, 3, 410, 320, "Tombol besar ≥ 48 × 48 px,\nlabel sehari-hari (REQ-N03)", x + 338, y + 176)
    note(d, 4, 410, 420, "Satu status per peserta per sesi:\nHADIR / IZIN / ALFA (REQ-F03)", x + 338, y + 282)
    note(d, 5, 410, 560, "Kirim ulang aman: sync_key\nmencegah data dobel (REQ-N02)", x + 338, yy + 56)
    d.save(OUT, "wireframe-2-presensi")


def wf_evaluasi():
    d = Diagram("Wireframe evaluasi", 720, 680, "Gambar 5.4 Layar 3: evaluasi, pengesahan, dan surat (Pengurus inti)")
    x, y = phone(d, h=610)
    d.node("hdr", "rect", x, y, 328, 58, "", fill="#f2f4f7", stroke="#cbd2d9")
    d.node("h1", "text", x + 10, y + 6, 300, 20, "Evaluasi kelulusan", size=13, bold=True)
    d.node("h2", "text", x + 10, y + 30, 300, 18, "Perbengkelan Motor A1 · 30 peserta", size=12)
    d.node("sum", "box", x, y + 68, 328, 42, "", fill="#f7f9fb")
    d.node("sum1", "text", x + 10, y + 70, 310, 38, "Lulus 26 · Tidak lulus 3\nBelum dapat dievaluasi 1", size=12, bold=True)
    d.node("th", "rect", x, y + 122, 328, 30, "", fill="#f2f4f7", stroke="#cbd2d9")
    for lab, dx in (("Nama", 8), ("Hadir", 120), ("Nilai", 172), ("Status", 232)):
        d.node(f"th{dx}", "text", x + dx, y + 128, 90, 18, lab, size=12, bold=True)
    rows = [("Budi S.", "9/10", "82,00", "LULUS"), ("Sari A.", "8/10", "74,90", "TIDAK LULUS"),
            ("Rudi H.", "7/10", "90,00", "TIDAK LULUS"), ("Dewi L.", "9/10", "—", "BELUM DAPAT\nDIEVALUASI")]
    yy = y + 152
    for i, (nm, hd, nl, st) in enumerate(rows):
        d.node(f"tr{i}", "rect", x, yy, 328, 46, "", stroke="#cbd2d9")
        d.node(f"t1{i}", "text", x + 8, yy + 14, 110, 18, nm, size=12)
        d.node(f"t2{i}", "text", x + 120, yy + 14, 50, 18, hd, size=12)
        d.node(f"t3{i}", "text", x + 172, yy + 14, 60, 18, nl, size=12)
        d.node(f"t4{i}", "text", x + 232, yy + 6, 96, 34, st, size=11, bold=True)
        yy += 46
    d.node("more", "text", x + 8, yy + 4, 300, 18, "… 26 peserta lain", size=11.5, color="#52606d")
    d.node("sah", "button", x, yy + 34, 328, 50, "Sahkan hasil (nonaktif)", size=13, fill="#e4e7eb")
    d.node("sahn", "text", x + 4, yy + 88, 320, 30, "Aktif bila 10 sesi dan semua nilai lengkap.\nHanya akun Pengurus inti.", size=11, color="#52606d")
    d.node("srt", "button", x, yy + 128, 328, 50, "Terbitkan surat (setelah disahkan)", size=12.5, fill="#e4e7eb")
    note(d, 1, 410, 200, "Hadir dihitung dari HADIR saja;\nIZIN dan ALFA tidak (REQ-D02)", x + 338, y + 137)
    note(d, 2, 410, 280, "74,90 tetap TIDAK LULUS,\ntanpa pembulatan (REQ-D02)", x + 338, y + 220)
    note(d, 3, 410, 360, "Data belum lengkap: belum bisa\ndievaluasi (REQ-D02)", x + 338, y + 312)
    note(d, 4, 410, 480, "Pengesahan oleh Pengurus inti,\ntercatat di audit (REQ-D05)", x + 338, yy + 58)
    note(d, 5, 410, 590, "Surat PDF bernomor + total JP,\nhanya LULUS sah (REQ-D06)", x + 338, yy + 152)
    d.save(OUT, "wireframe-3-evaluasi")


if __name__ == "__main__":
    usecase()
    flowmaps()
    arsitektur()
    wf_antrean()
    wf_presensi()
    wf_evaluasi()
