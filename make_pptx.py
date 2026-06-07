#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROFESSIONAL DIPLOM HIMOYA PREZENTATSIYASI
Amonov Sohibjon | TATU Samarqand | 2026
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
DARK3  = "081424"

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

def para(r, align="l", spc=0, lspc=0):
    al = {"l":"", "c":' algn="ctr"', "r":' algn="r"'}.get(align,"")
    sp = f'<a:spcBef><a:spcPts val="{spc}"/></a:spcBef>' if spc else ''
    ls = f'<a:spcAft><a:spcPts val="{lspc}"/></a:spcAft>' if lspc else ''
    return f'<a:p><a:pPr{al}>{sp}{ls}</a:pPr>{r}</a:p>'

def tbox(x,y,w,h,paras_xml,anchor="t"):
    return f'''<p:sp>
<p:nvSpPr><p:cNvPr id="1" name="tb"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
<p:txBody><a:bodyPr wrap="square" anchor="{anchor}" lIns="91440" rIns="91440" tIns="45720" bIns="45720"/>
<a:lstStyle/>{paras_xml}</p:txBody></p:sp>'''

def rect(x,y,w,h,fill,alpha=None,rx=0):
    if alpha:
        fx = f'<a:solidFill><a:srgbClr val="{fill}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>'
    else:
        fx = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    prst = "roundRect" if rx else "rect"
    avl = f'<a:avLst><a:gd name="adj" fmla="val {rx}"/></a:avLst>' if rx else '<a:avLst/>'
    return f'''<p:sp>
<p:nvSpPr><p:cNvPr id="2" name="r"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
<a:prstGeom prst="{prst}">{avl}</a:prstGeom>{fx}<a:ln><a:noFill/></a:ln></p:spPr>
<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'''

def img(rId,x,y,w,h):
    return f'''<p:pic>
<p:nvPicPr><p:cNvPr id="10" name="img"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
<p:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'''

def frame(x,y,w,h,color=CYAN,t=0.06):
    s  = rect(x,y,w,t,color)
    s += rect(x,y+h-t,w,t,color)
    s += rect(x,y,t,h,color)
    s += rect(x+w-t,y,t,h,color)
    return s

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
# SLAYD QURILISH FUNKSIYALARI
# ═══════════════════════════════════════════

def header(title, snum=None):
    """Sarlavha paneli"""
    s  = rect(0,0,33.87,2.8, DARK3)
    s += rect(0,2.7,33.87,0.12, CYAN)
    s += rect(0.4,0.35,0.28,2.1, PURP)
    s += tbox(1.0,0.3,31.5,2.2, para(run(title,21,True,WHITE),"l"))
    if snum:
        s += tbox(32,17.8,1.5,0.9, para(run(str(snum),11,False,CYAN),"r"))
    return s

def bg(dark=True):
    c = DARK if dark else DARK2
    return rect(0,0,33.87,19.05,c)

# ─── SLAYD 1: MUQOVA ───────────────────────
def s1_muqova():
    s  = bg()
    s += rect(0,0,33.87,0.7,PURP)
    s += rect(0,18.35,33.87,0.7,CYAN)
    s += rect(2,1.8,29.87,14.8,DARK2,alpha=75000,rx=18000)
    s += rect(2,1.8,29.87,0.1,CYAN)
    s += frame(2,1.8,29.87,14.8,PURP,0.05)
    # Univ
    s += tbox(2.5,1.9,28.5,1.3, para(run("O'ZBEKISTON RESPUBLIKASI  |  TATU SAMARQAND FILIALI  |  2026",10,False,CYAN,True),"c"))
    # Badge
    s += tbox(2.5,3.2,28.5,1.2, para(run("⚡  BITIRUV MALAKAVIY ISHI  ⚡",13,False,GOLD),"c"))
    # Sarlavha
    s += tbox(2.5,4.5,28.5,4.5,
        para(run("Dasturiy versiyalar orasidagi",24,True,WHITE),"c",60) +
        para(run("o'zgarishlarni tahlil qiluvchi",24,True,WHITE),"c",60) +
        para(run("dasturiy tizimni loyihalashtirish",24,True,WHITE),"c",60))
    s += rect(6,9.5,22,0.08,CYAN)
    # Info
    s += tbox(2.5,9.8,28.5,6.0,
        para(run("Bitiruvchi:",13,True,CYAN)+run("  Amonov Sohibjon",13,False,WHITE),"c",100) +
        para(run("Ilmiy rahbar:",13,True,CYAN)+run("  Yusupov O.",13,False,WHITE),"c",90) +
        para(run("HFX maslahatchi:",13,True,CYAN)+run("  Rajabov J.",13,False,WHITE),"c",90) +
        para(run("Kafedra:",13,True,CYAN)+run("  Dasturiy injiniring",13,False,WHITE),"c",90) +
        para(run(""),"c",80) +
        para(run("React  •  Node.js  •  Express.js  •  Google Gemini AI",11,False,LGRAY,True),"c",80))
    return s

