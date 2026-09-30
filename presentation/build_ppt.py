# Builds a Review-2 deck that STRICTLY follows Review2_PPT.ppt:
# same 11 slides, same order, same headings, same guiding scaffold —
# using the built-in Office-theme layouts, with the project's content filled in.
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# --- template BRANDING extracted from Review2_PPT.ppt (Aditya University template) ---
# The template embeds the Aditya University logo + brand palette on a white ground.
TITLE_BLUE = RGBColor(0x2E, 0x43, 0x74)   # Aditya navy (sampled from logo wordmark)
ORANGE     = RGBColor(0xC8, 0x5A, 0x2B)   # Aditya orange accent (sampled from emblem)
INK = RGBColor(0x00, 0x00, 0x00)          # body text (black)
SUB = RGBColor(0x33, 0x33, 0x33)
FONT = "Times New Roman"                  # required: entire deck in Times New Roman
LOGO_STACK = os.path.join(HERE, "_tpl_bg", "img0.png")  # stacked logo (title slide)
LOGO_WIDE  = os.path.join(HERE, "_tpl_bg", "img1.png")  # horizontal lockup (corner header)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# force theme major/minor fonts to Times New Roman so every placeholder inherits it
def set_theme_font(name):
    from lxml import etree
    for master in prs.slide_masters:
        try:
            part = master.part.part_related_by(RT.THEME)
        except KeyError:
            continue
        try:
            el = etree.fromstring(part.blob)
            fs = el.find(qn('a:themeElements')).find(qn('a:fontScheme'))
            for tag in ('a:majorFont', 'a:minorFont'):
                latin = fs.find(qn(tag)).find(qn('a:latin'))
                latin.set('typeface', name)
            part._blob = etree.tostring(el, xml_declaration=True,
                                        encoding='UTF-8', standalone=True)
        except Exception:
            pass
set_theme_font(FONT)

TITLE_SLIDE = prs.slide_layouts[0]
TITLE_CONTENT = prs.slide_layouts[1]

from pptx.enum.shapes import MSO_SHAPE

def brand_header(slide, title_slide=False):
    """Apply the Aditya University template look: corner logo + orange accent rule."""
    if title_slide:
        return
    # horizontal logo lockup, top-right corner (matches the template's header placement)
    try:
        slide.shapes.add_picture(LOGO_WIDE, Inches(9.75), Inches(0.30),
                                 width=Inches(3.15))
    except Exception:
        pass
    # thin orange rule beneath the title band
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0.55), Inches(1.28), Inches(12.23), Pt(3))
    bar.fill.solid(); bar.fill.fore_color.rgb = ORANGE
    bar.line.fill.background()
    bar.shadow.inherit = False

def style_title(shape, size=32):
    shape.left = Inches(0.55); shape.top = Inches(0.42)
    shape.width = Inches(9.0); shape.height = Inches(0.9)   # leaves room for corner logo
    p = shape.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    for r in p.runs:
        r.font.size = Pt(size); r.font.bold = True
        r.font.name = FONT; r.font.color.rgb = TITLE_BLUE

def body_ph(slide):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx != 0:
            return ph
    return None

def fill(title, items, gap=6, base=20):
    """items: (label, answer, level). answer None -> label-only bullet."""
    s = prs.slides.add_slide(TITLE_CONTENT)
    s.shapes.title.text = title
    style_title(s.shapes.title)
    brand_header(s)
    bp = body_ph(s)
    bp.left = Inches(0.7); bp.top = Inches(1.55)
    bp.width = Inches(12.0); bp.height = Inches(5.4)
    tf = bp.text_frame; tf.word_wrap = True
    first = True
    for label, answer, lvl in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = lvl; p.space_after = Pt(gap); p.alignment = PP_ALIGN.LEFT
        r = p.add_run(); r.text = label
        r.font.bold = (answer is not None) or (lvl == 0)
        r.font.size = Pt(base - lvl * 2); r.font.name = FONT
        r.font.color.rgb = INK
        if answer is not None:
            r2 = p.add_run(); r2.text = ": " + answer
            r2.font.bold = False; r2.font.size = Pt(base - lvl * 2)
            r2.font.name = FONT; r2.font.color.rgb = SUB
    return s


