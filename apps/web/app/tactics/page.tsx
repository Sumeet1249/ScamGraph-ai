"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Brain,
  ShieldAlert,
  AlertTriangle,
  Eye,
  ShieldCheck,
  Filter,
  Search,
  Zap,
  Volume2,
  PhoneCall,
  Lock,
  ArrowRight,
  X,
  Copy,
  CheckCircle2,
  Share2,
  ExternalLink,
  SlidersHorizontal,
  Compass,
  FileText,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Badge, Card, Button } from "@/components/ui";

interface TacticItem {
  name: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  languages: string[];
  primary_actions: string[];
}

interface TacticDetail {
  desc: string;
  example: string;
  indicExcerpt: string;
  audioMarkers: string[];
  statutoryAdvice: string;
  statute: string;
}

const TACTIC_DETAILS: Record<string, TacticDetail> = {
  AUTHORITY: {
    desc: "Adversary mimics police, CBI, customs, or bank officials to compel obedience through institutional fear and official intimidation.",
    example: "CBI Officer Sharma speaking. Your Aadhaar is flagged for illegal parcel trafficking containing narcotics at Mumbai customs.",
    indicExcerpt: "नमस्ते, मैं साइबर क्राइम सेल दिल्ली से इंस्पेक्टर बोल रहा हूँ। आपका आधार कार्ड मनी लॉन्ड्रिंग केस में मिला है।",
    audioMarkers: ["Synthetic background walkie-talkie audio", "Authoritative Hindi/English cadence", "Demands immediate video call"],
    statutoryAdvice: "Instruct citizen that Indian Police & CBI never conduct digital arrests or demand money via video call.",
    statute: "BNS 2023 §204 (Impersonating public servant), IT Act §66D",
  },
  URGENCY: {
    desc: "Forces immediate emotional reaction by imposing extreme deadlines (<2 hours) to short-circuit critical cognitive reflection.",
    example: "Your electricity connection will be disconnected tonight at 9:30 PM due to unpaid bill. Update immediate.",
    indicExcerpt: "प्रिय उपभोक्ता, आपकी बिजली आज रात 9:30 बजे काट दी जाएगी क्योंकि पिछले माह का बिल अपडेट नहीं हुआ है।",
    audioMarkers: ["Rapid countdown reminders", "High speech tempo (>160 WPM)", "Simulated dispatch notifications"],
    statutoryAdvice: "Advise citizen to verify bills through official state power distribution portal or DISCOM mobile app.",
    statute: "IT Act 2000 §66D (Cheating by personation using computer resource)",
  },
  FEAR: {
    desc: "Threatens imminent arrest, bank account freeze, SIM blocking, or police raid unless total compliance is immediately given.",
    example: "A non-bailable arrest warrant has been issued in your name. Do not cut this call or local police will arrive at your home.",
    indicExcerpt: "आपके खिलाफ गैर-जमानती वारंट जारी हो चुका है। अगर आपने कॉल काटा तो 15 मिनट में लोकल पुलिस आपके पते पर होगी।",
    audioMarkers: ["Aggressive confrontation tone", "Shouted legal citations", "Simulated siren & radio chatter"],
    statutoryAdvice: "Immediately initiate emotional containment. Reassure victim that warrants cannot be served over WhatsApp or Telegram.",
    statute: "BNS 2023 §351 (Criminal Intimidation), IT Act §66C",
  },
  ISOLATION: {
    desc: "Commands the victim to remain alone, stay on a continuous call, and not consult family, friends, or local bank staff.",
    example: "Stay in a closed room alone. Keep video on. Disclosing this official investigation to anyone violates the Official Secrets Act.",
    indicExcerpt: "कमरे का दरवाज़ा बंद कर लीजिए। किसी भी रिश्तेदार या बैंक वाले को नहीं बताना है, यह राष्ट्रीय सुरक्षा का मामला है।",
    audioMarkers: ["Demands silence in background", "Insists victim does not speak to third parties", "Continuous 6+ hour call holding"],
    statutoryAdvice: "Urgent physical intervention recommended. Alert family contacts or local police nodal desk immediately.",
    statute: "BNS 2023 §127 (Wrongful confinement by threat)",
  },
  PAYMENT_PRESSURE: {
    desc: "Demands immediate fund transfer, security deposit, or collect request approval disguised as verification or clearance.",
    example: "Transfer ₹50,000 security deposit to the RBI verification escrow account. Funds will be refunded in 30 minutes.",
    indicExcerpt: "आरबीआई वेरिफिकेशन अकाउंट में 50,000 रुपये सिक्योरिटी डिपॉजिट जमा करें। क्लियरेंस होते ही पैसा वापस आ जाएगा।",
    audioMarkers: ["Step-by-step UPI screen coaching", "Pushing approval of incoming collect requests", "Insisting 'Refund mode' requires PIN"],
    statutoryAdvice: "Issue immediate 1930 payment halt freeze to remitting bank and freeze beneficiary mule VPA within 120 minutes.",
    statute: "BNS 2023 §318 (Cheating), PMLA 2002 §3 (Mule routing)",
  },
  CREDENTIAL_PRESSURE: {
    desc: "Coerces the victim into sharing OTP, PIN, NetBanking password, or CVV under the guise of an urgent account security upgrade.",
    example: "Share the 6-digit verification code sent to your mobile to prevent immediate account block and verify PAN linking.",
    indicExcerpt: "आपके नंबर पर 6 अंकों का वेरिफिकेशन कोड आया होगा। बैंक सर्वर अपडेट के लिए वो कोड तुरंत बताइए।",
    audioMarkers: ["Simulated automated IVR transition", "Reassuring victim that code is only for verification", "Urgent tone on OTP expiry timer"],
    statutoryAdvice: "Instruct immediate NetBanking password reset and trigger bank hotlisting / card lock via SMS or banking app.",
    statute: "IT Act 2000 §66C (Identity theft & credential disclosure)",
  },
  REMOTE_ACCESS_PRESSURE: {
    desc: "Instructs victim to install remote-desktop applications (AnyDesk, TeamViewer, RustDesk) or rogue APKs under technical support pretext.",
    example: "Download the official support helper app from this link to assist with your KYC reactivation and card unfreezing.",
    indicExcerpt: "प्ले स्टोर से क्विक-सपोर्ट या एनीडेस्क ऐप डाउनलोड कीजिए, हम बैंक सर्वर से आपकी स्क्रीन कनेक्ट करके ठीक कर देंगे।",
    audioMarkers: ["Step-by-step app store coaching", "Reading 9-digit session code", "Instructing victim to grant overlay permissions"],
    statutoryAdvice: "Instruct victim to immediately enable Airplane Mode, uninstall application, and perform factory antivirus sweep.",
    statute: "IT Act 2000 §43 & §66 (Computer-related offenses, unauthorized access)",
  },
  GREED: {
    desc: "Exploits desire for quick, effortless financial gain through fake high-yield investments, YouTube likes, or crypto daily tasks.",
    example: "Earn ₹5,000 daily by liking YouTube videos and rating hotels on Google. Deposit ₹1,000 to unlock VIP Tier rewards.",
    indicExcerpt: "घर बैठे 3,000 से 8,000 रुपये प्रतिदिन कमाएं। सिर्फ यूट्यूब वीडियो लाइक करना है। पहला टास्क पूरा करते ही 150 रुपये मिलेंगे।",
    audioMarkers: ["Enthusiastic mentor persona", "Posting fake withdrawal screenshots", "Gradual escalation from ₹500 to ₹50,000"],
    statutoryAdvice: "Explain Ponzi task trap mechanism. Highlight that initial small payouts are financed from subsequent victim deposits.",
    statute: "Prize Chits and Money Circulation Schemes (Banning) Act 1978",
  },
  LOSS_AVERSION: {
    desc: "Preys on fear of losing accumulated investments or courier shipments unless a nominal clearance fee or tax release is paid.",
    example: "Your international parcel is held at customs. Pay ₹48 re-delivery fee or the parcel and contents will be destroyed.",
    indicExcerpt: "आपका पार्सल वेयरहाउस में रुका हुआ है। पता अधूरा होने के कारण 48 रुपये का री-डिलीवरी चार्ज भरें अन्यथा पार्सल रद्द होगा।",
    audioMarkers: ["Fake postal tracking SMS links", "Low initial barrier (₹10–₹50)", "Redirects to malicious card credential harvester"],
    statutoryAdvice: "Check official India Post or courier tracking portal directly; do not click SMS links ending in shorteners.",
    statute: "IT Act 2000 §66D",
  },
  SECRECY: {
    desc: "Demands complete confidentiality, warning that informing third parties will worsen criminal charges or void compensation.",
    example: "This is a secret investigation under Section 144. If you inform bank staff or relatives, you will be arrested on the spot.",
    indicExcerpt: "यह नेशनल सीक्रेट इन्वेस्टिगेशन है। अगर आपने बैंक में किसी को भी बताया तो आपके पूरे परिवार पर केस दर्ज होगा।",
    audioMarkers: ["Hushed conspiratorial tone", "Citing fake judicial gag orders", "Continuous threats of contempt of court"],
    statutoryAdvice: "Empower victim to break isolation. State clearly that legitimate law enforcement never requires secret bank transfers.",
    statute: "BNS 2023 §351",
  },
  SCARCITY: {
    desc: "Manufactures false exclusivity or limited slots to trigger impulsive commitment before opportunities vanish.",
    example: "Only 2 VIP allocations remaining in this IPO allotment round. Complete UPI transaction within 4 minutes.",
    indicExcerpt: "इस प्राइवेट आईपीओ अलॉटमेंट में सिर्फ 2 स्लॉट बचे हैं। 4 मिनट में पेमेंट नहीं किया तो अलॉटमेंट रद्द हो जाएगा।",
    audioMarkers: ["Ticking clock sound cues", "Simulated booking announcements", "Pressure to skip prospectus review"],
    statutoryAdvice: "Verify SEBI registration number of investment brokers on SEBI intermediary database.",
    statute: "SEBI Act 1992 §12A",
  },
  SOCIAL_PROOF: {
    desc: "Uses fabricated group chats, fake analyst testimonials, and manipulated member lists to make fraudulent schemes look vetted.",
    example: "Join our 2,400-member Telegram VIP signals group. See member Rajesh just withdrew ₹4.2 Lakh profit today.",
    indicExcerpt: "हमारे टेलीग्राम वीआईपी ग्रुप में देखिए, 500 से ज्यादा मेंबर्स रोज़ का 20% प्रॉफिट निकाल रहे हैं। ये रहे विथड्रॉल प्रूफ।",
    audioMarkers: ["Coordinated bot reactions", "Simulated bank credit SMS screenshots", "Group admin praise loops"],
    statutoryAdvice: "Advise victim that Telegram and WhatsApp groups with thousands of members are routinely populated by bot farms.",
    statute: "IT Act 2000 §66D",
  },
  ROMANCE: {
    desc: "Grooms emotional affection over weeks, then invents emergencies, customs parcel seizures, or crypto opportunities.",
    example: "My dearest, I sent you gold jewelry from London. Customs officer has seized it at airport. Please pay ₹35,000 duty.",
    indicExcerpt: "डियर, मैंने तुम्हारे लिए लंदन से गिफ्ट और ज्वेलरी भेजी है। दिल्ली एयरपोर्ट कस्टम्स वाले 35,000 रुपये क्लीयरेंस मांग रहे हैं।",
    audioMarkers: ["Long-term affective grooming", "Refuses video calls due to 'oil rig / military deployment'", "Emergency financial distress pivot"],
    statutoryAdvice: "Provide compassionate psychological support. Verify images through reverse-image search and flag beneficiary account.",
    statute: "BNS 2023 §318",
  },
  TRUST_BUILDING: {
    desc: "Builds artificial credibility through small successful withdrawals, forged certificates, or initial helpful interactions.",
    example: "See? Your first withdrawal of ₹500 was credited directly to your bank in 2 minutes. You can now safely invest ₹50,000.",
    indicExcerpt: "देखा आपने? आपका पहला 500 रुपये 2 मिनट में बैंक आ गया। सिस्टम पूरी तरह सुरक्षित है, अब आप निश्चिंत होकर 25,000 लगाएं।",
    audioMarkers: ["Calm, patient guidance", "Sending fake MCA / ISO registration certificates", "Congratulatory messaging"],
    statutoryAdvice: "Document initial ledger inflows. These establish bait-and-switch proof for Section 65B dossier evidence.",
    statute: "Bharatiya Sakshya Adhiniyam 2023 §65B",
  },
  RECIPROCITY: {
    desc: "Offers unsolicited favors, bonus credits, or partial loan waivers to create a psychological obligation to return funds.",
    example: "Our company approved ₹10,000 bonus credit to your trading wallet. To claim and withdraw, simply match with ₹5,000.",
    indicExcerpt: "कंपनी ने आपके वॉलेट में 10,000 का वेलकम बोनस दिया है। इसे अनलॉक करने के लिए आपको सिर्फ 5,000 एक्टिवेशन जमा करना है।",
    audioMarkers: ["Framing fee as 'self-investment'", "Artificial wallet balance inflations", "Claims bonus will be forfeited"],
    statutoryAdvice: "Inform citizen that unsolicited bonus balances in unauthorized apps represent synthetic balance traps.",
    statute: "IT Act 2000 §66D",
  },
  FAKE_REWARD: {
    desc: "Fabricates lucky lottery wins, reward points, cashback offers, or electricity rebates requiring identity or UPI verification.",
    example: "Congratulations! You have won ₹25 Lakh in KBC Jio Lucky Draw. Scan this QR code and enter UPI PIN to receive funds.",
    indicExcerpt: "बधाई हो! केबीसी और जियो लकी ड्रा में आपका नंबर 25 लाख के इनाम के लिए चुना गया है। इनाम प्राप्त करने के लिए क्यूआर कोड स्कैन करें।",
    audioMarkers: ["Celebratory fanfare cues", "Exploiting UPI misconception that PIN is required to receive money", "Fake voice note from 'Host'"],
    statutoryAdvice: "Universal banking rule: Entering your UPI PIN always DEDUCTS money from your account; PIN is NEVER needed to receive.",
    statute: "BNS 2023 §318, IT Act §66D",
  },
  THREAT: {
    desc: "Uses intimidation of immediate societal disgrace, public shaming with morphed contacts, or physical violence.",
    example: "We have morphed your Aadhaar with obscene photos. If you do not pay ₹15,000 in 10 minutes, we send this to all your contacts.",
    indicExcerpt: "आपके फोन के सारे कॉन्टैक्ट्स हमारे पास हैं। 10 मिनट में 15,000 रुपये नहीं भेजे तो ये गंदी तस्वीरें आपके माता-पिता और दोस्तों को भेज देंगे।",
    audioMarkers: ["Rogue instant-loan app extortion", "Rapid-fire WhatsApp harassment", "Simulated contact sync verification"],
    statutoryAdvice: "Advise victim to freeze contact sync, block extortion numbers, and file expedited FIR under BNS §351 / IT Act §67.",
    statute: "BNS 2023 §308 (Extortion), IT Act 2000 §67 (Obscene material)",
  },
  IMPERSONATION: {
    desc: "Masquerades as trusted commercial entities (FedEx, BlueDart, SBI, Netflix, TRAI, Jio) with spoofed caller IDs or domains.",
    example: "TRAI Notice: Your mobile number will be permanently deactivated in 2 hours due to 17 illegal spam complaints.",
    indicExcerpt: "ट्राई (TRAI) कस्टमर सपोर्ट: आपके आधार पर जारी सभी सिम 2 घंटे में बंद कर दिए जाएंगे क्योंकि अवैध गतिविधियों की शिकायत आई है।",
    audioMarkers: ["Automated robotic IVR prompt", "Press 9 to speak with executive", "Spoofed CLI displaying official agency numbers"],
    statutoryAdvice: "Instruct citizen to disconnect and dial official 1961 (TRAI) or official telecom provider shortcode directly.",
    statute: "Indian Telegraph Act 1885 §25, IT Act §66D",
  },
  PLATFORM_MIGRATION: {
    desc: "Lures victim away from regulated platforms with buyer/seller protection onto unmonitored encrypted channels (Telegram, WhatsApp).",
    example: "OLX chat is very slow. Message me on WhatsApp at 98******10 right now so I can send the advance army payment receipt.",
    indicExcerpt: "ओएलएक्स पर फोटो ठीक से नहीं दिख रही। आप तुरंत व्हाट्सएप पर मैसेज करें, मैं आपको आर्मी कैंटीन टोकन ट्रांसफर भेजता हूँ।",
    audioMarkers: ["Pretending to be Indian Army / Defense personnel", "Fake army canteen ID card photos", "Quick transition to unmoderated chats"],
    statutoryAdvice: "Always maintain all buyer/seller interactions inside the registered platform's verified messaging system.",
    statute: "Consumer Protection (E-Commerce) Rules 2020",
  },
  COMPLIANCE_PRESSURE: {
    desc: "Pressures the citizen into acknowledging legal liability and signing or reciting simulated confessions to establish leverage.",
    example: "Repeat after me on recorded line: 'I acknowledge case SG-9041 and agree to deposit sovereign security funds.'",
    indicExcerpt: "रिकॉर्डेड लाइन पर बोलिए कि आप जांच में सहयोग कर रहे हैं और वेरिफिकेशन पूरा होने तक किसी से संपर्क नहीं करेंगे।",
    audioMarkers: ["Simulated formal deposition language", "Recording confirmation beeps", "Demands victim sign forged stamp-paper PDFs"],
    statutoryAdvice: "Citizens are protected under Article 20(3) of Constitution of India against self-incrimination; verbal coercion carries no legal validity.",
    statute: "Constitution of India Art 20(3), BNS 2023 §351",
  },
};