# ─── SLAYD 2: REJA (MUNDARIJA) ─────────────
def s2_reja():
    s  = bg()
    s += header("MUNDARIJA")
    # 2 ustun
    # Chap
    s += rect(0.5,3.1,16,15.3,DARK2,alpha=70000,rx=10000)
    s += rect(0.5,3.1,16,0.1,CYAN)
    left = [
        ("KIRISH","Mavzuning dolzarbligi va tadqiqot maqsadi"),
        ("I BOB","Nazariy asoslar"),
        ("  1.1","VCS tizimlarining o'rni va ahamiyati"),
        ("  1.2","Diff tahlil metodologiyasi"),
        ("  1.3","LLM texnologiyalari integratsiyasi"),
    ]
    lxml = ""
    for num, title in left:
        if num.startswith("  "):
            lxml += para(run(f"    {num.strip()}  ",11,False,CYAN)+run(title,11,False,LGRAY),"l",60)
        else:
            lxml += para(run(f"  {num}  ",12,True,GOLD)+run(title,12,True,WHITE),"l",80)
    s += tbox(0.8,3.3,15.4,14.7, lxml)

    # O'ng
    s += rect(17,3.1,16.4,15.3,DARK2,alpha=70000,rx=10000)
    s += rect(17,3.1,16.4,0.1,PURP)
    right = [
        ("II BOB","Arxitektura va loyihalashtirish"),
        ("  2.1","Funksional talablar va 5 modul"),
        ("  2.2","Router-Controller arxitektura + Blok-sxema"),
        ("  2.3","Frontend-Backend integratsiyasi"),
        ("III BOB","Amaliy realizatsiya"),
        ("  3.1","Node.js/Express.js backend"),
        ("  3.2","React SPA frontend"),
        ("  3.3","Sinov natijalari va AI hisobotlar"),
        ("XULOSA","Natijalar va takliflar"),
    ]
    rxml = ""
    for num, title in right:
        if num.startswith("  "):
            rxml += para(run(f"    {num.strip()}  ",11,False,CYAN)+run(title,11,False,LGRAY),"l",55)
        else:
            rxml += para(run(f"  {num}  ",12,True,GOLD)+run(title,12,True,WHITE),"l",75)
    s += tbox(17.3,3.3,15.8,14.7, rxml)
    return s

# ─── SLAYD 3: KIRISH ───────────────────────
def s3_kirish():
    s  = bg(False)
    s += header("KIRISH", 3)
    # Chiroyli ramka ichida matn
    s += rect(0.5,3.1,32.87,15.2,DARK3,alpha=80000,rx=12000)
    s += frame(0.5,3.1,32.87,15.2,CYAN,0.07)
    # Yuqori label
    s += rect(1.2,2.7,12,0.9,PURP,rx=8000)
    s += tbox(1.2,2.65,12,0.9, para(run("  📋  Mavzuning dolzarbligi",10,True,WHITE),"l"))

    ktext = [
        "Axborot-kommunikatsiya texnologiyalarining shiddatli rivojlanishi davrida yuqori",
        "sifatli dasturiy ta'minot mahsulotlarini ishlab chiqish strategik yo'nalishga aylandi.",
        "",
        "Zamonaviy dasturiy mahsulotlar murakkab ko'p qatlamli arxitekturaga ega bo'lib,",
        "ularning hayotiy sikli davomida jamoalar tomonidan minglab o'zgarishlar kiritiladi.",
        "",
        "Muammo: Mavjud Diff vositalari o'zgarishlarni FAQAT sintaktik darajada ko'rsatadi —",
        "mantiqiy ma'nosi, xavfsizlikka ta'siri tushuntirilmaydi.",
        "",
        "Yechim: LLM texnologiyasini integratsiya qilish — Google Gemini 2.5 Flash modeli",
        "yordamida o'zbek tilida professional semantik hisobot generatsiya qilish.",
        "",
        "Maqsad: Versiyalar o'zgarishlarini tahlil qiluvchi SPA veb-platforma yaratish.",
        "",
        "Tadqiqot predmeti: Diff algoritmlari, JS asinxron metodlar, LLM semantik tahlil.",
        "",
        "Metodlar: OOD, Router-Controller, Prompt Engineering, Git oqimlarini boshqarish.",
    ]
    kxml = ""
    for line in ktext:
        if line == "":
            kxml += para(run(""),"l",25)
        elif line.startswith("Muammo") or line.startswith("Yechim") or line.startswith("Maqsad") or line.startswith("Tadqiqot") or line.startswith("Metodlar"):
            kxml += para(run(line,13,True,CYAN),"l",45)
        else:
            kxml += para(run(line,13,False,WHITE),"l",35)
    s += tbox(1.2,3.4,31.5,14.5, kxml)
    return s

