#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional PPTX Generator - Diplom Himoya Prezentatsiyasi
Muallif: Amonov Sohibjon | TATU Samarqand filiali | 2026
"""

import zipfile, os, shutil, textwrap
from pathlib import Path

# ─── RANGLAR ───────────────────────────────────────────────────────────────
BG1   = "0D1B2A"  # asosiy fon
BG2   = "0F2547"  # slayd foni
CYAN  = "00C6FF"  # neon ko'k
PURP  = "7B2FBE"  # binafsha
WHITE = "FFFFFF"
LGRAY = "B0C4DE"
GOLD  = "FFD700"
GREEN = "00E676"
RED   = "FF4444"

def emu(cm):
    return int(cm * 360000)

def hpt(pt):
    return int(pt * 100)

def esc(t):
    return (str(t)
            .replace("&","&amp;")
            .replace("<","&lt;")
            .replace(">","&gt;")
            .replace('"',"&quot;"))

def run(text, sz=14, bold=False, color=WHITE, italic=False):
    b = ' b="1"' if bold else ''
    i = ' i="1"' if italic else ''
    return (f'<a:r><a:rPr lang="uz-UZ" altLang="en-US" sz="{hpt(sz)}"{b}{i} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="Calibri"/>'
            f'</a:rPr><a:t>{esc(text)}</a:t></a:r>')

def para(runs_xml, align="l", spc_before=0):
    align_map = {"l": "", "c": ' algn="ctr"', "r": ' algn="r"'}
    al = align_map.get(align, "")
    sp = f'<a:spcBef><a:spcPts val="{spc_before}"/></a:spcBef>' if spc_before else ''
    return f'<a:p><a:pPr{al}>{sp}</a:pPr>{runs_xml}</a:p>'

def tbox(x, y, w, h, paras_xml, anchor="t", wrap=True):
    wr = "square" if wrap else "none"
    return f'''
  <p:sp>
    <p:nvSpPr>
      <p:cNvPr id="1" name="tb"/>
      <p:cNvSpPr txBox="1"/>
      <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      <a:noFill/>
    </p:spPr>
    <p:txBody>
      <a:bodyPr wrap="{wr}" anchor="{anchor}" lIns="91440" rIns="91440" tIns="45720" bIns="45720"/>
      <a:lstStyle/>
      {paras_xml}
    </p:txBody>
  </p:sp>'''

def rect(x, y, w, h, fill, alpha=None, rx=0):
    if alpha:
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>'
    else:
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    prst = "roundRect" if rx else "rect"
    avlst = f'<a:avLst><a:gd name="adj" fmla="val {rx}"/></a:avLst>' if rx else '<a:avLst/>'
    return f'''
  <p:sp>
    <p:nvSpPr>
      <p:cNvPr id="2" name="r"/>
      <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
      <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
      <a:prstGeom prst="{prst}">{avlst}</a:prstGeom>
      {fill_xml}
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
  </p:sp>'''

def line_rect(x, y, w, h_px, color, alpha=None):
    """Yupqa chiziq uchun"""
    return rect(x, y, w, h_px, color, alpha)

def image_shape(rId, x, y, w, h):
    return f'''
  <p:pic>
    <p:nvPicPr>
      <p:cNvPr id="10" name="img"/>
      <p:cNvPicPr/>
      <p:nvPr/>
    </p:nvPicPr>
    <p:blipFill>
      <a:blip r:embed="{rId}"/>
      <a:stretch><a:fillRect/></a:stretch>
    </p:blipFill>
    <p:spPr>
      <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    </p:spPr>
  </p:pic>'''

def img_border(x, y, w, h, color=CYAN):
    """Rasm atrofida chiroyli ramka"""
    t = 0.06
    shapes = ""
    shapes += rect(x-t, y-t, w+2*t, t, color)
    shapes += rect(x-t, y+h, w+2*t, t, color)
    shapes += rect(x-t, y-t, t, h+2*t, color)
    shapes += rect(x+w, y-t, t, h+2*t, color)
    return shapes

def slide_xml(shapes_xml):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {shapes_xml}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClr/></p:clrMapOvr>
</p:sld>'''

# ═══════════════════════════════════════════════════════════════════════════
# SLAYD QURUVCHILAR
# ═══════════════════════════════════════════════════════════════════════════

def make_title_slide():
    s = ""
    # Fon
    s += rect(0,0,33.87,19.05,BG1)
    # Yuqori dekorativ chiziq
    s += rect(0,0,33.87,0.7,PURP)
    # Pastki dekorativ chiziq
    s += rect(0,18.35,33.87,0.7,CYAN)
    # Chap vertikal aksent
    s += rect(0,0,0.5,19.05,CYAN,alpha=40000)
    # Markaziy panel
    s += rect(1.5,2.2,30.87,14.2,BG2,alpha=70000,rx=20000)
    # Panel ustidagi neon chiziq
    s += rect(1.5,2.2,30.87,0.1,CYAN)

    # Universitey nomi
    s += tbox(2,0.05,30,1.5,
        para(run("O'ZBEKISTON RESPUBLIKASI — TATU SAMARQAND FILIALI",10,False,CYAN,True),"c"))

    # Diplom ishi belgisi
    s += tbox(2,2.5,30,1.2,
        para(run("⚡  BITIRUV MALAKAVIY ISHI  ⚡",12,False,GOLD),"c"))

    # Asosiy sarlavha
    title1 = "Dasturiy versiyalar orasidagi"
    title2 = "o'zgarishlarni tahlil qiluvchi"
    title3 = "dasturiy tizimni loyihalashtirish"
    s += tbox(2,3.8,30,2.5,
        para(run(title1,22,True,WHITE),"c") +
        para(run(title2,22,True,WHITE),"c") +
        para(run(title3,22,True,WHITE),"c"))

    # Ajratuvchi chiziq
    s += rect(6,7.0,22,0.08,CYAN)

    # Muallif ma'lumotlari
    s += tbox(3,7.4,28,6,
        para(run("Bitiruvchi:",13,True,CYAN) + run("  Amonov Sohibjon",13,False,WHITE),"c",100) +
        para(run("Ilmiy rahbar:",13,True,CYAN) + run("  Yusupov O.",13,False,WHITE),"c",100) +
        para(run("Kafedra:",13,True,CYAN) + run("  Dasturiy injiniring",13,False,WHITE),"c",100) +
        para(run("Yil:",13,True,CYAN) + run("  2026",13,False,WHITE),"c",100) +
        para(run("") ,"c",80) +
        para(run("React  •  Node.js  •  Express.js  •  Google Gemini AI",11,False,LGRAY,True),"c",80))
    return s


def make_section_slide(num, title, items):
    s = ""
    s += rect(0,0,33.87,19.05,BG1)
    s += rect(0,0,33.87,0.6,PURP)
    s += rect(0,18.45,33.87,0.6,CYAN)

    # Bob raqami (katta)
    s += rect(1.5,3.5,5,5,BG2,rx=20000)
    s += tbox(1.5,3.5,5,5,
        para(run(str(num),60,True,CYAN),"c"))

    # Bob sarlavhasi
    s += rect(7,4,24,4,BG2,alpha=50000,rx=15000)
    s += rect(7,4,24,0.08,CYAN)
    words = title.split()
    mid = len(words)//2
    l1 = " ".join(words[:mid])
    l2 = " ".join(words[mid:])
    s += tbox(7.3,4.4,23.4,3.2,
        para(run(l1,20,True,WHITE),"l") +
        para(run(l2,20,True,WHITE),"l"))

    # Quyi items
    s += rect(1.5,9.5,31,8.5,BG2,alpha=40000,rx=10000)
    items_xml = ""
    for item in items:
        items_xml += para(run("  ▸  ",12,False,CYAN) + run(item,12,False,LGRAY),"l",60)
    s += tbox(2,10,30,7.5,items_xml)
    return s


def make_content_slide(title, bullets, slide_num, accent=CYAN):
    """Umumiy mazmun slayd"""
    s = ""
    s += rect(0,0,33.87,19.05,BG2)
    # Sarlavha paneli
    s += rect(0,0,33.87,2.8,BG1)
    s += rect(0,2.7,33.87,0.12,accent)
    # Chap aksent chiziq
    s += rect(0.5,0.4,0.3,1.9,accent)

    # Sarlavha
    s += tbox(1.2,0.3,31,2.2,para(run(title,21,True,WHITE),"l"))

    # Slayd raqami
    s += tbox(31.5,17.8,2,1,para(run(str(slide_num),11,False,accent),"r"))

    # Matn bloki
    content_xml = ""
    y_offset = 3.3
    for b in bullets:
        if b.startswith("══") or b.startswith("──"):
            content_xml += para(run(""), "l", 20)
            continue
        # Rang va indentni aniqlash
        clr = WHITE
        sz = 13
        bold = False
        indent = "    "
        if b.startswith("🔷") or b.startswith("✅") or b.startswith("📌"):
            clr = GREEN; bold = True
        elif b.startswith("⚠") or b.startswith("❌"):
            clr = RED
        elif b.startswith("  ") or b.startswith("    "):
            clr = LGRAY; sz = 12; indent = ""
        elif b.startswith("▸") or b.startswith("•"):
            clr = CYAN; bold = True
        content_xml += para(run(indent + b, sz, bold, clr), "l", 40)

    s += tbox(0.8, 3.0, 32.5, 15.5, content_xml)
    return s


def make_image_slide(title, rId, img_x, img_y, img_w, img_h, right_items, slide_num):
    """Rasm + o'ng taraf matni"""
    s = ""
    s += rect(0,0,33.87,19.05,BG2)
    s += rect(0,0,33.87,2.8,BG1)
    s += rect(0,2.7,33.87,0.12,CYAN)
    s += rect(0.5,0.4,0.3,1.9,CYAN)

    # Sarlavha
    s += tbox(1.2,0.3,31,2.2,para(run(title,21,True,WHITE),"l"))
    s += tbox(31.5,17.8,2,1,para(run(str(slide_num),11,False,CYAN),"r"))

    # Rasm + ramka
    s += image_shape(rId, img_x, img_y, img_w, img_h)
    s += img_border(img_x, img_y, img_w, img_h)

    # O'ng panel
    panel_x = img_x + img_w + 0.4
    panel_w = 33.87 - panel_x - 0.3
    s += rect(panel_x, img_y, panel_w, img_h, BG1, alpha=80000, rx=15000)
    s += rect(panel_x, img_y, 0.12, img_h, CYAN)

    items_xml = ""
    for item in right_items:
        items_xml += para(run(" ▸ ",11,False,CYAN) + run(item,11,False,LGRAY),"l",120)
    s += tbox(panel_x+0.25, img_y+0.3, panel_w-0.5, img_h-0.6, items_xml)
    return s