# ---------- SLIDE 1: Title of the Project ----------
s = prs.slides.add_slide(TITLE_SLIDE)
# Aditya University stacked logo, centered near the top (from the template)
try:
    logo_w = 3.6
    s.shapes.add_picture(LOGO_STACK, Inches((13.333 - logo_w) / 2), Inches(0.7),
                         width=Inches(logo_w))
except Exception:
    pass
s.shapes.title.text = "Student AI Chatbot"
t = s.shapes.title
t.left = Inches(1.0); t.top = Inches(3.0); t.width = Inches(11.33); t.height = Inches(1.3)
tp = s.shapes.title.text_frame.paragraphs[0]; tp.alignment = PP_ALIGN.CENTER
for r in tp.runs:
    r.font.name = FONT; r.font.bold = True; r.font.size = Pt(44); r.font.color.rgb = TITLE_BLUE
# orange brand rule under the title
_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.4), Inches(4.15), Inches(4.53), Pt(3))
_bar.fill.solid(); _bar.fill.fore_color.rgb = ORANGE
_bar.line.fill.background(); _bar.shadow.inherit = False
subph = s.placeholders[1]
subph.left = Inches(1.0); subph.top = Inches(4.4); subph.width = Inches(11.33); subph.height = Inches(2.6)
sub = subph.text_frame
sub.word_wrap = True
sub.paragraphs[0].text = "A Grounded College-Information Assistant using Intent Classification + RAG"
sub.paragraphs[0].runs[0].font.size = Pt(22)
p = sub.add_paragraph(); p.text = ""
p = sub.add_paragraph(); p.text = "Team Members:"
p.runs[0].font.bold = True; p.runs[0].font.size = Pt(20)
for _ in range(4):
    pr = sub.add_paragraph(); pr.text = "Name (Roll No)"; pr.runs[0].font.size = Pt(18)
for pp in sub.paragraphs:
    pp.alignment = PP_ALIGN.CENTER
    for r in pp.runs: r.font.name = FONT; r.font.color.rgb = INK


# ---------- SLIDE 2: CONTENTS ----------
fill("CONTENTS", [
    ("Introduction", None, 0),
    ("Problem Definition", None, 0),
    ("Proposed Solution", None, 0),
    ("Proposed Workflow", None, 0),
    ("Data Used", None, 0),
    ("Modules", None, 0),
    ("Text Preprocessing/Preprocessing", None, 1),
    ("Feature Extraction (Vector Representation)", None, 1),
    ("Python Implementation (NLTK concepts)", None, 1),
    ("NLP / ML Algorithm", None, 0),
    ("Output/ Result", None, 0),
    ("Conclusion and Future Scope", None, 0),
], gap=4, base=18)

# ---------- SLIDE 3: Introduction ----------
fill("Introduction", [
    ("What is the project about?",
     "A conversational assistant that answers students' questions on curriculum, courses, "
     "credits, exams and campus administration.", 0),
    ("What is the application/domain?",
     "Higher-education information access — an NLP + Retrieval-Augmented Generation (RAG) "
     "system over authoritative college documents.", 0),
    ("Why is this topic important?",
     "Syllabi, calendars and regulations are fragmented across PDFs and pages; students "
     "cannot easily find or trust the answer.", 0),
    ("What motivated the team to select this project?",
     "To give every student one reliable, source-cited interface that abstains instead of "
     "guessing — never fabricating a college fact.", 0),
], base=19, gap=10)

# ---------- SLIDE 4: Problem Definition ----------
fill("Problem Definition", [
    ("What is the existing problem?",
     "Campus information is scattered across curriculum PDFs, calendars, exam regulations "
     "and department pages.", 0),
    ("What difficulties are faced?",
     "Terminology varies (\"sem 4\" vs \"semester 4\"), keyword search is brittle, and generic "
     "chatbots hallucinate confident wrong answers.", 0),
    ("Why is the problem important?",
     "A wrong fact about credits, eligibility or exam rules directly misleads a student's "
     "academic decisions.", 0),
    ("Who is affected by the problem?",
     "Students primarily, plus faculty and office staff who field the same repeated queries.", 0),
    ("What needs to be improved?",
     "Accurate, source-cited answers with a reliable \"I don't know\" when evidence is missing "
     "— traceability over fluency.", 0),
], base=18, gap=8)