# ─── SLAYD 4: 1.1 ──────────────────────────
def s4_1_1():
    s  = bg(False)
    s += header("1.1 — VCS Tizimlarining O'rni va Ahamiyati", 4)
    s += rect(0.5,3.1,32.87,15.3,DARK3,alpha=80000,rx=8000)
    s += frame(0.5,3.1,32.87,15.3,PURP,0.05)

    lines = [
        ("h","Versiyalarni Boshqarish Tizimi (VCS) nima?"),
        ("t","Fayllar yoki dasturiy kodlarga kiritilgan har qanday o'zgarishlarni vaqtlar kesimida qayd etuvchi,"),
        ("t","zarur bo'lganda loyihani o'tmishdagi istalgan holatiga qaytarish imkonini beruvchi dasturiy muhit."),
        ("",""),
        ("h","VCS Tarixiy Rivojlanish Bosqichlari:"),
        ("b","🔸 LOKAL VCS"),
        ("t","  Barcha fayllar tarixi faqat shaxsiy kompyuterda. Jamoaviy ishlash MUMKIN EMAS."),
        ("b","🔸 MARKAZLASHTIRILGAN (CVCS) — SVN, CVS"),
        ("t","  Yagona server. Kamchilik: server o'chsa butun loyiha tarixi yo'qoladi."),
        ("b","✅ TAQSIMLANGAN (DVCS) — Git (2005-hozir, dunyo standarti)"),
        ("t","  Har dasturchi to'liq repozitoriyaga ega. Lokal operatsiyalar sekunddan kam."),
        ("t","  Snapshot asosida saqlash. Branch = 41 baytlik ko'rsatgich."),
        ("",""),
        ("h","Code Review va muammo:"),
        ("t","Git'ning Pull Request mexanizmi orqali jamoa a'zolari kodni tekshiradi."),
        ("t","Yirik loyihalarda qo'lda tekshirish inson resursini ko'p talab qiladi va xatolar o'tib ketadi."),
    ]
    xml = ""
    for tp, line in lines:
        if tp == "": xml += para(run(""),"l",15)
        elif tp == "h": xml += para(run(line,13,True,GOLD),"l",50)
        elif tp == "b": xml += para(run(line,13,True,GREEN),"l",45)
        else: xml += para(run(line,12,False,WHITE),"l",35)
    s += tbox(1.0,3.3,31.8,14.8, xml)
    return s

# ─── SLAYD 5: 1.2 ──────────────────────────
def s5_1_2():
    s  = bg(False)
    s += header("1.2 — Diff Tahlil Metodologiyasi va Vositalar Sharhi", 5)
    s += rect(0.5,3.1,32.87,15.3,DARK3,alpha=80000,rx=8000)
    s += frame(0.5,3.1,32.87,15.3,PURP,0.05)

    lines = [
        ("h","Differensial Tahlil (Diff) nima?"),
        ("t","Ikki xil dasturiy kod versiyalari orasidagi farqlarni aniqlash jarayoni."),
        ("t","Asosi: LCS (Longest Common Subsequence) — Eng uzun umumiy ketma-ketlik algoritmi."),
        ("",""),
        ("h","Asosiy Algoritmlar:"),
        ("b","📊 MAYERS ALGORITMI (Eugene Myers, 1986) — Git standart"),
        ("t","  Eng qisqa tahrirlash skriptini topadi. Unified Diff format hosil qiladi."),
        ("b","📊 PATIENCE DIFF — noyob qatorlarga tayanadi"),
        ("t","  Rename va refaktoring operatsiyalarida aniqroq natija beradi."),
        ("b","📊 HISTOGRAM DIFF — chastota asosida"),
        ("t","  Katta loyihalarda eng yuqori tezlik va aniqlik."),
        ("",""),
        ("h","jsdiff kutubxonasi (loyihamizda):"),
        ("t","Mayers algoritmining JavaScript realizatsiyasi. parsePatch() funksiyasi orqali"),
        ("t","Git diff matnini JSON massiviga o'tkazadi. Frontend vizualizatsiya uchun tayyorlaydi."),
        ("",""),
        ("h","⚠ Asosiy cheklov:"),
        ("t","Barcha algoritmlar FAQAT sintaktik — mantiqiy ma'no, xavfsizlik ta'siri aniqlanmaydi!"),
    ]
    xml = ""
    for tp, line in lines:
        if tp == "": xml += para(run(""),"l",12)
        elif tp == "h": xml += para(run(line,13,True,GOLD),"l",45)
        elif tp == "b": xml += para(run(line,13,True,CYAN),"l",40)
        else: xml += para(run(line,12,False,WHITE),"l",30)
    s += tbox(1.0,3.3,31.8,14.8, xml)
    return s

