'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function ProfilePrivacySettingsPage() {
  const [activeSection, setActiveSection] = useState<string>('account-security');
  const [language, setLanguage] = useState<string>('en-IN');
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  const [ephemeralStorage, setEphemeralStorage] = useState<boolean>(true);
  const [displayMasking, setDisplayMasking] = useState<boolean>(true);
  const [threatSharing, setThreatSharing] = useState<boolean>(true);
  const [savedToast, setSavedToast] = useState<boolean>(false);

  const handleSave = () => {
    setSavedToast(true);
    setTimeout(() => setSavedToast(false), 2500);
  };

  const navItems = [
    { id: 'account-security', label: 'Account & Security', icon: 'shield_person' },
    { id: 'language-theme', label: 'Language & Theme', icon: 'translate' },
    { id: 'privacy-dpdp', label: 'Privacy & Data Vault', icon: 'lock_reset', badge: 'Mandatory' },
    { id: 'threat-intelligence', label: 'Threat Sharing', icon: 'hub' },
    { id: 'export-deletion', label: 'Export & Deletion', icon: 'delete_forever', danger: true }
  ];

  return (
    <div className="w-full bg-ground py-4 sm:py-8 min-h-screen">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 pb-20 flex flex-col gap-6">
        {/* Top Breadcrumb & Status Header Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-border-divider">
          <div className="flex items-center gap-2 text-xs text-on-surface-variant">
            <Link className="hover:text-primary transition-colors" href="/">
              Home
            </Link>
            <span className="material-symbols-outlined text-[15px] text-viz-neutral">chevron_right</span>
            <span className="text-on-surface font-semibold">Profile and Settings</span>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-tone-info-bg text-tone-info-text text-xs border border-tone-info-text/20 self-start md:self-auto font-semibold uppercase tracking-wide">
            <span className="w-2 h-2 rounded-full bg-viz-info animate-pulse"></span>
            <span>DPDP Act 2023 Enforced · Sovereign Citizen Vault</span>
          </div>
        </div>

        {/* Page Title & Authority Descriptor */}
        <div className="max-w-3xl">
          <h1 className="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight">
            Profile and Privacy Settings
          </h1>
          <p className="text-sm text-viz-neutral mt-1 leading-relaxed">
            Manage your registered citizen credentials, local language preferences, and enforceable Digital Personal Data Protection (DPDP) Act 2023 sovereignty controls.
          </p>
        </div>

        {/* Master Two-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Navigation Rail (Sticky Desktop) */}
          <aside className="lg:col-span-3 lg:sticky lg:top-24 flex flex-col gap-4">
            <nav aria-label="Settings Sections" className="bg-surface rounded-xl p-2 border border-border-divider shadow-sm flex flex-col gap-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    activeSection === item.id
                      ? 'bg-primary text-white shadow-sm'
                      : item.danger
                      ? 'text-tone-danger-text hover:bg-tone-danger-bg'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-subtle'
                  }`}
                  type="button"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-surface-subtle text-primary border border-border-divider">
                      {item.badge}
                    </span>
                  )}
                </button>
              ))}

              <div className="my-1 h-px bg-border-divider"></div>

              <button
                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-viz-neutral hover:text-on-surface hover:bg-surface-subtle text-xs font-semibold text-left transition-colors"
                onClick={() => alert('Session terminated safely. Zero cache remains.')}
                type="button"
              >
                <span className="material-symbols-outlined text-[18px]">logout</span>
                <span>Sign out of session</span>
              </button>
            </nav>

            {/* Sovereign Guarantee Micro-Card */}
            <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-primary font-bold text-xs">
                <span className="material-symbols-outlined text-[16px]">verified_user</span>
                <span>Zero-Knowledge Proof</span>
              </div>
              <p className="text-[11px] text-viz-neutral leading-relaxed">
                Your profile vault is isolated by design. ScamGraph cannot view unredacted communications or personal payment handles.
              </p>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="lg:col-span-9 flex flex-col gap-6">
            {/* SECTION 1: ACCOUNT & SECURITY */}
            <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-5" id="account-security">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-border-divider">
                <div>
                  <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[20px]">badge</span>
                    <span>Citizen Account &amp; Credential Authentication</span>
                  </h2>
                  <p className="text-xs text-viz-neutral mt-0.5">Verified public identity anchor and hardware-level authentication status.</p>
                </div>
                <span className="text-xs text-primary px-3 py-1 rounded bg-secondary-container/40 font-mono font-bold self-start sm:self-center border border-primary/20">
                  Citizen ID: #CIT-84920-BLR
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Full Name */}
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface-variant">Registered Full Name</label>
                  <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs font-semibold">
                    <span>Aditi Sharma</span>
                    <span className="material-symbols-outlined text-[16px] text-viz-neutral">lock</span>
                  </div>
                  <span className="text-[10px] text-viz-neutral">Verified via Aadhaar Offline e-KYC Hash (Zero biometric log stored).</span>
                </div>

                {/* Email Anchor */}
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface-variant">Primary Emergency Contact Email</label>
                  <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs font-medium">
                    <span>aditi.sharma@example.com</span>
                    <span className="inline-flex items-center gap-1 text-viz-primary text-[10px] font-bold uppercase tracking-wider bg-tone-info-bg px-2 py-0.5 rounded border border-tone-info-text/20">
                      <span className="material-symbols-outlined text-[13px]">check_circle</span> Verified
                    </span>
                  </div>
                  <span className="text-[10px] text-viz-neutral">Receives urgent threat notifications and case timeline exports.</span>
                </div>

                {/* Mobile Anchor */}
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface-variant">Mobile Telephony Endpoint</label>
                  <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs font-mono font-semibold">
                    <span>+91 98765 43210</span>
                    <span className="inline-flex items-center gap-1 text-viz-primary text-[10px] font-bold">
                      <span className="material-symbols-outlined text-[14px]">sms</span> SMS 2FA Active
                    </span>
                  </div>
                </div>

                {/* Master Vault Passcode */}
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface-variant">Master Vault Passphrase</label>
                  <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs">
                    <span className="tracking-widest font-mono text-viz-neutral text-sm">••••••••••••••••</span>
                    <button
                      className="text-xs text-primary font-bold hover:underline"
                      onClick={() => alert('Password rotation prompt dispatched to your verified hardware key.')}
                      type="button"
                    >
                      Change password
                    </button>
                  </div>
                </div>
              </div>

              {/* MFA / Hardware Token */}
              <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-full bg-primary text-white flex items-center justify-center shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[20px]">key</span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-on-surface">Multi-Factor Authentication (MFA / Passkeys)</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-primary text-white">
                        Enforced
                      </span>
                    </div>
                    <p className="text-[11px] text-viz-neutral mt-0.5 leading-relaxed">
                      FIDO2 Hardware Key / App Authenticator (YubiKey 5Ci &amp; Google Authenticator active).
                    </p>
                  </div>
                </div>
                <button
                  className="h-8 px-3 rounded bg-surface border border-border-control text-on-surface text-xs font-semibold hover:bg-surface-subtle transition-colors shrink-0 shadow-sm"
                  onClick={() => alert('Hardware authenticator management module loaded.')}
                  type="button"
                >
                  Manage Keys
                </button>
              </div>
            </section>

            {/* SECTION 2: LANGUAGE & THEME */}
            <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-5" id="language-theme">
              <div className="pb-3 border-b border-border-divider">
                <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">language</span>
                  <span>Language &amp; Indic Script Adaptation</span>
                </h2>
                <p className="text-xs text-viz-neutral mt-0.5">Zero-clipping typographical metrics for high-stress comprehension across regional vernaculars.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Language Select */}
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-on-surface-variant" htmlFor="language-select">
                    Primary Interface Language
                  </label>
                  <select
                    id="language-select"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg bg-surface border border-border-control text-xs text-on-surface font-medium focus:ring-2 focus:ring-primary focus:outline-none"
                  >
                    <option value="en-IN">English (India) — Latin Baseline</option>
                    <option value="hi-IN">हिन्दी (Hindi) — Devanagari Script</option>
                    <option value="bn-IN">বাংলা (Bengali - Beta) — Eastern Nagari</option>
                    <option value="ta-IN">தமிழ் (Tamil - Coming Soon)</option>
                  </select>
                  <div className="p-3 rounded-lg bg-tone-info-bg text-tone-info-text flex items-start gap-2 border border-tone-info-text/20">
                    <span className="material-symbols-outlined text-[15px] shrink-0 mt-0.5">info</span>
                    <p className="text-[11px] leading-relaxed">
                      Indic typography automatically adapts line-height to prevent matra (halant &amp; vowel marker) clipping during active emergency triage.
                    </p>
                  </div>
                </div>

                {/* Theme Mode */}
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-on-surface-variant">Interface Display Calibration</label>
                  <div className="grid grid-cols-2 gap-3">
                    <div
                      onClick={() => setThemeMode('light')}
                      className={`p-3.5 rounded-lg cursor-pointer border-2 transition-all flex flex-col gap-1 ${
                        themeMode === 'light'
                          ? 'border-primary bg-selected-tint shadow-sm'
                          : 'border-border-divider bg-surface hover:bg-surface-subtle'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="material-symbols-outlined text-[18px] text-primary">light_mode</span>
                        <span className={`w-2.5 h-2.5 rounded-full ${themeMode === 'light' ? 'bg-primary' : 'bg-transparent'}`}></span>
                      </div>
                      <span className="text-xs font-bold text-on-surface mt-1">Sovereign Trust</span>
                      <span className="text-[10px] text-viz-neutral">High-contrast light mode</span>
                    </div>

                    <div
                      onClick={() => setThemeMode('dark')}
                      className={`p-3.5 rounded-lg cursor-pointer border-2 transition-all flex flex-col gap-1 ${
                        themeMode === 'dark'
                          ? 'border-primary bg-selected-tint shadow-sm'
                          : 'border-border-divider bg-surface hover:bg-surface-subtle'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="material-symbols-outlined text-[18px] text-viz-neutral">dark_mode</span>
                        <span className={`w-2.5 h-2.5 rounded-full ${themeMode === 'dark' ? 'bg-primary' : 'bg-transparent'}`}></span>
                      </div>
                      <span className="text-xs font-bold text-on-surface mt-1">Glacier Night</span>
                      <span className="text-[10px] text-viz-neutral">Low-glare subdued dark</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* SECTION 3: PRIVACY & DPDP CONTROLS */}
            <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-5" id="privacy-dpdp">
              <div className="pb-3 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-viz-primary text-[22px]">verified</span>
                  <h2 className="text-base font-bold text-on-surface">Privacy &amp; DPDP Sovereign Controls (§8 D12)</h2>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">Strict compliance with the Digital Personal Data Protection Act (2023) and client-side zero-credential scrub doctrine.</p>
              </div>

              <div className="flex flex-col gap-4">
                {/* Zero Credential Scrubbing */}
                <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex items-start gap-4">
                  <div className="w-9 h-9 rounded-full bg-primary text-white flex items-center justify-center shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[20px]">enhanced_encryption</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold text-on-surface">Client-Side Zero-Credential Scrubbing</h3>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-viz-primary text-white">
                        Always Active
                      </span>
                    </div>
                    <p className="text-[11px] text-viz-neutral mt-1 leading-relaxed">
                      Passwords, one-time passwords (OTPs), 6-digit UPI PINs, and credit card CVVs are intercepted and permanently scrubbed inside your local browser memory before data packets ever transmit to ScamGraph infrastructure. This protocol is mathematically mandatory and cannot be disabled.
                    </p>
                  </div>
                </div>

                {/* Ephemeral Check Storage Toggle */}
                <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-1.5">
                      <h3 className="text-xs font-bold text-on-surface">Ephemeral Check Storage (Auto-Purge 72h)</h3>
                      <span className="material-symbols-outlined text-[15px] text-viz-neutral">timer</span>
                    </div>
                    <p className="text-[11px] text-viz-neutral mt-0.5 leading-relaxed">
                      Automatically purge anonymous query artifacts, file hashes, and triage logs from your local session cache after 72 hours of inactivity.
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                    <input
                      checked={ephemeralStorage}
                      onChange={(e) => setEphemeralStorage(e.target.checked)}
                      className="sr-only peer"
                      type="checkbox"
                    />
                    <div className="w-11 h-6 bg-border-control rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border-control after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                {/* Pseudonymized Display Toggle */}
                <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-1.5">
                      <h3 className="text-xs font-bold text-on-surface">Pseudonymized Display Masking</h3>
                      <span className="material-symbols-outlined text-[15px] text-viz-neutral">visibility_off</span>
                    </div>
                    <p className="text-[11px] text-viz-neutral mt-0.5 leading-relaxed">
                      Mask suspect phone numbers, UPI handles, and bank account numbers across all graphs, triage reports, and shared evidence timelines (e.g. renders as <code className="bg-surface px-1 py-0.5 rounded text-primary font-mono text-[11px]">s•••••@okhdfcbank</code>).
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                    <input
                      checked={displayMasking}
                      onChange={(e) => setDisplayMasking(e.target.checked)}
                      className="sr-only peer"
                      type="checkbox"
                    />
                    <div className="w-11 h-6 bg-border-control rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border-control after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            </section>

            {/* SECTION 4: THREAT INTELLIGENCE SHARING */}
            <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-5" id="threat-intelligence">
              <div className="pb-3 border-b border-border-divider">
                <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">account_tree</span>
                  <span>Threat Intelligence Sharing &amp; Outbreak Clustering</span>
                </h2>
                <p className="text-xs text-viz-neutral mt-0.5">Empower collective civil defense while strictly segregating individual identities from topological graphs.</p>
              </div>

              <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-xs font-bold text-on-surface">Contribute Anonymized Threat Signatures</h3>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-tone-info-bg text-tone-info-text border border-tone-info-text/20">
                        Civil Defense Graph
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                      Allow anonymized, desensitized pattern signatures (e.g. fraudulent sender tags, malicious APK SHA-256 hashes, or newly observed fake payment gateways) to be clustered into the public outbreak graph to alert other citizens in real time.
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                    <input
                      checked={threatSharing}
                      onChange={(e) => setThreatSharing(e.target.checked)}
                      className="sr-only peer"
                      type="checkbox"
                    />
                    <div className="w-11 h-6 bg-border-control rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border-control after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="p-3 rounded-lg bg-surface border border-border-divider flex items-start gap-2.5 text-xs text-on-surface">
                  <span className="material-symbols-outlined text-viz-primary text-[18px] shrink-0 mt-0.5">gavel</span>
                  <div className="space-y-0.5">
                    <span className="font-bold">Strict Model &amp; Commercial Isolation Doctrine</span>
                    <p className="text-[11px] text-viz-neutral leading-relaxed">
                      Under no circumstances are citizen identity fields, real names, or unredacted conversation logs provided to commercial marketing brokers, data brokers, or third-party Large Language Model (LLM) training corpora.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* SECTION 5: DATA EXPORT & SOVEREIGN ERASURE */}
            <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-5" id="export-deletion">
              <div className="pb-3 border-b border-border-divider">
                <h2 className="text-base font-bold text-tone-danger-strong-text flex items-center gap-2">
                  <span className="material-symbols-outlined text-error text-[20px]">policy</span>
                  <span>Data Export &amp; Sovereign Erasure (Section 12 DPDP)</span>
                </h2>
                <p className="text-xs text-viz-neutral mt-0.5">Exercise your irrevocable legal right to data portability and complete digital erasure.</p>
              </div>

              {/* Action 1: Export Archive */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-surface-subtle border border-border-divider">
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold text-on-surface">Download Sovereign Data Archive (JSON + PDF)</span>
                  <p className="text-[11px] text-viz-neutral leading-relaxed max-w-xl">
                    Generate a cryptographically signed, timestamped archive containing all your submitted checks, forensic evidence uploads, and Rescue Dossier timelines.
                  </p>
                </div>
                <button
                  className="inline-flex items-center gap-1.5 px-4 h-9 rounded-lg border border-border-control bg-surface text-viz-text text-xs font-semibold hover:bg-surface-subtle shrink-0 transition-colors shadow-sm"
                  onClick={() => alert('Export request signed. Your encrypted ZIP download will compile within 60 seconds.')}
                  type="button"
                >
                  <span className="material-symbols-outlined text-[16px]">download</span>
                  <span>Request Data Archive</span>
                </button>
              </div>

              {/* Action 2: Sovereign Right to Erasure */}
              <div className="p-4 rounded-xl bg-tone-danger-bg border border-tone-danger-text/20 text-tone-danger-strong-text flex flex-col gap-4">
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-error text-[22px] shrink-0 mt-0.5">warning</span>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-bold text-tone-danger-strong-text">Execute Sovereign Right to Erasure</span>
                    <p className="text-xs text-tone-danger-text leading-relaxed">
                      Permanently purge your account, linked citizen ID, submitted evidence attachments, and active investigation dossiers across all ScamGraph data clusters. An immutable cryptographic tombstone receipt is produced as legal evidence of complete erasure.
                    </p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-tone-danger-strong-bg">
                  <span className="text-[11px] text-tone-danger-text font-semibold">
                    Warning: This operation is non-reversible under DPDP Section 12 doctrine.
                  </span>
                  <button
                    className="inline-flex items-center gap-1.5 px-4 h-9 rounded-lg bg-error text-white text-xs font-bold hover:bg-tone-danger-strong-text transition-colors shrink-0 shadow-sm"
                    onClick={() => {
                      if (confirm('ARE YOU ABSOLUTELY SURE?\n\nThis will permanently delete your account, dossiers, and encrypted artifacts. This action cannot be revoked.')) {
                        alert('Account erasure executed. Generating cryptographic proof of destruction.');
                      }
                    }}
                    type="button"
                  >
                    <span className="material-symbols-outlined text-[16px]">delete</span>
                    <span>Delete Account and All Case Data</span>
                  </button>
                </div>
              </div>
            </section>

            {/* Bottom Commit Bar */}
            <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
              <div className="flex items-center gap-2 text-xs text-on-surface-variant">
                <span className="material-symbols-outlined text-viz-primary text-[18px]">sync</span>
                <span>All modifications are cryptographically authenticated and synced with your session vault.</span>
              </div>
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  className="flex-1 sm:flex-none px-4 h-10 rounded-lg border border-border-control bg-surface text-xs font-semibold text-viz-text hover:bg-surface-subtle transition-colors"
                  type="button"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 h-10 px-6 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-all shadow-md"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[16px]">verified</span>
                  <span>{savedToast ? 'Changes Saved ✓' : 'Save Changes'}</span>
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
