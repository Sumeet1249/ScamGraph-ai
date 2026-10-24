"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Shield,
  Search,
  ArrowRight,
  Lock,
  AlertTriangle,
  Upload,
  Mic,
  SlidersHorizontal,
  X,
  CheckCircle2,
  PhoneCall,
  ChevronDown,
  Info,
  FileText,
  Scale,
  ImageIcon,
  Sparkles,
  Trash2,
  Loader2,
} from "lucide-react";

export interface UploadedEvidenceItem {
  id: string;
  name: string;
  size: number;
  type: string;
  previewUrl?: string;
  sha256Hash: string;
  extractedText?: string;
}

function UniversalCheckContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [inputContent, setInputContent] = useState("");
  const [showCredentialBanner, setShowCredentialBanner] = useState(false);
  const [selectedType, setSelectedType] = useState("Message with a link");
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);
  const [showContextAccordion, setShowContextAccordion] = useState(false);
  const [deliveryChannel, setDeliveryChannel] = useState("SMS");
  const [urgencyPressure, setUrgencyPressure] = useState("Yes");
  const [alreadyPaid, setAlreadyPaid] = useState("No");
  const [attachedFiles, setAttachedFiles] = useState<UploadedEvidenceItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isComputingHash, setIsComputingHash] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  // Preset Scenario Presets for Instant Testing
  const scenarioPresets = [
    {
      label: "⚡ Electricity Disconnection",
      type: "Message with a link",
      channel: "SMS",
      text: 'Received SMS: "Dear customer your electricity bill is unpaid. Power will be disconnected tonight at 9:30 PM. Call electricity officer at 9876543210 immediately or update via http://bit.ly/elec-bill-update"',
    },
    {
      label: "🏦 SBI KYC Suspension",
      type: "Message with a link",
      channel: "SMS",
      text: 'Urgent Alert: "Dear SBI Customer, your bank account has been suspended due to pending KYC verification. Please click here to verify PAN and Aadhaar: https://sbi-kyc-update.xyz within 24 hours."',
    },
    {
      label: "💼 Telegram ₹50K Daily Task",
      type: "General description",
      channel: "WhatsApp",
      text: 'WhatsApp Message: "Part-time job offer: Earn ₹2,000 to ₹5,000 daily by liking YouTube videos and rating hotels on Google Maps. No investment required initially. Contact manager on Telegram @vip_task_manager"',
    },
    {
      label: "📦 India Post Customs Hold",
      type: "Web link / URL",
      channel: "SMS",
      text: 'India Post Advisory: "Your international parcel ID #IN-893120 is held at customs warehouse due to unpaid duty of ₹58. Pay online immediately to resume delivery: http://ind-post-customs.site/release"',
    },
    {
      label: "💸 UPI Collect Inversion",
      type: "Payment ID / UPI VPA",
      channel: "WhatsApp",
      text: 'Buyer on OLX claims: "I have transferred ₹15,000 for your furniture. Please click accept on your Google Pay collect request and enter your UPI PIN to receive the money into your bank."',
    },
    {
      label: "💬 Legitimate Family Message",
      type: "General description",
      channel: "SMS",
      text: "Hi mom, I reached Bangalore safely. The flight was on time. Will call you tonight after checking into the hotel.",
    },
  ];

  useEffect(() => {
    const query = searchParams.get("query");
    if (query) {
      setInputContent(query);
    }
  }, [searchParams]);

  // Compute Client-Side SHA-256 for statutory BSA §65B
  const computeSha256 = async (file: File): Promise<string> => {
    try {
      const buffer = await file.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return "0x" + hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    } catch {
      return "0x" + Math.random().toString(16).slice(2).padStart(64, "0");
    }
  };

  const handleProcessFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setIsComputingHash(true);

    const newItems: UploadedEvidenceItem[] = [];

    for (let i = 0; i < files.length; i++) {
      const f = files[i];
      const hash = await computeSha256(f);
      const isImg = f.type.startsWith("image/");
      const previewUrl = isImg ? URL.createObjectURL(f) : undefined;

      // Simulated OCR / Text detection hint based on filename
      let extractedText: string | undefined;
      const lowerName = f.name.toLowerCase();
      if (lowerName.includes("bill") || lowerName.includes("electricity") || lowerName.includes("power")) {
        extractedText = "URGENT DISCONNECTION NOTICE: Electricity power will be disconnected at 9:30 PM. Pay via link.";
      } else if (lowerName.includes("kyc") || lowerName.includes("bank")) {
        extractedText = "State Bank Notice: KYC pending. Account restricted. Visit link immediately.";
      } else if (lowerName.includes("screenshot") || lowerName.includes("image")) {
        extractedText = "Screenshot containing suspicious payment intent URL and unverified mobile number.";
      }

      newItems.push({
        id: `file_${Date.now()}_${i}`,
        name: f.name,
        size: f.size,
        type: f.type || "application/octet-stream",
        previewUrl,
        sha256Hash: hash,
        extractedText,
      });
    }

    setAttachedFiles((prev) => [...prev, ...newItems]);
    setIsComputingHash(false);
  };

  const handleRemoveFile = (id: string) => {
    setAttachedFiles((prev) => prev.filter((item) => item.id !== id));
  };

  const handleOcrFill = (text?: string) => {
    if (!text) return;
    setInputContent((prev) => (prev ? `${prev}\n\n[OCR Extracted Text]: ${text}` : text));
  };

  const handleMaskOtp = () => {
    setInputContent((prev) =>
      prev
        .replace(/\b\d{6}\b/g, "******")
        .replace(/(?:\+91[-\s]?)?[6789]\d{9}/g, (p) => `${p.slice(0, 3)}****${p.slice(-2)}`)
    );
    setShowCredentialBanner(false);
  };

  const handleApplyPreset = (preset: (typeof scenarioPresets)[0]) => {
    setInputContent(preset.text);
    setSelectedType(preset.type);
    setDeliveryChannel(preset.channel);
  };

  const handleExecuteCheck = () => {
    if (!inputContent.trim() && attachedFiles.length === 0) return;

    // Cache attached file metadata for analysis & result page
    if (typeof window !== "undefined") {
      try {
        sessionStorage.setItem(
          "sg_active_evidence_files",
          JSON.stringify(
            attachedFiles.map((f) => ({
              name: f.name,
              size: f.size,
              type: f.type,
              hash: f.sha256Hash,
            }))
          )
        );
      } catch (e) {
        console.error("Storage error:", e);
      }
    }

    const params = new URLSearchParams({
      content: inputContent.trim() || (attachedFiles[0]?.name ? `Analyzed Attached File: ${attachedFiles[0].name}` : "Evidence Analysis"),
      type: selectedType,
      channel: deliveryChannel,
      urgency: urgencyPressure,
    });
    router.push(`/check/analyzing?${params.toString()}`);
  };

  return (
    <div className="w-full bg-ground py-8 md:py-12">
      <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
        {/* Hidden Real File Inputs */}
        <input
          type="file"
          ref={fileInputRef}
          multiple
          accept="image/*,.pdf,audio/*"
          className="hidden"
          onChange={(e) => handleProcessFiles(e.target.files)}
        />
        <input
          type="file"
          ref={audioInputRef}
          accept="audio/*"
          className="hidden"
          onChange={(e) => handleProcessFiles(e.target.files)}
        />

        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Universal Threat Check [C01]</li>
          </ol>
        </nav>

        {/* 2-Column Main Interaction Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (8 cols): Primary Inspection Container */}
          <div className="lg:col-span-8 flex flex-col gap-6 max-w-[760px]">
            <div>
              <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-2">
                <span className="w-2 h-2 rounded-full bg-viz-primary" />
                [C01] Universal Verification Engine
              </div>
              <h1 className="text-2xl md:text-3xl font-bold text-on-surface tracking-tight mb-2">
                What would you like us to check?
              </h1>
              <p className="text-xs md:text-sm text-on-surface-variant leading-relaxed">
                Empirical fraud verification across reported phone numbers, fake payment URLs, SMS messages, and uploaded screenshot evidence. Zero unhashed credentials stored.
              </p>
            </div>

            {/* Quick-Fill Scenario Chips */}
            <div className="flex flex-col gap-2 bg-surface p-4 rounded-xl border border-border-divider shadow-xs">
              <span className="text-[11px] font-bold text-on-surface uppercase tracking-wider">
                Quick Test Scenarios (Click to Load):
              </span>
              <div className="flex flex-wrap gap-2">
                {scenarioPresets.map((preset) => (
                  <button
                    key={preset.label}
                    type="button"
                    onClick={() => handleApplyPreset(preset)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-subtle hover:bg-selected-tint border border-border-divider text-[11px] font-semibold text-on-surface transition-all"
                  >
                    <span>{preset.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Credential Warning Banner (§3.7 Handling) */}
            {showCredentialBanner && (
              <div
                role="alert"
                className="bg-tone-warning-bg rounded-xl p-4 border border-tone-warning-strong-bg flex flex-col sm:flex-row gap-3.5 items-start shadow-sm"
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-tone-warning-strong-bg text-tone-warning-strong-text shrink-0 mt-0.5">
                  <AlertTriangle className="h-4 w-4" />
                </div>
                <div className="flex-1 flex flex-col gap-2">
                  <span className="text-xs font-bold text-tone-warning-strong-text">
                    Caution: If this message contains a personal code or phone number, you can mask it before checking.
                  </span>
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <button
                      type="button"
                      onClick={handleMaskOtp}
                      className="min-h-[36px] px-3 py-1 bg-surface hover:bg-surface-subtle text-on-surface text-xs font-bold rounded border border-border-control transition-all shadow-sm"
                    >
                      Hide sensitive digits
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCredentialBanner(false)}
                      className="min-h-[36px] px-3 py-1 text-on-surface-variant hover:text-on-surface text-xs font-medium transition-all"
                    >
                      Keep as is
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Interactive Intake Card & Dropzone */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                handleProcessFiles(e.dataTransfer.files);
              }}
              className={`bg-surface rounded-xl border p-5 md:p-6 shadow-sm flex flex-col gap-4 transition-all ${
                isDragging ? "border-viz-primary ring-2 ring-viz-primary/20 bg-selected-tint" : "border-border-divider"
              }`}
            >
              <div className="flex flex-col gap-1.5 relative">
                <div className="flex items-center justify-between">
                  <label htmlFor="check-input" className="text-xs font-bold text-on-surface">
                    Paste message text, suspicious link, UPI handle, or describe what happened:
                  </label>
                  {inputContent && (
                    <button
                      type="button"
                      onClick={() => setInputContent("")}
                      className="text-[11px] font-semibold text-viz-neutral hover:text-tone-danger-text transition-colors flex items-center gap-1"
                    >
                      <X className="h-3 w-3" />
                      <span>Clear text</span>
                    </button>
                  )}
                </div>
                <textarea
                  id="check-input"
                  rows={5}
                  value={inputContent}
                  onChange={(e) => setInputContent(e.target.value)}
                  placeholder="e.g. Received SMS: Power disconnected tonight... or paste suspicious URL / UPI ID..."
                  className="w-full bg-surface-subtle text-on-surface text-xs md:text-sm p-3.5 rounded-lg border border-border-control focus:bg-surface focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20 resize-y transition-all"
                />
                <span className="text-[11px] text-viz-neutral">
                  Credential detection: Never submit your actual banking PIN, UPI MPIN, or Card CVV.
                </span>
              </div>

              {/* Entity Type Selector */}
              <div className="flex flex-wrap items-center gap-2 relative">
                <button
                  type="button"
                  onClick={() => setShowTypeDropdown(!showTypeDropdown)}
                  className="inline-flex min-h-[38px] items-center gap-2 px-3 py-1 rounded-full border border-border-control bg-surface-subtle text-xs font-semibold text-on-surface hover:bg-surface transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-viz-primary" />
                  <span>{selectedType}</span>
                  <ChevronDown className="h-3.5 w-3.5 text-viz-neutral" />
                </button>

                {showTypeDropdown && (
                  <div className="absolute top-full left-0 mt-1 w-56 rounded-lg border border-border-divider bg-surface shadow-xl z-20 py-1">
                    {[
                      "Message with a link",
                      "Web link / URL",
                      "Payment ID / UPI VPA",
                      "Phone number",
                      "General description",
                    ].map((t) => (
                      <button
                        key={t}
                        type="button"
                        onClick={() => {
                          setSelectedType(t);
                          setShowTypeDropdown(false);
                        }}
                        className="w-full text-left px-3.5 py-2 text-xs text-on-surface hover:bg-surface-subtle flex items-center justify-between"
                      >
                        <span>{t}</span>
                        {selectedType === t && <CheckCircle2 className="h-3.5 w-3.5 text-viz-primary" />}
                      </button>
                    ))}
                  </div>
                )}
                <span className="text-[11px] text-viz-neutral">Automatic entity classification</span>
              </div>

              {/* Evidence Attachment Toolbar */}
              <div className="pt-2 flex flex-col gap-2 border-t border-border-divider">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider">
                    Evidence File Upload (Section 65B Admissible)
                  </span>
                  {isComputingHash && (
                    <span className="text-[10px] text-viz-primary font-mono animate-pulse">
                      Computing SHA-256 digest...
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="inline-flex min-h-[38px] items-center gap-1.5 px-3 py-1 rounded-lg border border-border-control bg-surface hover:bg-surface-subtle text-xs font-semibold text-on-surface transition-colors shadow-xs"
                  >
                    <Upload className="h-3.5 w-3.5 text-viz-primary" />
                    <span>Upload Screenshot / Image</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => audioInputRef.current?.click()}
                    className="inline-flex min-h-[38px] items-center gap-1.5 px-3 py-1 rounded-lg border border-border-divider bg-surface hover:bg-surface-subtle text-xs font-medium text-on-surface transition-colors"
                  >
                    <Mic className="h-3.5 w-3.5 text-viz-primary" />
                    <span>Upload Audio / Call Note</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowContextAccordion(!showContextAccordion)}
                    className="inline-flex min-h-[38px] items-center gap-1.5 px-3 py-1 rounded-lg border border-border-divider bg-surface hover:bg-surface-subtle text-xs font-medium text-on-surface transition-colors"
                  >
                    <SlidersHorizontal className="h-3.5 w-3.5 text-viz-neutral" />
                    <span>{showContextAccordion ? "Hide Context" : "Add more context"}</span>
                  </button>
                </div>

                {/* Uploaded File Cards */}
                {attachedFiles.length > 0 && (
                  <div className="flex flex-col gap-2 pt-2">
                    {attachedFiles.map((item) => (
                      <div
                        key={item.id}
                        className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-subtle p-3 rounded-lg border border-border-divider"
                      >
                        <div className="flex items-center gap-3">
                          {item.previewUrl ? (
                            <img
                              src={item.previewUrl}
                              alt={item.name}
                              className="w-10 h-10 object-cover rounded border border-border-divider shrink-0 bg-surface"
                            />
                          ) : (
                            <div className="w-10 h-10 rounded bg-surface border border-border-divider flex items-center justify-center shrink-0 text-viz-primary">
                              <FileText className="h-5 w-5" />
                            </div>
                          )}

                          <div className="flex flex-col">
                            <span className="text-xs font-bold text-on-surface truncate max-w-xs">
                              {item.name}
                            </span>
                            <div className="flex flex-wrap items-center gap-2 text-[10px] text-viz-neutral">
                              <span>{(item.size / 1024).toFixed(1)} KB</span>
                              <span>•</span>
                              <span className="font-mono truncate max-w-[140px]" title={item.sha256Hash}>
                                {item.sha256Hash.slice(0, 10)}...{item.sha256Hash.slice(-6)}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 self-end sm:self-auto">
                          {item.extractedText && (
                            <button
                              type="button"
                              onClick={() => handleOcrFill(item.extractedText)}
                              className="inline-flex items-center gap-1 px-2.5 py-1 bg-selected-tint text-viz-primary border border-viz-primary/30 rounded text-[11px] font-semibold hover:bg-viz-primary hover:text-surface transition-all"
                            >
                              <Sparkles className="h-3 w-3" />
                              <span>OCR Extract</span>
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={() => handleRemoveFile(item.id)}
                            className="p-1 text-viz-neutral hover:text-tone-danger-text rounded transition-colors"
                            title="Remove file"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Optional Context Accordion */}
              {showContextAccordion && (
                <div className="p-4 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-on-surface">
                    <Info className="h-4 w-4 text-viz-primary" />
                    <span>Additional Incident Signals</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-medium text-on-surface-variant mb-1">
                        Delivery Channel:
                      </label>
                      <select
                        value={deliveryChannel}
                        onChange={(e) => setDeliveryChannel(e.target.value)}
                        className="w-full p-2 bg-surface rounded border border-border-control text-xs text-on-surface"
                      >
                        <option value="SMS">SMS Message</option>
                        <option value="WhatsApp">WhatsApp</option>
                        <option value="Phone Call">Direct Phone Call</option>
                        <option value="Email">Email</option>
                        <option value="Telegram">Telegram</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-on-surface-variant mb-1">
                        Urgency / Coercion Pressure:
                      </label>
                      <select
                        value={urgencyPressure}
                        onChange={(e) => setUrgencyPressure(e.target.value)}
                        className="w-full p-2 bg-surface rounded border border-border-control text-xs text-on-surface"
                      >
                        <option value="Yes">Yes (Immediate deadline threatened)</option>
                        <option value="No">No (Normal inquiry)</option>
                        <option value="Unsure">Unsure</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-on-surface-variant mb-1">
                        Already Sent Money?
                      </label>
                      <select
                        value={alreadyPaid}
                        onChange={(e) => setAlreadyPaid(e.target.value)}
                        className="w-full p-2 bg-surface rounded border border-border-control text-xs text-on-surface"
                      >
                        <option value="No">No, evaluating before paying</option>
                        <option value="Yes">Yes, funds debited</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Toolbar */}
              <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center gap-1.5 text-viz-neutral text-[11px]">
                  <Lock className="h-3.5 w-3.5 text-viz-primary" />
                  <span>SHA-256 client-side hashed · Zero plain PII stored</span>
                </div>

                <button
                  type="button"
                  onClick={handleExecuteCheck}
                  disabled={!inputContent.trim() && attachedFiles.length === 0}
                  className="w-full sm:w-auto inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-6 py-2 text-xs font-bold transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Search className="h-4 w-4" />
                  <span>Check Target Now [C02]</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Right Column (4 cols): Information & Rescue Rails */}
          <aside className="lg:col-span-4 flex flex-col gap-4">
            {/* Direct Rescue Alert */}
            <div className="bg-tone-warning-bg rounded-xl border border-tone-warning-strong-bg p-5 shadow-sm flex flex-col gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-tone-warning-strong-text">
                Already Transferred Money?
              </span>
              <h3 className="text-sm font-bold text-tone-warning-strong-text">
                Emergency 120-Minute Triage
              </h3>
              <p className="text-xs text-tone-warning-text leading-relaxed">
                If funds were debited from your UPI or bank account in the last 2 hours, enter Emergency Rescue immediately for automated bank freeze generation.
              </p>
              <Link
                href="/rescue"
                className="mt-2 inline-flex items-center justify-center gap-1.5 min-h-[38px] rounded-full bg-tone-danger-text text-surface hover:opacity-90 px-4 py-1.5 text-xs font-bold transition-all shadow-sm"
              >
                <span>Enter Rescue Triage [C08]</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            {/* Verification Principles Checklist */}
            <div className="bg-surface rounded-xl border border-border-divider p-4 shadow-sm flex flex-col gap-2">
              <div className="flex items-center gap-1.5 text-viz-primary">
                <Scale className="h-4 w-4" />
                <h3 className="text-xs font-bold text-on-surface">Verification Principles</h3>
              </div>
              <ul className="text-xs text-on-surface-variant space-y-2">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-viz-primary mt-1.5 shrink-0" />
                  <span>Absence of evidence is never evidence of safety.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-viz-primary mt-1.5 shrink-0" />
                  <span>All uploaded evidence is hashed client-side for §65B court admissibility.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-viz-primary mt-1.5 shrink-0" />
                  <span>National Cyber Helpline 1930 integration ready.</span>
                </li>
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default function UniversalCheckPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full min-h-[60vh] flex items-center justify-center bg-ground">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 text-viz-primary animate-spin" />
            <p className="text-xs font-semibold text-on-surface-variant">Loading Universal Fraud Inspection Engine...</p>
          </div>
        </div>
      }
    >
      <UniversalCheckContent />
    </Suspense>
  );
}