def make_final_slide():
    s = ""
    s += rect(0,0,33.87,19.05,BG1)
    s += rect(0,0,33.87,0.6,CYAN)
    s += rect(0,18.45,33.87,0.6,CYAN)

    # Markaziy katta panel
    s += rect(3,2.5,27.87,14,BG2,rx=20000)
    s += rect(3,2.5,27.87,0.12,PURP)
    s += rect(3,16.38,27.87,0.12,PURP)

    s += tbox(3,3.0,27.87,2.5,
        para(run("🎓  E'tiboringiz uchun",26,True,CYAN),"c") +
        para(run("RAHMAT!",32,True,WHITE),"c"))

    s += rect(7,6.2,20,0.1,CYAN)

    s += tbox(3,6.7,27.87,8,
        para(run("Dasturiy versiyalar tahlil tizimi",15,False,LGRAY,True),"c",150) +
        para(run("─────────────────────────────────────────",10,False,PURP,False),"c",80) +
        para(run("Bitiruvchi:  Amonov Sohibjon",14,False,WHITE),"c",150) +
        para(run("Ilmiy rahbar:  Yusupov O.",14,False,WHITE),"c",120) +
        para(run("TATU Samarqand filiali  —  2026",13,False,LGRAY),"c",120) +
        para(run("─────────────────────────────────────────",10,False,PURP,False),"c",80) +
        para(run("React  •  Node.js  •  Express.js  •  Google Gemini AI",12,False,CYAN,True),"c",150) +
        para(run("") ,"c",150) +
        para(run("Savollar uchun tayyorman!",15,True,GREEN),"c",100))
    return s