# ---------- SLIDE 5: Proposed Solution ----------
fill("Proposed Solution", [
    ("Major functions",
     "Intent classification → hybrid retrieval → grounded generation → citation validation "
     "→ abstention.", 0),
    ("Input → Processing → Output",
     "Input: a free-text question. Processing: normalize → classify (24 intents) → retrieve "
     "evidence (BM25 + dense, fused) → answer only from retrieved chunks. Output: answer + "
     "citations + intent/confidence + trace ID, or a safe abstention.", 0),
    ("Expected users",
     "College students; secondarily faculty and office staff.", 0),
    ("Expected benefits",
     "Fast, consistent, source-backed answers; zero fabricated facts; auditable responses.", 0),
    ("Proposed methodology/workflow",
     "Abstention-first, evidence-grounded RAG with defense-in-depth safety gates (approval/"
     "currency filter, private-record gate, relevance gate, citation validation).", 0),
], gap=5, base=17)

# ---------- SLIDE 6: Data Used ----------
fill("Data Used", [
    ("Source of data",
     "CampusFAQ-50K v1.0 — project-owned dataset built from approved institutional document "
     "templates (syllabi, regulations, calendar, exam rules, department & office pages). "
     "Content is synthetic DEMO_ONLY.", 0),
    ("Type of data",
     "Labeled question–answer pairs, each with an intent, supporting evidence chunk and "
     "provenance.", 0),
    ("Number of records",
     "50,000 total  →  Train 40,000 | Validation 5,000 | Test 5,000; 24 intents balanced "
     "(~2,083 each).", 0),
    ("Important attributes/columns",
     "query, intent, response, document_id, evidence[quote, location], entities, answerable, "
     "difficulty, split.", 0),
    ("Data format",
     "JSONL + CSV with SHA-256 checksums and a versioned dataset manifest.", 0),
], gap=5, base=17)

# ---------- SLIDE 7: Modules ----------
fill("Modules", [
    ("Text Preprocessing/Preprocessing", None, 0),
    ("Unicode NFKC normalization, whitespace & punctuation cleanup, control-char removal; "
     "domain terms like \"CSE101\" and \"sem 4\" preserved (no aggressive stemming).", None, 1),
    ("Feature Extraction (Vector Representation)", None, 0),
    ("Lexical: TF-IDF (word 1–2 grams + char 3–5 grams). Dense: sentence-transformers "
     "all-MiniLM-L6-v2 (384-dim), with a deterministic hash-embedding fallback.", None, 1),
    ("Python Implementation (NLTK concepts)", None, 0),
    ("NLTK-style tokenization/normalization + scikit-learn TF-IDF & classifiers; NumPy vector "
     "index and self-contained BM25; FastAPI backend + React/Vite UI; offline, seed = 42.", None, 1),
], gap=8, base=18)

# ---------- SLIDE 8: NLP / ML Algorithm ----------
fill("NLP / ML Algorithm", [
    ("Logistic Regression",
     "Trained on TF-IDF features — the selected MVP intent classifier (calibrated "
     "probabilities for confidence thresholds).", 0),
    ("Support Vector Machine",
     "Linear SVM on TF-IDF — strong linear baseline for the 24-intent task.", 0),
    ("N-gram Language Model",
     "Word 1–2 grams and character 3–5 grams supply the lexical signal for classification "
     "and BM25 retrieval.", 0),
    ("TF-IDF",
     "Primary sparse vectorizer (min_df=2, max_df=0.9, sublinear_tf) for all classical "
     "models.", 0),
    ("Word2Vec",
     "Dense semantic embeddings (realized via MiniLM sentence embeddings) power the vector "
     "side of hybrid retrieval.", 0),
], gap=6, base=17)