# ─── SLAYD 6: 1.3 + JADVAL ────────────────
def s6_1_3():
    s  = bg(False)
    s += header("1.3 — LLM Texnologiyalarini Dasturiy Kod Tahliliga Integratsiya", 6)

    # Chap matn
    s += rect(0.4,3.1,18.5,15.3,DARK3,alpha=80000,rx=8000)
    s += frame(0.4,3.1,18.5,15.3,PURP,0.05)
    lines = [
        ("h","LLM nima?"),
        ("t","Transformer arxitekturasiga asoslangan"),
        ("t","katta til modellari. Kod mantiqini"),
        ("t","tushunib, tabiiy tilda izohlaydi."),
        ("",""),
        ("h","Google Gemini 2.5 Flash:"),
        ("b","✅ 1 MILLON token kontekst"),
        ("t","  Butun diff bitta so'rovda"),
        ("b","✅ O'zbek tilini tushunadi"),
        ("t","  Milliy terminologiya"),
        ("b","✅ Streaming JSON javob"),
        ("t","  Past kechikish, yuqori tezlik"),
        ("",""),
        ("h","3 qatlamli Prompt Engineering:"),
        ("t","1) System Prompt — mutaxassis roli"),
        ("t","2) Context — diff + meta-ma'lumot"),
        ("t","3) Output — Markdown format"),
    ]
    xml = ""
    for tp, line in lines:
        if tp == "": xml += para(run(""),"l",12)
        elif tp == "h": xml += para(run(line,12,True,GOLD),"l",40)
        elif tp == "b": xml += para(run(line,12,True,GREEN),"l",35)
        else: xml += para(run(line,11,False,WHITE),"l",28)
    s += tbox(0.7,3.3,17.8,14.8, xml)

    # O'ng — taqqoslash jadvali
    s += rect(19.3,3.1,14.1,15.3,DARK3,alpha=80000,rx=8000)
    s += frame(19.3,3.1,14.1,15.3,CYAN,0.05)
    s += rect(19.3,3.1,14.1,0.9,CYAN,alpha=40000)
    s += tbox(19.3,3.1,14.1,0.9, para(run("  Taqqoslash Jadvali",11,True,WHITE),"c"))

    rows = [
        ("Xususiyat","An'anaviy Diff","LLM (Gemini)"),
        ("Tahlil turi","Sintaktik","Semantik"),
        ("Mantiq","❌ Yo'q","✅ Bor"),
        ("Xavfsizlik","❌ Yo'q","✅ Aniqlaydi"),
        ("Til","Kod","O'zbek tili"),
        ("Tezlik","Tez","<5 sekund"),
        ("Auto-fix","❌","✅ Kod beradi"),
    ]
    row_colors = [PURP, None, None, None, None, None, None]
    ry = 4.1
    for i,(c1,c2,c3) in enumerate(rows):
        bg_row = PURP if i == 0 else ("0a1a2e" if i%2==0 else "0d2040")
        s += rect(19.4,ry,14,0.92,bg_row,alpha=60000)
        bold = (i==0)
        cl1 = GOLD if i==0 else LGRAY
        cl2 = GOLD if i==0 else (RED if "❌" in c2 else (GREEN if "✅" in c2 else WHITE))
        cl3 = GOLD if i==0 else (GREEN if "✅" in c3 else WHITE)
        s += tbox(19.5,ry+0.06,4.5,0.82, para(run(c1,10,bold,cl1),"c"))
        s += tbox(24.1,ry+0.06,4.5,0.82, para(run(c2,10,bold,cl2),"c"))
        s += tbox(28.7,ry+0.06,4.5,0.82, para(run(c3,10,bold,cl3),"c"))
        # ustun chiziqlari
        s += rect(24.0,ry,0.04,0.92,CYAN,alpha=50000)
        s += rect(28.6,ry,0.04,0.92,CYAN,alpha=50000)
        ry += 0.94
    return s

# ─── SLAYD 7: 2.1 + HOME PAGE rasmi ────────
def s7_2_1(img_rId):
    s  = bg(False)
    s += header("2.1 — Funksional Talablar: Bosh Sahifa (Home Page)", 7)

    # Chap — rasm
    s += img(img_rId, 0.4, 2.9, 20.5, 13.5)
    s += frame(0.4, 2.9, 20.5, 13.5, CYAN, 0.07)
    s += rect(0.4,16.45,20.5,0.7,DARK3,alpha=90000)
    s += tbox(0.4,16.48,20.5,0.65, para(run("  📸  Home Page — Tizimning kirish moduli",9,False,CYAN),"l"))

    # O'ng — matn
    s += rect(21.4,2.9,12,13.5,DARK3,alpha=85000,rx=8000)
    s += frame(21.4,2.9,12,13.5,PURP,0.05)
    s += rect(21.4,2.9,12,0.85,PURP,alpha=40000)
    s += tbox(21.4,2.9,12,0.85, para(run("  Funksional vazifalar",10,True,WHITE),"l"))

    lines = [
        ("GitHub/GitLab URL qabul qilish","t"),
        ("Regex validatsiya + xavfsizlik tekshiruvi","t"),
        ("",""),
        ("Progressiv yuklanish animatsiyasi","t"),
        ("Tayyor repozitoriyalar ro'yxati","t"),
        ("",""),
        ("Dark Mode + Neon effektli dizayn","t"),
        ("Kirish qayta ishlash mantiqiy zanjiri:","h"),
        ("  URL → Validatsiya → Backend clone","t"),
        ("  → Commits sahifasiga yo'naltirish","t"),
        ("",""),
        ("Nofunksional talablar:","h"),
        ("  API javob vaqti < 200ms","t"),
        ("  CORS himoya protokoli","t"),
        ("  Input sanitizatsiya (XSS himoya)","t"),
    ]
    rxml = ""
    for line, tp in lines:
        if line == "": rxml += para(run(""),"l",10)
        elif tp == "h": rxml += para(run(line,11,True,GOLD),"l",35)
        else: rxml += para(run("▸ "+line,11,False,WHITE),"l",28)
    s += tbox(21.6,3.9,11.5,12, rxml)
    return s