# ═══════════════════════════════════════════════════════════════════════════
# BARCHA SLAYDLAR MA'LUMOTLARI
# ═══════════════════════════════════════════════════════════════════════════

SLIDES = [
    # (tur, parametrlar)
    ("title", {}),

    ("section", {
        "num": "📋", "title": "MUNDARIJA",
        "items": [
            "1. Mavzuning dolzarbligi va tadqiqot maqsadi",
            "2. I Bob — Versiyalarni boshqarish tizimlari: nazariy asoslar",
            "3. II Bob — Arxitektura va dasturiy tizimni loyihalashtirish",
            "4. III Bob — Amaliy realizatsiya va sinov natijalari",
            "5. Xulosa, takliflar va istiqbollar",
        ]
    }),

    ("content", {
        "title": "Mavzuning Dolzarbligi",
        "num": 3,
        "bullets": [
            "▸ Zamonaviy dasturiy mahsulotlar o'ta murakkab va ko'p qatlamli arxitekturaga ega",
            "▸ Jamoaviy ishlashda minglab o'zgarishlar (commit) kiritiladi — nazorat zarur",
            "══",
            "⚠ Muammo: An'anaviy Diff vositalari FAQAT sintaktik farqlarni ko'rsatadi",
            "  • Mantiqiy ma'no va xavfsizlikka ta'sir aniqlanmaydi",
            "  • Kodi qayta ko'rib chiqish (Code Review) inson resursini ko'p talab qiladi",
            "  • Yirik loyihalarda xatolar o'tkazib yuboriladi — xavfli!",
            "══",
            "✅ Yechim: LLM (Large Language Models) texnologiyasini integratsiya qilish",
            "▸ Google Gemini 2.5 Flash — o'zbek tilida semantik tahlil",
            "▸ React + Node.js + Express.js — zamonaviy SPA veb-platforma",
        ]
    }),

    ("content", {
        "title": "Tadqiqot Maqsadi va Vazifalari",
        "num": 4,
        "bullets": [
            "📌 MAQSAD: Versiyalar o'zgarishlarini tahlil qiluvchi SPA veb-platforma yaratish",
            "   Dasturiy kod o'zgarishlarini qatorlar darajasida aniqlash va AI bilan izohlash",
            "══",
            "▸ Git va VCS nazariy asoslarini o'rganish",
            "▸ LLM API integratsiya imkoniyatlarini tadqiq etish",
            "▸ 5 oynali mantiqiy-funksional model ishlab chiqish",
            "▸ Router-Controller andozasida backend loyihalash",
            "▸ Prompt Engineering modeli yaratish (o'zbek tilida)",
            "▸ React SPA interfeysi amalga oshirish",
            "══",
            "📌 Tadqiqot obyekti: DT hayotiy sikli, versiyalarni boshqarish jarayonlari",
            "📌 Predmeti: Diff algoritmlari, JS asinxron metodlar, LLM semantik tahlil",
        ]
    }),

    ("section", {
        "num": "I", "title": "BOB: NAZARIY ASOSLAR",
        "items": [
            "1.1 — Versiyalarni boshqarish tizimlari (VCS) tarixi va ahamiyati",
            "1.2 — Diff tahlil metodologiyasi va mavjud dasturiy vositalar sharhi",
            "1.3 — LLM texnologiyalarini dasturiy kod tahliliga integratsiya istiqbollari",
        ]
    }),

    ("content", {
        "title": "Versiyalarni Boshqarish Tizimlari (VCS)",
        "num": 6,
        "bullets": [
            "▸ LOKAL VCS — fayllar faqat shaxsiy kompyuterda saqlangan",
            "   Kamchiligi: boshqa dasturchilarga uzatish imkoni yo'q",
            "══",
            "▸ MARKAZLASHTIRILGAN (CVCS) — SVN, CVS tizimlar",
            "   Yagona server — server o'chsa, butun loyiha tarixi yo'qoladi ⚠",
            "══",
            "▸ TAQSIMLANGAN (DVCS) — Git (zamonaviy standart)",
            "   ✅ Har dasturchi to'liq repozitoriyaga ega (lokal klon)",
            "   ✅ Internet shart emas — lokal operatsiyalar sekunddan kam",
            "   ✅ Snapshot asosida saqlash — tezlik va xavfsizlik kafolati",
            "   ✅ Yengil tarmoqlanish — branch = 41 baytlik ko'rsatgich",
            "══",
            "📌 Git — dunyo dasturiy injeneriyasining DE FACTO standarti (2005-hozir)",
        ]
    }),

    ("content", {
        "title": "Diff Tahlil Algoritmlari — Mayers, Patience, Histogram",
        "num": 7,
        "bullets": [
            "▸ MAYERS ALGORITMI (1986) — Git standart algoritmi",
            "  Asosi: LCS (Longest Common Subsequence) — eng qisqa tahrirlash skripti",
            "══",
            "▸ PATIENCE DIFF — noyob qatorlarga tayanadi",
            "  Rename, refaktoring operatsiyalarida aniqroq natija beradi",
            "══",
            "▸ HISTOGRAM DIFF — chastota asosida optimallashtirish",
            "  Katta loyihalarda eng yuqori tezlik ko'rsatadi",
            "══",
            "▸ Unified Diff format: qo'shilgan (+), o'chirilgan (-), o'zgarmagan",
            "▸ jsdiff kutubxonasi — Mayers + JSON parsing (loyihamizda ishlatildi)",
            "══",
            "⚠ Asosiy muammo: Barcha algoritmlar faqat SINTAKTIK tahlil qiladi",
            "   Mantiqiy ma'no, xavfsizlik ta'siri — AI tahlilisiz aniqlab bo'lmaydi!",
        ]
    }),

    ("content", {
        "title": "Google Gemini LLM Integratsiyasi — Nima uchun?",
        "num": 8,
        "bullets": [
            "▸ Gemini 2.5 Flash modeli tanlangan — asosiy sabablar:",
            "══",
            "✅ 1 MILLION TOKEN kontekst oynasi",
            "   → Butun loyiha diff matni bitta so'rovda tahlil qilinadi",
            "   → Fragment-fragment yuborish kerak emas — to'liq tahlil",
            "══",
            "✅ O'ZBEK TILI semantikasini mukammal tushunadi",
            "   → Texnik terminologiyani to'g'ri tarjima va izohlash",
            "══",
            "✅ Streaming JSON response — past kechikish, yuqori tezlik",
            "══",
            "▸ PROMPT ENGINEERING — 3 qatlamli tuzilma:",
            "  1) System Prompt — mutaxassis roli va o'zbek tili talabi",
            "  2) Context Injection — diff matni + loyiha metama'lumoti",
            "  3) Output Format — Markdown: sarlavhalar + ro'yxatlar + kod",
            "══",
            "📌 Hallucination muammosi: Faqat berilgan diff asosida fikr yuritish talabi",
        ]
    }),

    ("section", {
        "num": "II", "title": "BOB: ARXITEKTURA VA LOYIHALASH",
        "items": [
            "2.1 — Funksional talablar, 5 ta asosiy modul va mantiqiy model",
            "2.2 — Router-Controller andozasida backend arxitekturasi",
            "2.3 — Frontend-Backend integratsiyasi va axborot oqimlari",
        ]
    }),

    ("content", {
        "title": "Tizimning 5 Ta Asosiy Moduli (Mantiqiy Model)",
        "num": 10,
        "bullets": [
            "1️⃣  HOME — URL kiritish, regex validatsiya, progressiv yuklanish animatsiyasi",
            "══",
            "2️⃣  COMMITS — Commitlar tarixi, qidiruv (xabar/muallif/ID bo'yicha)",
            "   Statistika kartochkalari: jami commit, qatorlar, mualliflar soni",
            "══",
            "3️⃣  DIFF VIEWER — Qatorlar darajasida vizualizatsiya",
            "   Yashil = qo'shilgan (+)  |  Qizil = o'chirilgan (-)  |  Chap: fayllar paneli",
            "══",
            "4️⃣  AI ANALYSIS — Google Gemini semantik hisoboti (o'zbek tilida)",
            "   Sintaktik o'zgarishlar + Biznes/Xavfsizlik mantiqi + Auto-fix tavsiyalar",
            "══",
            "5️⃣  DASHBOARD — Loyiha analitikasi",
            "   Top fayllar grafigi + Dasturchilar reytingi (Leaderboard)",
            "══",
            "📌 SPA arxitektura: Sahifalar almashinishida brauzer QAYTA YUKLANMAYDI",
            "   history.pushState orqali URL yo'llari dinamik aks ettiriladi",
        ]
    }),

    ("image", {
        "title": "Tizimning Kirish Qismi — Home Page",
        "num": 11,
        "img": "image1.jpg",
        "items": [
            "GitHub/GitLab URL manzilini qabul qiladi",
            "Regex validatsiya va xavfsizlik tekshiruvi",
            "Progressiv yuklanish animatsiyasi",
            "Tayyor ommabop repozitoriyalar ro'yxati",
            "Dark Mode + Neon effektli zamonaviy dizayn",
        ]
    }),

    ("image", {
        "title": "Commitlar Tarixi — Repository Explorer",
        "num": 12,
        "img": "image2.jpg",
        "items": [
            "Backend klonlashdan so'ng avtomatik o'tish",
            "Commit xabar, muallif, sana bo'yicha qidiruv",
            "Real vaqtda 4 ta statistik kartochka",
            "Commit tanlanganda — Diff sahifasiga o'tish",
            "Sorting va filtering imkoniyatlari",
        ]
    }),

    ("content", {
        "title": "Router-Controller Andozasi — Backend Arxitekturasi",
        "num": 13,
        "bullets": [
            "▸ ROUTER QATLAMI (routes/) — faqat endpoint va HTTP metodlar:",
            "   gitRoutes.js → /api/git/clone, /api/git/commits, /api/git/diff",
            "   aiRoutes.js  → /api/ai/analyze",
            "══",
            "▸ CONTROLLER QATLAMI (controllers/) — biznes mantiq:",
            "   gitController.js → clone, log, diff, parse operatsiyalari",
            "   aiController.js  → Gemini API chaqiruvi, Prompt injection",
            "══",
            "✅ AFZALLIK: Loose Coupling — komponentlar mustaqil",
            "   Gemini o'rniga boshqa LLM qo'shish = FAQAT 1 fayl o'zgartirish!",
            "══",
            "▸ Global Error Handling Middleware — try/catch barcha controllerlarda",
            "   HTTP 400 (noto'g'ri so'rov), 404 (topilmadi), 500 (server xatosi)",
            "══",
            "📌 Non-blocking I/O: sekundiga 50+ asinxron so'rov parallel qayta ishlash",
        ]
    }),

    ("image", {
        "title": "Axborot Oqimlari — Mantiqiy Blok-sxema",
        "num": 14,
        "img": "image3.jpg",
        "items": [
            "React → Express.js → Git/AI yadrolari",
            "Parallel asinxron qayta ishlash",
            "JSON Response → React State",
            "SPA: sahifa qayta yuklanmaydi",
            "Global xatolik boshqaruvi",
        ]
    }),

    ("image", {
        "title": "Diff Tahlil Oynasi — Kod Vizualizatsiyasi",
        "num": 15,
        "img": "image4.jpg",
        "items": [
            "Commit ichidagi fayl o'zgarishlari",
            "Yashil satir: qo'shilgan (+)",
            "Qizil satir: o'chirilgan (-)",
            "Chap panel: fayllar ro'yxati",
            "O'ng: diff viewer oynasi",
            "'AI izohi' tugmasi — Gemini tahlili",
        ]
    }),

    ("content", {
        "title": "Frontend-Backend Integratsiyasi",
        "num": 16,
        "bullets": [
            "▸ RESTful API arxitekturasi — HTTP/JSON protokoli",
            "   React → Axios asinxron so'rov → Express.js backend",
            "══",
            "▸ CORS xavfsizlik sozlamasi:",
            "   Faqat ruxsat etilgan domenlardan so'rovlarni qabul qilish",
            "   Kross-sayt so'rov qalbakishtirish (CSRF) oldini olish",
            "══",
            "▸ 3 qatlamli axborot oqimi:",
            "   1) React: so'rov yuborish + yuklanish animatsiyasi",
            "   2) Express: marshrutlash → Controller → Git/AI yadro",
            "   3) JSON javob → React state yangilanish → DOM qayta chizish",
            "══",
            "▸ Global holat boshqaruvi (State Management):",
            "   App.jsx markaziy useState — 5 sahifaga prop drilling",
            "══",
            "✅ Kesh mexanizmi: klonlangan repolar lokal diskda saqlanadi",
            "   Qayta so'rovda internet sarflanmaydi — tezlik oshadi",
        ]
    }),

    ("section", {
        "num": "III", "title": "BOB: AMALIY REALIZATSIYA",
        "items": [
            "3.1 — Node.js/Express.js backend: klonlash va diff tahlil funksionalligi",
            "3.2 — React SPA frontend: sahifalararo ma'lumotlar zanjiri",
            "3.3 — Real repozitoriyalarda sinov va AI hisobot natijalari tahlili",
        ]
    }),

    ("content", {
        "title": "Backend Texnik Stack — Node.js/Express.js",
        "num": 18,
        "bullets": [
            "▸ Node.js — asinxron non-blocking I/O muhiti",
            "   EventLoop: server yadrosini bloklamasdan parallel so'rovlar",
            "══",
            "▸ Express.js — Router-Controller andoza",
            "▸ simple-git — Git operatsiyalari: clone, log, diff, pull",
            "▸ jsdiff — Mayers diff algoritmi, JSON parsing",
            "▸ @google/generative-ai — Gemini SDK",
            "▸ dotenv — API kalitlar muhit o'zgaruvchilari (xavfsizlik)",
            "▸ cors — Cross-Origin xavfsizlik protokoli",
            "══",
            "✅ Kesh mexanizmi: Klonlangan repolar lokal saqlanadi",
            "   Qayta yuklab o'tirmasdan tezroq javob berish",
            "══",
            "✅ Xatolik boshqaruvi: try/catch + Global Middleware",
            "   HTTP 400/404/500 + O'zbek tilida xabar",
        ]
    }),

    ("content", {
        "title": "Frontend Texnik Stack — React SPA",
        "num": 19,
        "bullets": [
            "▸ React 18 — komponentli SPA arxitektura",
            "   Virtual DOM: faqat o'zgargan komponent qayta chiziladi",
            "══",
            "▸ useState + useEffect — holat boshqaruvi",
            "   App.jsx — markaziy xotira, 5 sahifaga prop drilling",
            "══",
            "▸ Axios — HTTP interceptors, asinxron so'rovlar",
            "   Global baseURL, so'rov/javob interceptorlari",
            "══",
            "▸ ReactMarkdown — AI hisobotini render qilish",
            "   Markdown → chiroyli formatlangan tahlil matni",
            "══",
            "▸ CSS Dark Mode — Neon effektlar, animatsiyalar",
            "   history.pushState — URL yo'llari dinamik yangilanadi",
            "══",
            "📌 Loading states: spinner va progress-bar animatsiyalari",
            "   Double-submit xatolarining oldini olish",
        ]
    }),

    ("image", {
        "title": "AI Semantik Hisobot — Google Gemini Natijasi",
        "num": 20,
        "img": "image5.jpg",
        "items": [
            "O'zbek tilida professional tahlil",
            "Sintaktik o'zgarishlar tavsifi",
            "Xavfsizlik va mantiq tahlili",
            "Auto-fix tayyor kod namunalari",
            "Markdown formatida render",
        ]
    }),

    ("image", {
        "title": "Dashboard — Loyiha Analitikasi",
        "num": 21,
        "img": "image6.jpg",
        "items": [
            "Eng ko'p o'zgargan top fayllar",
            "Progress-bar animatsiyali grafik",
            "Dasturchilar faolligi reytingi",
            "Umumiy statistika kartochkalari",
            "Real vaqtda hisoblash",
        ]
    }),

    ("content", {
        "title": "Sinov Natijalari — Real Repozitoriyalarda",
        "num": 22,
        "bullets": [
            "▸ Real GitHub repozitoriyalari ustida sinov o'tkazildi",
            "   JavaScript ekotizimida yozilgan murakkab loyihalar",
            "══",
            "✅ Barcha 5 modul muvaffaqiyatli ishladi",
            "✅ AI o'zbek tilida professional semantik hisobot berdi",
            "✅ Kiberxavfsizlik kamchiliklari avtomatik aniqlandi",
            "✅ Auto-fix tavsiyalari bilan tayyor kod namunalari berildi",
            "══",
            "📌 ASOSIY NATIJALAR:",
            "  ✅ Code Review vaqti 40-50% qisqardi",
            "  ✅ Mantiqiy xatolarni aniqlash aniqligi sezilarli oshdi",
            "  ✅ AI modeli hallucination kamaytirildi (qat'iy diff-based prompt)",
            "══",
            "▸ Dashboard: commitlar, qatorlar, mualliflar statistikasi real vaqtda",
        ]
    }),

    ("content", {
        "title": "Ilmiy Yangilik va Amaliy Ahamiyat",
        "num": 23,
        "bullets": [
            "▸ ILMIY YANGILIK:",
            "   Kod o'zgarishlarini LLM yordamida o'zbek tilida semantik tahlil qilishning",
            "   integratsiyalashgan mantiqiy-arxitekturaviy modeli BIRINCHI MARTA ishlab chiqildi",
            "══",
            "▸ AMALIY AHAMIYAT:",
            "  ✅ IT kompaniyalar uchun Code Review avtomatizatsiyasi",
            "  ✅ Loyiha audit va monitoring tizimi — real vaqt",
            "  ✅ Jamoa faolligini kuzatish (Dashboard + Leaderboard)",
            "  ✅ Dasturiy xavfsizlikni ta'minlash vositasi",
            "══",
            "▸ Nofunksional talablar bajarildi:",
            "   Ishlash tezligi: oddiy API so'rovlar < 200ms",
            "   Ishonchlilik: Global Error Handling + Retry mexanizmi",
            "   Xavfsizlik: Regex validatsiya + CORS + dotenv API kalit",
        ]
    }),

    ("content", {
        "title": "Xulosa",
        "num": 24,
        "bullets": [
            "1️⃣  An'anaviy diff vositalari sintaktik darajada qoladi",
            "    Semantik tahlil uchun AI integratsiya ZARUR ekanligi isbotlandi",
            "══",
            "2️⃣  Router-Controller + React SPA arxitekturasi",
            "    Barqarorlik, tezkorlik va modullilikni ta'minladi",
            "══",
            "3️⃣  Gemini 2.5 Flash: o'zbek tilida professional semantik hisobot",
            "    Prompt Engineering 3 qatlamli tuzilmasi muvaffaqiyatli ishladi",
            "══",
            "4️⃣  Real sinov natijasi:",
            "    Code Review vaqti 40-50% qisqardi",
            "    Kiberxavfsizlik muammolari avtomatik aniqlanadi",
            "══",
            "📌 Ishlab chiqilgan SPA veb-platforma IT kompaniyalar uchun",
            "   tayyor amaliy dasturiy mahsulot sifatida foydalanishga tayyor!",
        ]
    }),

    ("content", {
        "title": "Takliflar va Kelajak Istiqbollari",
        "num": 25,
        "bullets": [
            "🔷 CI/CD Integratsiya (GitHub Actions plugin)",
            "   Har commit da — avtomatik AI tahlil, dasturchiga ogohlantirish",
            "══",
            "🔷 Lokal LLM modeli (Llama-3, CodeLlama, DeepSeek-Coder)",
            "   Ma'lumotlar maxfiyligi — GDPR muvofiqlik, korporativ tarmoq",
            "══",
            "🔷 Shaxsiylashtirilgan Prompt Sozlash Paneli",
            "   Kompaniya ichki standartlariga moslashtirilgan tahlil",
            "══",
            "🔷 Interaktiv Vizualizatsiya",
            "   Fayllararo bog'liqlik grafigi, arxitektura diagrammasi",
            "══",
            "🔷 Ko'p tillik qo'llab-quvvatlash",
            "   Rus, ingliz, qozoq tillarida semantik hisobotlar",
            "══",
            "🔷 Korporativ Dashboard — Jamoa samaradorligi va audit tizimi",
        ]
    }),

    ("final", {}),
]


