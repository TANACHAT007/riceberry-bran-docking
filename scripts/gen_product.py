"""Prototype dossier (Thai): Riceberry bran jelly drink — formula, process, sensory protocol, score sheet."""
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

ROOT = Path(__file__).resolve().parent.parent
F = "TH Sarabun New"


def style(d):
    st = d.styles["Normal"]; st.font.name = F; st.font.size = Pt(16)
    st.element.rPr.rFonts.set(qn("w:cs"), F); st.element.rPr.rFonts.set(qn("w:eastAsia"), F)
    szcs = st.element.rPr.makeelement(qn("w:szCs"), {qn("w:val"): "32"}); st.element.rPr.append(szcs)
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2.5); s.top_margin = s.bottom_margin = Cm(2.2)


def h(d, t, size=20):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(size); r.font.name = F
    r._element.rPr.rFonts.set(qn("w:cs"), F); p.paragraph_format.space_before = Pt(10)
    return p


def para(d, t, bold_lead=None):
    p = d.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead); r.bold = True
    p.add_run(t); p.paragraph_format.space_after = Pt(4)
    return p


def bullets(d, items):
    for t in items:
        p = d.add_paragraph(); p.add_run("•  " + t)
        p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.5); p.paragraph_format.space_after = Pt(2)


def steps(d, items):
    for i, t in enumerate(items, 1):
        p = d.add_paragraph(); r = p.add_run(f"{i}. "); r.bold = True; p.add_run(t)
        p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.space_after = Pt(2)


def table(d, rows, widths=None, header=True):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    try:
        t.style = "Table Grid"
    except KeyError:
        borders = t._tbl.tblPr.makeelement(qn("w:tblBorders"), {})
        for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
            borders.append(borders.makeelement(qn(f"w:{e}"), {qn("w:val"): "single", qn("w:sz"): "4", qn("w:color"): "8A93A8"}))
        t._tbl.tblPr.append(borders)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ""; r = c.paragraphs[0].add_run(str(v)); r.font.size = Pt(15)
            r.bold = header and i == 0
            if widths: c.width = Cm(widths[j])
    d.add_paragraph()
    return t


def fix_fonts(d):
    """Force TH Sarabun New on every run/style; theme font attributes would otherwise win for Thai (cs) text."""
    els = list(d.element.body.iter(qn("w:r")))
    for r in els:
        rpr = r.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = rpr.makeelement(qn("w:rFonts"), {}); rpr.insert(0, rf)
        for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(k), F)
    for rf in list(d.styles.element.iter(qn("w:rFonts"))):
        for k in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            rf.attrib.pop(qn(k), None)
        for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(k), F)


