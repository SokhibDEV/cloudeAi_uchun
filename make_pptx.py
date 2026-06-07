#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional PPTX Generator - To'liq qayta yozilgan versiya
Rasmlar to'g'ri joyda, matnlar to'liq va mantiqiy
"""
import zipfile, os, shutil
from pathlib import Path

# ── RANGLAR ──────────────────────────────────────────────────────
DARK   = "0D1B2A"
DARK2  = "0F2547"
CYAN   = "00C6FF"
PURP   = "7B2FBE"
WHITE  = "FFFFFF"
LGRAY  = "B0C4DE"
GOLD   = "FFD700"
GREEN  = "00E676"
RED    = "FF5252"
YELLOW = "FFD740"

def emu(cm):   return int(cm * 360000)
def hpt(pt):   return int(pt * 100)
def esc(t):
    return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def run(text, sz=14, bold=False, color=WHITE, italic=False):
    b = ' b="1"' if bold else ''
    i = ' i="1"' if italic else ''
    return (f'<a:r><a:rPr lang="uz-UZ" altLang="en-US" sz="{hpt(sz)}"{b}{i} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="Calibri"/></a:rPr><a:t>{esc(text)}</a:t></a:r>')

def para(runs_xml, align="l", spc=0):
    al = {"l":"", "c":' algn="ctr"', "r":' algn="r"'}.get(align,"")
    sp = f'<a:spcBef><a:spcPts val="{spc}"/></a:spcBef>' if spc else ''
    return f'<a:p><a:pPr{al}>{sp}</a:pPr>{runs_xml}</a:p>'

def tbox(x,y,w,h, paras_xml, anchor="t"):
    return f'''<p:sp>
    <p:nvSpPr><p:cNvPr id="1" name="tb"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
    <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
    <p:txBody><a:bodyPr wrap="square" anchor="{anchor}" lIns="91440" rIns="91440" tIns="45720" bIns="45720"/>
    <a:lstStyle/>{paras_xml}</p:txBody></p:sp>'''

def rect(x,y,w,h, fill, alpha=None):
    if alpha:
        fx = f'<a:solidFill><a:srgbClr val="{fill}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>'
    else:
        fx = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    return f'''<p:sp>
    <p:nvSpPr><p:cNvPr id="2" name="r"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>
    <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fx}<a:ln><a:noFill/></a:ln></p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'''

def img(rId, x,y,w,h):
    return f'''<p:pic>
    <p:nvPicPr><p:cNvPr id="10" name="img"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
    <p:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
    <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'''

def sxml(shapes):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
    <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {shapes}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClr/></p:clrMapOvr></p:sld>'''

# ═══════════════════════════════════════════
# SLAYD SHABLONLARI
# ═══════════════════════════════════════════

def title_slide():
    s = ""
    s += rect(0,0,33.87,19.05, DARK)
    s += rect(0,0,33.87,0.7, PURP)
    s += rect(0,18.35,33.87,0.7, CYAN)
    s += rect(1.5,2.0,30.87,14.5, DARK2, alpha=70000)
    s += rect(1.5,2.0,30.87,0.1, CYAN)
    # Universitet
    s += tbox(2,0.1,30,1.5, para(run("O'ZBEKISTON RESPUBLIKASI | TATU SAMARQAND FILIALI | 2026",11,False,CYAN,True),"c"))
    # BMI belgisi
    s += tbox(2,2.4,30,1.1, para(run("⚡  BITIRUV MALAKAVIY ISHI  ⚡",13,False,GOLD),"c"))
    # Sarlavha
    s += tbox(2,3.7,30,3.5,
        para(run("Dasturiy versiyalar orasidagi",22,True,WHITE),"c") +
        para(run("o'zgarishlarni tahlil qiluvchi",22,True,WHITE),"c") +
        para(run("dasturiy tizimni loyihalashtirish",22,True,WHITE),"c"))
    s += rect(5,7.7,24,0.08,CYAN)
    # Ma'lumotlar
    s += tbox(2,8.1,30,6.5,
        para(run("Bitiruvchi:",13,True,CYAN)+run("  Amonov Sohibjon",13,False,WHITE),"c",80) +
        para(run("Ilmiy rahbar:",13,True,CYAN)+run("  Yusupov O.",13,False,WHITE),"c",80) +
        para(run("Kafedra:",13,True,CYAN)+run("  Dasturiy injiniring",13,False,WHITE),"c",80) +
        para(run(""),"c",80) +
        para(run("React  •  Node.js  •  Express.js  •  Google Gemini AI  •  Git",11,False,LGRAY,True),"c",80))
    return s

def section_slide(num, title, items):
    s = ""
    s += rect(0,0,33.87,19.05, DARK)
    s += rect(0,0,33.87,0.6, PURP)
    s += rect(0,18.45,33.87,0.6, CYAN)
    s += rect(1.5,3.5,5,5.5, DARK2, alpha=80000)
    s += tbox(1.5,3.5,5,5.5, para(run(str(num),58,True,CYAN),"c"))
    s += rect(7,4,24,4.5, DARK2, alpha=50000)
    s += rect(7,4,24,0.1, CYAN)
    words = title.split()
    mid = len(words)//2
    s += tbox(7.3,4.5,23.4,3.5,
        para(run(" ".join(words[:mid]),22,True,WHITE),"l") +
        para(run(" ".join(words[mid:]),22,True,WHITE),"l"))
    s += rect(1.5,10,31,8, DARK2, alpha=40000)
    items_xml = ""
    for item in items:
        items_xml += para(run("  ▸  ",12,False,CYAN)+run(item,12,False,LGRAY),"l",60)
    s += tbox(2,10.5,30,7.5, items_xml)
    return s

def content_slide(title, bullets, snum):
    s = ""
    s += rect(0,0,33.87,19.05, DARK2)
    s += rect(0,0,33.87,2.8, "0a1628")
    s += rect(0,2.7,33.87,0.12, CYAN)
    s += rect(0.5,0.4,0.3,1.9, CYAN)
    s += tbox(1.2,0.3,31,2.2, para(run(title,21,True,WHITE),"l"))
    s += tbox(31.5,17.8,2,1, para(run(str(snum),11,False,CYAN),"r"))
    cxml = ""
    for b in bullets:
        if b.startswith("══") or b.startswith("──"):
            cxml += para(run(""),"l",20)
            continue
        cl = WHITE; sz = 13; bold = False
        if b.startswith("📌") or b.startswith("✅") or b.startswith("🔷"):
            cl = GREEN; bold = True
        elif b.startswith("⚠") or b.startswith("❌"):
            cl = RED
        elif b.startswith("  ") or b.startswith("   "):
            cl = LGRAY; sz = 12
        elif b.startswith("▸") or b.startswith("•"):
            cl = CYAN; bold = True
        cxml += para(run(b,sz,bold,cl),"l",40)
    s += tbox(0.8,3.0,32.5,15.5, cxml)
    return s

def img_right_slide(title, rId, bullets, snum):
    """Rasm chap, matn o'ng"""
    s = ""
    s += rect(0,0,33.87,19.05, DARK2)
    s += rect(0,0,33.87,2.8, "0a1628")
    s += rect(0,2.7,33.87,0.12, CYAN)
    s += rect(0.5,0.4,0.3,1.9, CYAN)
    s += tbox(1.2,0.3,31,2.2, para(run(title,21,True,WHITE),"l"))
    s += tbox(31.5,17.8,2,1, para(run(str(snum),11,False,CYAN),"r"))
    # Rasm chap taraf
    s += img(rId, 0.5, 2.9, 22, 14.5)
    # Ramka
    t = 0.06
    s += rect(0.5-t, 2.9-t, 22+2*t, t, CYAN)
    s += rect(0.5-t, 2.9+14.5, 22+2*t, t, CYAN)
    s += rect(0.5-t, 2.9-t, t, 14.5+2*t, CYAN)
    s += rect(0.5+22, 2.9-t, t, 14.5+2*t, CYAN)
    # O'ng matn paneli
    s += rect(23.2,2.9,10.3,14.5, "0a1628", alpha=90000)
    s += rect(23.2,2.9,0.1,14.5, CYAN)
    bxml = ""
    for b in bullets:
        if b.startswith("══"):
            bxml += para(run(""),"l",40)
            continue
        cl = LGRAY; sz = 12; bold = False
        if b.startswith("✅") or b.startswith("📌"):
            cl = GREEN; bold = True
        elif b.startswith("▸"):
            cl = CYAN
        bxml += para(run(" "+b,sz,bold,cl),"l",100)
    s += tbox(23.5,3.2,9.8,13.8, bxml)
    return s