# ─── SLAYD 8: 2.1 davomi + COMMITS rasmi ──
def s8_commits(img_rId):
    s  = bg(False)
    s += header("2.1 — Commits Sahifasi: Repository Explorer", 8)

    s += img(img_rId, 0.4, 2.9, 20.5, 13.5)
    s += frame(0.4, 2.9, 20.5, 13.5, CYAN, 0.07)
    s += rect(0.4,16.45,20.5,0.7,DARK3,alpha=90000)
    s += tbox(0.4,16.48,20.5,0.65, para(run("  📸  Commits sahifasi — Repository Explorer",9,False,CYAN),"l"))

    s += rect(21.4,2.9,12,13.5,DARK3,alpha=85000,rx=8000)
    s += frame(21.4,2.9,12,13.5,PURP,0.05)
    s += rect(21.4,2.9,12,0.85,PURP,alpha=40000)
    s += tbox(21.4,2.9,12,0.85, para(run("  Commits sahifasi",10,True,WHITE),"l"))

    lines = [
        ("Backend klonlashdan so'ng avtomatik ochiladi","t"),
        ("",""),
        ("4 ta statistik kartochka:","h"),
        ("  Jami commitlar soni","t"),
        ("  Jami qo'shilgan/o'chirilgan qatorlar","t"),
        ("  Mualliflar soni","t"),
        ("  O'zgargan fayllar soni","t"),
        ("",""),
        ("Qidiruv va saralash:","h"),
        ("  Commit xabar matni bo'yicha","t"),
        ("  Muallif ismi bo'yicha","t"),
        ("  Commit ID bo'yicha","t"),
        ("",""),
        ("Commit tanlash:","h"),
        ("  To'liq ob'ekt xotirada saqlanadi","t"),
        ("  Diff sahifasiga uzatiladi","t"),
    ]
    rxml = ""
    for line, tp in lines:
        if line == "": rxml += para(run(""),"l",10)
        elif tp == "h": rxml += para(run(line,11,True,GOLD),"l",35)
        else: rxml += para(run("▸ "+line,11,False,WHITE),"l",28)
    s += tbox(21.6,3.9,11.5,12, rxml)
    return s

# ─── SLAYD 9: 2.2 + BLOK-SXEMA ────────────
def s9_2_2_bloksxema(img_rId):
    s  = bg(False)
    s += header("2.2 — Router-Controller Andozasi va Axborot Oqimlari", 9)

    # Matn tepada
    s += rect(0.4,2.9,32.87,4.2,DARK3,alpha=80000,rx=8000)
    s += frame(0.4,2.9,32.87,4.2,PURP,0.05)

    text_lines = [
        ("Router qatlami (routes/)","h"),
        ("gitRoutes.js → /api/git/clone, /api/git/commits, /api/git/diff  |  aiRoutes.js → /api/ai/analyze","t"),
        ("Controller qatlami (controllers/)","h"),
        ("gitController.js → simple-git: clone, log, diff  |  aiController.js → Gemini SDK + Prompt Engineering","t"),
        ("Afzallik: LOOSE COUPLING — Gemini o'rniga boshqa LLM = FAQAT 1 fayl o'zgartirish!","b"),
    ]
    txml = ""
    for line, tp in text_lines:
        if tp == "h": txml += para(run(line,12,True,GOLD),"l",40)
        elif tp == "b": txml += para(run("✅ "+line,12,True,GREEN),"l",40)
        else: txml += para(run(line,11,False,LGRAY),"l",25)
    s += tbox(0.8,3.0,32,3.9, txml)

    # Blok-sxema rasmi
    s += img(img_rId, 0.4, 7.3, 32.87, 10.5)
    s += frame(0.4, 7.3, 32.87, 10.5, CYAN, 0.07)
    s += rect(0.4,17.8,32.87,0.7,DARK3,alpha=90000)
    s += tbox(0.4,17.83,32.87,0.65, para(run("  📊  Axborot oqimlari arxitekturasi blok-sxemasi",9,False,CYAN),"l"))
    return s

# ─── SLAYD 10: 2.3 + DIFF VIEWER rasmi ────
def s10_diff(img_rId):
    s  = bg(False)
    s += header("2.3 — Diff Viewer: Frontend-Backend Integratsiyasi", 10)

    s += img(img_rId, 0.4, 2.9, 20.5, 13.5)
    s += frame(0.4, 2.9, 20.5, 13.5, CYAN, 0.07)
    s += rect(0.4,16.45,20.5,0.7,DARK3,alpha=90000)
    s += tbox(0.4,16.48,20.5,0.65, para(run("  📸  Diff Viewer — Kod o'zgarishlari vizualizatsiyasi",9,False,CYAN),"l"))

    s += rect(21.4,2.9,12,13.5,DARK3,alpha=85000,rx=8000)
    s += frame(21.4,2.9,12,13.5,PURP,0.05)
    s += rect(21.4,2.9,12,0.85,PURP,alpha=40000)
    s += tbox(21.4,2.9,12,0.85, para(run("  Diff Viewer va Integratsiya",10,True,WHITE),"l"))

    lines = [
        ("Diff Viewer vazifalari:","h"),
        ("  Yashil (+): qo'shilgan qatorlar","t"),
        ("  Qizil (-): o'chirilgan qatorlar","t"),
        ("  Chap panel: fayllar ro'yxati","t"),
        ("  'AI izohi' tugmasi → Gemini","t"),
        ("",""),
        ("RESTful integratsiya:","h"),
        ("  Axios asinxron HTTP so'rovlari","t"),
        ("  Global baseURL + interceptorlar","t"),
        ("  Loading state animatsiyasi","t"),
        ("",""),
        ("CORS xavfsizlik:","h"),
        ("  Faqat ruxsat etilgan domenlar","t"),
        ("  CSRF hujumlardan himoya","t"),
        ("",""),
        ("State Management:","h"),
        ("  App.jsx markaziy useState","t"),
        ("  5 sahifaga prop drilling","t"),
    ]
    rxml = ""
    for line, tp in lines:
        if line == "": rxml += para(run(""),"l",8)
        elif tp == "h": rxml += para(run(line,11,True,GOLD),"l",30)
        else: rxml += para(run(line,11,False,WHITE),"l",22)
    s += tbox(21.6,3.9,11.5,12, rxml)
    return s

