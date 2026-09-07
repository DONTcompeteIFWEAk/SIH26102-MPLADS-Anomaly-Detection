// =========================================================
// BILINGUAL (EASY ENGLISH + सरल हिंदी) EXPLAINABILITY UTILITIES
// Designed for SIH26102 Hackathon Presentation to Judges & Evaluators
// =========================================================

/**
 * Generates plain, easy-to-understand English & Hindi explanations for any work record.
 * Strips away heavy bureaucratic jargon so judges and citizens can understand immediately.
 */
export function getBilingualExplanation(work) {
  if (!work) {
    return {
      easyEnglish: "Work metrics are in line with regular development guidelines.",
      hindi: "इस काम का बजट और विवरण सामान्य सरकारी नियमों के अनुकूल है।",
      reasons: ["Standard project clearance"],
      hindiReasons: ["सामान्य परियोजना"]
    };
  }

  const alloc = Number(work.allocation_amount || 0);
  const isSplit = Boolean(work.split_tender_flag);
  const isCluster = Boolean(work.cluster_work_flag);
  const isInaction = Boolean(work.prolonged_inaction_flag);
  const repeats = Number(work.same_work_location_count || 1);
  const days = Number(work.days_since_recommendation || 30);
  const ratio = Number(work.allocation_vs_state_median || 1.0);
  const status = String(work.status || "").toLowerCase();

  const englishPoints = [];
  const hindiPoints = [];

  // 1. GFR Rule 149 Tender-Splitting
  if (isSplit || (alloc >= 475000 && alloc <= 499999) || (alloc >= 950000 && alloc <= 999999) || (alloc >= 2400000 && alloc <= 2499999)) {
    let threshold = "₹5 Lakh";
    if (alloc >= 950000 && alloc <= 999999) threshold = "₹10 Lakh";
    if (alloc >= 2400000 && alloc <= 2499999) threshold = "₹25 Lakh";

    englishPoints.push({
      title: "Suspicious Budget (Tender-Splitting Trick)",
      desc: `The project cost of ₹${alloc.toLocaleString("en-IN")} is deliberately kept just below the mandatory ${threshold} e-tendering threshold (GFR Rule 149). Government law requires open competitive public bidding for projects worth ${threshold} or more. Setting it just below allows awarding contracts directly to favored contractors without open competition.`
    });

    hindiPoints.push({
      title: "ई-टेंडर से बचने की चालाकी (Tender Splitting)",
      desc: `इस काम का बजट ₹${alloc.toLocaleString("en-IN")} रखा गया है, जो सरकारी टेंडर सीमा (${threshold}) से ठीक थोड़ा कम है। सरकारी नियम (GFR 149) के अनुसार ${threshold} या उससे बड़े काम के लिए खुली बोली (e-tender) जरूरी होती है। शक है कि खुली प्रतिस्पर्धा से बचने और अपने चहेते ठेकेदार को बिना टेंडर काम देने के लिए बजट जानबूझकर सीमा से ठीक नीचे रखा गया है।`
    });
  }

  // 2. Localized Duplicate Clusters
  if (isCluster || repeats >= 3) {
    englishPoints.push({
      title: "Repeated Work in Same Village (Ghost Asset Risk)",
      desc: `The exact same work description was approved ${repeats > 1 ? repeats : 4} times in the exact same village/ward. In CAG audits, this frequently indicates 'ghost works' where the actual work is completed only once (or not at all), but multiple bills are passed on paper to siphon public funds.`
    });

    hindiPoints.push({
      title: "एक ही जगह बार-बार काम (फर्जी / दोहरा काम)",
      desc: `एक ही गांव या वार्ड में बिल्कुल एक जैसा काम ${repeats > 1 ? repeats : 4} बार मंजूर किया गया है। कैग (CAG) ऑडिट के अनुसार, कई बार जमीन पर काम केवल एक ही बार होता है या बिल्कुल नहीं होता, लेकिन कागजों पर 3-4 अलग-अलग बिल पास करवाकर सरकारी पैसे का गबन कर लिया जाता है।`
    });
  }

  // 3. Excessive Cost Inflation
  if (ratio >= 2.5) {
    englishPoints.push({
      title: "Severe Cost Inflation (Overpriced Work)",
      desc: `The cost of this project is ${ratio.toFixed(1)}x higher than the typical median cost of similar projects in this state. This signals heavy inflation of contractor estimates and detailed project reports (DPR).`
    });

    hindiPoints.push({
      title: "अत्यधिक लागत (ओवर-बिलिंग का शक)",
      desc: `इस काम की लागत राज्य में होने वाले इसी तरह के अन्य कामों के औसत से ${ratio.toFixed(1)} गुना ज्यादा है। इसमें ठेकेदार और अधिकारियों की मिलीभगत से कागजों पर लागत बढ़ाकर (Over-billing) दिखाने की प्रबल संभावना है।`
    });
  }

  // 4. Prolonged Inaction / Dormancy
  if (isInaction || (days >= 180 && status.includes("unsanctioned"))) {
    englishPoints.push({
      title: "Extreme Administrative Inaction (Project Stalled)",
      desc: `This work was recommended ${days} days ago by the MP but district authorities have kept it pending without sanction. MPLADS guidelines mandate clearance within 45 days. This 6+ month delay severely hurts local public welfare.`
    });

    hindiPoints.push({
      title: "काम में भारी देरी (प्रशासनिक लापरवाही)",
      desc: `सांसद द्वारा सिफारिश किए हुए ${days} दिन से अधिक बीत चुके हैं, लेकिन जिला प्रशासन ने इसे अब तक मंजूरी नहीं दी। सरकारी नियम के अनुसार 45 दिनों में काम मंजूर होना चाहिए था। यह जनता के विकास कार्य में घोर लापरवाही है।`
    });
  }

  // Fallback if none of the above
  if (englishPoints.length === 0) {
    englishPoints.push({
      title: "Conforms to Normal Developmental Guidelines",
      desc: `Work allocation amount ₹${alloc.toLocaleString("en-IN")} and location indicators conform to standard administrative patterns without red flags.`
    });
    hindiPoints.push({
      title: "सामान्य और पारदर्शी कार्य",
      desc: `इस काम का बजट ₹${alloc.toLocaleString("en-IN")} और अन्य विवरण सरकारी मानकों के अनुसार हैं। इसमें कोई वित्तीय गड़बड़ी नहीं पाई गई है।`
    });
  }

  return {
    easyEnglishSummary: englishPoints.map(p => `${p.title}: ${p.desc}`).join(" | "),
    hindiSummary: hindiPoints.map(p => `${p.title}: ${p.desc}`).join(" | "),
    englishPoints,
    hindiPoints
  };
}