# ---------- SLIDE 9: NLP / ML Algorithm (models compared) ----------
fill("NLP / ML Algorithm", [
    ("Models compared (intent classification, 24 classes)", None, 0),
    ("Logistic Regression + word TF-IDF", None, 1),
    ("Linear SVM + word TF-IDF", None, 1),
    ("Multinomial Naïve Bayes + word TF-IDF", None, 1),
    ("Hybrid TF-IDF (word + char n-grams) + Logistic Regression", None, 1),
    ("DistilBERT transformer — optional upgrade, skipped in the offline MVP to stay lightweight", None, 1),
    ("Retrieval algorithm", "BM25 (lexical) + dense cosine fused via Reciprocal Rank Fusion "
     "→ top-5 evidence.", 0),
    ("Selected model", "Logistic Regression — reaches the performance ceiling and gives "
     "calibrated predict_proba for robust confidence thresholds.", 0),
], gap=5, base=17)

# ---------- reusable helpers for result/analytics slides ----------
TITLE_ONLY = prs.slide_layouts[5]

def new_result_slide(title):
    s = prs.slides.add_slide(TITLE_ONLY)
    s.shapes.title.text = title
    style_title(s.shapes.title)
    brand_header(s)
    return s

def add_caption(slide, text, left, top, width, size=13, bold=True, color=TITLE_BLUE):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(0.35))
    tb.text_frame.word_wrap = True
    r = tb.text_frame.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT; r.font.color.rgb = color
    return tb

def add_table(slide, rows, left, top, width, height, col_ratios, fsize=12):
    nr, nc = len(rows), len(rows[0])
    tb = slide.shapes.add_table(nr, nc, Inches(left), Inches(top),
                                Inches(width), Inches(height)).table
    tot = float(sum(col_ratios))
    for ci, ratio in enumerate(col_ratios):
        tb.columns[ci].width = Inches(width * ratio / tot)
    for ri, row in enumerate(rows):
        for cii, val in enumerate(row):
            c = tb.cell(ri, cii); c.text = str(val)
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if cii == 0 else PP_ALIGN.CENTER
            pr = p.runs[0]
            pr.font.name = FONT; pr.font.size = Pt(fsize)
            pr.font.bold = (ri == 0)
            pr.font.color.rgb = TITLE_BLUE if ri == 0 else INK
    return tb

def add_bullets(slide, items, left, top, width, height, fsize=15, gap=6):
    sb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = sb.text_frame; tf.word_wrap = True
    for i, t in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap); p.alignment = PP_ALIGN.LEFT
        r = p.add_run(); r.text = "•  " + t
        r.font.size = Pt(fsize); r.font.name = FONT; r.font.color.rgb = INK
    return sb

# ---------- SLIDE 10: Output / Result (primary results, genuine values) ----------
s = new_result_slide("Output / Result")
add_caption(s, "Intent classification — 24 classes, held-out test set "
               "(trained scikit-learn models)", 0.6, 1.35, 12.1)
add_table(s, [
    ["Model", "Accuracy", "Macro F1", "Weighted F1", "Precision", "Recall", "Latency (ms/query)"],
    ["Logistic Regression (MVP)", "1.000", "1.000", "1.000", "1.000", "1.000", "0.006"],
    ["Linear SVM",                "1.000", "1.000", "1.000", "1.000", "1.000", "0.011"],
    ["Multinomial Naïve Bayes",   "1.000", "1.000", "1.000", "1.000", "1.000", "0.011"],
    ["Hybrid TF-IDF + LogReg",    "1.000", "1.000", "1.000", "1.000", "1.000", "0.128"],
], left=0.6, top=1.75, width=12.1, height=1.9,
   col_ratios=[3.0, 1.15, 1.15, 1.25, 1.15, 1.0, 1.6], fsize=12)

nt = s.shapes.add_textbox(Inches(0.6), Inches(3.85), Inches(12.1), Inches(0.85))
nt.text_frame.word_wrap = True
rr = nt.text_frame.paragraphs[0].add_run()
rr.text = ("Trained models reach the ceiling because CampusFAQ-50K's synthetic classes are cleanly "
           "separable (LogReg train time 1.79 s). Deployed offline demo — zero-training lexical "
           "fallback, no model loaded — scores accuracy 0.6725 / macro-F1 0.6616 on 1,200 held-out rows.")