# ─── SLAYD 11: 3.1 Backend ─────────────────
def s11_backend():
    s  = bg(False)
    s += header("3.1 — Node.js/Express.js Backend Realizatsiyasi", 11)

    # 2 ustun
    s += rect(0.4,3.1,16.2,15.2,DARK3,alpha=80000,rx=8000)
    s += frame(0.4,3.1,16.2,15.2,PURP,0.05)
    s += rect(0.4,3.1,16.2,0.85,PURP,alpha=40000)
    s += tbox(0.4,3.1,16.2,0.85, para(run("  Texnik stack",10,True,WHITE),"l"))

    left = [
        ("Node.js","Non-blocking I/O, EventLoop, 50+ parallel so'rov"),
        ("Express.js","Router-Controller andoza, CORS, middleware"),
        ("simple-git","clone, log, diff, pull — Git operatsiyalari"),
        ("jsdiff","Mayers algoritmi, JSON parsing, structured output"),
        ("Gemini SDK","@google/generative-ai, Prompt injection"),
        ("dotenv","API kalitlar muhit o'zgaruvchilari"),
        ("cors","Cross-Origin xavfsizlik protokoli"),
    ]
    lxml = ""
    for tech, desc in left:
        lxml += para(run("▸ ",11,False,CYAN)+run(tech,11,True,GOLD),"l",40)
        lxml += para(run("   "+desc,10,False,LGRAY),"l",20)
    s += tbox(0.7,4.1,15.5,13.8, lxml)

    s += rect(17,3.1,16.3,15.2,DARK3,alpha=80000,rx=8000)
    s += frame(17,3.1,16.3,15.2,CYAN,0.05)
    s += rect(17,3.1,16.3,0.85,CYAN,alpha=30000)
    s += tbox(17,3.1,16.3,0.85, para(run("  Asosiy funksionallik",10,True,WHITE),"l"))

    right = [
        ("Klonlash optimizatsiyasi:","Repo mavjud bo'lsa pull, yo'q bo'lsa clone"),
        ("Kesh mexanizmi:","Lokal disk — qayta so'rovda internet yo'q"),
        ("Error Handling:","try/catch + Global Middleware, HTTP 400/404/500"),
        ("URL validatsiya:","Regex sanitizatsiya, XSS himoya"),
        ("Diff parsing:","Raw patch → JSON massiv → Frontend"),
        ("Prompt injection:","3 qatlamli prompt + o'zbek tili talabi"),
    ]
    rxml = ""
    for title, desc in right:
        rxml += para(run("✅ ",11,False,GREEN)+run(title,11,True,WHITE),"l",45)
        rxml += para(run("   "+desc,10,False,LGRAY),"l",20)
    s += tbox(17.3,4.1,15.7,13.8, rxml)
    return s

# ─── SLAYD 12: 3.2 + AI rasmi ──────────────
def s12_ai(img_rId):
    s  = bg(False)
    s += header("3.2 — React SPA va AI Semantik Hisobot", 12)

    s += img(img_rId, 0.4, 2.9, 20.5, 13.5)
    s += frame(0.4, 2.9, 20.5, 13.5, CYAN, 0.07)
    s += rect(0.4,16.45,20.5,0.7,DARK3,alpha=90000)
    s += tbox(0.4,16.48,20.5,0.65, para(run("  📸  AI Semantik Hisobot — Google Gemini natijasi",9,False,CYAN),"l"))

    s += rect(21.4,2.9,12,13.5,DARK3,alpha=85000,rx=8000)
    s += frame(21.4,2.9,12,13.5,PURP,0.05)
    s += rect(21.4,2.9,12,0.85,PURP,alpha=40000)
    s += tbox(21.4,2.9,12,0.85, para(run("  React SPA va AI",10,True,WHITE),"l"))

    lines = [
        ("React SPA:","h"),
        ("  useState + useEffect holat boshqaruvi","t"),
        ("  Virtual DOM — faqat o'zgargan qayta chizish","t"),
        ("  history.pushState — URL dinamik","t"),
        ("",""),
        ("AI Hisobot qismlari:","h"),
        ("  Sintaktik o'zgarishlar tavsifi","t"),
        ("  Biznes/xavfsizlik mantiqi tahlili","t"),
        ("  Auto-fix tayyor kod namunalari","t"),
        ("  Markdown formatida render","t"),
        ("",""),
        ("Hallucination himoya:","h"),
        ("  Faqat berilgan diff asosida","t"),
        ("  Tashqi manbaga tayanmaslik","t"),
        ("",""),
        ("Natija:","h"),
        ("  O'zbek tilida professional hisobot","t"),
    ]
    rxml = ""
    for line, tp in lines:
        if line == "": rxml += para(run(""),"l",8)
        elif tp == "h": rxml += para(run(line,11,True,GOLD),"l",30)
        else: rxml += para(run(line,11,False,WHITE),"l",22)
    s += tbox(21.6,3.9,11.5,12, rxml)
    return s