def img_full_slide(title, rId, caption, snum):
    """Rasm katta, pastda izoh"""
    s = ""
    s += rect(0,0,33.87,19.05, DARK2)
    s += rect(0,0,33.87,2.8, "0a1628")
    s += rect(0,2.7,33.87,0.12, CYAN)
    s += rect(0.5,0.4,0.3,1.9, CYAN)
    s += tbox(1.2,0.3,31,2.2, para(run(title,21,True,WHITE),"l"))
    s += tbox(31.5,17.8,2,1, para(run(str(snum),11,False,CYAN),"r"))
    # Rasm to'liq
    s += img(rId, 1.0, 2.9, 31.87, 13.5)
    # Ramka
    s += rect(1.0,2.9,31.87,0.06,CYAN)
    s += rect(1.0,16.4,31.87,0.06,CYAN)
    # Pastki izoh
    s += rect(1.0,16.5,31.87,2.0, "0a1628", alpha=90000)
    bxml = ""
    for c in caption:
        bxml += para(run("  ▸  ",11,False,CYAN)+run(c,11,False,LGRAY),"l",30)
    s += tbox(1.5,16.5,31,2.0, bxml)
    return s

def final_slide():
    s = ""
    s += rect(0,0,33.87,19.05, DARK)
    s += rect(0,0,33.87,0.6, CYAN)
    s += rect(0,18.45,33.87,0.6, CYAN)
    s += rect(3,2.5,27.87,14, DARK2)
    s += rect(3,2.5,27.87,0.12, PURP)
    s += rect(3,16.38,27.87,0.12, PURP)
    s += tbox(3,3.0,27.87,2.5,
        para(run("🎓  E'tiboringiz uchun",26,True,CYAN),"c") +
        para(run("RAHMAT!",34,True,WHITE),"c"))
    s += rect(7,6.2,20,0.1,CYAN)
    s += tbox(3,6.7,27.87,9,
        para(run("Dasturiy versiyalar tahlil tizimi (SPA veb-platforma)",14,False,LGRAY,True),"c",120) +
        para(run("─────────────────────────────────────",10,False,PURP),"c",60) +
        para(run("Bitiruvchi:  Amonov Sohibjon",14,False,WHITE),"c",130) +
        para(run("Ilmiy rahbar:  Yusupov O.",14,False,WHITE),"c",110) +
        para(run("TATU Samarqand filiali  —  2026",13,False,LGRAY),"c",110) +
        para(run("─────────────────────────────────────",10,False,PURP),"c",60) +
        para(run("React  •  Node.js  •  Express.js  •  Google Gemini AI",12,False,CYAN,True),"c",130) +
        para(run(""),"c",130) +
        para(run("💬  Savollar uchun tayyorman!",16,True,GREEN),"c",100))
    return s