# ═══════════════════════════════════════════════════════════════════════════
# PPTX FAYL GENERATSIYA QILISH
# ═══════════════════════════════════════════════════════════════════════════

def generate():
    out = Path("pptx_build")
    shutil.rmtree(out, ignore_errors=True)

    slides_dir = out / "ppt" / "slides"
    rels_dir   = out / "ppt" / "slides" / "_rels"
    media_dir  = out / "ppt" / "media"
    (out / "ppt").mkdir(parents=True)
    slides_dir.mkdir(parents=True)
    rels_dir.mkdir(parents=True)
    media_dir.mkdir(parents=True)
    (out / "_rels").mkdir()
    (out / "ppt" / "_rels").mkdir()
    (out / "docProps").mkdir()
    (out / "ppt" / "slideLayouts").mkdir()
    (out / "ppt" / "slideLayouts" / "_rels").mkdir()
    (out / "ppt" / "slideMasters").mkdir()
    (out / "ppt" / "slideMasters" / "_rels").mkdir()

    # Rasmlarni media papkaga nusxalash
    img_map = {}  # img_filename -> (rId_str, media_name)
    img_counter = 1
    img_files = {
        "image1.jpg":"image1.jpg",
        "image2.jpg":"image2.jpg",
        "image3.jpg":"image3.jpg",
        "image4.jpg":"image4.jpg",
        "image5.jpg":"image5.jpg",
        "image6.jpg":"image6.jpg",
    }
    for orig, dest in img_files.items():
        src = Path("images") / orig
        if src.exists():
            shutil.copy(src, media_dir / dest)
            img_map[orig] = (f"rId{img_counter+5}", dest)
            img_counter += 1

    # Har bir slayd uchun shapes HTML yaratish
    slide_shapes = []
    for sdata in SLIDES:
        stype, params = sdata[0], sdata[1]
        if stype == "title":
            shapes = make_title_slide()
        elif stype == "section":
            shapes = make_section_slide(params["num"], params["title"], params["items"])
        elif stype == "content":
            shapes = make_content_slide(params["title"], params["bullets"], params["num"])
        elif stype == "image":
            img_name = params["img"]
            if img_name in img_map:
                rId, _ = img_map[img_name]
            else:
                rId = None
            if rId:
                shapes = make_image_slide(
                    params["title"], rId,
                    0.8, 3.0, 20.5, 14.5,
                    params["items"], params["num"])
            else:
                shapes = make_content_slide(params["title"], params["items"], params["num"])
        elif stype == "final":
            shapes = make_final_slide()
        else:
            shapes = make_content_slide("Slayd", [], 0)
        slide_shapes.append((stype, shapes, params))

    # Slayd XML fayllarini yozish
    for i, (stype, shapes, params) in enumerate(slide_shapes):
        xml = slide_xml(shapes)
        with open(slides_dir / f"slide{i+1}.xml", "w", encoding="utf-8") as f:
            f.write(xml)

    # Har bir slayd uchun .rels fayl
    for i, (stype, shapes, params) in enumerate(slide_shapes):
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n')
        # Agar rasm slayd bo'lsa
        if stype == "image" and "img" in params:
            img_name = params["img"]
            if img_name in img_map:
                rId, dest = img_map[img_name]
                rels += f'  <Relationship Id="{rId}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{dest}"/>\n'
        rels += "</Relationships>"
        with open(rels_dir / f"slide{i+1}.xml.rels", "w", encoding="utf-8") as f:
            f.write(rels)

    n = len(SLIDES)

    # slideLayout
    layout_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             type="blank" preserve="1">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
    <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClr/></p:clrMapOvr>
