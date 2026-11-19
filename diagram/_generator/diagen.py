"""Generator diagram kecil: satu spesifikasi -> berkas .drawio (bisa diedit di draw.io) + .svg (untuk dicetak).

Bentuk: rect, round, circle, ellipse, store (penyimpanan DFD terbuka kanan), actor (orang lidi),
text (teks lepas), lane (kolom swimlane), frame (bingkai HP/layar), button, input.
Panah: polyline lewat titik-titik; label diletakkan pada fraksi t sepanjang garis.
"""
import math
from xml.sax.saxutils import escape

FONT = "Liberation Sans, Arial, Helvetica, sans-serif"
INK = "#1f2933"
LINE = "#52606d"
FILL = "#ffffff"
SOFT = "#f2f4f7"
ACCENT = "#e8f0fe"
ACCENT_LINE = "#3b6fd6"


class Diagram:
    def __init__(self, name, width, height, title=None):
        self.name, self.w, self.h, self.title = name, width, height, title
        self.nodes, self.edges, self.order = {}, [], []

    # ---------- nodes ----------
    def node(self, nid, kind, x, y, w, h, label="", **kw):
        n = dict(id=nid, kind=kind, x=x, y=y, w=w, h=h, label=label, **kw)
        self.nodes[nid] = n
        self.order.append(n)
        return n

    def edge(self, src, dst, label="", pts=None, t=0.5, arrow=True, dashed=False, both=False,
             sp=None, dp=None, loff=(0, 0), lpos=None):
        self.edges.append(dict(src=src, dst=dst, label=label, pts=pts or [], t=t, arrow=arrow,
                               dashed=dashed, both=both, sp=sp, dp=dp, loff=loff, lpos=lpos))

    # ---------- geometry ----------
    def center(self, n):
        return (n["x"] + n["w"] / 2, n["y"] + n["h"] / 2)

    def boundary(self, n, toward):
        cx, cy = self.center(n)
        dx, dy = toward[0] - cx, toward[1] - cy
        if dx == 0 and dy == 0:
            return (cx, cy)
        if n["kind"] in ("circle", "ellipse"):
            a, b = n["w"] / 2, n["h"] / 2
            k = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
            return (cx + dx * k, cy + dy * k)
        if n["kind"] == "actor":
            a, b = n["w"] / 2, n["h"] / 2
        else:
            a, b = n["w"] / 2, n["h"] / 2
        kx = a / abs(dx) if dx else 1e9
        ky = b / abs(dy) if dy else 1e9
        k = min(kx, ky)
        return (cx + dx * k, cy + dy * k)

    def path_points(self, e):
        s, d = self.nodes[e["src"]], self.nodes[e["dst"]]
        mids = list(e["pts"])
        first = mids[0] if mids else (e["dp"] or self.center(d))
        last = mids[-1] if mids else (e["sp"] or self.center(s))
        p0 = e["sp"] or self.boundary(s, first)
        p1 = e["dp"] or self.boundary(d, last)
        return [p0] + mids + [p1]

    @staticmethod
    def along(pts, t):
        segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        lens = [math.dist(a, b) for a, b in segs]
        total = sum(lens) or 1
        target = total * t
        for (a, b), L in zip(segs, lens):
            if target <= L:
                f = target / L if L else 0
                return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            target -= L
        return pts[-1]

    # ---------- SVG ----------
    def svg(self):
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
             f'width="{self.w}" height="{self.h}" font-family="{FONT}">',
             '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{LINE}"/></marker></defs>',
             f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#ffffff"/>']
        if self.title:
            o.append(f'<text x="16" y="26" font-size="15" font-weight="bold" fill="{INK}">{escape(self.title)}</text>')
        for n in [n for n in self.order if n["kind"] in ("lane", "frame", "group")]:
            o.append(self._svg_node(n))
        for e in self.edges:
            pts = self.path_points(e)
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
            dash = ' stroke-dasharray="6 4"' if e["dashed"] else ""
            me = ' marker-end="url(#ar)"' if e["arrow"] else ""
            ms = ' marker-start="url(#ar)"' if e["both"] else ""
            o.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.3"{dash}{me}{ms}/>')
        for n in [n for n in self.order if n["kind"] not in ("lane", "frame", "group")]:
            o.append(self._svg_node(n))
        for e in self.edges:
            if e["label"]:
                if e.get("lpos"):
                    x, y = e["lpos"]
                else:
                    x, y = self.along(self.path_points(e), e["t"])
                    x += e["loff"][0]
                    y += e["loff"][1]
                o.append(self._svg_label(x, y, e["label"]))
        o.append("</svg>")
        return "\n".join(o)

    def _lines(self, label):
        return label.split("\n") if label else []

    def _svg_text(self, cx, cy, label, size=13, bold=False, anchor="middle", color=INK, lh=None):
        lines = self._lines(label)
        lh = lh or size * 1.25
        y0 = cy - (len(lines) - 1) * lh / 2 + size * 0.35
        fw = ' font-weight="bold"' if bold else ""
        out = []
        for i, ln in enumerate(lines):
            out.append(f'<text x="{cx:.1f}" y="{y0 + i * lh:.1f}" font-size="{size}"{fw} text-anchor="{anchor}" '
                       f'fill="{color}">{escape(ln)}</text>')
        return "".join(out)

    def _svg_label(self, x, y, label, size=12):
        lines = self._lines(label)
        w = max(len(l) for l in lines) * size * 0.53 + 8
        h = len(lines) * size * 1.25 + 4
        return (f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#ffffff" '
                f'fill-opacity="0.95"/>' + self._svg_text(x, y, label, size=size, color="#323f4b"))

    def _svg_node(self, n):
        k, x, y, w, h = n["kind"], n["x"], n["y"], n["w"], n["h"]
        cx, cy = x + w / 2, y + h / 2
        size = n.get("size", 13)
        bold = n.get("bold", False)
        fill = n.get("fill", FILL)
        stroke = n.get("stroke", LINE)
        dash = ' stroke-dasharray="6 4"' if n.get("dashed") else ""
        if k == "rect":
            s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"{dash}/>'
        elif k == "round":
            s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.3"{dash}/>'
        elif k in ("circle", "ellipse"):
            s = f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2}" ry="{h / 2}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>'
        elif k == "store":
            idw = n.get("idw", 34)
            s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="none"/>'
                 f'<path d="M{x + w} {y} L{x} {y} L{x} {y + h} L{x + w} {y + h}" fill="none" stroke="{stroke}" stroke-width="1.3"/>'
                 f'<line x1="{x + idw}" y1="{y}" x2="{x + idw}" y2="{y + h}" stroke="{stroke}" stroke-width="1.3"/>')
            sid, sname = n["label"].split(" ", 1)
            return (s + self._svg_text(x + idw / 2, cy, sid, size=size, bold=True)
                    + self._svg_text(x + idw + 8, cy, sname, size=size, anchor="start"))
        elif k == "actor":
            hx, hy, r = cx, y + 10, 9
            s = (f'<circle cx="{hx}" cy="{hy}" r="{r}" fill="#fff" stroke="{stroke}" stroke-width="1.4"/>'
                 f'<path d="M{hx} {hy + r} V{y + 42} M{hx - 16} {y + 28} H{hx + 16} M{hx} {y + 42} L{hx - 13} {y + 60} '
                 f'M{hx} {y + 42} L{hx + 13} {y + 60}" stroke="{stroke}" stroke-width="1.4" fill="none"/>')
            return s + self._svg_text(cx, y + h - 6, n["label"], size=size, bold=True)
        elif k == "lane":
            s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{n.get("fill", "#ffffff")}" stroke="{stroke}" stroke-width="1"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="34" fill="{SOFT}" stroke="{stroke}" stroke-width="1"/>')
            return s + self._svg_text(cx, y + 17, n["label"], size=13, bold=True)
        elif k == "group":
            s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{n.get("fill", "#fafbfc")}" stroke="{stroke}" stroke-width="1" stroke-dasharray="5 4"/>'
            return s + self._svg_text(x + 12, y + 18, n["label"], size=12.5, bold=True, anchor="start", color="#3e4c59")
        elif k == "frame":
            s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
                 f'<rect x="{x + w / 2 - 30}" y="{y + 10}" width="60" height="6" rx="3" fill="#cbd2d9"/>')
            return s
        elif k == "button":
            f2 = n.get("fill", "#ffffff")
            s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{f2}" stroke="{INK}" stroke-width="1.4"/>'
            return s + self._svg_text(cx, cy, n["label"], size=size, bold=True)
        elif k == "input":
            s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#ffffff" stroke="#9aa5b1" stroke-width="1.2"/>'
            return s + self._svg_text(x + 8, cy, n["label"], size=size, anchor="start", color="#7b8794")
        elif k == "text":
            anchor = n.get("anchor", "start")
            tx = x if anchor == "start" else (cx if anchor == "middle" else x + w)
            return self._svg_text(tx, cy, n["label"], size=size, bold=bold, anchor=anchor, color=n.get("color", INK))
        elif k == "line":
            return f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y + h}" stroke="#cbd2d9" stroke-width="1.2"/>'
        elif k == "box":  # kotak abu untuk area gambar/placeholder
            s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#9aa5b1" stroke-width="1"{dash}/>'
        else:
            raise ValueError(k)
        if n["label"] and k not in ("store",):
            if n.get("align") == "left":
                s += self._svg_text(x + 10, cy, n["label"], size=size, bold=bold, anchor="start")
            else:
                s += self._svg_text(cx, cy, n["label"], size=size, bold=bold)
        return s

    # ---------- draw.io ----------
    def drawio(self):
        cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
        base = f"fontFamily=Helvetica;fontColor={INK};html=1;whiteSpace=wrap;"
        ids = {}
        if self.title:
            cells.append(f'<mxCell id="title" value="{escape(self.title)}" style="text;{base}fontSize=15;fontStyle=1;align=left;" '
                         f'vertex="1" parent="1"><mxGeometry x="16" y="8" width="{self.w - 32}" height="28" as="geometry"/></mxCell>')
        order = [n for n in self.order if n["kind"] in ("lane", "frame", "group")] + \
                [n for n in self.order if n["kind"] not in ("lane", "frame", "group")]
        for i, n in enumerate(order):
            cid = f"n{i}"
            ids[n["id"]] = cid
            k = n["kind"]
            fs = n.get("size", 13)
            fstyle = "fontStyle=1;" if n.get("bold") else ""
            dash = "dashed=1;" if n.get("dashed") else ""
            fill = n.get("fill", FILL)
            stroke = n.get("stroke", LINE)
            val = escape(n["label"]).replace("\n", "&lt;br&gt;")
            if k == "rect":
                st = f"rounded=0;fillColor={fill};strokeColor={stroke};{dash}"
            elif k == "round":
                st = f"rounded=1;arcSize=12;fillColor={fill};strokeColor={stroke};{dash}"
            elif k in ("circle", "ellipse"):
                st = f"ellipse;fillColor={fill};strokeColor={stroke};"
            elif k == "store":
                st = f"shape=partialRectangle;right=0;fillColor={fill};strokeColor={stroke};align=left;spacingLeft=6;"
                sid, sname = n["label"].split(" ", 1)
                val = f"&lt;b&gt;{escape(sid)}&lt;/b&gt;&amp;nbsp;&amp;nbsp;|&amp;nbsp; {escape(sname)}"
            elif k == "actor":
                st = f"shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fillColor=#ffffff;strokeColor={stroke};fontStyle=1;"
            elif k == "lane":
                st = f"swimlane;startSize=34;fillColor={SOFT};swimlaneFillColor={n.get('fill', '#ffffff')};strokeColor={stroke};fontStyle=1;"
            elif k == "group":
                st = f"rounded=1;arcSize=4;dashed=1;fillColor={n.get('fill', '#fafbfc')};strokeColor={stroke};verticalAlign=top;align=left;spacingLeft=10;fontStyle=1;"
            elif k == "frame":
                st = f"rounded=1;arcSize=6;fillColor=#ffffff;strokeColor={INK};strokeWidth=2;"
            elif k == "button":
                st = f"rounded=1;fillColor={n.get('fill', '#ffffff')};strokeColor={INK};strokeWidth=1.4;fontStyle=1;"
            elif k == "input":
                st = "rounded=1;arcSize=8;fillColor=#ffffff;strokeColor=#9aa5b1;align=left;spacingLeft=8;fontColor=#7b8794;"
            elif k == "text":
                al = n.get("anchor", "start")
                st = f"text;align={'left' if al == 'start' else ('center' if al == 'middle' else 'right')};verticalAlign=middle;fontColor={n.get('color', INK)};"
            elif k == "line":
                st = "line;strokeColor=#cbd2d9;"
            elif k == "box":
                st = f"rounded=1;arcSize=4;fillColor={fill};strokeColor=#9aa5b1;{dash}"
            else:
                raise ValueError(k)
            if n.get("align") == "left" and k not in ("store", "text"):
                st += "align=left;spacingLeft=10;"
            st = base + st + f"fontSize={fs};{fstyle}"
            if k == "lane":
                st = st.replace("fontStyle=1;fontSize", "fontSize")
            h = n["h"] if k != "line" else max(n["h"], 1)
            cells.append(f'<mxCell id="{cid}" value="{val}" style="{st}" vertex="1" parent="1">'
                         f'<mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"] or 1}" height="{h}" as="geometry"/></mxCell>')
        for j, e in enumerate(self.edges):
            pts = self.path_points(e)
            val = escape(e["label"]).replace("\n", "&lt;br&gt;")
            st = (base + f"edgeStyle=none;rounded=0;strokeColor={LINE};fontSize=12;labelBackgroundColor=#ffffff;"
                  + ("endArrow=classic;" if e["arrow"] else "endArrow=none;")
                  + ("startArrow=classic;" if e["both"] else "startArrow=none;")
                  + ("dashed=1;" if e["dashed"] else ""))
            arr = "".join(f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for x, y in e["pts"])
            arr = f'<Array as="points">{arr}</Array>' if arr else ""
            rel = 2 * e["t"] - 1
            cells.append(f'<mxCell id="e{j}" value="{val}" style="{st}" edge="1" parent="1" source="{ids[e["src"]]}" '
                         f'target="{ids[e["dst"]]}"><mxGeometry x="{rel:.2f}" relative="1" as="geometry">'
                         f'<mxPoint x="{pts[0][0]:.1f}" y="{pts[0][1]:.1f}" as="sourcePoint"/>'
                         f'<mxPoint x="{pts[-1][0]:.1f}" y="{pts[-1][1]:.1f}" as="targetPoint"/>{arr}'
                         f'<mxPoint x="{e["loff"][0]}" y="{e["loff"][1]}" as="offset"/></mxGeometry></mxCell>')
        body = "".join(cells)
        return (f'<mxfile host="diagen" type="device"><diagram name="{escape(self.name)}" id="{escape(self.name)}">'
                f'<mxGraphModel dx="{self.w}" dy="{self.h}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" math="0" shadow="0">'
                f'<root>{body}</root></mxGraphModel></diagram></mxfile>')

    def save(self, outdir, stem):
        import os
        os.makedirs(outdir, exist_ok=True)
        with open(f"{outdir}/{stem}.drawio", "w") as f:
            f.write(self.drawio())
        with open(f"{outdir}/{stem}.svg", "w") as f:
            f.write(self.svg())
