// Build the presentation deck:  cd slides && node build_deck.js
// Output: slides/out/ClinicAnalytics_Slides.pptx  (PDF: see build.sh)
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(process.env.PPTX_SKILL_DIR
  ? path.join(process.env.PPTX_SKILL_DIR, "scripts/apply_theme.js")
  : "./apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const FIG = (f) => path.join(ROOT, "outputs", "figures", f);
const LOGO = path.join(ROOT, "report", "assets", "uit_logo.png");
const OUT = path.join(__dirname, "out");

const THEME = {
  name: "Clinic Teal",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2A2F", lt1: "FFFFFF", dk2: "0B4F5C", lt2: "EAF3F3",
    accent1: "0B7A75", accent2: "F26B5B", accent3: "F2B134", accent4: "5B8DB8",
    accent5: "7A8B8F", accent6: "2E9C6A", hlink: "0B7A75", folHlink: "5B8DB8",
  },
};
const HEX = THEME.colors;
const W = 13.333, H = 7.5, MX = 0.6;

async function icon(Comp, color = "FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Ho Van Hieu";
  pres.title = "ClinicAnalytics - STAT3013 Final Project";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // ------------------------------------------------------------------ layouts
  pres.defineSlideMaster({
    title: "DARK_TITLE",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: MX, y: 2.3, w: W - 2 * MX, h: 1.9,
          fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", fontFace: THEME.headFontFace, margin: 0 } } },
      { placeholder: { options: { name: "body", type: "body", x: MX, y: 4.35, w: W - 2 * MX, h: 0.7,
          fontSize: 20, color: "BFE3E1", valign: "top", align: "left", margin: 0 } } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    slideNumber: { x: W - 1.1, y: H - 0.5, w: 0.6, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
    objects: [
      { text: { text: "STAT3013.R11.CTTT  ·  Group 10  ·  ClinicAnalytics",
          options: { x: MX, y: H - 0.5, w: 6, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
      { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.35, w: W - 2 * MX, h: 0.95,
          fontSize: 30, bold: true, color: C.text2, valign: "middle", fontFace: THEME.headFontFace, margin: 0 } } },
    ],
  });

  const content = (section, title) => {
    const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
    s.addText(title, { placeholder: "title" });
    return s;
  };
  const circleIcon = async (s, Comp, x, y, d, fill, name) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name + "-circle" });
    s.addImage({ data: await icon(Comp), x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52, objectName: name + "-icon" });
  };
  const card = (s, x, y, w, h, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: name });
  const stat = (s, x, y, w, big, label, color, name, bigSize = 40) => {
    s.addText(big, { x, y, w, h: 0.8, fontSize: bigSize, bold: true, color, fontFace: THEME.headFontFace,
      margin: 0, isTextBox: true, objectName: name + "-value" });
    s.addText(label, { x, y: y + 0.8, w, h: 0.75, fontSize: 14, color: C.text1, margin: 0, valign: "top",
      isTextBox: true, objectName: name + "-label" });
  };
  const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
    titleFontFace: "+mn-lt", legendFontFace: "+mn-lt", catAxisLabelColor: HEX.dk1, valAxisLabelColor: HEX.accent5,
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontSize: 11, titleFontSize: 14, titleColor: HEX.dk1,
    valGridLine: { color: "D9E4E4", size: 0.5 }, catGridLine: { style: "none" } };

  // ------------------------------------------------------------------ 1 title
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "DARK_TITLE", sectionTitle: "Introduction" });
  s.addShape(pres.shapes.OVAL, { x: MX, y: 0.55, w: 1.25, h: 1.25, fill: { color: C.background1 }, line: { color: C.background1 }, objectName: "logo-circle" });
  s.addImage({ path: LOGO, x: MX + 0.17, y: 0.72, w: 0.91, h: 0.736, objectName: "uit-logo" });
  s.addText([{ text: "UNIVERSITY OF INFORMATION TECHNOLOGY, VNU-HCM", options: { bold: true, breakLine: true } },
             { text: "Statistical Analysis (STAT3013.R11.CTTT)  ·  Instructor: Nguyen Minh Nhut  ·  Group 10" }],
    { x: 2.1, y: 0.75, w: 9, h: 0.85, fontSize: 14, color: C.background1, margin: 0, isTextBox: true, objectName: "header" });
  s.addText("Statistical & Machine Learning Analytics for a Private Outpatient Clinic", { placeholder: "title" });
  s.addText("Patient value  ·  Satisfaction  ·  Retention  ·  Demand", { placeholder: "body" });
  s.addText("Ho Van Hieu  —  Student ID 19521497          November 2026",
    { x: MX, y: 6.4, w: 10, h: 0.5, fontSize: 16, color: C.background1, margin: 0, isTextBox: true, objectName: "author" });
  s.addNotes("Good morning. My name is Ho Van Hieu, student ID 19521497. My project applies the statistics and machine-learning methods of this course to one realistic business: a private outpatient clinic. I will show how one connected workflow answers the questions a clinic manager really asks about patient value, satisfaction, retention and demand.");

  // ------------------------------------------------------------------ 2 questions
  s = content("Introduction", "Three questions every private clinic asks");
  const qs = [
    [fa.FaUserMd, C.accent1, "Who is valuable?", "Which patients will spend the most next year?", "Two-part regression → Patient Lifetime Value"],
    [fa.FaHeartbeat, C.accent2, "What keeps patients loyal?", "Which parts of the service drive satisfaction, and does it bring patients back?", "SEM on a satisfaction survey"],
    [fa.FaCalendarAlt, C.accent4, "How much demand, who will leave?", "How many visits next quarter, and which patients will not return?", "ARIMA forecasting + churn ML"],
  ];
  const cw = (W - 2 * MX - 2 * 0.4) / 3;
  for (let i = 0; i < 3; i++) {
    const [Ic, col, head, desc, method] = qs[i];
    const x = MX + i * (cw + 0.4);
    card(s, x, 1.6, cw, 4.2, "question-card-" + (i + 1));
    await circleIcon(s, Ic, x + 0.35, 1.9, 0.95, col, "question-" + (i + 1));
    s.addText(head, { x: x + 0.35, y: 3.05, w: cw - 0.7, h: 0.85, fontSize: 20, bold: true, color: C.text2, margin: 0, valign: "top", isTextBox: true, objectName: `q${i + 1}-head` });
    s.addText(desc, { x: x + 0.35, y: 3.95, w: cw - 0.7, h: 0.95, fontSize: 15, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: `q${i + 1}-desc` });
    s.addText(method, { x: x + 0.35, y: 4.95, w: cw - 0.7, h: 0.6, fontSize: 14, italic: true, color: col, margin: 0, isTextBox: true, objectName: `q${i + 1}-method` });
  }
  s.addText("Six methods, one patient base:  descriptive → inferential → regression → SEM → ARIMA → ML",
    { x: MX, y: 6.15, w: W - 2 * MX, h: 0.45, fontSize: 16, color: C.text2, bold: true, margin: 0, isTextBox: true, objectName: "method-chain" });
  s.addNotes("A private clinic earns most of its money from patients who come back, so it behaves like a service business. The manager has three questions: who is valuable, what keeps patients loyal, and how much demand to expect and who will leave. Each question maps to methods from the course outline, and all six methods run on the same patient base, so one stage feeds the next.");

  // ------------------------------------------------------------------ 3 data
  pres.addSection({ title: "Data & Method" });
  s = content("Data & Method", "A simulated clinic with a known ground truth");
  const stats3 = [["5,000", "patients"], ["24,872", "visits, 2023–2025"], ["1,500", "survey responses (20 Likert items)"], ["3", "linked tables: patients, visits, survey"]];
  for (let i = 0; i < 4; i++) {
    const x = MX + (i % 2) * 3.2, y = 1.65 + Math.floor(i / 2) * 2.25;
    card(s, x, y, 2.95, 2.0, "data-card-" + (i + 1));
    stat(s, x + 0.3, y + 0.25, 2.4, stats3[i][0], stats3[i][1], C.accent1, "data-stat-" + (i + 1));
  }
  s.addText("Why simulate?", { x: 7.3, y: 1.65, w: 5.4, h: 0.5, fontSize: 22, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: "why-head" });
  const whys = [[fa.FaLock, "Real patient records are confidential"],
                [fa.FaLink, "Need survey answers and visit history for the same patients"],
                [fa.FaCheckCircle, "True effects are known, so every method can be checked against the truth"]];
  for (let i = 0; i < 3; i++) {
    const y = 2.45 + i * 1.15;
    await circleIcon(s, whys[i][0], 7.3, y, 0.7, i === 2 ? C.accent2 : C.accent1, "why-" + (i + 1));
    s.addText(whys[i][1], { x: 8.25, y, w: 4.45, h: 0.8, fontSize: 16, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "why-text-" + (i + 1) });
  }
  s.addText("Generated by src/simulate.py (seed 3013): flu season, Tet holiday, growth, loyalty-driven return visits",
    { x: 7.3, y: 5.95, w: 5.4, h: 0.6, fontSize: 12, italic: true, color: C.accent5, margin: 0, isTextBox: true, objectName: "sim-note" });
  s.addNotes("Real patient data is confidential, and public datasets rarely have a survey and visit history for the same people. So I simulated a clinic in Ho Chi Minh City: 5,000 patients, about 25,000 visits over three years, and a 1,500-person survey. The simulation includes flu season, Tet and growth, and the same hidden loyalty score drives both the survey answers and how long a patient stays. Because I wrote the rules, I know the true effects and can check whether each method finds them.");

  // ------------------------------------------------------------------ 4 workflow
  s = content("Data & Method", "One workflow, six analysis stages");
  s.addImage({ path: FIG("f0_workflow.png"), x: 1.2, y: 1.45, w: 10.9, h: 10.9 * 515 / 1192, objectName: "workflow-diagram" });
  s.addText([{ text: "No data leakage: ", options: { bold: true } },
             { text: "features use visits up to 31 Dec 2024; targets (2025 spending, return in H1-2025) come only from later visits. Models are tested on a held-out 20% of patients." }],
    { x: MX, y: 6.15, w: W - 2 * MX, h: 0.55, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, objectName: "leakage-note" });
  s.addNotes("This is the workflow. The data are prepared once into patient features such as frequency, spending and recency, then six stages run. An important design choice is the cut-off date of 31 December 2024: features use only the past, targets use only the future. That is how a clinic would really use the model, and it prevents leakage.");

  // ------------------------------------------------------------------ 5 descriptive
  pres.addSection({ title: "Results" });
  s = content("Results", "A growing clinic with strong seasons and skewed money data");
  s.addImage({ path: FIG("f4_weekly_visits.png"), x: MX, y: 1.55, w: 8.3, h: 8.3 * 495 / 1246, objectName: "weekly-visits" });
  s.addText("Weekly visits grow from ~50 to ~300, with a winter peak and a sharp Tet drop every year",
    { x: MX, y: 4.95, w: 8.3, h: 0.5, fontSize: 13, italic: true, color: C.accent5, margin: 0, isTextBox: true, objectName: "weekly-caption" });
  const st5 = [["60%", "of patients spend nothing in the following year"], ["25 min", "median waiting time; longest in General Medicine"], ["1.7–3.1", "skewness of cost, wait and spend → log models and robust tests"]];
  for (let i = 0; i < 3; i++) {
    stat(s, 9.4, 1.55 + i * 1.65, 3.3, st5[i][0], st5[i][1], i === 0 ? C.accent2 : C.accent1, "desc-stat-" + (i + 1), 36);
  }
  s.addNotes("First, descriptive statistics. The clinic grows from about 50 to 300 visits a week, with a winter flu peak and a sharp drop at Tet. Money and time variables are strongly right-skewed, and 60 percent of patients spend nothing in the next year. These shapes decide the later methods: log transformation, a two-part model, and non-parametric robustness checks.");

  // ------------------------------------------------------------------ 6 tests
  s = content("Results", "Hypothesis tests: 3 of 6 supported, and the nulls matter too");
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
  const ok = (t) => ({ text: t, options: { bold: true, color: C.accent6 } });
  const no = (t) => ({ text: t, options: { color: C.accent5 } });
  const rows = [
    [hdr("Hypothesis"), hdr("Test"), hdr("Result"), hdr("Effect"), hdr("Decision")],
    ["H1  Programme members spend more", "Welch t + Mann–Whitney", "1.82M vs 1.09M VND, p < .001", "d = 0.37", ok("Supported")],
    ["H2b Chronic patients return more", "Chi-square", "48.7% vs 32.6%, p < .001", "V = 0.15", ok("Supported")],
    ["H4  Waiting time differs by department", "ANOVA + Kruskal–Wallis", "F = 491.6, p < .001", "η² = 0.073", ok("Supported")],
    ["H2  Return depends on insurance", "Chi-square", "p = .208", "V = 0.02", no("Not supported")],
    ["H3  Return depends on channel", "Chi-square", "p = .882", "V = 0.01", no("Not supported")],
    ["H5  Programme raises satisfaction", "Welch t", "p = .852", "d = 0.01", no("Not supported")],
  ];
  s.addTable(rows, { x: MX, y: 1.55, w: W - 2 * MX, colW: [3.9, 2.6, 2.9, 1.3, 1.433], fontSize: 14, color: C.text1,
    border: { type: "solid", pt: 0.75, color: "C9D8D8" }, rowH: 0.52, valign: "middle", margin: [0, 0.1, 0, 0.1], objectName: "tests-table" });
  card(s, MX, 5.4, W - 2 * MX, 1.05, "nulls-card");
  s.addText([{ text: "Why the nulls are useful: ", options: { bold: true, color: C.text2 } },
             { text: "online patients are as loyal as walk-ins, so the marketing channel can be chosen on cost alone. Effect sizes show H4 is real but modest." }],
    { x: MX + 0.3, y: 5.5, w: W - 2 * MX - 0.6, h: 0.85, fontSize: 15, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "nulls-text" });
  s.addNotes("I tested six hypotheses at alpha 0.05. Three are supported: programme members spend more, chronic patients return more, and waiting time differs by department, although the effect is modest. Three are not: insurance, acquisition channel, and programme membership do not affect returning or satisfaction. I report effect sizes, not just p-values, and robustness tests because the data are skewed.");

  // ------------------------------------------------------------------ 7 PLV model
  s = content("Results", "Two-part model ranks patients by next-year value");
  card(s, MX, 1.55, 5.2, 1.3, "part1-card");
  s.addText([{ text: "Part 1  ·  Will the patient spend?", options: { bold: true, color: C.accent1, breakLine: true } },
             { text: "Logistic regression, P(PLV > 0)" }],
    { x: MX + 0.3, y: 1.65, w: 4.6, h: 1.1, fontSize: 16, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "part1-text" });
  card(s, MX, 3.05, 5.2, 1.3, "part2-card");
  s.addText([{ text: "Part 2  ·  How much, if they spend?", options: { bold: true, color: C.accent1, breakLine: true } },
             { text: "OLS on log(PLV) + Duan smearing" }],
    { x: MX + 0.3, y: 3.15, w: 4.6, h: 1.1, fontSize: 16, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "part2-text" });
  stat(s, MX, 4.65, 2.5, "R² 0.40", "on unseen patients (baseline 0.00)", C.accent2, "plv-r2", 34);
  stat(s, MX + 2.7, 4.65, 2.5, "3.9M", "VND average spend of the top decile", C.accent1, "plv-top", 34);
  s.addChart(pres.charts.BAR, [{ name: "Mean actual 2025 spend ('000 VND)", labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
      values: [0, 7, 100, 161, 316, 662, 1258, 1675, 1898, 3925] }],
    { x: 6.2, y: 1.5, w: 6.5, h: 5.0, barDir: "col", chartColors: [HEX.accent1], showValue: true, dataLabelPosition: "outEnd",
      dataLabelColor: HEX.dk1, dataLabelFormatCode: "#,##0", showTitle: true, title: "Actual 2025 spend by predicted decile ('000 VND)",
      showLegend: false, catAxisTitle: "Predicted decile (1 = lowest)", showCatAxisTitle: true, catAxisTitleFontSize: 12,
      catAxisTitleColor: HEX.accent5, valAxisLabelFormatCode: "#,##0", barGapWidthPct: 40, ...chartText, objectName: "plv-decile-chart" });
  s.addNotes("For Patient Lifetime Value, 60 percent of patients spend zero, so ordinary regression fails. My first version actually gave a negative R-squared. The fix is the two-part model from health economics: a logistic model for whether a patient spends, times a log-OLS for how much, with Duan's smearing correction. On unseen patients it explains 40 percent of spending, and the decile chart shows it ranks patients very well: the top decile spends almost 4 million VND, the bottom spends nothing.");

  // ------------------------------------------------------------------ 8 PLV drivers
  s = content("Results", "Chronic and programme patients are worth the most");
  const drv = [[fa.FaHeartbeat, "+74%", "spending of chronic patients", C.accent2],
               [fa.FaClipboardList, "+30%", "spending of care-programme members", C.accent1],
               [fa.FaShieldAlt, "−25%", "out-of-pocket for insured patients", C.accent4],
               [fa.FaUserClock, "×0.61", "odds of any spending per extra month since last visit", C.accent3]];
  const dw = (W - 2 * MX - 3 * 0.35) / 4;
  for (let i = 0; i < 4; i++) {
    const x = MX + i * (dw + 0.35);
    card(s, x, 1.6, dw, 3.6, "driver-card-" + (i + 1));
    await circleIcon(s, drv[i][0], x + 0.3, 1.9, 0.85, drv[i][3], "driver-" + (i + 1));
    stat(s, x + 0.3, 2.95, dw - 0.6, drv[i][1], drv[i][2], drv[i][3], "driver-stat-" + (i + 1), 40);
  }
  card(s, MX, 5.5, W - 2 * MX, 0.95, "truth-card");
  s.addText([{ text: "Ground-truth check: ", options: { bold: true, color: C.text2 } },
             { text: "the true chronic visit multiplier (×1.82) lies inside the estimate's 95% CI (+53% to +98%). Diagnostics: max VIF 3.9, Durbin–Watson 2.00, HC3 robust SEs." }],
    { x: MX + 0.3, y: 5.55, w: W - 2 * MX - 0.6, h: 0.85, fontSize: 15, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "truth-text" });
  s.addNotes("The coefficients are easy to explain. Chronic patients spend 74 percent more, programme members 30 percent more, and insured patients pay 25 percent less out of pocket. Recency dominates whether a patient spends at all. These match the simulation rules: the true chronic effect lies inside the confidence interval. Assumption checks are fine, and I use robust standard errors because of mild heteroscedasticity.");

  // ------------------------------------------------------------------ 9 SEM
  s = content("Results", "Doctor communication drives satisfaction the most");
  s.addImage({ path: FIG("f8_sem_path_diagram.png"), x: MX - 0.1, y: 1.45, w: 7.6, h: 7.6 * 546 / 960, objectName: "sem-path-diagram" });
  const semStats = [["CFI 1.00", "RMSEA 0.000: excellent fit (expected: data follow the model)"], ["0.74–0.83", "Cronbach's α and CR: all constructs reliable"], ["CFI 0.50", "single-factor model fits badly: no common-method bias"]];
  for (let i = 0; i < 3; i++) stat(s, 8.6, 1.5 + i * 1.65, 4.1, semStats[i][0], semStats[i][1], i === 2 ? C.accent2 : C.accent1, "sem-stat-" + (i + 1), 32);
  s.addNotes("The structural equation model has six constructs measured by 20 Likert items. Doctor communication is the strongest driver of satisfaction, then service quality, access and price. Satisfaction drives loyalty with beta 0.69. Reliability is good, and validity checks pass. The fit is perfect because the survey was generated from this exact structure, and I say that openly. To show the fit indices can discriminate, a one-factor model fits badly.");

  // ------------------------------------------------------------------ 10 SEM vs truth
  s = content("Results", "SEM recovers the true effects, and loyalty predicts real visits");
  s.addChart(pres.charts.BAR, [
      { name: "Estimated", labels: ["SAT ← SQ", "SAT ← DC", "SAT ← AC", "SAT ← PF", "LOY ← SAT"], values: [0.347, 0.366, 0.269, 0.219, 0.692] },
      { name: "True value", labels: ["SAT ← SQ", "SAT ← DC", "SAT ← AC", "SAT ← PF", "LOY ← SAT"], values: [0.341, 0.399, 0.232, 0.244, 0.680] }],
    { x: MX, y: 1.5, w: 7.6, h: 5.0, barDir: "col", barGrouping: "clustered", chartColors: [HEX.accent1, HEX.accent5],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelColor: HEX.dk1,
      showLegend: true, legendPos: "t", legendFontSize: 12, showTitle: true, title: "Standardised path coefficients",
      valAxisMinVal: 0, valAxisMaxVal: 0.8, valAxisLabelFormatCode: "0.0", barGapWidthPct: 60, ...chartText, objectName: "sem-truth-chart" });
  card(s, 8.6, 1.6, 4.1, 2.2, "error-card");
  stat(s, 8.9, 1.8, 3.6, "≤ 0.04", "largest gap between estimate and truth", C.accent1, "sem-error", 40);
  card(s, 8.6, 4.1, 4.1, 2.4, "loyalty-card");
  stat(s, 8.9, 4.3, 3.6, "× 1.60", "odds of a real return visit per +1 SD of stated loyalty (p < .001)", C.accent2, "loyalty-or", 40);
  s.addNotes("Because I know the truth, I can compare: every estimated path is within 0.04 of its true value. The most practical finding links the survey to behaviour. For respondents in the cohort, one standard deviation more stated loyalty raises the odds of actually coming back by 1.6 times, even after controlling for recency. So a short survey carries real information.");

  // ------------------------------------------------------------------ 11 forecast
  s = content("Results", "Weekly demand forecast within ~5% error");
  s.addImage({ path: FIG("f10_forecast.png"), x: MX, y: 1.5, w: 8.0, h: 8.0 * 558 / 1379, objectName: "forecast-plot" });
  s.addChart(pres.charts.BAR, [{ name: "MAPE (%)", labels: ["Holt–Winters", "ARIMA(2,1,1)+Fourier", "Seasonal naive"], values: [4.51, 5.75, 19.38] }],
    { x: 8.9, y: 1.45, w: 3.85, h: 3.4, barDir: "bar", chartColors: [HEX.accent1, HEX.accent1, HEX.accent5], showValue: true,
      dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelColor: HEX.dk1, showLegend: false, showTitle: true,
      title: "Test MAPE, last 13 weeks (%)", valAxisHidden: true, catAxisLabelFontSize: 11, barGapWidthPct: 45, ...chartText,
      valGridLine: { style: "none" }, objectName: "mape-chart" });
  const fcNotes = [["Box–Jenkins:", "ADF → d = 1; AIC picks (2,1,1); Ljung–Box p = 0.90 (white-noise residuals)"],
                   ["Q1-2026 outlook:", "≈ 4,050 visits, ~310–330 per week, Tet week −61 visits"]];
  for (let i = 0; i < 2; i++) {
    card(s, MX + i * 6.15, 5.05, 5.9, 1.4, "fc-card-" + (i + 1));
    s.addText([{ text: fcNotes[i][0] + " ", options: { bold: true, color: C.text2 } }, { text: fcNotes[i][1] }],
      { x: MX + i * 6.15 + 0.3, y: 5.1, w: 5.3, h: 1.3, fontSize: 15, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "fc-text-" + (i + 1) });
  }
  s.addNotes("For demand, I aggregated visits by week. Following Box–Jenkins, differencing once makes the series stationary, AIC selects ARIMA(2,1,1) with Fourier terms for the yearly cycle and a Tet dummy, and the residuals are white noise. On the last quarter, ARIMA has 5.8 percent error and all points fall inside its interval. Holt–Winters is slightly better at 4.5 percent, and I report that honestly. Both beat the seasonal naive forecast by far. The outlook for Q1 2026 is about 4,050 visits.");

  // ------------------------------------------------------------------ 12 churn models
  s = content("Results", "Simple logistic regression predicts churn best");
  s.addChart(pres.charts.BAR, [{ name: "CV AUC", labels: ["Logistic regression", "Random forest", "MLP neural network", "Gradient boosting"], values: [0.887, 0.885, 0.879, 0.876] }],
    { x: MX, y: 1.5, w: 5.2, h: 3.6, barDir: "bar", chartColors: [HEX.accent2, HEX.accent1, HEX.accent1, HEX.accent1], showValue: true,
      dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000", dataLabelColor: HEX.dk1, showLegend: false, showTitle: true,
      title: "5-fold cross-validated AUC", valAxisMinVal: 0.8, valAxisMaxVal: 0.9, valAxisHidden: true, catAxisOrientation: "maxMin",
      barGapWidthPct: 45, ...chartText, valGridLine: { style: "none" }, objectName: "auc-chart" });
  s.addImage({ path: FIG("f12_roc_confusion.png"), x: 6.1, y: 1.5, w: 6.6, h: 6.6 * 611 / 1337, objectName: "roc-confusion" });
  card(s, MX, 5.35, W - 2 * MX, 1.1, "churn-card");
  s.addText([{ text: "Best model on test set: ", options: { bold: true, color: C.text2 } },
             { text: "accuracy 0.81, sensitivity 0.78, specificity 0.84. 300 of 383 churners caught; only 37 loyal patients contacted unnecessarily." }],
    { x: MX + 0.3, y: 5.4, w: W - 2 * MX - 0.6, h: 1.0, fontSize: 15, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "churn-text" });
  s.addNotes("Churn means a patient does not return within six months. I compared logistic regression, random forest, gradient boosting and a neural network with five-fold cross-validation. All are close, around 0.88 AUC, and the simple logistic regression is best. It catches 300 of 383 churners on the test set. Deep learning does not help on small tabular data, which matches the literature, and the simple model is easier for managers to trust.");

  // ------------------------------------------------------------------ 13 churn drivers
  s = content("Results", "Recency is the warning sign");
  s.addChart(pres.charts.BAR, [{ name: "AUC drop", labels: ["Recency", "Visit frequency", "Chronic condition", "Care programme", "Total spend", "Waiting time"],
      values: [0.343, 0.0124, 0.0061, 0.0030, 0.0029, 0.0014] }],
    { x: MX, y: 1.5, w: 7.4, h: 4.9, barDir: "bar", chartColors: [HEX.accent2, HEX.accent5, HEX.accent5, HEX.accent5, HEX.accent5, HEX.accent5],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000", dataLabelColor: HEX.dk1, showLegend: false,
      showTitle: true, title: "Permutation importance (drop in test AUC when shuffled)", valAxisHidden: true, catAxisOrientation: "maxMin",
      barGapWidthPct: 40, ...chartText, valGridLine: { style: "none" }, objectName: "importance-chart" });
  card(s, 8.4, 1.6, 4.3, 2.3, "recency-card");
  stat(s, 8.7, 1.8, 3.7, "× 16", "odds of churn per SD of recency (~6.5 months since last visit)", C.accent2, "recency-or", 44);
  card(s, 8.4, 4.15, 4.3, 2.25, "protect-card");
  stat(s, 8.7, 4.35, 3.7, "0.72 / 0.76", "odds ratios for chronic patients / programme members: they stay", C.accent1, "protect-or", 32);
  s.addNotes("What drives churn? Shuffling recency drops the AUC by 0.34, far more than any other feature. In odds terms, each standard deviation of time since the last visit, about six and a half months, multiplies churn odds by 16. Chronic patients and programme members are less likely to leave. So the practical rule is simple: watch the time since the last visit.");

  // ------------------------------------------------------------------ 14 recommendations
  pres.addSection({ title: "Conclusion" });
  s = content("Conclusion", "Recommendations for the clinic");
  const cols = [["For management & marketing", C.accent1, [
      [fa.FaChartLine, "Score patients by PLV every quarter; focus retention on the top deciles"],
      [fa.FaBell, "Send a reminder when a patient's last visit is ~3 months ago"],
      [fa.FaClipboardList, "Promote the care programme to chronic patients"]]],
    ["For patient care", C.accent2, [
      [fa.FaComments, "Train doctors in communication: the #1 driver of satisfaction"],
      [fa.FaUserClock, "Cut General Medicine waits with better scheduling"],
      [fa.FaCalendarAlt, "Staff to the weekly forecast: more in January, less at Tet"]]]];
  for (let c = 0; c < 2; c++) {
    const x = MX + c * 6.2;
    card(s, x, 1.55, 5.9, 4.95, "rec-card-" + (c + 1));
    s.addText(cols[c][0], { x: x + 0.35, y: 1.75, w: 5.2, h: 0.55, fontSize: 21, bold: true, color: cols[c][1], margin: 0, isTextBox: true, objectName: "rec-head-" + (c + 1) });
    for (let i = 0; i < 3; i++) {
      const y = 2.55 + i * 1.3;
      await circleIcon(s, cols[c][2][i][0], x + 0.35, y, 0.75, cols[c][1], `rec-${c + 1}-${i + 1}`);
      s.addText(cols[c][2][i][1], { x: x + 1.35, y: y - 0.1, w: 4.25, h: 0.95, fontSize: 16, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: `rec-text-${c + 1}-${i + 1}` });
    }
  }
  s.addNotes("Putting it together, for management: score patients by value every quarter, set an automatic reminder at about three months since the last visit, and promote the care programme to chronic patients. For patient care: train doctors in communication, reduce waiting times in General Medicine, and staff according to the weekly forecast.");

  // ------------------------------------------------------------------ 15 limitations
  s = content("Conclusion", "Limitations and future work");
  const lim = [["Limitations", C.accent5, ["Simulated data: shows the methods work, not facts about real clinics", "Near-perfect SEM fit would not happen with a real survey", "Random survey sample; fixed 6-month churn window", "Only three years of weekly data"]],
               ["Future work", C.accent1, ["Run the same code on real, anonymised clinic records", "Explainable AI (SHAP) for each churn prediction", "Survival analysis for time-to-churn", "Ethical AI: fairness audit across age, gender, insurance"]]];
  for (let c = 0; c < 2; c++) {
    const x = MX + c * 6.2;
    card(s, x, 1.55, 5.9, 4.95, "lim-card-" + (c + 1));
    await circleIcon(s, c === 0 ? fa.FaExclamationTriangle : fa.FaLightbulb, x + 0.35, 1.8, 0.75, lim[c][1], "lim-icon-" + (c + 1));
    s.addText(lim[c][0], { x: x + 1.3, y: 1.8, w: 4.3, h: 0.75, fontSize: 21, bold: true, color: C.text2, margin: 0, valign: "middle", isTextBox: true, objectName: "lim-head-" + (c + 1) });
    s.addText(lim[c][2].map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < lim[c][2].length - 1 } })),
      { x: x + 0.35, y: 2.85, w: 5.25, h: 3.4, fontSize: 16, color: C.text1, paraSpaceAfter: 10, margin: 0, valign: "top", isTextBox: true, objectName: "lim-list-" + (c + 1) });
  }
  s.addNotes("The main limitation is that the data are simulated. The project proves the methods work and recover known effects, not facts about real Vietnamese clinics. Next steps are real anonymised data, explainable AI so staff see why a patient is flagged, survival analysis, and a fairness audit so the models treat all patient groups fairly.");

  // ------------------------------------------------------------------ 16 closing
  s = pres.addSlide({ masterName: "DARK_TITLE", sectionTitle: "Conclusion" });
  s.addText("Thank you: questions?", { placeholder: "title" });
  s.addText("Value · Loyalty · Demand: one reproducible workflow, six methods", { placeholder: "body" });
  s.addText([{ text: "Code & data: ", options: { bold: true } }, { text: "github.com/Langl3y/STAT3013.R11.CTTT_Group10", options: { breakLine: true } },
             { text: "Reproduce: ", options: { bold: true } }, { text: "python src/run_all.py  (≈ 15 s)", options: { breakLine: true } },
             { text: "Demo video: ", options: { bold: true } }, { text: "see submission links file" }],
    { x: MX, y: 5.35, w: 10, h: 1.4, fontSize: 16, color: C.background1, margin: 0, valign: "top", isTextBox: true, objectName: "links" });
  s.addNotes("Thank you. All code and data are on GitHub and the whole analysis reproduces in about 15 seconds. I am happy to take questions.");

  fs.mkdirSync(OUT, { recursive: true });
  const file = path.join(OUT, "ClinicAnalytics_Slides.pptx");
  await pres.writeFile({ fileName: file });
  await applyTheme(file, THEME);
  console.log("saved", file);
}

main().catch((e) => { console.error(e); process.exit(1); });
