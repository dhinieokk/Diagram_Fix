"""ERD DayaMuda dalam dua bagian agar terbaca di A4. Kardinalitas ditulis sebagai teks (1, 0..1, 0..N, 1..N)."""
from diagen import Diagram

OUT = "/home/claude/diagram/src"
ROW = 20

ATTR = {
    "PENGGUNA": ("E-01", [("PK", "pengguna_id", "BIGINT"), ("", "nama", "VARCHAR(100)"), ("UK", "username", "VARCHAR(60)"),
                          ("", "password_hash", "VARCHAR(255)"), ("", "peran", "ENUM"), ("", "aktif", "BOOLEAN"),
                          ("", "dibuat_pada", "DATETIME")]),
    "PESERTA": ("E-02", [("PK", "peserta_id", "BIGINT"), ("UK", "kode_peserta", "CHAR(9)"), ("", "pin_hash", "VARCHAR(255)"),
                         ("", "nama", "VARCHAR(100)"), ("", "nik_enkripsi", "VARBINARY(64)"), ("UK", "nik_hash", "CHAR(64)"),
                         ("", "nik_samaran", "CHAR(16)"), ("", "jenis_kelamin", "ENUM"), ("", "tanggal_lahir", "DATE"),
                         ("", "dusun_rw", "VARCHAR(50)"), ("", "no_wa", "VARCHAR(20)"),
                         ("", "persetujuan_data_pada", "DATETIME"), ("", "dibuat_pada", "DATETIME")]),
    "KELAS_PELATIHAN": ("E-03", [("PK", "kelas_id", "BIGINT"), ("", "nama_kelas", "VARCHAR(120)"),
                                 ("", "jenis_keterampilan", "VARCHAR(100)"), ("", "tanggal_mulai", "DATE"),
                                 ("", "tanggal_selesai", "DATE"), ("", "kuota_maks", "TINYINT"),
                                 ("FK", "instruktur_id", "BIGINT"), ("", "status_kelas", "ENUM"), ("", "dibuat_pada", "DATETIME")]),
    "SESI_PELATIHAN": ("E-04", [("PK", "sesi_id", "BIGINT"), ("FK", "kelas_id", "BIGINT"), ("", "nomor_sesi", "TINYINT"),
                                ("", "waktu_mulai", "DATETIME"), ("", "waktu_selesai", "DATETIME"), ("", "durasi_jp", "TINYINT"),
                                ("", "keterangan", "VARCHAR(255)")]),
    "PENDAFTARAN": ("E-05", [("PK", "pendaftaran_id", "BIGINT"), ("FK", "peserta_id", "BIGINT"), ("FK", "kelas_id", "BIGINT"),
                             ("", "created_at", "DATETIME(3)"), ("", "status_pendaftaran", "ENUM"),
                             ("FK", "didaftarkan_oleh", "BIGINT"), ("FK", "diputuskan_oleh", "BIGINT"),
                             ("", "diputuskan_pada", "DATETIME"), ("", "alasan_penolakan", "VARCHAR(255)")]),
    "PRESENSI": ("E-06", [("PK", "presensi_id", "BIGINT"), ("FK", "pendaftaran_id", "BIGINT"), ("FK", "sesi_id", "BIGINT"),
                          ("", "status_hadir", "ENUM"), ("FK", "dicatat_oleh", "BIGINT"), ("", "dicatat_pada", "DATETIME"),
                          ("UK", "sync_key", "VARCHAR(100)")]),
    "EVALUASI_PRAKTIK": ("E-07", [("PK", "evaluasi_id", "BIGINT"), ("FK", "pendaftaran_id", "BIGINT"),
                                  ("FK", "instruktur_id", "BIGINT"), ("", "nilai_praktik", "DECIMAL(5,2)"),
                                  ("", "dinilai_pada", "DATETIME"), ("", "status_kelulusan", "ENUM"),
                                  ("FK", "disahkan_oleh", "BIGINT"), ("", "disahkan_pada", "DATETIME"),
                                  ("", "catatan", "VARCHAR(500)")]),
    "SURAT_HASIL": ("E-08", [("PK", "surat_id", "BIGINT"), ("FK", "pendaftaran_id", "BIGINT"),
                             ("UK", "nomor_registrasi", "VARCHAR(40)"), ("", "tanggal_terbit", "DATE"),
                             ("", "total_jp", "SMALLINT"), ("", "lokasi_file_pdf", "VARCHAR(255)"), ("", "status_surat", "ENUM")]),
    "AUDIT_LOG": ("E-09", [("PK", "audit_id", "BIGINT"), ("", "aktor", "ENUM"), ("FK", "pengguna_id", "BIGINT"),
                           ("", "entitas", "VARCHAR(30)"), ("", "entitas_id", "BIGINT"), ("", "aksi", "VARCHAR(50)"),
                           ("", "nilai_sebelum", "VARCHAR(100)"), ("", "nilai_sesudah", "VARCHAR(100)"),
                           ("", "alasan", "VARCHAR(255)"), ("", "waktu_aksi", "DATETIME")]),
}


