# บรีฟทำโปสเตอร์ใน Canva (สำหรับ ChatGPT / ผู้ออกแบบ)

## เงื่อนไขที่ห้ามละเมิด
1. **ขนาด 80 × 142 ซม. แนวตั้ง** (ตามเทมเพลตของผู้จัด) — ตั้งเป็น Custom size ใน Canva: width 80 cm, height 142 cm
2. **แถบหัวและแถบท้ายของเทมเพลตทางการต้องคงไว้เหมือนเดิม** ดูไฟล์ `OFFICIAL_TEMPLATE_blank.png` คือเทมเพลตเปล่าของผู้จัด (โลโก้ INMU 50 ปี, ชื่องาน "Real World Impact in Food and Nutrition", วันที่ 11–12 February 2027, กล่องติดต่อด้านล่าง) — ห้ามลบ ห้ามย้าย ห้ามเปลี่ยนสี/โลโก้ ออกแบบได้เฉพาะ "พื้นที่เนื้อหา" ตรงกลาง
3. **ห้ามแก้ตัวเลข ชื่อสาร ชื่อกรดอะมิโน รหัส PDB หรือข้อความข้อจำกัด** ทุกค่ามาจากการคำนวณจริง แก้แล้วอ้างอิงย้อนกลับไม่ได้
4. **ห้ามตัดย่อหน้า "What this cannot tell you"** และห้ามเขียนในเชิงวิจารณ์งานวิจัยผู้อื่น (นี่คือการประกวดนวัตกรรม)
5. **ห้ามเพิ่มการกล่าวอ้างสรรพคุณทางสุขภาพ** ทุกชนิด
6. ข้อความเป็นภาษาอังกฤษทั้งแผ่น (ตามที่ผู้จัดกำหนดสำหรับโปสเตอร์) ใช้ฟอนต์ sans-serif อ่านง่าย เช่น Inter / Lato / Montserrat
7. อ่านออกจากระยะ 1.5–2 เมตร: ชื่อเรื่อง ≥ 90 pt, หัวข้อหลัก ≥ 46 pt, เนื้อหา ≥ 24 pt, คำบรรยายรูป ≥ 19 pt (ขนาดจริงบนแผ่น 80 × 142 ซม.)
8. ต้องมี QR code (`qr.png`) พร้อมข้อความ "Rotate the binding sites in 3D"
9. รูปทุกรูปต้องมีคำบรรยาย Fig. 1 / Fig. 2 ตามข้อความด้านล่าง ห้ามสลับรูปกับคำบรรยาย

## ไฟล์รูปในโฟลเดอร์นี้ (ใช้ไฟล์เหล่านี้ ห้ามสร้างกราฟใหม่เอง)
- `OFFICIAL_TEMPLATE_blank.png` — เทมเพลตเปล่าของผู้จัด ใช้เป็นพื้นหลัง/อ้างอิงหัว-ท้าย
- `selectivity.png` — **Fig. 1** แผนที่ ΔΔG เทียบอะคาร์โบสบนสองเอนไซม์ (รูปหลัก วางใหญ่)
- `pose_MGAM_cyanidin_3_O_glucoside.png` + `pose_HPA_cyanidin_3_O_glucoside.png` — **Fig. 2** วางคู่กัน ซ้าย = α-glucosidase, ขวา = α-amylase
- `affinity.png` — กราฟแท่งพลังงานการจับของทุกสาร (รูปเสริม ใส่ได้ถ้ามีที่)
- `structures.png` — โครงสร้างโมเลกุล (ไม่จำเป็น ของเดิมตัดออกเพราะเล็กเกินไป ถ้าจะใส่ต้องใหญ่พอให้อ่านชื่อได้)
- `qr.png` — QR ไปหน้าเว็บโมเดล 3D

## โครงหน้าที่แนะนำ (ลำดับการอ่านต้องเป็น 1 → 2 → 3 ชัดเจน)
หัวเทมเพลต → ชื่อเรื่อง → ผู้เขียน/สถาบัน → แถวบน: A BY-PRODUCT WORTH MINING | THE QUESTION → MATERIALS AND METHODS (5 ขั้นเรียงแนวนอน) → แถบ validation → RESULTS (Fig. 1 ใหญ่ซ้าย, Fig. 2 + ข้อความผลขวา) → FROM SCREEN TO PRODUCT (3 คอลัมน์ ①②③) → CONCLUSION → อ้างอิง + QR → ท้ายเทมเพลต

## ข้อความทั้งหมด (คัดลอกไปใช้ตามตัวอักษร)

### ชื่อเรื่อง
DOCKING-BASED PRIORITISATION OF RICEBERRY BRAN CONSTITUENTS AGAINST HUMAN α-GLUCOSIDASE AND α-AMYLASE FOR BY-PRODUCT VALORISATION

### ผู้เขียน
Puttitada Pruetchayakul*
Bodindecha (Sing Singhaseni) School, Bangkok, Thailand

### A BY-PRODUCT WORTH MINING
Starch becomes glucose via pancreatic α-amylase and intestinal α-glucosidase. Acarbose slows both, but is poorly tolerated (flatulence 74% vs 29% on placebo, US label).