def main():
    d = Document(ROOT / "templates" / "th.docx")  # Thai-ready styles; drop template body and header art
    for el in list(d.element.body):
        if el.tag != qn("w:sectPr"):
            d.element.body.remove(el)
    style(d)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ผลิตภัณฑ์ต้นแบบ: เจลลี่ดริ้งก์รำข้าวไรซ์เบอร์รี่ สูตรไม่เติมน้ำตาล"); r.bold = True; r.font.size = Pt(24)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Riceberry Bran Jelly Drink (no added sugar) · ส่วนต่อยอดของโครงงาน INMU 50th").italic = True

    h(d, "1. ทำไมต้องเป็นผลิตภัณฑ์นี้")
    bullets(d, [
        "ผล docking ชี้ว่าแอนโทไซยานิน (cyanidin-/peonidin-3-O-glucoside) เป็นสารที่สมดุลที่สุด จับเอนไซม์ย่อยแป้งทั้ง 2 ตัวในระดับใกล้เคียงยาอะคาร์โบส และละลายน้ำได้ จึงเหมาะกับเครื่องดื่มที่ทำงานในทางเดินอาหาร",
        "แอนโทไซยานินคงตัวดีที่สุดในสภาวะกรด (pH ≤ 3.5) และไม่ชอบความร้อนสูงหรือนาน งานวิจัยรำข้าวดำพบว่าการสลายตัวเร็วขึ้นเมื่ออุณหภูมิและ pH สูงขึ้น เจลลี่ดริ้งก์รสเปรี้ยวที่ให้ความร้อนสั้นๆ จึงรักษาสารสำคัญได้ดีกว่าขนมอบ",
        "เจลลี่บุกให้ใยอาหารและความอิ่ม ใช้อิริทริทอลหรือหญ้าหวานแทนน้ำตาล จึงเป็นสูตรไม่เติมน้ำตาล",
        "ใช้รำซึ่งเป็นผลพลอยได้จากโรงสี ตรงกับธีม Real World Impact และเศรษฐกิจ BCG",
    ])

    h(d, "2. วัตถุดิบและอุปกรณ์ (หาซื้อได้ทั่วไป)")
    table(d, [
        ["วัตถุดิบ", "หมายเหตุ"],
        ["รำข้าวไรซ์เบอร์รี่ (ใหม่ ไม่หืน) 200 g", "ซื้อจากโรงสีหรือร้านออนไลน์ เก็บในตู้เย็น ใช้ภายใน 1–2 สัปดาห์เพราะรำหืนเร็ว"],
        ["กรดซิตริก (ผงมะนาว) เกรดอาหาร", "ปรับ pH"],
        ["ผงเจลลี่บุก/คาราจีแนนสำเร็จรูป", "ใช้ตามฉลาก ประมาณ 0.6–1.0% ของน้ำหนัก"],
        ["อิริทริทอล และ/หรือ หญ้าหวาน", "สารให้ความหวานแทนน้ำตาล"],
        ["เกลือ 1 หยิบมือ, น้ำดื่ม", "—"],
        ["อุปกรณ์", "ตาชั่งดิจิทัล 0.1 g, เทอร์โมมิเตอร์, กระดาษวัด pH หรือ pH meter, ผ้าขาวบาง + กระดาษกรองกาแฟ, หม้อสแตนเลส, ถ้วยพลาสติกมีฝา 100 mL"],
    ], [6, 10])

    h(d, "3. ขั้นตอนที่ 1 — สกัดสีม่วงจากรำ (สารสกัดน้ำกรด)")
    steps(d, [
        "ชั่งรำ 100 g ใส่น้ำ 600 mL คนให้เข้ากัน",
        "เติมกรดซิตริกทีละน้อยจนได้ pH 3.0 (วัดด้วยกระดาษ pH) จดปริมาณที่ใช้",
        "อุ่นและคนที่ 50–60 °C นาน 30 นาที ห้ามเดือด เพราะความร้อนสูงทำลายแอนโทไซยานิน",
        "กรองผ่านผ้าขาวบาง แล้วกรองซ้ำด้วยกระดาษกรองกาแฟ จะได้น้ำสีม่วงแดงประมาณ 400–450 mL (จดปริมาตรจริง)",
        "เก็บในขวดทึบแสงในตู้เย็น และใช้ภายในวันเดียวกัน",
    ])

    h(d, "4. ขั้นตอนที่ 2 — ทำเจลลี่ดริ้งก์ 3 สูตร (สูตรละ 500 g)")
    para(d, "ทำ 3 สูตรเพื่อหาปริมาณสารสกัดที่คนชอบที่สุด แต่ละสูตรมีส่วนผสมอื่นเท่ากัน และปรับน้ำให้น้ำหนักรวมเท่ากับ 500 g")
    table(d, [
        ["ส่วนผสม (g)", "สูตร A (20%)", "สูตร B (30%)", "สูตร C (40%)"],
        ["สารสกัดรำ", "100", "150", "200"],
        ["น้ำดื่ม", "≈ 365", "≈ 315", "≈ 265"],
        ["ผงเจลลี่บุก/คาราจีแนน", "4 (0.8%)", "4", "4"],
        ["อิริทริทอล", "30 (6%)", "30", "30"],
        ["หญ้าหวาน (ถ้าใช้)", "ปรับตามรส", "ปรับตามรส", "ปรับตามรส"],
        ["กรดซิตริก", "ปรับให้ pH 3.2–3.5", "เท่ากัน", "เท่ากัน"],
        ["เกลือ", "0.3", "0.3", "0.3"],
    ], [5, 3.6, 3.6, 3.6])
    steps(d, [
        "ผสมผงเจลลี่กับอิริทริทอลให้เข้ากันแบบแห้ง (กันผงจับตัวเป็นก้อน)",
        "โรยลงในน้ำดื่มพร้อมคน ให้ความร้อนถึง 85 °C จนผงละลายหมด (ประมาณ 2–3 นาที)",
        "ลดไฟให้อุณหภูมิลงมาที่ประมาณ 70 °C แล้วเติมสารสกัดรำ คนให้เข้ากัน",
        "ปรับ pH ด้วยกรดซิตริกให้ได้ 3.2–3.5 (pH < 4.6 เป็นอาหารกรด ช่วยด้านความปลอดภัยและรักษาสี)",
        "อุ่นทั้งส่วนผสมให้ถึง 80 °C นาน 1 นาที แล้วบรรจุร้อนลงถ้วยที่ล้างและลวกน้ำร้อนแล้ว ปิดฝาทันที",
        "ทำให้เย็นแล้วเก็บในตู้เย็น ≤ 4 °C และชิมภายใน 48 ชั่วโมง (ต้นแบบนี้ยังไม่ได้ทดสอบอายุการเก็บ)",
    ])

    h(d, "5. สิ่งที่ต้องวัดและจด (ใช้เป็นข้อมูลจริงในบทคัดย่อ)")
    table(d, [
        ["รายการ", "วิธี", "อุปกรณ์"],
        ["ปริมาณสารสกัดที่ได้ (% yield)", "ปริมาตรสารสกัด ÷ น้ำที่ใช้ × 100", "ถ้วยตวง"],
        ["pH ของแต่ละสูตร", "วัด 3 ครั้ง รายงานค่าเฉลี่ย ± SD", "pH meter/กระดาษ pH"],
        ["สี", "ถ่ายรูปบนพื้นขาวใต้แสงเดียวกัน แล้วอ่านค่า L*, a*, b* ด้วยแอปวัดสี", "มือถือ"],
        ["ความคงตัวของสี (ถ้ามีเวลา)", "เก็บ 4 °C และอุณหภูมิห้อง ถ่ายรูปวันที่ 0, 1, 2, 3", "มือถือ"],
        ["แอนโทไซยานินทั้งหมด (ถ้ามีแล็บ)", "pH-differential (pH 1.0 / 4.5, อ่าน 520 และ 700 nm) คิดเป็น C3G", "Spectrophotometer"],
        ["การยอมรับของผู้บริโภค", "ทดสอบชิมแบบ 9-point hedonic ตามข้อ 6", "แบบประเมิน"],
    ], [5, 7, 4])

    h(d, "6. การทดสอบทางประสาทสัมผัส (Sensory evaluation)")
    bullets(d, [
        "ผู้ทดสอบ: ไม่ต่ำกว่า 30 คน (เพื่อน ครู ผู้ปกครอง) เป็นผู้ทดสอบแบบไม่ผ่านการฝึก ไม่แพ้อาหาร ได้รับคำอธิบายและยินยอมก่อนชิม ผู้ทดสอบที่อายุต่ำกว่า 18 ปีให้ขออนุญาตครูหรือผู้ปกครอง และอย่าอ้างว่าลดน้ำตาลในเลือด",
        "ตัวอย่าง: สูตรละ 30 g ในถ้วยใส ใส่รหัสเลขสุ่ม 3 หลัก (เช่น 482, 157, 903) สลับลำดับการเสิร์ฟให้แต่ละคนต่างกัน และให้บ้วนปากด้วยน้ำเปล่าระหว่างตัวอย่าง",
        "ให้คะแนน: ความชอบแบบ 9-point hedonic (1 = ไม่ชอบมากที่สุด ถึง 9 = ชอบมากที่สุด) ด้านลักษณะปรากฏ สี กลิ่น รสชาติ เนื้อสัมผัส และความชอบโดยรวม และใช้ JAR 5 ระดับสำหรับความหวานและความเปรี้ยว",
        "ถามความตั้งใจซื้อ: ซื้อ / ไม่แน่ใจ / ไม่ซื้อ และราคาที่ยอมจ่ายต่อถ้วย",
        "วิเคราะห์: ใช้ Friedman test หรือ ANOVA แบบวัดซ้ำ แล้วเปรียบเทียบรายคู่ โดยรันสคริปต์ scripts/sensory.py กับไฟล์ sensory.csv",
    ])

    h(d, "7. ฉลากและข้อกล่าวอ้าง (ทำให้ถูกต้อง)")
    bullets(d, [
        "เขียนได้: “ไม่เติมน้ำตาล” (ถ้าไม่ได้ใส่น้ำตาลจริง), “มีส่วนผสมของรำข้าวไรซ์เบอร์รี่”, “ใยอาหารจากบุก”",
        "ห้ามเขียน: “ลดน้ำตาลในเลือด”, “รักษาเบาหวาน” หรือข้อกล่าวอ้างทางสุขภาพใดๆ ที่ยังไม่ได้รับอนุญาตจาก อย.",
        "ในโปสเตอร์ให้เขียนว่า “ต้นแบบผลิตภัณฑ์ที่ออกแบบจากผลการทำนายด้วยคอมพิวเตอร์ ยังต้องทดสอบฤทธิ์ยับยั้งเอนไซม์และค่าดัชนีน้ำตาลต่อไป”",
    ])

    h(d, "8. ประโยคที่จะเพิ่มในบทคัดย่อหลังได้ผลจริง")
    para(d, "“A no-added-sugar Riceberry bran jelly drink (pH 3.x) was prototyped; formula X (YY% extract) received the highest overall liking (Z.Z ± Z.Z on a 9-point scale, n = NN).”")
    para(d, "แทน X, YY, Z.Z และ NN ด้วยตัวเลขจริงจากการทดสอบเท่านั้น ห้ามเดาตัวเลข", "หมายเหตุ: ")

    h(d, "9. แผน 4 วัน")
    table(d, [
        ["วัน", "งาน"],
        ["วันที่ 1", "ซื้อวัตถุดิบ ทำสารสกัด ลองทำสูตร B 1 รอบเพื่อปรับความหวานและเนื้อสัมผัส"],
        ["วันที่ 2", "ทำ 3 สูตร วัด pH และถ่ายรูปสี แล้วทดสอบชิมกับผู้ทดสอบ 30 คนขึ้นไป"],
        ["วันที่ 3", "กรอก sensory.csv รัน scripts/sensory.py แล้วใส่ผลลงบทคัดย่อและโปสเตอร์"],
        ["วันที่ 4", "อาจารย์ตรวจทาน แล้วส่งบทคัดย่อก่อน 30 ต.ค."],
    ], [3, 13])

    d.add_page_break()
    h(d, "ภาคผนวก: แบบประเมินการชิม (พิมพ์ 1 แผ่นต่อผู้ทดสอบ 1 คน)", 18)
    para(d, "ผู้ทดสอบหมายเลข ______   เพศ ______   อายุ ______   วันที่ ______")
    para(d, "คะแนน 1 = ไม่ชอบมากที่สุด · 5 = เฉยๆ · 9 = ชอบมากที่สุด")
    table(d, [["คุณลักษณะ", "รหัส ____", "รหัส ____", "รหัส ____"]] +
          [[k, "", "", ""] for k in ["ลักษณะปรากฏ", "สี", "กลิ่น", "รสชาติ", "เนื้อสัมผัส", "ความชอบโดยรวม"]] +
          [["ความหวาน (1 น้อยไป · 3 พอดี · 5 มากไป)", "", "", ""], ["ความเปรี้ยว (1 น้อยไป · 3 พอดี · 5 มากไป)", "", "", ""],
           ["จะซื้อไหม (ซื้อ/ไม่แน่ใจ/ไม่ซื้อ)", "", "", ""]], [6.5, 3.2, 3.2, 3.2])
    para(d, "ข้อเสนอแนะ: ________________________________________________")

    fix_fonts(d)
    out = ROOT / "submission" / "Prototype_Riceberry_Jelly_Drink.docx"; d.save(out); print(out)


if __name__ == "__main__":
    main()