# ─── SLAYD 13: 3.3 + DASHBOARD rasmi ───────
def s13_dashboard(img_rId):
    s  = bg(False)
    s += header("3.3 — Sinov Natijalari va Dashboard", 13)

    s += img(img_rId, 0.4, 2.9, 20.5, 13.5)
    s += frame(0.4, 2.9, 20.5, 13.5, CYAN, 0.07)
    s += rect(0.4,16.45,20.5,0.7,DARK3,alpha=90000)
    s += tbox(0.4,16.48,20.5,0.65, para(run("  📸  Dashboard — Loyiha analitikasi va monitoring",9,False,CYAN),"l"))

    s += rect(21.4,2.9,12,13.5,DARK3,alpha=85000,rx=8000)
    s += frame(21.4,2.9,12,13.5,PURP,0.05)
    s += rect(21.4,2.9,12,0.85,PURP,alpha=40000)
    s += tbox(21.4,2.9,12,0.85, para(run("  Sinov va Dashboard",10,True,WHITE),"l"))

    lines = [
        ("Sinov natijalari:","h"),
        ("  ✅ Barcha 5 modul ishladi","t"),
        ("  ✅ O'zbek tili — professional hisobot","t"),
        ("  ✅ Xavfsizlik kamchiliklari aniqlandi","t"),
        ("  ✅ Auto-fix kod namunalari berildi","t"),
        ("",""),
        ("O'lchovli natijalar:","h"),
        ("  Code Review 40-50% tezlashdi","t"),
        ("  Hallucination kamaytirish ishladi","t"),
        ("",""),
        ("Dashboard funksiyalari:","h"),
        ("  Umumiy statistika kartochkalari","t"),
        ("  Top fayllar progress-bar grafigi","t"),
        ("  Dasturchilar reytingi (Leaderboard)","t"),
        ("  Real vaqtda hisoblash","t"),
    ]
    rxml = ""
    for line, tp in lines:
        if line == "": rxml += para(run(""),"l",8)
        elif tp == "h": rxml += para(run(line,11,True,GOLD),"l",30)
        else: rxml += para(run(line,11,False,WHITE),"l",22)
    s += tbox(21.6,3.9,11.5,12, rxml)
    return s

# ─── SLAYD 14: XULOSA ──────────────────────
def s14_xulosa():
    s  = bg(False)
    s += header("XULOSA VA TAKLIFLAR", 14)
    s += rect(0.4,3.1,32.87,15.3,DARK3,alpha=80000,rx=8000)
    s += frame(0.4,3.1,32.87,15.3,CYAN,0.07)

    lines = [
        ("h","Xulosa"),
        ("t","1. An'anaviy Diff vositalari sintaktik darajada qoladi — semantik tahlil uchun AI zarur."),
        ("t","2. Router-Controller + React SPA arxitekturasi barqarorlik va tezkorlikni ta'minladi."),
        ("t","3. Gemini 2.5 Flash — o'zbek tilida professional semantik hisobot muvaffaqiyatli ishladi."),
        ("t","4. Real sinov: Code Review vaqti 40-50% qisqardi, kiberxavfsizlik muammolari aniqland."),
        ("",""),
        ("h","Takliflar va Istiqbollar"),
        ("b","🔷 CI/CD Integratsiya — GitHub Actions plagin: har commitda avtomatik AI tahlil"),
        ("b","🔷 Lokal LLM — Llama-3, CodeLlama: ma'lumotlar maxfiyligi, GDPR muvofiqlik"),
        ("b","🔷 Shaxsiylashtirilgan Prompt — kompaniya ichki standartlariga moslash"),
        ("b","🔷 Interaktiv vizualizatsiya — fayllararo bog'liqlik grafigi, arxitektura sxemasi"),
        ("b","🔷 Ko'p tillik — rus, ingliz, qozoq tillarida semantik hisobotlar"),
        ("",""),
        ("h","Ilmiy yangilik"),
        ("t","Kod o'zgarishlarini LLM yordamida o'ZBEK TILIDA semantik tahlil qilishning"),
        ("t","integratsiyalashgan mantiqiy-arxitekturaviy modeli BIRINCHI MARTA ishlab chiqildi."),
    ]
    xml = ""
    for tp, line in lines:
        if tp == "": xml += para(run(""),"l",18)
        elif tp == "h": xml += para(run(line,13,True,GOLD),"l",55)
        elif tp == "b": xml += para(run(line,12,True,GREEN),"l",42)
        else: xml += para(run(line,12,False,WHITE),"l",32)
    s += tbox(0.8,3.3,32,14.8, xml)
    return s

# ─── SLAYD 15: RAHMAT ──────────────────────
def s15_rahmat():
    s  = bg()
    s += rect(0,0,33.87,0.6,CYAN)
    s += rect(0,18.45,33.87,0.6,CYAN)
    s += rect(3,2.5,27.87,14,DARK2)
    s += rect(3,2.5,27.87,0.12,PURP)
    s += rect(3,16.38,27.87,0.12,PURP)
    s += frame(3,2.5,27.87,14,CYAN,0.06)
    s += tbox(3,3.0,27.87,2.5,
        para(run("🎓  E'tiboringiz uchun",26,True,CYAN),"c")+
        para(run("RAHMAT!",36,True,WHITE),"c"))
    s += rect(7,6.2,20,0.1,CYAN)
    s += tbox(3,6.7,27.87,9,
        para(run("Dasturiy versiyalar orasidagi o'zgarishlarni tahlil qiluvchi tizim",14,False,LGRAY,True),"c",120)+
        para(run("─────────────────────────────────────",10,False,PURP),"c",60)+
        para(run("Bitiruvchi:  Amonov Sohibjon",14,False,WHITE),"c",130)+
        para(run("Ilmiy rahbar:  Yusupov O.",14,False,WHITE),"c",110)+
        para(run("TATU Samarqand filiali  —  2026",13,False,LGRAY),"c",110)+
        para(run("─────────────────────────────────────",10,False,PURP),"c",60)+
        para(run("React  •  Node.js  •  Express.js  •  Google Gemini AI  •  Git",12,False,CYAN,True),"c",130)+
        para(run(""),"c",130)+
        para(run("💬  Savollar uchun tayyorman!",16,True,GREEN),"c",100))
    return s