</p:sldLayout>'''
    with open(out / "ppt" / "slideLayouts" / "slideLayout1.xml", "w") as f:
        f.write(layout_xml)
    layout_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''
    with open(out / "ppt" / "slideLayouts" / "_rels" / "slideLayout1.xml.rels", "w") as f:
        f.write(layout_rels)

    # slideMaster
    master_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
    <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2"
            accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6"
            hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle><a:lstStyle/></p:titleStyle>
    <p:bodyStyle><a:lstStyle/></p:bodyStyle>
    <p:otherStyle><a:lstStyle/></p:otherStyle>
  </p:txStyles>
</p:sldMaster>'''
    with open(out / "ppt" / "slideMasters" / "slideMaster1.xml", "w") as f:
        f.write(master_xml)
    master_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''
    with open(out / "ppt" / "slideMasters" / "_rels" / "slideMaster1.xml.rels", "w") as f:
        f.write(master_rels)

    # presentation.xml
    slide_ids = "\n".join(
        f'    <p:sldId id="{256+i}" r:id="rId{i}"/>'
        for i in range(1, n+1)
    )
    prs_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                saveSubsetFonts="1">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId{n+1}"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
{slide_ids}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen4x3"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>'''
    with open(out / "ppt" / "presentation.xml", "w") as f:
        f.write(prs_xml)

    # ppt/_rels/presentation.xml.rels
    prs_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    for i in range(1, n+1):
        prs_rels += f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n'
    prs_rels += f'  <Relationship Id="rId{n+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>\n'
    prs_rels += "</Relationships>"
    with open(out / "ppt" / "_rels" / "presentation.xml.rels", "w") as f:
        f.write(prs_rels)

    # _rels/.rels
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>'''
    with open(out / "_rels" / ".rels", "w") as f:
        f.write(root_rels)

    # docProps/core.xml
    core_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Dasturiy versiyalar tahlil tizimi - Diplom Himoya Prezentatsiyasi</dc:title>
  <dc:creator>Amonov Sohibjon</dc:creator>
  <dc:subject>Bitiruv Malakaviy Ishi - TATU Samarqand filiali 2026</dc:subject>
</cp:coreProperties>'''
    with open(out / "docProps" / "core.xml", "w") as f:
        f.write(core_xml)

    # [Content_Types].xml
    ct = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
'''
    for i in range(1, n+1):
        ct += f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
    ct += '  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>\n'
    ct += "</Types>"
    with open(out / "[Content_Types].xml", "w") as f:
        f.write(ct)

    # ZIP ga yig'ish
    output_file = "Amonov_Diplom_Prezentatsiya.pptx"
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in out.rglob("*"):
            if fpath.is_file():
                zf.write(fpath, str(fpath.relative_to(out)))

    shutil.rmtree(out)
    size = os.path.getsize(output_file)
    print(f"✅ YARATILDI: {output_file}")
    print(f"📊 Hajm: {size/1024:.1f} KB")
    print(f"📑 Slaydlar: {n} ta")
    print(f"🖼  Rasmlar: {len(img_map)} ta")

if __name__ == "__main__":
    generate()