Riceberry bran is a low-value by-product of Thai rice milling. Pigmented-rice anthocyanins are already known from in vitro work to inhibit both enzymes (Akkarachiyasit et al., 2010).

Bran carries many candidates at once, and a food ingredient must also dissolve where the enzymes are. These have never been compared on the human enzymes.

### THE QUESTION
Riceberry bran, a low-value by-product of Thai rice mills, carries anthocyanins, γ-oryzanol, vitamin E and phenolic acids.

Which fraction should a food project extract and assay first? That is the question this screen answers.

> 11 bran constituents ranked on both human enzymes, scoring predicted binding and solubility together

### MATERIALS AND METHODS (5 ขั้น)
**1 Targets** — Human MGAM (PDB 2QMJ, 1.9 Å) and pancreatic α-amylase (PDB 3BAJ, 2.1 Å), both crystallised with acarbose
**2 Protein prep** — PDBFixer: waters and ions removed, missing atoms and hydrogens added at pH 7.4; Meeko PDBQT
**3 Ligands** — 12 structures from PubChem; RDKit ETKDG + MMFF94 optimisation; Meeko
**4 Docking** — AutoDock Vina 1.2.7 in the acarbose site, exhaustiveness 16, 3 independent seeds (78 runs)
**5 Analysis** — ΔΔG vs acarbose on each enzyme; contact residues ≤ 4 Å, H-bonds ≤ 3.5 Å, logP, ligand efficiency

แถบเน้น: Protocol validation: acarbose re-docked from a randomised start returned to its MGAM crystal pose in every run (RMSD 2.04–2.06 Å, n = 3).

### RESULTS · RANKING THE BRAN
**The tightest binder is not the usable one**
γ-Oryzanol esters topped the ranking (cycloartenyl ferulate −8.87 / −10.52 kcal/mol), but with logP > 10 they will not dissolve in the gut lumen, and they sit in the bran's oil fraction.

**Anthocyanins are the only soluble front-runners**
Cyanidin-3-O-glucoside (−7.71 / −8.09) and peonidin-3-O-glucoside (−7.64 / −8.09) ranked next, hydrogen-bonded the catalytic acids Asp443/Asp542 and Asp197/Glu233, and were the only high-ranking compounds with logP < 0.7.

คำบรรยายรูป:
Fig. 1 Each constituent placed against acarbose on both enzymes (ΔΔG, mean of 3 seeds). Circles dissolve in water, squares do not. The shaded area marks where a usable food candidate would sit.
Fig. 2 Cyanidin-3-O-glucoside (purple) in α-glucosidase (left) and α-amylase (right). Gold = catalytic residues, green = hydrogen-bond partners.

### FROM SCREEN TO PRODUCT (3 คอลัมน์)
**① Take this fraction**
The acidified aqueous extract of fresh Riceberry bran — the anthocyanin-bearing fraction.
Not whole bran, not the oil fraction: the γ-oryzanol that ranks highest sits in the oil and will not dissolve.
Bran must be fresh; it turns rancid within weeks.

**② Prove it on the bench**
Two-enzyme IC₅₀, not one. Run α-glucosidase and α-amylase assays side by side against acarbose.
Report a selectivity index (IC₅₀ amylase ÷ IC₅₀ glucosidase) so potency and selectivity are measured, not inferred.
Quantify anthocyanin by pH-differential (520/700 nm) as cyanidin-3-glucoside equivalents.

**③ Build it into food**
Anthocyanins survive acid and short heat, not long baking. The prototype is a no-added-sugar jelly drink: pH 3.2–3.5, 80 °C for 1 min, hot-filled.
Three extract levels (20/30/40%), 9-point hedonic test, n ≥ 30.
Label claims stay factual: no health claim without FDA approval.

### CONCLUSION
Scoring binding together with solubility changes which molecule a food project should chase. The highest-scoring constituents of Riceberry bran, the γ-oryzanol esters, cannot dissolve where the enzymes work; the anthocyanins rank just below them and are the only front-runners that can.

This turns a rice-mill by-product into one defined fraction to extract and one assay that would settle it, instead of a vague claim about rice bran being healthy.

**What this cannot tell you.** Docking ranks predicted binding, not inhibitory potency or selectivity; differences below ~1 kcal/mol sit inside the scoring error. Prior in vitro work established that these anthocyanins do inhibit both enzymes, and the two-enzyme IC₅₀ comparison above is what would rank them. No health claim is made here.

### อ้างอิงท้ายแผ่น (ตัวเล็ก)
Structures PDB 2QMJ (Sim et al., J Mol Biol 2008) and 3BAJ (Maurus et al., Biochemistry 2008). Software AutoDock Vina 1.2.7 (Eberhardt et al., JCIM 2021); Meeko; RDKit; PDBFixer. Ligands from PubChem. Prior in vitro data Akkarachiyasit et al., Int J Mol Sci 2010;11:3387. Acarbose tolerability US prescribing information. All scripts and raw results via the QR link.

*Corresponding author: Puttitada Pruetchayakul (graciepiewppiew@gmail.com)

ข้างคิวอาร์โค้ด: Rotate the binding sites in 3D