def entity(d, name, x, y, w=240, stub=False):
    code, attrs = ATTR[name]
    if stub:
        attrs = attrs[:1]
    h = 28 + ROW * len(attrs) + 8
    d.node(name, "rect", x, y, w, h, "", fill="#ffffff")
    d.node(name + "_h", "rect", x, y, w, 28, f"{code} {name}" + (" (lihat bagian 1)" if stub else ""),
           size=12 if stub else 13, bold=True, fill="#eef4ff", stroke="#52606d")
    for i, (k, n, t) in enumerate(attrs):
        yy = y + 32 + i * ROW
        if k:
            d.node(f"{name}_k{i}", "text", x + 8, yy, 26, ROW, k, size=11, bold=True, color="#3b6fd6")
        d.node(f"{name}_n{i}", "text", x + 38, yy, 140, ROW, n, size=11.5, bold=(k == "PK"))
        d.node(f"{name}_t{i}", "text", x + w - 96, yy, 88, ROW, t, size=11, anchor="end", color="#52606d")
    return h


def card(d, key, x, y, text):
    d.node(key, "text", x - 20, y - 9, 40, 18, text, size=11.5, bold=True, anchor="middle", color="#9c4221")


def rel(d, a, b, name, sp, dp, pts, lpos, ca, cpa, cb, cpb):
    d.edge(a, b, name, sp=sp, dp=dp, pts=pts, arrow=False, lpos=lpos)
    card(d, f"c_{a}_{b}_{name}_a", cpa[0], cpa[1], ca)
    card(d, f"c_{a}_{b}_{name}_b", cpb[0], cpb[1], cb)


def bagian1():
    d = Diagram("ERD bagian 1", 910, 660, "Gambar 4.8a ERD bagian 1: pengguna, peserta, kelas, sesi, pendaftaran")
    entity(d, "PENGGUNA", 20, 80)
    entity(d, "PESERTA", 20, 330)
    entity(d, "PENDAFTARAN", 330, 330)
    entity(d, "KELAS_PELATIHAN", 640, 80)
    entity(d, "SESI_PELATIHAN", 640, 410)
    rel(d, "PENGGUNA", "KELAS_PELATIHAN", "mengampu", (260, 130), (640, 130), [], (450, 118),
        "1", (272, 142), "0..N", (618, 142))
    rel(d, "PENGGUNA", "PENDAFTARAN", "memutuskan /\nmendaftarkan", (260, 210), (450, 330), [(450, 210)], (450, 265),
        "0..1", (276, 198), "0..N", (472, 318))
    rel(d, "KELAS_PELATIHAN", "PENDAFTARAN", "menerima", (640, 260), (570, 390), [(605, 260), (605, 390)], (605, 325),
        "1", (626, 248), "0..N", (588, 378))
    rel(d, "KELAS_PELATIHAN", "SESI_PELATIHAN", "terdiri atas\n10 sesi", (760, 296), (760, 410), [], (820, 352),
        "1", (772, 308), "1..N", (780, 398))
    rel(d, "PESERTA", "PENDAFTARAN", "mengajukan", (260, 430), (330, 430), [], (295, 416),
        "1", (270, 442), "0..N", (314, 442))
    d.save(OUT, "erd-1-pendaftaran")


def bagian2():
    d = Diagram("ERD bagian 2", 940, 720, "Gambar 4.8b ERD bagian 2: presensi, evaluasi, surat, audit")
    entity(d, "PENGGUNA", 20, 80, stub=True)
    entity(d, "PENDAFTARAN", 350, 80, stub=True)
    entity(d, "SESI_PELATIHAN", 660, 80, stub=True)
    entity(d, "AUDIT_LOG", 20, 230)
    entity(d, "EVALUASI_PRAKTIK", 350, 230)
    entity(d, "SURAT_HASIL", 350, 510)
    entity(d, "PRESENSI", 660, 230)
    rel(d, "PENGGUNA", "AUDIT_LOG", "melakukan", (100, 136), (100, 230), [], (150, 183),
        "0..1", (124, 148), "0..N", (124, 218))
    rel(d, "PENGGUNA", "EVALUASI_PRAKTIK", "menilai", (260, 98), (350, 270), [(322, 98), (322, 270)], (322, 200),
        "1", (272, 88), "0..N", (336, 258))
    rel(d, "PENGGUNA", "EVALUASI_PRAKTIK", "mengesahkan", (260, 120), (350, 330), [(288, 120), (288, 330)], (308, 345),
        "0..1", (278, 110), "0..N", (332, 318))
    rel(d, "PENGGUNA", "PRESENSI", "mencatat", (140, 80), (900, 300), [(140, 60), (920, 60), (920, 300)], (540, 60),
        "1", (152, 70), "0..N", (910, 316))
    rel(d, "PENDAFTARAN", "EVALUASI_PRAKTIK", "dinilai", (470, 136), (470, 230), [], (510, 183),
        "1", (482, 148), "0..1", (486, 218))
    rel(d, "PENDAFTARAN", "PRESENSI", "dicatat", (590, 98), (720, 230), [(632, 98), (632, 180), (720, 180)], (676, 180),
        "1", (602, 88), "0..N", (736, 218))
    rel(d, "PENDAFTARAN", "SURAT_HASIL", "menghasilkan", (590, 122), (590, 570), [(612, 122), (612, 570)], (612, 470),
        "1", (602, 112), "0..1", (602, 558))
    rel(d, "SESI_PELATIHAN", "PRESENSI", "memuat", (820, 136), (820, 230), [], (860, 190),
        "1", (832, 148), "0..N", (838, 218))
    d.save(OUT, "erd-2-pelaksanaan")


if __name__ == "__main__":
    bagian1()
    bagian2()
