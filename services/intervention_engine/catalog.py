"""Multilingual Message Catalog for Contextual Interventions (Phase 4B / Prompt 14).

Provides calm, non-alarmist, actionable consumer warnings localized across
English, Hindi, and Hinglish. No raw ML scores or internal engine jargon.
"""

from typing import Dict, List, NamedTuple


class LocalizedMessage(NamedTuple):
    headline: str
    message: str
    steps: List[str]


MESSAGE_CATALOG: Dict[str, Dict[str, LocalizedMessage]] = {
    # ── High-Risk Pre-Payment Interventions ──
    "payment.pause.high_risk": {
        "en": LocalizedMessage(
            headline="Pause Before Paying: High-Risk Threat Detected",
            message="This payment request exhibits signs of aggressive social-engineering and advance-fee fraud. Take a cooling-off period before initiating any transfer.",
            steps=[
                "Pause payment for 2 hours to break psychological manipulation.",
                "Verify beneficiary directly through official bank channels, not via caller links.",
                "Call the recipient on their known, verified personal number.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="भुगतान करने से पहले रुकें: उच्च जोखिम का खतरा",
            message="इस भुगतान अनुरोध में हेरफेर और धोखाधड़ी के स्पष्ट संकेत हैं। कोई भी राशि भेजने से पहले 2 घंटे का विश्राम लें।",
            steps=[
                "मनोवैज्ञानिक दबाव से बचने के लिए भुगतान 2 घंटे के लिए टालें।",
                "बैंक के आधिकारिक माध्यम से लाभार्थी की पुष्टि करें, कॉलर के लिंक से नहीं।",
                "प्राप्तकर्ता से उनके आधिकारिक या ज्ञात नंबर पर सीधे बात करें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Payment Karne Se Pehle Rukein: High Risk Alert",
            message="Is payment request mein fraud aur manipulation ke signs mile hain. Kisi bhi transfer se pehle thoda samay lein aur verify karein.",
            steps=[
                "Jaldbaazi mein payment na karein — 2 ghante ka cooling-off period lein.",
                "Beneficiary ko official bank app se check karein, message wale link se nahi.",
                "Recipient ko unke personal phone number par direct call karein.",
            ],
        ),
    },

    "payment.delay.task_scam": {
        "en": LocalizedMessage(
            headline="Task Scam Warning: Deposit Request After Small Reward",
            message="A common manipulation pattern observed: small initial payouts are used to build trust, followed by demands for larger deposits to unlock funds or tasks.",
            steps=[
                "Do not deposit funds to withdraw previously earned bonuses.",
                "Stop communication with the Telegram or WhatsApp task coordinator.",
                "Legitimate employers never demand security fees to assign tasks.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="टास्क स्कैम चेतावनी: छोटे इनाम के बाद जमा राशि की मांग",
            message="धोखाधड़ी का जाना-पहचाना तरीका: पहले छोटा इनाम देकर विश्वास जीतते हैं, फिर पैसे निकालने या नया टास्क देने के नाम पर बड़े डिपॉजिट मांगते हैं।",
            steps=[
                "कमाए हुए पैसे निकालने के लिए कोई भी नया भुगतान न करें।",
                "टेलीग्राम या व्हाट्सएप टास्क ग्रुप से तुरंत बाहर निकलें।",
                "कोई भी असली कंपनी काम देने के लिए अग्रिम शुल्क नहीं मांगती।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Task Scam Alert: Chhota Reward Dekar Badi Rakam Ki Maang",
            message="Scammers pehle 200-500 rupaye dekar trust banate hain, fir 'VIP Task' ya withdrawal ke naam par hazaron rupaye maangte hain.",
            steps=[
                "Apne paise nikalne ke liye koi extra deposit na karein.",
                "Telegram ya WhatsApp task group se turant exit karein.",
                "Asli companies kabhi kaam dene ke liye security deposit nahi maangti.",
            ],
        ),
    },

    # ── Anti-Isolation & Authority Interventions ──
    "isolation.talk_to_trusted_person": {
        "en": LocalizedMessage(
            headline="Anti-Isolation Warning: Talk to Someone You Trust",
            message="If someone instructed you to stay on video call, remain in a private room, or not consult family, bank, or police — this is a classic isolation tactic.",
            steps=[
                "Disconnect the call immediately; legitimate police will never interrogate via Skype/WhatsApp.",
                "Contact a trusted family member or friend right now and explain the situation.",
                "Call 1930 (National Cybercrime Helpline) or visit your local police station.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="अलगाव से बचें: किसी विश्वसनीय व्यक्ति से तुरंत बात करें",
            message="यदि कोई आपको वीडियो कॉल पर रहने, किसी कमरे में अकेले रहने या परिवार/पुलिस से बात न करने का दबाव बना रहा है — तो यह 'डिजिटल अरेस्ट' का तरीका है।",
            steps=[
                "कॉल तुरंत काट दें; पुलिस या सीबीआई कभी व्हाट्सएप/स्काइप पर गिरफ्तारी का वारंट नहीं भेजती।",
                "तुरंत अपने परिवार के किसी सदस्य या दोस्त को पूरी बात बताएं।",
                "राष्ट्रीय साइबर अपराध हेल्पलाइन 1930 पर कॉल करें या नजदीकी थाने जाएं।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Kisi Se Chhupayein Nahi: Apne Family Ya Dost Se Baat Karein",
            message="Agar samne wala keh raha hai ki 'kisi ko mat batana' ya 'video call disconnect mat karna' — toh ye Digital Arrest manipulation hai.",
            steps=[
                "Call turant disconnect karein; police WhatsApp ya Skype par case solve nahi karti.",
                "Apne kisi trusted dost ya family member ko abhi call karke batayein.",
                "Cybercrime helpline 1930 par call karke report karein.",
            ],
        ),
    },

    "authority.verify_independently": {
        "en": LocalizedMessage(
            headline="Authority Claim Alert: Verify Through Independent Channels",
            message="Demands for money backed by threats of arrest, legal prosecution, or SIM card disconnection are fraudulent. Verify directly with official departments.",
            steps=[
                "Do not make any payment under threat of immediate legal penalty.",
                "Find official phone numbers on verified .gov.in websites or your telecom provider's app.",
                "No Indian law enforcement agency demands fine payment via UPI personal handles.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="अधिकारी होने का दावा: आधिकारिक माध्यम से सीधे जांचें",
            message="गिरफ्तारी, कानूनी कार्रवाई या सिम बंद होने की धमकी देकर पैसे मांगना सरासर धोखाधड़ी है। संबंधित विभाग से सीधे संपर्क करें।",
            steps=[
                "कानूनी कार्रवाई की धमकी में आकर कोई भुगतान न करें।",
                "सरकारी .gov.in वेबसाइट या टेलीकॉम कंपनी के आधिकारिक ऐप से नंबर लेकर बात करें।",
                "कोई भी सरकारी संस्था यूपीआई पर्सनल हैंडल पर जुर्माना जमा नहीं करवाती।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Police Ya Officer Ka Dawa: Official Channel Se Check Karein",
            message="Arrest ya legal action ki dhamki dekar paise maangna 100% fraud hai. Kisi bhi official department ki direct inquiry karein.",
            steps=[
                "Dhamki ke darr se koi bhi transfer na karein.",
                "Official .gov.in portal ya bank branch jaakar confirm karein.",
                "Police ya CBI kabhi kisi personal UPI ID par paise nahi maangti.",
            ],
        ),
    },

    # ── Credential, OTP & Remote Access Safety ──
    "otp.do_not_share": {
        "en": LocalizedMessage(
            headline="Critical Warning: Never Share One-Time Passwords (OTPs)",
            message="An unverified party has requested an OTP or transaction authentication code. Sharing this gives the requester immediate access to your funds or account.",
            steps=[
                "Never share OTPs, UPI PINs, or MPINs with any caller or in chat.",
                "Legitimate bank or support representatives will never ask for your OTP.",
                "If you already entered an OTP, lock your card/account via your official mobile banking app immediately.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="अति महत्वपूर्ण: कभी भी अपना ओटीपी (OTP) साझा न करें",
            message="अनजान व्यक्ति ने आपसे ओटीपी या प्रमाणीकरण कोड मांगा है। ओटीपी देने पर आपके बैंक खाते से पैसे तुरंत कट सकते हैं।",
            steps=[
                "किसी भी कॉलर या चैट में ओटीपी, यूपीआई पिन या पासवर्ड न बताएं।",
                "बैंक या कस्टमर केयर कभी भी आपसे ओटीपी नहीं मांगते।",
                "यदि आपने ओटीपी बता दिया है, तो तुरंत अपने बैंकिंग ऐप से कार्ड/अकाउंट ब्लॉक करें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Alert: Apna OTP Kisi Ko Mat Dena",
            message="Kisine aapse OTP ya UPI PIN maanga hai. OTP share karte hi aapke account se paise kat sakte hain.",
            steps=[
                "Kisi bhi caller, message ya customer support ko OTP kabhi na dein.",
                "Bank ya official team kabhi OTP nahi maangti.",
                "Agar galti se share ho gaya hai toh turant bank app se card/UPI freeze karein.",
            ],
        ),
    },

    "credentials.do_not_share": {
        "en": LocalizedMessage(
            headline="Credential Theft Alert: Do Not Share Banking Passwords or PINs",
            message="This interaction attempts to collect private authentication credentials (PIN, password, CVV, or netbanking login).",
            steps=[
                "Do not type your banking password or PIN on third-party links.",
                "Ensure website URL is the exact official domain before logging in.",
                "Reset your netbanking password if entered on an unverified webpage.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="पासवर्ड सुरक्षा अलर्ट: गोपनीय बैंकिंग जानकारी न दें",
            message="यह बातचीत आपके गोपनीय बैंकिंग क्रेडेंशियल्स (पिन, पासवर्ड, सीवीवी या नेटबैंकिंग लॉगिन) चुराने का प्रयास कर रही है।",
            steps=[
                "किसी भी अनजान लिंक पर अपना पासवर्ड या यूपीआई पिन दर्ज न करें।",
                "लॉगिन करने से पहले हमेशा आधिकारिक डोमेन की जांच करें।",
                "यदि गलती से पासवर्ड दर्ज कर दिया है, तो तुरंत अपनी नेटबैंकिंग का पासवर्ड बदलें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Security Alert: Password Aur PIN Share Na Karein",
            message="Ye link ya caller aapse private password, ATM PIN ya CVV maang raha hai. Ye direct fraud ka sign hai.",
            steps=[
                "Kisi third-party link par apna banking password enter na karein.",
                "Sirf verified official banking app ka use karein.",
                "Agar password enter kar diya hai toh turant reset karein.",
            ],
        ),
    },

    "remote_access.do_not_install": {
        "en": LocalizedMessage(
            headline="High Risk: Do Not Install Remote-Access Software or APKs",
            message="You have been asked to install screen-sharing tools (AnyDesk, TeamViewer, RustDesk, QuickSupport) or an unknown APK file. This grants full control of your device.",
            steps=[
                "Refuse to install screen-sharing or remote-control apps.",
                "If already installed, turn off Wi-Fi/Mobile Data immediately and uninstall the app.",
                "Call your bank from another phone to temporarily lock digital transactions.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="भारी जोखिम: रिमोट-एक्सेस ऐप या अज्ञात APK इंस्टॉल न करें",
            message="आपसे स्क्रीन-शेयरिंग ऐप (जैसे AnyDesk, TeamViewer, RustDesk) या अज्ञात APK इंस्टॉल करने को कहा गया है। इससे जालसाज आपके पूरे फोन को नियंत्रित कर सकता है।",
            steps=[
                "किसी के कहने पर स्क्रीन-शेयरिंग या रिमोट कंट्रोल ऐप डाउनलोड न करें।",
                "यदि ऐप डाउनलोड हो गया है, तो तुरंत फोन का इंटरनेट बंद करें और ऐप अनइंस्टॉल करें।",
                "किसी अन्य फोन से अपने बैंक को कॉल करके डिजिटल सेवाएं ब्लॉक करवाएं।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Danger Alert: Screen-Sharing App Ya Unknown APK Install Mat Karein",
            message="Aapse AnyDesk, TeamViewer, QuickSupport ya koi unknown APK download karne ko bola gaya hai. Isse scammer aapka pura phone control kar lega.",
            steps=[
                "Kisi ke bolne par aisi koi app download na karein.",
                "Agar download ho gayi hai toh turant Mobile Data/Wi-Fi off karke app uninstall karein.",
                "Dusre phone se bank helpline par call karke accounts freeze karein.",
            ],
        ),
    },

    # ── Post-Loss Emergency Response ──
    "emergency.already_paid": {
        "en": LocalizedMessage(
            headline="Emergency Response: Action Required Immediately",
            message="You have indicated that a fraudulent transaction was completed. Quick action within the golden hour can help freeze the transfer before funds are cashed out.",
            steps=[
                "Call 1930 immediately (National Cybercrime Reporting Portal Helpline).",
                "Call your bank's 24/7 fraud emergency hotline to request an urgent transaction recall/freeze.",
                "Save transaction reference numbers (UTR, UPI Transaction ID) and chat screenshots.",
                "Beware of follow-up 'recovery agents' or 'lawyers' demanding fees to recover your money.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="आपातकालीन प्रतिक्रिया: तुरंत यह कदम उठाएं",
            message="धोखाधड़ी वाला लेनदेन पूरा हो चुका है। 'गोल्डन ऑवर' (पहले कुछ घंटों) में की गई कार्रवाई से पैसे रोके जा सकते हैं।",
            steps=[
                "तुरंत 1930 (राष्ट्रीय साइबर अपराध हेल्पलाइन) पर कॉल करें।",
                "अपने बैंक के 24/7 फ्रॉड हेल्पलाइन पर कॉल करके लेनदेन फ्रीज करने का अनुरोध करें।",
                "लेनदेन संदर्भ संख्या (UTR / UPI Transaction ID) और चैट के स्क्रीनशॉट संभाल कर रखें।",
                "पैसे वापस दिलाने का दावा करने वाले फर्जी वकीलों या 'रिकवरी एजेंटों' से सावधान रहें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Emergency Action: Paise Bhejne Ke Turant Baad Ye Karein",
            message="Agar transaction ho chuka hai toh 'Golden Hour' mein action lene se bank paise freeze kar sakta hai.",
            steps=[
                "Turant 1930 par call karein (National Cybercrime Portal helpline).",
                "Apne bank ki fraud hotline par call karke transaction UTR freeze karne ki request dalein.",
                "Transaction screenshot aur UTR number safe save karein.",
                "Paise wapas karane ke naam par dobara fees maangne wale fake recovery agents se bachein.",
            ],
        ),
    },

    # ── Legitimate & Educational ──
    "payment.safe.legitimate": {
        "en": LocalizedMessage(
            headline="Verified Context: No Significant Threat Observed",
            message="The payment context corresponds to standard regular transactions (e.g. rent, family transfer, verified utility bill) without social-engineering pressure.",
            steps=[
                "Confirm beneficiary name on your banking screen before authorizing.",
                "Normal security hygiene applies.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="सत्यापित संदर्भ: कोई दुर्भावनापूर्ण संकेत नहीं",
            message="यह भुगतान सामान्य लेनदेन (जैसे किराया, पारिवारिक सहायता, आधिकारिक बिल) से संबंधित प्रतीत होता है।",
            steps=[
                "भुगतान अधिकृत करने से पहले लाभार्थी का नाम बैंक स्क्रीन पर जांचें।",
                "सामान्य सुरक्षा सावधानियों का पालन करें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Verified Activity: Normal Payment Context",
            message="Ye payment request normal personal transfer (rent, family, bills) lag rahi hai bina kisi pressure ke.",
            steps=[
                "Payment finalize karne se pehle recipient ka naam check karein.",
                "Normal UPI security follow karein.",
            ],
        ),
    },

    "general.verify_independently": {
        "en": LocalizedMessage(
            headline="Verify Independently: Ambiguous Threat Indicators",
            message="Evidence is insufficient to confirm safety or malice. Independently verify the contact information before sharing details or money.",
            steps=[
                "Do not use contact numbers or links provided in the message.",
                "Search the official organization portal or app manually.",
                "Verify with a trusted acquaintance if unsure.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="स्वतंत्र रूप से पुष्टि करें: संदिग्ध संकेत मौजूद",
            message="सुरक्षा या खतरे की पुष्टि के लिए पर्याप्त सबूत नहीं हैं। कोई भी कदम उठाने से पहले आधिकारिक माध्यम से पुष्टि करें।",
            steps=[
                "संदेश में दिए गए फोन नंबर या लिंक पर भरोसा न करें।",
                "संबंधित संस्था के आधिकारिक ऐप या वेबसाइट पर जाकर सीधे जांचें।",
                "संदेह होने पर किसी परिचित व्यक्ति से सलाह लें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="Independently Verify Karein: Warning Signs Present",
            message="Pura confirmation nahi hai, lekin request thodi suspicious hai. Direct official channel se verify karein.",
            steps=[
                "Message wale number ya link par call/click na karein.",
                "Official app ya website par jakar manually check karein.",
                "Family ya kisi trusted person se consult karein.",
            ],
        ),
    },

    "general.educate": {
        "en": LocalizedMessage(
            headline="Security Advisory: Standard Precautions Apply",
            message="Mild anomalies observed in communication headers or unverified accounts. Exercise general vigilance.",
            steps=[
                "Check sender email or phone authenticity.",
                "Do not click unsolicited links.",
            ],
        ),
        "hi": LocalizedMessage(
            headline="सुरक्षा सलाह: सामान्य सतर्कता बरतें",
            message="संचार में कुछ असामान्य संकेत मिले हैं। सामान्य सावधानी बरतें।",
            steps=[
                "प्रेषक के ईमेल या फोन की प्रामाणिकता जांचें।",
                "अवांछित लिंक पर क्लिक न करें।",
            ],
        ),
        "hinglish": LocalizedMessage(
            headline="General Security Advice: Savdhani Bartein",
            message="Minor anomalies dikhi hain. Normal safety rules follow karein.",
            steps=[
                "Sender ki identity check karein.",
                "Unknown links par click na karein.",
            ],
        ),
    },
}


def get_localized_message(key: str, lang: str = "en") -> LocalizedMessage:
    """Retrieve localized message entry with fallback to English."""
    normalized_lang = (lang or "en").lower()
    if normalized_lang not in ("en", "hi", "hinglish"):
        normalized_lang = "en"
    
    catalog_entry = MESSAGE_CATALOG.get(key)
    if not catalog_entry:
        catalog_entry = MESSAGE_CATALOG["general.verify_independently"]
    
    return catalog_entry.get(normalized_lang) or catalog_entry["en"]