/**
 * Generates simple, actionable audit directives in Easy English & Easy Hindi.
 */
export function getBilingualActions(work) {
  if (!work) {
    return {
      easyEnglish: "Routine administrative sanction and verification.",
      hindi: "नियमित प्रशासनिक जांच और सामान्य स्वीकृति।"
    };
  }

  const isSplit = Boolean(work.split_tender_flag);
  const isCluster = Boolean(work.cluster_work_flag);
  const isInaction = Boolean(work.prolonged_inaction_flag);
  const ratio = Number(work.allocation_vs_state_median || 1.0);

  const englishActions = [];
  const hindiActions = [];

  if (isSplit) {
    englishActions.push("Verify procurement method under GFR Rule 149 to check if open e-tenders were deliberately evaded.");
    hindiActions.push("खरीद नियमों (GFR 149) की जांच करें कि क्या खुली ई-टेंडरिंग से बचने के लिए बजट जानबूझकर छोटा रखा गया था।");
  }

  if (isCluster) {
    englishActions.push("Conduct a physical on-site audit with geo-tagged photographs to confirm if real assets exist on the ground and prevent ghost billing.");
    hindiActions.push("अधिकारी मौके पर जाकर जियो-टैग्ड फोटो के साथ भौतिक सत्यापन करें कि क्या काम वास्तव में हुआ है या सिर्फ कागजों पर बिल बनाया गया है।");
  }

  if (ratio >= 2.5) {
    englishActions.push("Scrutinize Detailed Project Report (DPR) and Schedule of Rates (SOR) to identify artificial cost inflation.");
    hindiActions.push("प्रोजेक्ट रिपोर्ट (DPR) और सरकारी रेट लिस्ट (SOR) की जांच करें ताकि पता चले कि लागत इतनी ज्यादा क्यों दिखाई गई है।");
  }

  if (isInaction) {
    englishActions.push("Issue statutory inquiry to the District Authority for violating the mandatory 45-day clearance deadline.");
    hindiActions.push("जिला अधिकारी को 45 दिनों में काम मंजूर न करने के संबंध में कारण बताओ नोटिस जारी करें।");
  }

  if (englishActions.length === 0) {
    englishActions.push("Proceed with routine milestone-based fund release upon receipt of physical progress certificate.");
    hindiActions.push("काम की प्रगति रिपोर्ट मिलने के बाद सामान्य तरीके से फंड जारी किया जा सकता है।");
  }

  return {
    englishActions,
    hindiActions,
    englishActionSummary: englishActions.join(" • "),
    hindiActionSummary: hindiActions.join(" • ")
  };
}

/**
 * Hindi explanations for Live Simulator drivers
 */