# ═══════════════════════════════════════════
# BARCHA SLAYDLAR
# ═══════════════════════════════════════════
# Rasmlar:
# image1 = Home Page
# image2 = Commits sahifasi
# image3 = Blok-sxema (axborot oqimi)
# image4 = Diff Viewer
# image5 = AI Analiz hisoboti
# image6 = Dashboard

SLIDES = [
    # (tur, params)
    ("title", {}),

    ("section", {"num":"📋","title":"MUNDARIJA",
     "items":[
        "1. Kirish — Mavzuning dolzarbligi",
        "2. I Bob — Versiyalarni boshqarish: nazariy asoslar",
        "3. II Bob — Arxitektura va dasturiy tizimni loyihalashtirish",
        "4. III Bob — Amaliy realizatsiya va sinov natijalari",
        "5. Xulosa, takliflar va kelajak istiqbollari",
     ]}),

    ("content", {"num":3,"title":"Mavzuning Dolzarbligi",
     "bullets":[
        "▸ Zamonaviy dasturiy mahsulotlar o'ta murakkab, ko'p qatlamli arxitekturaga ega",
        "▸ Jamoaviy ishlashda minglab commit (o'zgarish) kiritiladi — nazorat zarur",
        "══",
        "⚠ Asosiy MUAMMO: An'anaviy Diff vositalari FAQAT sintaktik tahlil qiladi",
        "   • Qizil/yashil qatorlar — nima o'zgarganini KO'RSATADI",
        "   • Lekin NIMA UCHUN o'zgardi? — hech qachon tushuntirib BERMAYDI",
        "   • Kiberxavfsizlik xatarlari, mantiqiy muammolar aniqlanmaydi",
        "══",
        "✅ Yechim: LLM (Large Language Models) texnologiyasi",
        "▸ Google Gemini 2.5 Flash — o'zbek tilida semantik tahlil",
        "▸ React + Node.js + Express.js — zamonaviy SPA veb-platforma",
        "▸ Natija: Code Review vaqti 40-50% qisqaradi",
     ]}),

    ("content", {"num":4,"title":"Tadqiqot Maqsadi va Vazifalari",
     "bullets":[
        "📌 ASOSIY MAQSAD:",
        "   Versiyalar orasidagi o'zgarishlarni qatorlar darajasida aniqlash,",
        "   AI yordamida o'zbek tilida semantik tahlil qiluvchi SPA platforma yaratish",
        "══",
        "▸ Git va VCS nazariy asoslarini o'rganish",
        "▸ jsdiff kutubxonasi va LLM API integratsiyasini tadqiq etish",
        "▸ 5 oynali mantiqiy-funksional model ishlab chiqish",
        "▸ Router-Controller andozasida backend arxitekturasi yaratish",
        "▸ Prompt Engineering — 3 qatlamli model (o'zbek tilida)",
        "▸ React SPA — sahifalararo ma'lumotlar zanjiri amalga oshirish",
        "══",
        "📌 Tadqiqot predmeti: Diff algoritmlari + LLM semantik tahlil metodlari",
        "📌 Metodlar: OOD, Router-Controller, Prompt Engineering, Git oqimlari",
     ]}),

    ("section", {"num":"I","title":"BOB: VERSIYALARNI BOSHQARISH TIZIMLARINING NAZARIY ASOSLARI",
     "items":[
        "1.1 — VCS tarixi: Lokal, Markazlashtirilgan, Taqsimlangan tizimlar",
        "1.2 — Diff tahlil metodologiyasi: Mayers, Patience, Histogram algoritmlari",
        "1.3 — LLM texnologiyalarini dasturiy kod tahliliga integratsiya istiqbollari",
     ]}),

    ("content", {"num":6,"title":"Versiyalarni Boshqarish Tizimlari (VCS) Tarixiy Tahlili",
     "bullets":[
        "▸ LOKAL VCS — fayllar faqat shaxsiy kompyuterda",
        "   Kamchiligi: jamoaviy ishlash MUMKIN EMAS, server o'chsa tarix yo'qoladi",
        "══",
        "▸ MARKAZLASHTIRILGAN (CVCS) — SVN, CVS (bitta server)",
        "   ⚠ Server o'chsa — butun jamoa ishi to'xtaydi, tarix yo'qoladi",
        "══",
        "▸ TAQSIMLANGAN (DVCS) — Git (zamonaviy standart, 2005-hozir)",
        "   ✅ Har dasturchi to'liq repozitoriyani lokal klonlaydi",
        "   ✅ Internet shart emas — lokal operatsiyalar sekunddan kam",
        "   ✅ Snapshot asosida saqlash — tezlik va ishonchlilik kafolati",
        "   ✅ Branch = 41 baytlik ko'rsatgich — yengil va tezkor tarmoqlanish",
        "══",
        "📌 Git — dunyo dasturiy injeneriyasining DE FACTO standarti",
        "   Code Review jarayoni: Pull Request → jamoa tekshiruvi → merge",
        "   Muammo: Yirik loyihalarda qo'lda tekshirish inson resursini ko'p oladi",
     ]}),

    ("content", {"num":7,"title":"Diff Tahlil Algoritmlari — Ilmiy Tahlil",
     "bullets":[
        "▸ UNIFIED DIFF FORMATI — xalqaro standart:",
        "   (+) — qo'shilgan qatorlar  |  (-) — o'chirilgan qatorlar",
        "   @@ koordinatlar — qaysi satrdan boshlangani aniq ko'rsatiladi",
        "══",
        "▸ MAYERS ALGORITMI (Eugene Myers, 1986) — Git standart algoritmi",
        "   LCS (Longest Common Subsequence) asosida — eng qisqa tahrirlash skripti",
        "   Kamchiligi: bir xil kalit so'zlar bo'lsa chalg'ituvchi natija",
        "══",
        "▸ PATIENCE DIFF — noyob qatorlarga tayanadi",
        "   Rename, refaktoring operatsiyalarida aniqroq natija",
        "══",
        "▸ HISTOGRAM DIFF — chastota asosida optimallashtirish",
        "   Katta loyihalarda eng yuqori tezlik va aniqlik",
        "══",
        "📌 Loyihada: jsdiff kutubxonasi — Mayers algoritmi + JSON parsing",
        "   Asosiy muammo: Barchasi FAQAT sintaktik — mantiqiy ma'no yo'q!",
     ]}),

    ("content", {"num":8,"title":"Google Gemini LLM Integratsiyasi — Nima Uchun?",
     "bullets":[
        "▸ Transformer arxitekturasi + Self-Attention mexanizmi",
        "   Kod blokining UMUMIY kontekstini to'liq qamrab oladi",
        "   An'anaviy linter: faqat qoidalar → LLM: mantiqiy tahlil",
        "══",
        "✅ Gemini 2.5 Flash tanlanganligi sabablari:",
        "══",
        "📌 1 MILLION TOKEN kontekst oynasi",
        "   → Butun loyiha diff matni BITTA so'rovda tahlil qilinadi",
        "   → Fragment-fragment yuborish kerak emas — to'liq va izchil natija",
        "══",
        "📌 O'ZBEK TILI semantikasini mukammal tushunadi",
        "   → Texnik terminologiya + milliy til + professional uslub",
        "══",
        "▸ 3 QATLAMLI PROMPT ENGINEERING tuzilmasi:",
        "   1) System Prompt — mutaxassis roli + o'zbek tili talabi",
        "   2) Context Injection — diff matni + loyiha meta-ma'lumoti",
        "   3) Output Format — Markdown: sarlavha + ro'yxat + kod namunalari",
        "📌 Hallucination kamaytirish: FAQAT berilgan diff asosida fikr yuritish",
     ]}),

    ("section", {"num":"II","title":"BOB: ARXITEKTURA VA DASTURIY TIZIMNI LOYIHALASHTIRISH",
     "items":[
        "2.1 — Funksional talablar, 5 ta asosiy modul va mantiqiy model",
        "2.2 — Router-Controller andozasida backend arxitekturasi",
        "2.3 — Frontend-Backend integratsiyasi va axborot oqimlari",
     ]}),

    ("content", {"num":10,"title":"Tizimning 5 Ta Asosiy Moduli — Mantiqiy Model",
     "bullets":[
        "1️⃣  HOME — Kirish moduli",
        "   GitHub/GitLab URL qabul qilish, Regex validatsiya, yuklanish animatsiyasi",
        "══",
        "2️⃣  COMMITS — Repository Explorer",
        "   Commitlar tarixi, qidiruv (xabar/muallif/ID), 4 ta statistik kartochka",
        "   Commit tanlash → ma'lumot zanjiri orqali keyingi sahifaga uzatish",
        "══",
        "3️⃣  DIFF VIEWER — Kod Vizualizatsiya yadro",
        "   Yashil (+) = qo'shilgan  |  Qizil (-) = o'chirilgan  |  Chap: fayllar paneli",
        "══",
        "4️⃣  AI ANALYSIS — Gemini Semantik Hisoboti",
        "   O'zbek tilida: sintaktik tahlil + biznes/xavfsizlik mantiqi + Auto-fix",
        "══",
        "5️⃣  DASHBOARD — Loyiha Analitikasi",
        "   Top fayllar grafigi + Dasturchilar reytingi (Leaderboard)",
        "══",
        "📌 SPA arxitektura: Brauzer QAYTA YUKLANMAYDI — history.pushState",
        "   Nofunksional talablar: <200ms API javob, 50+ parallel so'rov, CORS himoya",
     ]}),

    # image1 = Home Page
    ("img_right", {"num":11,"title":"Home Page — Tizimning Kirish Moduli","img":"image1.jpg",
     "bullets":[
        "▸ GitHub/GitLab URL manzilini qabul qiladi",
        "══",
        "▸ Regex validatsiya:",
        "   URL formati va xavfsizlik tekshiruvi",
        "══",
        "▸ Progressiv loading animatsiyasi",
        "══",
        "▸ Tayyor ommabop repozitoriyalar ro'yxati",
        "══",
        "▸ Dark Mode dizayn",
        "   Neon effektli zamonaviy interfeys",
        "══",
        "▸ Backend bilan asinxron",
        "   so'rov-javob sikli",
     ]}),

    # image2 = Commits sahifasi
    ("img_right", {"num":12,"title":"Commits Sahifasi — Repository Explorer","img":"image2.jpg",
     "bullets":[
        "▸ Backend klonlashdan so'ng",
        "   avtomatik o'tish",
        "══",
        "▸ Real vaqt qidiruv:",
        "   xabar / muallif / commit ID",
        "══",
        "▸ 4 ta statistik kartochka:",
        "   commit soni, qatorlar,",
        "   mualliflar, o'zgargan fayllar",
        "══",
        "▸ Commit tanlash →",
        "   Diff sahifasiga yo'naltirish",
        "══",
        "▸ Sorting va filtering",
        "   imkoniyatlari",
     ]}),

    ("content", {"num":13,"title":"Router-Controller Andozasi — Backend Arxitekturasi",
     "bullets":[
        "▸ ROUTER QATLAMI (routes/) — faqat endpoint va HTTP metodlar:",
        "   gitRoutes.js → /api/git/clone, /api/git/commits, /api/git/diff",
        "   aiRoutes.js  → /api/ai/analyze",
        "══",
        "▸ CONTROLLER QATLAMI (controllers/) — biznes mantiq:",
        "   gitController.js → simple-git: clone, log, diff, parse",
        "   aiController.js  → Gemini SDK: prompt injection, semantik tahlil",
        "══",
        "✅ LOOSE COUPLING — komponentlar mustaqil",
        "   Gemini o'rniga boshqa LLM = FAQAT 1 fayl o'zgartirish!",
        "══",
        "▸ Global Error Handling Middleware:",
        "   try/catch barcha controllerlarda",
        "   HTTP 400/404/500 + O'zbek tilida xabar",
        "══",
        "📌 Non-blocking I/O: sekundiga 50+ asinxron so'rov parallel qayta ishlash",
        "   Kesh mexanizmi: klonlangan repolar lokal saqlanadi — tezlik oshadi",
     ]}),

    # image3 = Blok-sxema
    ("img_full", {"num":14,"title":"Axborot Oqimlari — Mantiqiy Blok-Sxema","img":"image3.jpg",
     "caption":[
        "React Frontend → Axios so'rov → Express Router → Controller → Git/AI yadrolar → JSON Response",
        "Parallel asinxron qayta ishlash  |  Har qatlam mustaqil  |  SPA: brauzer qayta yuklanmaydi",
     ]}),

    # image4 = Diff Viewer
    ("img_right", {"num":15,"title":"Diff Viewer — Kod O'zgarishlarini Vizualizatsiya","img":"image4.jpg",
     "bullets":[
        "▸ Commit tanlanganda",
        "   backend bilan asinxron bog'lanish",
        "══",
        "▸ YASHIL satir (+):",
        "   qo'shilgan kod qatorlari",
        "══",
        "▸ QIZIL satir (-):",
        "   o'chirilgan kod qatorlari",
        "══",
        "▸ Chap panel:",
        "   o'zgargan fayllar ro'yxati",
        "══",
        "▸ O'ng panel: diff viewer",
        "══",
        "▸ 'AI izohi' tugmasi →",
        "   Gemini tahlilini boshlash",
     ]}),

    ("content", {"num":16,"title":"Frontend-Backend Integratsiyasi — RESTful Arxitektura",
     "bullets":[
        "▸ RESTful API arxitekturasi — HTTP/JSON protokoli",
        "   React → Axios asinxron so'rov → Express.js backend → JSON javob",
        "══",
        "▸ CORS xavfsizlik sozlamasi:",
        "   Faqat ruxsat etilgan domenlardan so'rovlarni qabul qilish",
        "   CSRF hujumlarining oldini olish — birinchi himoya qatlami",
        "══",
        "▸ 3 qatlamli axborot oqimi:",
        "   1) React: so'rov + yuklanish animatsiyasi",
        "   2) Express: marshrutlash → Controller → Git/AI yadro",
        "   3) JSON javob → React state → DOM qayta chizish",
        "══",
        "▸ Global holat boshqaruvi (State Management):",
        "   App.jsx markaziy useState — 5 sahifaga prop drilling",
        "══",
        "✅ Kesh mexanizmi: klonlangan repolar lokal — qayta so'rovda internet yo'q",
        "📌 API kalitlar: dotenv — GitHub'ga tasodifan tushib qolmaslik kafolati",
     ]}),

    ("section", {"num":"III","title":"BOB: AMALIY REALIZATSIYA VA SINOV NATIJALARI",
     "items":[
        "3.1 — Node.js/Express.js backend: klonlash va diff tahlil funksionalligi",
        "3.2 — React SPA frontend: 5 sahifali ma'lumotlar zanjiri",
        "3.3 — Real repozitoriyalarda sinov va AI semantik hisobotlar tahlili",
     ]}),

    ("content", {"num":18,"title":"Backend Texnik Stack — Node.js/Express.js",
     "bullets":[
        "▸ Node.js — asinxron non-blocking I/O muhiti",
        "   EventLoop: server yadrosini bloklamasdan parallel so'rovlar qayta ishlash",
        "══",
        "▸ Express.js — Router-Controller andoza",
        "▸ simple-git — Git operatsiyalari: clone, log, diff, pull",
        "   URL sanitizatsiya → unikal klonlash jildi → diff generatsiya",
        "▸ jsdiff — Mayers diff algoritmi, structured JSON parsing",
        "▸ @google/generative-ai — Gemini 2.5 Flash SDK",
        "▸ dotenv — API kalitlar muhit o'zgaruvchilari (xavfsizlik)",
        "▸ cors — Cross-Origin xavfsizlik protokoli",
        "══",
        "✅ Klonlash optimizatsiyasi:",
        "   Agar repo lokal mavjud → qayta yuklamasdan pull bilan yangilash",
        "══",
        "✅ Xatolik boshqaruvi: try/catch + Global Middleware",
        "   HTTP 400 (noto'g'ri so'rov) | 404 (topilmadi) | 500 (server xatosi)",
        "📌 Barcha xatoliklar o'zbek tilida foydalanuvchiga tushunarli xabar",
     ]}),

    ("content", {"num":19,"title":"Frontend Texnik Stack — React SPA",
     "bullets":[
        "▸ React 18 — komponentli SPA arxitektura",
        "   Virtual DOM: FAQAT o'zgargan komponent qayta chiziladi — tezlik",
        "══",
        "▸ useState + useEffect — holat boshqaruvi",
        "   App.jsx markaziy xotira → 5 sahifaga prop drilling",
        "   history.pushState — URL yo'llari dinamik yangilanadi",
        "══",
        "▸ Axios — HTTP interceptors, asinxron so'rovlar",
        "   Global baseURL + so'rov/javob interceptorlari",
        "   Double-submit xatolarining oldini olish (loading state)",
        "══",
        "▸ ReactMarkdown — AI hisobotini render qilish",
        "   Markdown → chiroyli formatlangan professional tahlil",
        "══",
        "▸ CSS Dark Mode — Neon effektlar, progress animatsiyalari",
        "══",
        "📌 Virtual Scrolling: 10000+ qatorli diff-ni brauzer muzlatmasdan ko'rsatish",
        "📌 Exponential Backoff Retry: API nosozligida avtomatik qayta urinish",
     ]}),

    # image5 = AI Analiz
    ("img_right", {"num":20,"title":"AI Semantik Hisobot — Google Gemini Natijasi","img":"image5.jpg",
     "bullets":[
        "▸ O'zbek tilida",
        "   professional tahlil",
        "══",
        "▸ Sintaktik o'zgarishlar:",
        "   nima o'zgargan",
        "══",
        "▸ Biznes/Xavfsizlik:",
        "   nima uchun o'zgargan",
        "══",
        "▸ Auto-fix tavsiyalar:",
        "   tayyor kod namunalari",
        "══",
        "▸ Markdown formatida",
        "   render qilinadi",
        "══",
        "▸ Hallucination kamaytirish:",
        "   faqat diff asosida",
     ]}),

    # image6 = Dashboard
    ("img_right", {"num":21,"title":"Dashboard — Loyiha Analitikasi va Monitoring","img":"image6.jpg",
     "bullets":[
        "▸ Umumiy statistika:",
        "   commitlar, qatorlar,",
        "   mualliflar soni",
        "══",
        "▸ Top fayllar grafigi:",
        "   progress-bar animatsiya",
        "   (binafsha-yashil ranglar)",
        "══",
        "▸ Dasturchilar reytingi:",
        "   Leaderboard — eng faol",
        "   jamoa a'zolari",
        "══",
        "▸ Real vaqtda hisoblash",
        "══",
        "▸ Loyiha audit uchun",
        "   monitoring vositasi",
     ]}),

    ("content", {"num":22,"title":"Sinov Natijalari — Real Repozitoriyalarda",
     "bullets":[
        "▸ Real GitHub repozitoriyalari ustida sinov: JavaScript ekotizimi, murakkab loyihalar",
        "══",
        "✅ Barcha 5 modul muvaffaqiyatli ishladi",
        "✅ AI o'zbek tilida professional semantik hisobot berdi",
        "✅ Kiberxavfsizlik kamchiliklari avtomatik aniqlandi",
        "✅ Auto-fix: tayyor optimallashtirilgan kod namunalari generatsiya qilindi",
        "══",
        "📌 ASOSIY O'LCHOVLI NATIJALAR:",
        "══",
        "   Code Review vaqti 40-50% qisqardi",
        "   Mantiqiy xatolarni aniqlash aniqligi sezilarli oshdi",
        "   AI hallucination kamaytirish samarali ishladi",
        "   Dashboard: commitlar, qatorlar, mualliflar statistikasi real vaqtda",
        "══",
        "📌 Nofunksional talablar bajarildi:",
        "   Ishlash tezligi: oddiy API so'rovlar < 200ms",
        "   Ishonchlilik: Global Error Handling + Retry mexanizmi",
        "   Xavfsizlik: Regex validatsiya + CORS + dotenv API kalit himoyasi",
     ]}),

    ("content", {"num":23,"title":"Ilmiy Yangilik va Amaliy Ahamiyat",
     "bullets":[
        "▸ ILMIY YANGILIK:",
        "   Kod o'zgarishlarini LLM yordamida o'ZBEK TILIDA semantik tahlil qilishning",
        "   integratsiyalashgan mantiqiy-arxitekturaviy modeli birinchi marta ishlab chiqildi",
        "══",
        "▸ AMALIY AHAMIYAT:",
        "   ✅ IT kompaniyalar uchun Code Review avtomatizatsiyasi",
        "   ✅ Loyiha audit va monitoring tizimi — real vaqt",
        "   ✅ Jamoa faolligini kuzatish (Dashboard + Leaderboard)",
        "   ✅ Dasturiy xavfsizlikni ta'minlash vositasi",
        "══",
        "▸ KELAJAKDAGI CHEKLOVLAR:",
        "   Tashqi bulutli API — ma'lumotlar xavfsizligi masalasi",
        "   Lokal LLM modeli zarur (Llama-3, CodeLlama, DeepSeek-Coder)",
        "══",
        "📌 IQTISODIY AHAMIYAT:",
        "   Adapter Pattern orqali tashqi + lokal LLM ga moslashtirilgan",
        "   Korporativ NDAs va GDPR talablariga javob bera oladi",
     ]}),

    ("content", {"num":24,"title":"Xulosa",
     "bullets":[
        "1️⃣  An'anaviy diff vositalari faqat sintaktik darajada qoladi",
        "    Semantik tahlil uchun AI integratsiya ZARUR ekanligi isbotlandi",
        "══",
        "2️⃣  Router-Controller + React SPA arxitekturasi",
        "    Barqarorlik, tezkorlik va modullilikni ta'minladi",
        "══",
        "3️⃣  Gemini 2.5 Flash: o'zbek tilida professional semantik hisobot",
        "    3 qatlamli Prompt Engineering tuzilmasi muvaffaqiyatli ishladi",
        "══",
        "4️⃣  Real sinov natijalari:",
        "    Code Review vaqti 40-50% qisqardi",
        "    Kiberxavfsizlik muammolari avtomatik aniqlanadi",
        "══",
        "📌 Ishlab chiqilgan SPA veb-platforma IT kompaniyalar uchun",
        "   tayyor amaliy dasturiy mahsulot sifatida foydalanishga tayyor!",
     ]}),

    ("content", {"num":25,"title":"Takliflar va Kelajak Istiqbollari",
     "bullets":[
        "🔷 CI/CD Integratsiya — GitHub Actions/GitLab CI plagin",
        "   Har commitda avtomatik AI tahlil → dasturchi ogohlantirish oladi",
        "══",
        "🔷 Lokal LLM modeli — Llama-3, CodeLlama, DeepSeek-Coder",
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
        "🔷 Korporativ Dashboard — Jamoa samaradorligi monitoring tizimi",
        "   SonarQube + LLM kombinatsiyasi — to'liq kod sifat portali",
     ]}),

    ("final", {}),
]