rr.font.size = Pt(12); rr.font.italic = True; rr.font.color.rgb = SUB; rr.font.name = FONT

add_bullets(s, [
    "RAG safety: out-of-scope hallucination 0.00 · OOS abstention 1.00 · citation violations 0 · mean grounding 1.00.",
    "In-scope answer rate 0.7035 (809 / 1,150 answered) · every out-of-scope query silenced (50 / 50).",
    "Quality gates: 146 / 146 unit + integration + adversarial tests passed · 11 / 11 behavioural regression.",
], left=0.6, top=4.85, width=12.1, height=2.3, fsize=15, gap=8)

# ---------- SLIDE 11: Output / Result — Analytics (genuine values) ----------
s = new_result_slide("Output / Result — Analytics")

add_caption(s, "Retrieval quality  (in-scope 1,144 queries)", 0.6, 1.35, 6.0)
add_table(s, [
    ["k", "Recall@k", "Hit@k"],
    ["1", "0.280", "0.549"],
    ["3", "0.533", "0.779"],
    ["5", "0.643", "0.859"],
], left=0.6, top=1.75, width=5.9, height=1.7, col_ratios=[1.0, 1.6, 1.6], fsize=13)
add_caption(s, "MRR 0.6699 · nDCG@5 0.5774 · OOS silence rate 0.00",
            0.6, 3.55, 6.0, size=11, bold=False, color=SUB)

add_caption(s, "Latency  (ms · 10 queries × 5 reps)", 6.9, 1.35, 5.8)
add_table(s, [
    ["Stage", "Mean", "p95", "p99", "Max"],
    ["Intent",     "0.08", "0.10", "0.15", "0.15"],
    ["Retrieval",  "8.19", "10.28", "12.57", "12.57"],
    ["End-to-end", "8.79", "10.63", "11.31", "11.31"],
], left=6.9, top=1.75, width=5.8, height=1.7, col_ratios=[2.0, 1.3, 1.3, 1.3, 1.3], fsize=13)
add_caption(s, "Offline, extractive provider; retrieval dominates end-to-end cost",
            6.9, 3.55, 5.8, size=11, bold=False, color=SUB)

add_caption(s, "End-to-end RAG evaluation  (1,200 rows)", 0.6, 4.15, 12.1)
add_bullets(s, [
    "In-scope 1,150 → 809 answered / 341 abstained (answer rate 0.7035); mean grounding 1.00.",
    "Out-of-scope 50 → 0 answered / 50 abstained: hallucination rate 0.00, citation-integrity violations 0.",
    "Dataset: 50,000 records (train 40k / val 5k / test 5k), 24 balanced intents; answerable 47,917 / 2,083.",
    "Reproducible: seed 42, fully offline, SHA-256-checksummed dataset manifest.",
], left=0.6, top=4.55, width=12.1, height=2.6, fsize=14, gap=7)

# ---------- SLIDE 12: Conclusion and Future Scope ----------
fill("Conclusion and Future Scope", [
    ("Conclusion", None, 0),
    ("Delivered a runnable, tested, offline prototype: intent → hybrid retrieval → grounded "
     "generation → citation validation → abstention.", None, 1),
    ("Primary goal met — zero out-of-scope fabrication (hallucination 0.00, abstention 1.00) "
     "with valid citations and reproducible results (seed 42).", None, 1),
    ("Classical TF-IDF + Logistic Regression is an accurate, fast, interpretable MVP classifier.", None, 1),
    ("Future Scope", None, 0),
    ("Fine-tune DistilBERT and enable MiniLM dense embeddings for better semantic generalization.", None, 1),
    ("Ground on real approved institutional sources; add PostgreSQL + pgvector at scale.", None, 1),
    ("Enable a live LLM provider (Gemini / Claude) behind the same evidence-only contract.", None, 1),
    ("Add multilingual support, a reranker and human-in-the-loop evaluation before release.", None, 1),
], gap=6, base=17)

out = os.path.join(HERE, "Review2_Student_AI_Chatbot.pptx")
prs.save(out)
print("SAVED:", out, "| slides:", len(prs.slides._sldIdLst))