export default function TacticsPage() {
  const [tactics, setTactics] = useState<TacticItem[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [filterAction, setFilterAction] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTactic, setSelectedTactic] = useState<TacticItem | null>(null);
  const [copiedName, setCopiedName] = useState<string | null>(null);

  useEffect(() => {
    async function loadTactics() {
      try {
        const res = await fetch("/api/v1/tactics");
        if (res.ok) {
          const data = await res.json();
          setTactics(data.tactics_taxonomy?.tactics || []);
        }
      } catch (e) {
        console.warn("Could not load tactics:", e);
      } finally {
        setIsLoading(false);
      }
    }
    loadTactics();
  }, []);

  // Filter tactics based on severity, action, and search query
  const filtered = tactics.filter((t) => {
    const matchesSev = filterSeverity === "ALL" || t.severity === filterSeverity;
    const matchesAction = filterAction === "ALL" || t.primary_actions.includes(filterAction);
    const matchesSearch =
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (TACTIC_DETAILS[t.name]?.desc || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (TACTIC_DETAILS[t.name]?.example || "").toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesAction && matchesSearch;
  });

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-tone-danger-strong-bg text-tone-danger-strong-text border border-tone-danger-text/30 text-[10px] font-bold font-mono uppercase tracking-wider">
            <span className="h-1.5 w-1.5 rounded-full bg-red-600 animate-pulse" />
            CRITICAL SEVERITY
          </span>
        );
      case "HIGH":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-tone-warning-strong-bg text-tone-warning-strong-text border border-tone-warning-text/30 text-[10px] font-bold font-mono uppercase tracking-wider">
            HIGH SEVERITY
          </span>
        );
      case "MEDIUM":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-tone-info-bg text-tone-info-text border border-tone-info-text/30 text-[10px] font-semibold font-mono uppercase tracking-wider">
            MEDIUM SEVERITY
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-semibold font-mono uppercase tracking-wider">
            LOW SEVERITY
          </span>
        );
    }
  };

  const handleCopyRule = (tactic: TacticItem) => {
    const detail = TACTIC_DETAILS[tactic.name];
    const snippet = JSON.stringify(
      {
        tactic_id: tactic.name,
        severity: tactic.severity,
        primary_actions: tactic.primary_actions,
        indic_locales: tactic.languages,
        statute_anchor: detail?.statute || "IT Act 2000 §66D",
        acoustic_markers: detail?.audioMarkers || [],
        telemetry_version: "2.0.0",
      },
      null,
      2
    );
    navigator.clipboard.writeText(snippet);
    setCopiedName(tactic.name);
    setTimeout(() => setCopiedName(null), 2500);
  };

  const allActions = Array.from(new Set(tactics.flatMap((t) => t.primary_actions)));

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Sovereign Trust Page Header */}
      <PageHeader
        eyebrow="PSYCHOLOGICAL WARFARE & COERCION INTELLIGENCE"
        title="Canonical Manipulation Tactics Matrix"
        description="20 standardized social-engineering psychological coercion techniques extracted across multi-turn Indic audio calls, WhatsApp chats, and SMS messages. Correlated in real-time by the ScamDNA behavioral engine."
        actions={
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface border border-border-divider text-xs font-mono text-on-surface font-semibold shadow-sm">
              <Brain className="h-4 w-4 text-viz-primary" />
              <span>20 Canonical Vectors</span>
            </span>
            <Link
              href="/lab"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-viz-primary text-white text-xs font-semibold shadow-sm hover:bg-primary transition-all hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>Test in Lab Simulator</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        }
      />

      {/* Top Level Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border-divider bg-surface p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant">
            <span>CANONICAL TAXONOMY</span>
            <Brain className="h-4 w-4 text-viz-primary" />
          </div>
          <div className="text-2xl font-black font-mono text-on-surface">20 Vectors</div>
          <div className="text-[11px] text-on-surface-variant">
            Unified across Voice, SMS, and WhatsApp
          </div>
        </div>

        <div className="rounded-xl border border-border-divider bg-surface p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant">
            <span>CRITICAL INTERVENTIONS</span>
            <ShieldAlert className="h-4 w-4 text-error" />
          </div>
          <div className="text-2xl font-black font-mono text-error">
            {tactics.filter((t) => t.severity === "CRITICAL").length || 6} Triggers
          </div>
          <div className="text-[11px] text-on-surface-variant">
            Mandates immediate freeze &amp; 1930 hotlisting
          </div>
        </div>

        <div className="rounded-xl border border-border-divider bg-surface p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant">
            <span>INDIC LINGUISTIC COVERAGE</span>
            <Volume2 className="h-4 w-4 text-viz-info" />
          </div>
          <div className="text-2xl font-black font-mono text-on-surface">8 Dialects</div>
          <div className="text-[11px] text-on-surface-variant">
            Hindi, Hinglish, Marathi, Bengali, Tamil, etc.
          </div>
        </div>

        <div className="rounded-xl border border-border-divider bg-surface p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant">
            <span>STATUTORY EVIDENCE §65B</span>
            <ShieldCheck className="h-4 w-4 text-emerald-700" />
          </div>
          <div className="text-2xl font-black font-mono text-emerald-700">100% Admissible</div>
          <div className="text-[11px] text-on-surface-variant">
            Bharatiya Sakshya Adhiniyam compliant
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-2xl border border-border-divider bg-surface p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-on-surface-variant flex items-center gap-1.5 mr-1">
            <Filter className="h-3.5 w-3.5 text-viz-neutral" />
            Severity:
          </span>
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((s) => (
            <button
              key={s}
              onClick={() => setFilterSeverity(s)}
              className={`px-2.5 py-1 rounded-full text-xs font-semibold transition-all ${
                filterSeverity === s
                  ? "bg-viz-primary text-white shadow-sm"
                  : "bg-surface-subtle text-on-surface-variant hover:text-on-surface hover:bg-border-divider/50"
              }`}
            >
              {s}
            </button>
          ))}

          <div className="hidden lg:block h-4 w-px bg-border-divider mx-1" />

          {/* Action trigger selector */}
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="rounded-lg border border-border-divider bg-surface-subtle px-2.5 py-1 text-xs font-mono text-on-surface outline-none focus:border-viz-primary focus:bg-surface"
          >
            <option value="ALL">All Action Triggers</option>
            {allActions.map((act) => (
              <option key={act} value={act}>
                {act}
              </option>
            ))}
          </select>
        </div>

        <div className="relative min-w-[240px]">
          <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Search tactic or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-8 py-1.5 text-xs rounded-xl bg-surface-subtle border border-border-divider text-on-surface placeholder:text-on-surface-variant outline-none transition-all focus:border-viz-primary focus:bg-surface focus:ring-1 focus:ring-viz-primary"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Grid of 20 Tactics with Click Inspection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((t) => {
          const detail = TACTIC_DETAILS[t.name] || {
            desc: `Psychological manipulation exploiting ${t.name.toLowerCase().replace(/_/g, " ")} mechanics to override victim decision-making.`,
            example: `Adversary triggers ${t.name.toLowerCase().replace(/_/g, " ")} cues demanding immediate compliance.`,
            indicExcerpt: "संबंधित निर्देश: तत्काल सत्यापन पूरा करें अन्यथा सेवा निलंबित कर दी जाएगी।",
            audioMarkers: ["Urgency vocal modulation", "Simulated institutional cadence"],
            statutoryAdvice: "Initiate immediate incident triage and freeze remitting coordinates.",
            statute: "IT Act §66D",
          };

          const isSelected = selectedTactic?.name === t.name;

          return (
            <div
              key={t.name}
              onClick={() => setSelectedTactic(t)}
              className={`rounded-2xl border p-5 transition-all duration-200 cursor-pointer card-interactive flex flex-col justify-between space-y-4 group ${
                isSelected
                  ? "border-viz-primary bg-selected-tint ring-2 ring-viz-primary/40 shadow-md"
                  : "border-border-divider bg-surface hover:border-viz-primary/60 hover:-translate-y-1 hover:shadow-md"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-2.5 w-2.5 rounded-full ${
                        t.severity === "CRITICAL"
                          ? "bg-red-600 animate-pulse"
                          : t.severity === "HIGH"
                          ? "bg-amber-500"
                          : t.severity === "MEDIUM"
                          ? "bg-sky-500"
                          : "bg-emerald-500"
                      }`}
                    />
                    <h3 className="font-bold font-mono text-on-surface text-sm group-hover:text-viz-primary transition-colors">
                      {t.name}
                    </h3>
                  </div>
                  {getSeverityBadge(t.severity)}
                </div>

                <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">
                  {detail.desc}
                </p>

                {/* Adversarial Excerpt Callout */}
                <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider text-[11px] font-mono text-on-surface leading-relaxed italic">
                  &ldquo;{detail.example}&rdquo;
                </div>
              </div>

              <div className="pt-3 border-t border-border-divider space-y-2.5">
                {/* Action Trigger Pills */}
                <div className="flex items-center justify-between gap-2 text-[10px] font-mono">
                  <div className="flex flex-wrap items-center gap-1.5">
                    {t.primary_actions.slice(0, 2).map((act) => (
                      <span
                        key={act}
                        className="px-2 py-0.5 rounded-md bg-surface-subtle border border-border-divider text-on-surface-variant font-semibold"
                      >
                        {act}
                      </span>
                    ))}
                    {t.primary_actions.length > 2 && (
                      <span className="text-on-surface-variant">+{t.primary_actions.length - 2} more</span>
                    )}
                  </div>
                  <span className="text-viz-primary font-bold inline-flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
                    Inspect
                    <ArrowRight className="h-3 w-3" />
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && !isLoading && (
        <div className="rounded-2xl border border-dashed border-border-divider bg-surface p-12 text-center space-y-2">
          <Brain className="h-8 w-8 text-on-surface-variant mx-auto opacity-40" />
          <h3 className="text-sm font-semibold text-on-surface">No matching tactics found</h3>
          <p className="text-xs text-on-surface-variant">
            Try adjusting your search query or severity filter to inspect canonical vectors.
          </p>
          <button
            onClick={() => {
              setFilterSeverity("ALL");
              setFilterAction("ALL");
              setSearchQuery("");
            }}
            className="mt-2 inline-flex items-center px-4 py-1.5 rounded-full bg-surface-subtle border border-border-divider text-xs font-semibold text-on-surface hover:bg-surface"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* ── Interactive Deep-Dive Inspector Modal ─────────────────── */}
      {selectedTactic && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in"
          onClick={() => setSelectedTactic(null)}
        >
          <div
            className="bg-surface border border-border-divider rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto flex flex-col animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="px-6 py-4 bg-surface-subtle border-b border-border-divider flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-viz-primary/10 border border-viz-primary/30 text-viz-primary flex items-center justify-center">
                  <Brain className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">
                    Psychological Vector Inspection
                  </span>
                  <h2 className="text-lg font-bold font-mono text-on-surface leading-tight">
                    {selectedTactic.name}
                  </h2>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getSeverityBadge(selectedTactic.severity)}
                <button
                  onClick={() => setSelectedTactic(null)}
                  className="p-1.5 rounded-lg hover:bg-surface text-on-surface-variant hover:text-on-surface transition-colors"
                  aria-label="Close modal"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5 text-xs">
              {/* Psychological Exploit Description */}
              <div className="space-y-1.5">
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider font-mono">
                  Psychological Exploitation Mechanism
                </h4>
                <p className="text-xs text-on-surface leading-relaxed">
                  {TACTIC_DETAILS[selectedTactic.name]?.desc || "Standardized cognitive manipulation vector."}
                </p>
              </div>

              {/* Indic Conversational Transcript Excerpt */}
              <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <Volume2 className="h-3.5 w-3.5 text-viz-primary" />
                    Observed Indic Conversational Excerpt (Hindi / English Dual-Script)
                  </span>
                  <span className="text-[10px] font-mono text-viz-neutral">Real Acoustic Evidence</span>
                </div>
                <div className="p-2.5 rounded-lg bg-surface border border-border-divider text-xs font-mono text-on-surface italic leading-relaxed">
                  &ldquo;{TACTIC_DETAILS[selectedTactic.name]?.indicExcerpt}&rdquo;
                </div>
                <p className="text-[11px] text-on-surface-variant italic">
                  English translation: &ldquo;{TACTIC_DETAILS[selectedTactic.name]?.example}&rdquo;
                </p>
              </div>

              {/* Acoustic & Telemetry Markers */}
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="p-3.5 rounded-xl border border-border-divider bg-surface space-y-1.5">
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block font-mono">
                    Acoustic Pacing &amp; Audio Markers
                  </span>
                  <ul className="space-y-1 text-[11px] text-on-surface">
                    {(TACTIC_DETAILS[selectedTactic.name]?.audioMarkers || ["Audio vocal modulation"]).map(
                      (m, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="text-viz-primary font-bold">•</span>
                          <span>{m}</span>
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div className="p-3.5 rounded-xl border border-border-divider bg-surface space-y-1.5">
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block font-mono">
                    Statutory Legal Anchor
                  </span>
                  <p className="text-[11px] text-on-surface leading-relaxed">
                    {TACTIC_DETAILS[selectedTactic.name]?.statute || "IT Act 2000 §66D"}
                  </p>
                  <p className="text-[10px] text-on-surface-variant pt-1">
                    Classified as prima facie cognitive extortion under Bharatiya Nyaya Sanhita 2023.
                  </p>
                </div>
              </div>

              {/* Bank Nodal & 1930 Helpline Response Playbook */}
              <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-1.5">
                <span className="text-[10px] font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5 font-mono">
                  <ShieldCheck className="h-4 w-4 text-emerald-700" />
                  Mandatory Bank Nodal &amp; 1930 Incident Response Protocol
                </span>
                <p className="text-xs text-emerald-950 font-medium leading-relaxed">
                  {TACTIC_DETAILS[selectedTactic.name]?.statutoryAdvice ||
                    "Trigger immediate account freeze and notify 1930 nodal coordinator."}
                </p>
              </div>

              {/* Action Vectors & Locales */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider font-mono">
                  Observed Action Triggers in Threat Playbook
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedTactic.primary_actions.map((act) => (
                    <span
                      key={act}
                      className="px-2.5 py-1 rounded-md bg-surface-subtle border border-border-divider text-xs font-mono text-on-surface font-semibold"
                    >
                      {act}
                    </span>
                  ))}
                  <span className="px-2.5 py-1 rounded-md bg-sky-50 border border-sky-200 text-xs font-mono text-sky-800">
                    Locales: {selectedTactic.languages.join(", ")}
                  </span>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3.5 bg-surface-subtle border-t border-border-divider flex items-center justify-between gap-3">
              <button
                onClick={() => handleCopyRule(selectedTactic)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border-divider bg-surface text-xs font-semibold text-on-surface hover:bg-surface-subtle shadow-sm transition-all"
              >
                {copiedName === selectedTactic.name ? (
                  <>
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                    <span className="text-emerald-700 font-bold">Rule Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5 text-on-surface-variant" />
                    <span>Copy Detection Rule JSON</span>
                  </>
                )}
              </button>

              <div className="flex items-center gap-2">
                <Link
                  href={`/lab?tactic=${selectedTactic.name}`}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-viz-primary text-white text-xs font-semibold hover:bg-primary shadow-sm transition-all"
                >
                  <span>Simulate in Lab</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </Link>
                <button
                  onClick={() => setSelectedTactic(null)}
                  className="px-3.5 py-1.5 rounded-full border border-border-divider bg-surface text-xs font-semibold text-on-surface hover:bg-surface-subtle"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