# ═══════════════════════════════════════════
# PPTX YARATISH
# ═══════════════════════════════════════════

def generate():
    out = Path("pptx_build")
    shutil.rmtree(out, ignore_errors=True)

    d = {
        "ppt/slides": out/"ppt"/"slides",
        "ppt/slides/_rels": out/"ppt"/"slides"/"_rels",
        "ppt/media": out/"ppt"/"media",
        "_rels": out/"_rels",
        "ppt/_rels": out/"ppt"/"_rels",
        "ppt/slideLayouts": out/"ppt"/"slideLayouts",
        "ppt/slideLayouts/_rels": out/"ppt"/"slideLayouts"/"_rels",
        "ppt/slideMasters": out/"ppt"/"slideMasters",
        "ppt/slideMasters/_rels": out/"ppt"/"slideMasters"/"_rels",
        "docProps": out/"docProps",
    }
    for k,v in d.items():
        v.mkdir(parents=True, exist_ok=True)

    # Rasmlarni ko'chirish
    img_map = {}
    img_files = ["image1.jpg","image2.jpg","image3.jpg","image4.jpg","image5.jpg","image6.jpg"]
    for i, fname in enumerate(img_files):
        src = Path("images") / fname
        if src.exists():
            shutil.copy(src, out/"ppt"/"media"/fname)
            img_map[fname] = f"rId{i+6}"

    # Slayd shapes generatsiya
    slide_shapes = []
    for sd in SLIDES:
        stype = sd[0]
        p = sd[1]
        if stype == "title":
            shapes = title_slide()
        elif stype == "section":
            shapes = section_slide(p["num"], p["title"], p["items"])
        elif stype == "content":
            shapes = content_slide(p["title"], p["bullets"], p["num"])
        elif stype == "img_right":
            rId = img_map.get(p["img"])
            if rId:
                shapes = img_right_slide(p["title"], rId, p["bullets"], p["num"])
            else:
                shapes = content_slide(p["title"], p["bullets"], p["num"])
        elif stype == "img_full":
            rId = img_map.get(p["img"])
            if rId:
                shapes = img_full_slide(p["title"], rId, p["caption"], p["num"])
            else:
                shapes = content_slide(p["title"], p["caption"], p["num"])
        elif stype == "final":
            shapes = final_slide()
        else:
            shapes = ""
        slide_shapes.append((stype, shapes, p))

    n = len(SLIDES)

    # Slayd XML fayllar
    for i, (stype, shapes, p) in enumerate(slide_shapes):
        with open(out/"ppt"/"slides"/f"slide{i+1}.xml","w",encoding="utf-8") as f:
            f.write(sxml(shapes))

    # Slayd rels
    for i, (stype, shapes, p) in enumerate(slide_shapes):
        rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        rels += '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n'
        img_key = p.get("img") if isinstance(p, dict) else None
        if img_key and img_key in img_map:
            rId = img_map[img_key]
            rels += f'  <Relationship Id="{rId}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{img_key}"/>\n'
        rels += "</Relationships>"
        with open(out/"ppt"/"slides"/"_rels"/f"slide{i+1}.xml.rels","w",encoding="utf-8") as f:
            f.write(rels)

    # slideLayout
    layout = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             type="blank" preserve="1">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
    <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld><p:clrMapOvr><a:masterClr/></p:clrMapOvr></p:sldLayout>'''
    with open(out/"ppt"/"slideLayouts"/"slideLayout1.xml","w") as f: f.write(layout)
    lr = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''
    with open(out/"ppt"/"slideLayouts"/"_rels"/"slideLayout1.xml.rels","w") as f: f.write(lr)

    # slideMaster
    master = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
  </p:txStyles></p:sldMaster>'''
    with open(out/"ppt"/"slideMasters"/"slideMaster1.xml","w") as f: f.write(master)
    mr = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''
    with open(out/"ppt"/"slideMasters"/"_rels"/"slideMaster1.xml.rels","w") as f: f.write(mr)

    # presentation.xml
    sids = "\n".join(f'    <p:sldId id="{256+i}" r:id="rId{i}"/>' for i in range(1,n+1))
    prs = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" saveSubsetFonts="1">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{n+1}"/></p:sldMasterIdLst>
  <p:sldIdLst>\n{sids}\n  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen4x3"/>
  <p:notesSz cx="6858000" cy="9144000"/></p:presentation>'''
    with open(out/"ppt"/"presentation.xml","w") as f: f.write(prs)

    pr2 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    for i in range(1,n+1):
        pr2 += f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n'
    pr2 += f'  <Relationship Id="rId{n+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>\n'
    pr2 += "</Relationships>"
    with open(out/"ppt"/"_rels"/"presentation.xml.rels","w") as f: f.write(pr2)

    # _rels/.rels
    rr = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>'''
    with open(out/"_rels"/".rels","w") as f: f.write(rr)

    # docProps/core.xml
    with open(out/"docProps"/"core.xml","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Dasturiy versiyalar tahlil tizimi - Diplom Himoya</dc:title>
  <dc:creator>Amonov Sohibjon</dc:creator>
</cp:coreProperties>''')

    # [Content_Types].xml
    ct = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
'''
    for i in range(1,n+1):
        ct += f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
    ct += '  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>\n</Types>'
    with open(out/"[Content_Types].xml","w") as f: f.write(ct)

    # ZIP
    outfile = "Amonov_Diplom_Prezentatsiya.pptx"
    with zipfile.ZipFile(outfile,"w",zipfile.ZIP_DEFLATED) as zf:
        for fp in out.rglob("*"):
            if fp.is_file():
                zf.write(fp, str(fp.relative_to(out)))
    shutil.rmtree(out)
    sz = os.path.getsize(outfile)
    print(f"TAYYOR: {outfile}")
    print(f"Hajm: {sz/1024:.1f} KB")
    print(f"Slaydlar: {n} ta")
    print(f"Rasmlar: {len(img_map)} ta")

if __name__ == "__main__":
    generate()