export const HINDI_SIMULATOR_TRANSLATIONS = {
  split_tender: {
    en: "Allocation falls in tender-split avoidance window (GFR Rule 149 evasion pattern)",
    hi: "ई-टेंडर से बचने का शक: बजट ₹5 लाख या ₹10 लाख की सीमा से ठीक थोड़ा कम रखा गया है।"
  },
  cluster: {
    en: "Repeated identical work count in the exact same village/block",
    hi: "फर्जी काम का खतरा: एक ही गांव में बार-बार वही काम दोहराया गया है।"
  },
  high_cost: {
    en: "Cost is significantly higher than standard state median benchmarks",
    hi: "लागत में हेराफेरी: राज्य के औसत खर्च से कई गुना ज्यादा महंगा बजट दिखाया गया है।"
  },
  inaction: {
    en: "Prolonged administrative dormancy elapsed without sanction",
    hi: "प्रशासनिक लापरवाही: 180 से अधिक दिन बीतने पर भी काम को लटका कर रखा गया है।"
  },
  clean: {
    en: "Work metrics conform to standard developmental distribution benchmarks",
    hi: "सामान्य कार्य: यह कार्य पूरी तरह से पारदर्शी और सरकारी नियमों के अनुकूल है।"
  }
};

/**
 * Returns clean, plain Hindi explanation for any detected anomaly reason.
 */
export function getSimulatorHindiReason(reason) {
  if (!reason) return "";
  const r = String(reason).toLowerCase();
  if (r.includes("tender-split") || r.includes("149") || r.includes("threshold") || r.includes("avoidance") || r.includes("evasion")) {
    return "ई-टेंडर से बचने का शक: बजट सरकारी ई-टेंडरिंग सीमा (₹5 लाख / ₹10 लाख) से ठीक नीचे रखा गया है ताकि खुली बोली से बचा जा सके।";
  }
  if (r.includes("repeat") || r.includes("cluster") || r.includes("identical") || r.includes("duplicate") || r.includes("village")) {
    return "दोहरा या फर्जी काम: एक ही गांव/वार्ड में बार-बार वही काम दोहराया गया है (कागजी बिलिंग का खतरा)।";
  }
  if (r.includes("cost") || r.includes("median") || r.includes("high") || r.includes("disparit") || r.includes("inflat")) {
    return "लागत में हेराफेरी: राज्य के सामान्य औसत से कई गुना ज्यादा बजट दिखाया गया है (ओवर-बिलिंग)।";
  }
  if (r.includes("delay") || r.includes("inaction") || r.includes("dormanc") || r.includes("pending") || r.includes("elapsed")) {
    return "प्रशासनिक लापरवाही: सिफारिश के बाद भी महीनों से काम बिना मंजूरी के लटका हुआ है।";
  }
  if (r.includes("vague") || r.includes("description") || r.includes("transparency")) {
    return "अस्पष्ट विवरण: काम का ब्योरा साफ नहीं है लेकिन बजट ₹5 लाख से ज्यादा पास किया गया है।";
  }
  return "वित्तीय विसंगति: यह कार्य सामान्य विकास मानकों से मेल नहीं खा रहा है।";
}

/**
 * Returns actionable Hindi directive for any statutory recommendation.
 */
export function getSimulatorHindiAction(action) {
  if (!action) return "";
  const a = String(action).toLowerCase();
  if (a.includes("gfr") || a.includes("tender") || a.includes("procurement") || a.includes("evad")) {
    return "सरकारी खरीद नियमों (GFR 149) की जांच करें कि क्या खुली ई-टेंडरिंग से बचने के लिए बजट जानबूझकर छोटा रखा गया।";
  }
  if (a.includes("physical") || a.includes("geo-tag") || a.includes("photo") || a.includes("site") || a.includes("ground") || a.includes("on-site")) {
    return "अधिकारी मौके पर जाकर जियो-टैग्ड फोटो के साथ भौतिक सत्यापन करें कि क्या काम वास्तव में जमीन पर हुआ है।";
  }
  if (a.includes("dpr") || a.includes("rates") || a.includes("sor") || a.includes("scrutiniz") || a.includes("inflat")) {
    return "विस्तृत प्रोजेक्ट रिपोर्ट (DPR) और सरकारी रेट लिस्ट (SOR) की जांच करें ताकि कृत्रिम लागत वृद्धि पकड़ी जा सके।";
  }
  if (a.includes("inquiry") || a.includes("deadline") || a.includes("notice") || a.includes("sla") || a.includes("statutory")) {
    return "45 दिनों में काम मंजूर न करने के संबंध में जिला अधिकारी को कारण बताओ नोटिस जारी करें।";
  }
  if (a.includes("routine") || a.includes("milestone") || a.includes("release")) {
    return "काम की भौतिक प्रगति रिपोर्ट मिलने के बाद सामान्य तरीके से फंड जारी किया जा सकता है।";
  }
  return "संबंधित दस्तावेजों और खर्च के बिलों का गहन ऑडिट करें।";
}