# ═══════════════════════════════════════════
# PPTX GENERATSIYA
# ═══════════════════════════════════════════

def generate():
    out = Path("pptx_build")
    shutil.rmtree(out, ignore_errors=True)

    dirs = [
        out/"ppt"/"slides", out/"ppt"/"slides"/"_rels",
        out/"ppt"/"media", out/"_rels", out/"ppt"/"_rels",
        out/"ppt"/"slideLayouts", out/"ppt"/"slideLayouts"/"_rels",
        out/"ppt"/"slideMasters", out/"ppt"/"slideMasters"/"_rels",
        out/"docProps",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Rasmlar
    img_files = {
        "image1.jpg": "rId6",   # Home Page
        "image2.jpg": "rId7",   # Commits
        "image3.jpg": "rId8",   # Blok-sxema
        "image4.jpg": "rId9",   # Diff Viewer
        "image5.jpg": "rId10",  # AI Analiz
        "image6.jpg": "rId11",  # Dashboard
    }
    for fname, rId in img_files.items():
        src = Path("images") / fname
        if src.exists():
            shutil.copy(src, out/"ppt"/"media"/fname)

    # Slaydlar
    slides_data = [
        (s1_muqova(),  {}),
        (s2_reja(),    {}),
        (s3_kirish(),  {}),
        (s4_1_1(),     {}),
        (s5_1_2(),     {}),
        (s6_1_3(),     {}),
        (s7_2_1(img_files["image1.jpg"]),        {"img":"image1.jpg","rId":"rId6"}),
        (s8_commits(img_files["image2.jpg"]),     {"img":"image2.jpg","rId":"rId7"}),
        (s9_2_2_bloksxema(img_files["image3.jpg"]),{"img":"image3.jpg","rId":"rId8"}),
        (s10_diff(img_files["image4.jpg"]),        {"img":"image4.jpg","rId":"rId9"}),
        (s11_backend(),{}),
        (s12_ai(img_files["image5.jpg"]),          {"img":"image5.jpg","rId":"rId10"}),
        (s13_dashboard(img_files["image6.jpg"]),   {"img":"image6.jpg","rId":"rId11"}),
        (s14_xulosa(), {}),
        (s15_rahmat(), {}),
    ]

    n = len(slides_data)

    for i, (shapes, meta) in enumerate(slides_data):
        with open(out/"ppt"/"slides"/f"slide{i+1}.xml","w",encoding="utf-8") as f:
            f.write(sxml(shapes))

        rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        rels += '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n'
        if "img" in meta:
            rels += f'  <Relationship Id="{meta["rId"]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{meta["img"]}"/>\n'
        rels += "</Relationships>"
        with open(out/"ppt"/"slides"/"_rels"/f"slide{i+1}.xml.rels","w") as f:
            f.write(rels)

    # slideLayout
    with open(out/"ppt"/"slideLayouts"/"slideLayout1.xml","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             type="blank" preserve="1">
<p:cSld><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClr/></p:clrMapOvr></p:sldLayout>''')
    with open(out/"ppt"/"slideLayouts"/"_rels"/"slideLayout1.xml.rels","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>''')

    # slideMaster
    with open(out/"ppt"/"slideMasters"/"slideMaster1.xml","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
</p:txStyles></p:sldMaster>''')
    with open(out/"ppt"/"slideMasters"/"_rels"/"slideMaster1.xml.rels","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>''')

    # presentation.xml
    sids = "\n".join(f'<p:sldId id="{256+i}" r:id="rId{i}"/>' for i in range(1,n+1))
    with open(out/"ppt"/"presentation.xml","w") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" saveSubsetFonts="1">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{n+1}"/></p:sldMasterIdLst>
<p:sldIdLst>{sids}</p:sldIdLst>
<p:sldSz cx="12192000" cy="6858000" type="screen4x3"/>
<p:notesSz cx="6858000" cy="9144000"/></p:presentation>''')

    pr2 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    for i in range(1,n+1):
        pr2 += f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n'
    pr2 += f'<Relationship Id="rId{n+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>\n</Relationships>'
    with open(out/"ppt"/"_rels"/"presentation.xml.rels","w") as f:
        f.write(pr2)

    with open(out/"_rels"/".rels","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>''')

    with open(out/"docProps"/"core.xml","w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>Dasturiy versiyalar tahlil tizimi</dc:title>
<dc:creator>Amonov Sohibjon</dc:creator>
</cp:coreProperties>''')

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
        ct += f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
    ct += '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>\n</Types>'
    with open(out/"[Content_Types].xml","w") as f:
        f.write(ct)

    outfile = "Amonov_Diplom_Prezentatsiya.pptx"
    with zipfile.ZipFile(outfile,"w",zipfile.ZIP_DEFLATED) as zf:
        for fp in out.rglob("*"):
            if fp.is_file():
                zf.write(fp, str(fp.relative_to(out)))
    shutil.rmtree(out)
    sz = os.path.getsize(outfile)
    print(f"✅ TAYYOR: {outfile}")
    print(f"📊 Hajm: {sz/1024:.1f} KB")
    print(f"📑 Slaydlar: {n} ta")

if __name__ == "__main__":
    generate()
