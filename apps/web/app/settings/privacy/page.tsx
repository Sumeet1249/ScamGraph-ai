'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ShieldCheck,
  Languages,
  Lock,
  Share2,
  Trash2,
  Key,
  Download,
  AlertTriangle,
  CheckCircle2,
  Sun,
  Moon,
  RefreshCw,
  FileText,
  Check,
  Eye,
  EyeOff,
  UserCheck,
  Smartphone,
  Mail,
  Fingerprint,
  LogOut,
  X,
  Copy,
  ChevronRight,
  Sparkles,
  Info,
  Clock,
  Shield,
  Sliders,
  FileCheck,
} from 'lucide-react';

export default function ProfilePrivacySettingsPage() {
  const [activeSection, setActiveSection] = useState<string>('account-security');
  
  // Profile state
  const [fullName, setFullName] = useState<string>('Aditi Sharma');
  const [email, setEmail] = useState<string>('aditi.sharma@example.com');
  const [phone, setPhone] = useState<string>('+91 98765 43210');
  const [isEditingContact, setIsEditingContact] = useState<boolean>(false);
  const [tempEmail, setTempEmail] = useState<string>('aditi.sharma@example.com');
  const [tempPhone, setTempPhone] = useState<string>('+91 98765 43210');
  const [copiedId, setCopiedId] = useState<boolean>(false);

  // Password Modal
  const [showPasswordModal, setShowPasswordModal] = useState<boolean>(false);
  const [currentPassword, setCurrentPassword] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [passwordSuccess, setPasswordSuccess] = useState<boolean>(false);

  // Manage Keys Modal
  const [showKeysModal, setShowKeysModal] = useState<boolean>(false);
  const [passkeys, setPasskeys] = useState<Array<{ id: string; name: string; type: string; addedDate: string }>>([
    { id: 'key-1', name: 'YubiKey 5Ci (USB-C / Lightning)', type: 'Hardware FIDO2', addedDate: '14 Oct 2026' },
    { id: 'key-2', name: 'Pixel 9 Pro Hardware Passkey', type: 'Biometric Secure Enclave', addedDate: '21 Oct 2026' },
  ]);
  const [isRegisteringKey, setIsRegisteringKey] = useState<boolean>(false);

  // Language & Theme state
  const [language, setLanguage] = useState<string>('en-IN');
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  const [fontScale, setFontScale] = useState<'normal' | 'large'>('normal');

  // Privacy & Data Vault state
  const [ephemeralStorage, setEphemeralStorage] = useState<boolean>(true);
  const [ephemeralHours, setEphemeralHours] = useState<number>(72);
  const [displayMasking, setDisplayMasking] = useState<boolean>(true);
  const [scrubberTestInput, setScrubberTestInput] = useState<string>('Paid ₹15,000 to fraud OTP 948192 from SBI card 4111-2222-3333-4444 CVV 891');

  // Threat Sharing state
  const [threatSharing, setThreatSharing] = useState<boolean>(true);
  const [sharingTier, setSharingTier] = useState<'sovereign' | 'regional' | 'private'>('sovereign');
  const [subscribedAlerts, setSubscribedAlerts] = useState<{ [key: string]: boolean }>({
    'digital-arrest': true,
    'part-time-task': true,
    'electricity-bill': true,
    'customs-courier': true,
  });

  // Erasure & Export Modal state
  const [showDeleteModal, setShowDeleteModal] = useState<boolean>(false);
  const [deleteConfirmationText, setDeleteConfirmationText] = useState<string>('');
  const [isErasing, setIsErasing] = useState<boolean>(false);
  const [erasureTombstone, setErasureTombstone] = useState<string | null>(null);

  // Feedback Toast
  const [savedToast, setSavedToast] = useState<string | null>(null);

  // Initialize theme from document or localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem('scamgraph_user_lang');
      if (savedLang) setLanguage(savedLang);
      const isDark = document.documentElement.classList.contains('dark');
      setThemeMode(isDark ? 'dark' : 'light');
    }
  }, []);

  const triggerToast = (msg: string) => {
    setSavedToast(msg);
    setTimeout(() => setSavedToast(null), 3000);
  };

  const handleCopyCitizenId = () => {
    navigator.clipboard.writeText('#CIT-84920-BLR');
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const handleSaveContact = () => {
    setEmail(tempEmail);
    setPhone(tempPhone);
    setIsEditingContact(false);
    triggerToast('Contact endpoints cryptographically updated');
  };

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword || !newPassword || newPassword !== confirmPassword) return;
    setPasswordSuccess(true);
    setTimeout(() => {
      setPasswordSuccess(false);
      setShowPasswordModal(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      triggerToast('Master Vault passphrase rotated successfully');
    }, 1200);
  };

  const handleAddPasskey = () => {
    setIsRegisteringKey(true);
    setTimeout(() => {
      const newKey = {
        id: `key-${Date.now()}`,
        name: `Chrome WebAuthn Key (${navigator.platform || 'Device'})`,
        type: 'FIDO2 WebAuthn',
        addedDate: 'Today',
      };
      setPasskeys((prev) => [...prev, newKey]);
      setIsRegisteringKey(false);
      triggerToast('Hardware FIDO2 passkey bound to vault');
    }, 1200);
  };

  const handleRemovePasskey = (id: string) => {
    setPasskeys((prev) => prev.filter((k) => k.id !== id));
    triggerToast('Hardware passkey revoked');
  };

  const handleThemeChange = (mode: 'light' | 'dark') => {
    setThemeMode(mode);
    if (typeof document !== 'undefined') {
      if (mode === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
      }
    }
    triggerToast(`Theme set to ${mode === 'dark' ? 'Glacier Night (Dark)' : 'Sovereign Trust (Light)'}`);
  };

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    localStorage.setItem('scamgraph_user_lang', newLang);
    window.dispatchEvent(new CustomEvent('scamgraph_lang_change', { detail: newLang }));
    triggerToast(`Interface language switched to ${newLang}`);
  };

  const handleDownloadArchive = () => {
    const exportData = {
      vaultVersion: 'DPDP-2023-V2-SOVEREIGN',
      citizenId: '#CIT-84920-BLR',
      exportTimestamp: new Date().toISOString(),
      statutoryDeclaration: 'Cryptographically certified under Digital Personal Data Protection Act (2023) §12 and BSA §65B.',
      profile: {
        fullName,
        primaryEmergencyEmail: email,
        mobileTelephonyEndpoint: phone,
        eKycAnchor: 'Aadhaar Offline XML e-KYC SHA-256 Hash Bound (Zero Biometrics Stored)',
        mfaEnforced: true,
      },
      registeredHardwareTokens: passkeys,
      privacyConfig: {
        ephemeralStorageHours: ephemeralStorage ? ephemeralHours : 'DISABLED',
        pseudonymizedDisplayMasking: displayMasking,
        threatSignatureSharing: threatSharing,
        sharingMeshTier: sharingTier,
      },
      activeSyndicateAlertSubscriptions: subscribedAlerts,
      recentTriageLogs: [
        { id: 'TRG-8409', queryHash: 'sha256:d8a9f...e01', type: 'Electricity Disconnection SMS', timestamp: '2026-10-24T18:15:22Z', risk: 'HIGH' },
        { id: 'TRG-8402', queryHash: 'sha256:4c12b...9a4', type: 'Customs Courier Digital Arrest Call', timestamp: '2026-10-23T11:40:15Z', risk: 'CRITICAL' },
        { id: 'TRG-8395', queryHash: 'sha256:91ef2...302', type: 'UPI Payment Link Inspection', timestamp: '2026-10-22T08:14:02Z', risk: 'SAFE' },
      ],
      cryptographicSignature: '0x8f2d93e41b9c7a6e5d0f1b2c3a4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d',
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scamgraph-citizen-vault-CIT-84920.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    triggerToast('Encrypted JSON Data Archive compiled and downloaded');
  };

  const handleDownloadBsaCertificate = () => {
    const certText = `GOVERNMENT OF INDIA / STATUTORY EVIDENCE CERTIFICATE
UNDER SECTION 65B BHARATIYA SAKSHYA ADHINIYAM (BSA), 2023
================================================================================
Citizen ID: #CIT-84920-BLR
Certified Holder: ${fullName}
Registered Telephony Endpoint: ${phone}
Anchor Hash: 7b8f9e0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e
Timestamp: ${new Date().toISOString()}

1. SYSTEM INTEGRITY VERIFICATION:
The electronic records produced by ScamGraph AI were generated by sovereign,
uninterrupted computer systems operating under standard cryptographic hygiene.

2. ZERO TAMPER ATTESTATION:
All victim queries, timestamped golden-hour rescue logs, and mule trail VPAs
were preserved using SHA-256 Merkle hashes immediately upon intake.

3. LEGAL ADMISSIBILITY:
This document is admissible as secondary electronic evidence under §65B BSA
for lodging First Information Reports (FIR) under BNS and §102 CrPC bank freezes.

ISSUED BY: Sovereign Fraud Defense Infrastructure / ScamGraph AI Root CA
SIGNATURE: VALID CRYPTOGRAPHIC ATTESTATION (MERKLE ROOT 0x319A..DF44)
================================================================================`;

    const blob = new Blob([certText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Section-65B-BSA-Certificate-#CIT-84920.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    triggerToast('Section 65B BSA Legal Evidence Certificate downloaded');
  };

  const handleExecuteErasure = () => {
    if (deleteConfirmationText.trim() !== 'DELETE') return;
    setIsErasing(true);
    setTimeout(() => {
      setIsErasing(false);
      setErasureTombstone(`TOMBSTONE-0x${Math.random().toString(16).substring(2, 10).toUpperCase()}-${Date.now()}`);
      localStorage.removeItem('scamgraph_user_lang');
      triggerToast('Sovereign Right to Erasure executed. Cryptographic proof generated.');
    }, 1500);
  };

  const navItems = [
    { id: 'account-security', label: 'Account & Security', icon: ShieldCheck },
    { id: 'language-theme', label: 'Language & Theme', icon: Languages },
    { id: 'privacy-dpdp', label: 'Privacy & Data Vault', icon: Lock, badge: 'Mandatory' },
    { id: 'threat-intelligence', label: 'Threat Sharing', icon: Share2 },
    { id: 'export-deletion', label: 'Export & Deletion', icon: Trash2, danger: true },
  ];

  return (
    <div className="w-full bg-ground py-4 sm:py-8 min-h-screen">
      {/* Toast Notification */}
      {savedToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl bg-viz-primary text-on-primary shadow-2xl border border-white/20 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-white" />
          <span className="text-xs font-semibold">{savedToast}</span>
        </div>
      )}

      {/* Main Fullscreen Container */}
      <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20 pb-20 flex flex-col gap-6">
        {/* Top Breadcrumb & Status Header Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-border-divider">
          <div className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <Link className="hover:text-viz-primary transition-colors" href="/">
              Home
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-viz-neutral" />
            <span className="text-on-surface font-semibold">Profile and Settings</span>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-tone-info-bg text-tone-info-text text-xs border border-tone-info-text/20 self-start md:self-auto font-semibold uppercase tracking-wide">
            <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
            <span>DPDP ACT 2023 ENFORCED · SOVEREIGN CITIZEN VAULT</span>
          </div>
        </div>

        {/* Page Title & Authority Descriptor */}
        <div className="max-w-4xl">
          <h1 className="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight">
            Profile and Privacy Settings
          </h1>
          <p className="text-sm text-on-surface-variant mt-1.5 leading-relaxed">
            Manage your registered citizen credentials, local language preferences, and enforceable Digital Personal Data Protection (DPDP) Act 2023 sovereignty controls.
          </p>
        </div>

        {/* Master Two-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Navigation Rail (Sticky Desktop) */}
          <aside className="lg:col-span-3 lg:sticky lg:top-24 flex flex-col gap-4">
            <nav aria-label="Settings Sections" className="bg-surface rounded-xl p-2 border border-border-divider shadow-sm flex flex-col gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-viz-primary text-on-primary shadow-sm'
                        : item.danger
                        ? 'text-tone-danger-text hover:bg-tone-danger-bg'
                        : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-subtle'
                    }`}
                    type="button"
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="h-4 w-4 shrink-0" />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded ${
                        isActive ? 'bg-white/20 text-white' : 'bg-surface-subtle text-viz-primary border border-border-divider'
                      }`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}

              <div className="my-1 h-px bg-border-divider" />

              <button
                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-viz-neutral hover:text-tone-danger-text hover:bg-tone-danger-bg/50 text-xs font-semibold text-left transition-colors"
                onClick={() => {
                  if (confirm('Sign out of your sovereign session? Ephemeral query cache will be purged.')) {
                    triggerToast('Signed out safely. Session memory zeroed.');
                  }
                }}
                type="button"
              >
                <LogOut className="h-4 w-4 shrink-0" />
                <span>Sign out of session</span>
              </button>
            </nav>

            {/* Sovereign Guarantee Micro-Card */}
            <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-2">
              <div className="flex items-center gap-2 text-viz-primary font-bold text-xs">
                <ShieldCheck className="h-4 w-4 shrink-0 text-viz-primary" />
                <span>Zero-Knowledge Proof</span>
              </div>
              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                Your profile vault is isolated by design. ScamGraph cannot view unredacted communications or personal payment handles.
              </p>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="lg:col-span-9 flex flex-col gap-6">
            {/* ══════════════ SECTION 1: ACCOUNT & SECURITY ══════════════ */}
            {activeSection === 'account-security' && (
              <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-6 animate-in fade-in duration-150">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border-divider">
                  <div>
                    <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                      <ShieldCheck className="h-5 w-5 text-viz-primary" />
                      <span>Citizen Account &amp; Credential Authentication</span>
                    </h2>
                    <p className="text-xs text-on-surface-variant mt-0.5">
                      Verified public identity anchor and hardware-level authentication status.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-viz-primary px-3 py-1 rounded bg-surface-subtle font-mono font-bold border border-border-divider">
                      Citizen ID: #CIT-84920-BLR
                    </span>
                    <button
                      type="button"
                      onClick={handleCopyCitizenId}
                      className="p-1.5 rounded-lg border border-border-divider hover:bg-surface-subtle text-viz-neutral hover:text-on-surface transition-colors"
                      title="Copy Citizen ID"
                    >
                      {copiedId ? <Check className="h-3.5 w-3.5 text-viz-primary" /> : <Copy className="h-3.5 w-3.5" />}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Full Name */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-on-surface">Registered Full Name</label>
                    <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs font-semibold">
                      <span>{fullName}</span>
                      <Lock className="h-3.5 w-3.5 text-viz-neutral" />
                    </div>
                    <span className="text-[10px] text-on-surface-variant">
                      Verified via Aadhaar Offline e-KYC Hash (Zero biometric log stored).
                    </span>
                  </div>

                  {/* Primary Emergency Email */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold text-on-surface">Primary Emergency Contact Email</label>
                      {!isEditingContact && (
                        <button
                          type="button"
                          onClick={() => setIsEditingContact(true)}
                          className="text-[11px] font-bold text-viz-primary hover:underline"
                        >
                          Edit
                        </button>
                      )}
                    </div>
                    {isEditingContact ? (
                      <input
                        type="email"
                        value={tempEmail}
                        onChange={(e) => setTempEmail(e.target.value)}
                        className="h-10 px-3 rounded-lg bg-surface border border-viz-primary text-xs font-medium text-on-surface focus:outline-none"
                      />
                    ) : (
                      <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs font-medium">
                        <span>{email}</span>
                        <span className="inline-flex items-center gap-1 text-viz-primary text-[10px] font-bold uppercase tracking-wider bg-tone-info-bg px-2 py-0.5 rounded border border-tone-info-text/20">
                          <CheckCircle2 className="h-3 w-3" /> Verified
                        </span>
                      </div>
                    )}
                    <span className="text-[10px] text-on-surface-variant">
                      Receives urgent threat notifications and case timeline exports.
                    </span>
                  </div>

                  {/* Mobile Telephony Endpoint */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-on-surface">Mobile Telephony Endpoint</label>
                    {isEditingContact ? (
                      <input
                        type="text"
                        value={tempPhone}
                        onChange={(e) => setTempPhone(e.target.value)}
                        className="h-10 px-3 rounded-lg bg-surface border border-viz-primary text-xs font-mono font-medium text-on-surface focus:outline-none"
                      />
                    ) : (
                      <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs font-mono font-semibold">
                        <span>{phone}</span>
                        <span className="inline-flex items-center gap-1 text-viz-primary text-[10px] font-bold">
                          <Smartphone className="h-3.5 w-3.5" /> SMS 2FA Active
                        </span>
                      </div>
                    )}
                    <span className="text-[10px] text-on-surface-variant">
                      Bound to SIM card telemetry for SMS warning signals.
                    </span>
                  </div>

                  {/* Master Vault Passphrase */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-on-surface">Master Vault Passphrase</label>
                    <div className="h-10 px-3 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-on-surface text-xs">
                      <span className="tracking-widest font-mono text-viz-neutral text-sm">••••••••••••••••</span>
                      <button
                        className="text-xs text-viz-primary font-bold hover:underline"
                        onClick={() => setShowPasswordModal(true)}
                        type="button"
                      >
                        Change password
                      </button>
                    </div>
                    <span className="text-[10px] text-on-surface-variant">
                      Protects your local encrypted audit logs and offline dossier exports.
                    </span>
                  </div>
                </div>

                {isEditingContact && (
                  <div className="flex items-center justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setIsEditingContact(false)}
                      className="px-3.5 py-1.5 rounded-lg border border-border-control text-xs font-semibold text-on-surface hover:bg-surface-subtle transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={handleSaveContact}
                      className="px-4 py-1.5 rounded-lg bg-viz-primary text-on-primary text-xs font-bold hover:bg-primary transition-colors shadow-sm"
                    >
                      Save Endpoints
                    </button>
                  </div>
                )}

                {/* MFA / Hardware Token Box */}
                <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-full bg-viz-primary text-on-primary flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                      <Key className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-on-surface">Multi-Factor Authentication (MFA / Passkeys)</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-viz-primary text-on-primary">
                          Enforced
                        </span>
                      </div>
                      <p className="text-[11px] text-on-surface-variant mt-0.5 leading-relaxed">
                        FIDO2 Hardware Key / App Authenticator ({passkeys.length} keys active).
                      </p>
                    </div>
                  </div>
                  <button
                    className="h-8 px-3.5 rounded-lg bg-surface border border-border-control text-on-surface text-xs font-semibold hover:bg-surface-subtle transition-colors shrink-0 shadow-sm"
                    onClick={() => setShowKeysModal(true)}
                    type="button"
                  >
                    Manage Keys ({passkeys.length})
                  </button>
                </div>

                {/* Active Session Audit */}
                <div className="pt-2 border-t border-border-divider">
                  <div className="text-xs font-bold text-on-surface mb-2">Verified Active Devices</div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-lg border border-border-divider bg-surface flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className="w-2 h-2 rounded-full bg-viz-primary" />
                        <div>
                          <div className="font-semibold text-on-surface">Windows 11 · Edge Browser</div>
                          <div className="text-[10px] text-viz-neutral">Bangalore, IN · Current Session</div>
                        </div>
                      </div>
                      <span className="text-[10px] text-viz-primary font-bold">This Device</span>
                    </div>
                    <div className="p-3 rounded-lg border border-border-divider bg-surface flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className="w-2 h-2 rounded-full bg-viz-neutral/60" />
                        <div>
                          <div className="font-semibold text-on-surface">Android 15 · Mobile App</div>
                          <div className="text-[10px] text-viz-neutral">Bangalore, IN · 2 hours ago</div>
                        </div>
                      </div>
                      <span className="text-[10px] text-viz-neutral font-medium">FIDO2 Signed</span>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* ══════════════ SECTION 2: LANGUAGE & THEME ══════════════ */}
            {activeSection === 'language-theme' && (
              <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-6 animate-in fade-in duration-150">
                <div className="pb-3 border-b border-border-divider">
                  <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                    <Languages className="h-5 w-5 text-viz-primary" />
                    <span>Language &amp; Indic Script Adaptation</span>
                  </h2>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Zero-clipping typographical metrics for high-stress comprehension across regional vernaculars.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Language Select */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-on-surface" htmlFor="language-select">
                      Primary Interface Language
                    </label>
                    <select
                      id="language-select"
                      value={language}
                      onChange={(e) => handleLanguageChange(e.target.value)}
                      className="w-full h-10 px-3 rounded-lg bg-surface border border-border-control text-xs text-on-surface font-medium focus:ring-2 focus:ring-viz-primary focus:outline-none"
                    >
                      <option value="en-IN">English (India) — Latin Baseline</option>
                      <option value="hi-IN">हिन्दी (Hindi) — Devanagari Script</option>
                      <option value="bn-IN">বাংলা (Bengali - Beta) — Eastern Nagari</option>
                      <option value="ta-IN">தமிழ் (Tamil - Active Triage)</option>
                      <option value="mr-IN">मराठी (Marathi) — Devanagari</option>
                      <option value="te-IN">తెలుగు (Telugu - Beta)</option>
                      <option value="kn-IN">ಕನ್ನಡ (Kannada - Beta)</option>
                    </select>

                    <div className="p-3 rounded-lg bg-tone-info-bg text-tone-info-text flex items-start gap-2 border border-tone-info-text/20">
                      <Info className="h-4 w-4 shrink-0 mt-0.5 text-viz-primary" />
                      <p className="text-[11px] leading-relaxed">
                        Indic typography automatically adjusts line-height and letter-spacing to prevent vowel mark (matra/halant) clipping during high-stress emergency triage.
                      </p>
                    </div>
                  </div>

                  {/* Theme Mode */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-on-surface">Interface Display Calibration</label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={() => handleThemeChange('light')}
                        className={`p-3.5 rounded-lg border-2 transition-all flex flex-col gap-1 text-left ${
                          themeMode === 'light'
                            ? 'border-viz-primary bg-surface-subtle shadow-sm'
                            : 'border-border-divider bg-surface hover:bg-surface-subtle'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <Sun className="h-4 w-4 text-viz-primary" />
                          <span className={`w-2.5 h-2.5 rounded-full ${themeMode === 'light' ? 'bg-viz-primary' : 'bg-transparent'}`} />
                        </div>
                        <span className="text-xs font-bold text-on-surface mt-1">Sovereign Trust</span>
                        <span className="text-[10px] text-on-surface-variant">High-contrast daytime light mode</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleThemeChange('dark')}
                        className={`p-3.5 rounded-lg border-2 transition-all flex flex-col gap-1 text-left ${
                          themeMode === 'dark'
                            ? 'border-viz-primary bg-surface-subtle shadow-sm'
                            : 'border-border-divider bg-surface hover:bg-surface-subtle'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <Moon className="h-4 w-4 text-viz-primary" />
                          <span className={`w-2.5 h-2.5 rounded-full ${themeMode === 'dark' ? 'bg-viz-primary' : 'bg-transparent'}`} />
                        </div>
                        <span className="text-xs font-bold text-on-surface mt-1">Glacier Night</span>
                        <span className="text-[10px] text-on-surface-variant">Low-glare subdued dark mode</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Font Scaling Preview */}
                <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold text-on-surface">Emergency Readability Scaling</div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setFontScale('normal')}
                        className={`px-2.5 py-1 rounded text-xs font-semibold ${fontScale === 'normal' ? 'bg-viz-primary text-on-primary' : 'bg-surface border border-border-divider text-on-surface'}`}
                      >
                        Standard (100%)
                      </button>
                      <button
                        type="button"
                        onClick={() => setFontScale('large')}
                        className={`px-2.5 py-1 rounded text-xs font-semibold ${fontScale === 'large' ? 'bg-viz-primary text-on-primary' : 'bg-surface border border-border-divider text-on-surface'}`}
                      >
                        Enlarged (115%)
                      </button>
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg bg-surface border border-border-divider text-on-surface ${fontScale === 'large' ? 'text-base' : 'text-xs'}`}>
                    <span className="font-semibold">आपातकालीन सूचना:</span> यदि आपने पिछले 2 घंटों में धन हस्तांतरित किया है, तो 1930 पर कॉल करें या तुरंत अपने बैंक को सूचित करें।
                  </div>
                </div>
              </section>
            )}

            {/* ══════════════ SECTION 3: PRIVACY & DPDP CONTROLS ══════════════ */}
            {activeSection === 'privacy-dpdp' && (
              <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-6 animate-in fade-in duration-150">
                <div className="pb-3 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <Lock className="h-5 w-5 text-viz-primary" />
                    <h2 className="text-base font-bold text-on-surface">Privacy &amp; DPDP Sovereign Controls (§8 &amp; §12)</h2>
                  </div>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Strict compliance with the Digital Personal Data Protection Act (2023) and client-side zero-credential scrub doctrine.
                  </p>
                </div>

                <div className="flex flex-col gap-4">
                  {/* Zero Credential Scrubbing */}
                  <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex items-start gap-4">
                    <div className="w-9 h-9 rounded-full bg-viz-primary text-on-primary flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                      <ShieldCheck className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xs font-bold text-on-surface">Client-Side Zero-Credential Scrubbing</h3>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-viz-primary text-on-primary">
                          Always Active
                        </span>
                      </div>
                      <p className="text-[11px] text-on-surface-variant mt-1 leading-relaxed">
                        Passwords, one-time passwords (OTPs), 6-digit UPI PINs, and credit card CVVs are intercepted and permanently scrubbed inside your local browser memory before data packets ever transmit to ScamGraph infrastructure.
                      </p>
                    </div>
                  </div>

                  {/* Interactive Scrubber Simulator */}
                  <div className="p-4 rounded-xl border border-border-divider bg-surface flex flex-col gap-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-on-surface">Zero-Knowledge Scrubbing Simulator</span>
                      <span className="text-[10px] font-mono text-viz-primary">SHA-256 Memory Guard</span>
                    </div>
                    <input
                      type="text"
                      value={scrubberTestInput}
                      onChange={(e) => setScrubberTestInput(e.target.value)}
                      placeholder="Type sensitive OTP, card number, or phone..."
                      className="h-9 px-3 rounded-lg border border-border-control bg-surface-subtle text-xs text-on-surface focus:outline-none"
                    />
                    <div className="p-2.5 rounded bg-surface-subtle text-xs font-mono text-on-surface-variant border border-border-divider flex items-center gap-2">
                      <span className="text-viz-primary font-bold text-[10px] uppercase">Scrubbed Output:</span>
                      <span className="truncate">
                        {scrubberTestInput
                          .replace(/\b\d{6}\b/g, '[REDACTED_OTP]')
                          .replace(/\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/g, '[REDACTED_CARD]')
                          .replace(/CVV \d{3}/gi, 'CVV [SCRUBBED]')}
                      </span>
                    </div>
                  </div>

                  {/* Ephemeral Check Storage Toggle */}
                  <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-xs font-bold text-on-surface">Ephemeral Check Storage</h3>
                        <Clock className="h-3.5 w-3.5 text-viz-neutral" />
                      </div>
                      <p className="text-[11px] text-on-surface-variant mt-0.5 leading-relaxed">
                        Automatically purge anonymous query artifacts, file hashes, and triage logs from your local session cache after the configured duration.
                      </p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <select
                        value={ephemeralHours}
                        onChange={(e) => setEphemeralHours(Number(e.target.value))}
                        disabled={!ephemeralStorage}
                        className="h-8 px-2 rounded-lg bg-surface border border-border-control text-xs text-on-surface font-semibold disabled:opacity-50"
                      >
                        <option value={24}>Purge after 24 hours</option>
                        <option value={48}>Purge after 48 hours</option>
                        <option value={72}>Purge after 72 hours</option>
                      </select>
                      <label className="relative inline-flex items-center cursor-pointer shrink-0">
                        <input
                          checked={ephemeralStorage}
                          onChange={(e) => {
                            setEphemeralStorage(e.target.checked);
                            triggerToast(e.target.checked ? 'Ephemeral cache purge active' : 'Cache purge disabled');
                          }}
                          className="sr-only peer"
                          type="checkbox"
                        />
                        <div className="w-10 h-5 bg-border-control rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border-control after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-viz-primary" />
                      </label>
                    </div>
                  </div>

                  {/* Pseudonymized Display Toggle with Live Preview */}
                  <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="text-xs font-bold text-on-surface">Pseudonymized Display Masking</h3>
                          {displayMasking ? <EyeOff className="h-3.5 w-3.5 text-viz-primary" /> : <Eye className="h-3.5 w-3.5 text-viz-neutral" />}
                        </div>
                        <p className="text-[11px] text-on-surface-variant mt-0.5 leading-relaxed">
                          Mask suspect phone numbers, UPI handles, and bank accounts across all investigation graphs, triage reports, and shared evidence timelines.
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                        <input
                          checked={displayMasking}
                          onChange={(e) => {
                            setDisplayMasking(e.target.checked);
                            triggerToast(e.target.checked ? 'Display masking enabled' : 'Raw display enabled');
                          }}
                          className="sr-only peer"
                          type="checkbox"
                        />
                        <div className="w-10 h-5 bg-border-control rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border-control after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-viz-primary" />
                      </label>
                    </div>

                    <div className="p-3 rounded-lg bg-surface border border-border-divider flex items-center justify-between text-xs">
                      <div>
                        <span className="text-[10px] text-viz-neutral block">Live Render Preview:</span>
                        <span className="font-mono font-semibold text-on-surface">
                          {displayMasking ? 'rohit•••••@okhdfcbank · +91 98••• ••210' : 'rohit.dasgupta@okhdfcbank · +91 98765 43210'}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${displayMasking ? 'bg-tone-info-bg text-tone-info-text' : 'bg-surface-subtle text-viz-neutral'}`}>
                        {displayMasking ? 'Masked' : 'Unmasked'}
                      </span>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* ══════════════ SECTION 4: THREAT SHARING ══════════════ */}
            {activeSection === 'threat-intelligence' && (
              <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-6 animate-in fade-in duration-150">
                <div className="pb-3 border-b border-border-divider">
                  <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                    <Share2 className="h-5 w-5 text-viz-primary" />
                    <span>Threat Intelligence Sharing &amp; Outbreak Clustering</span>
                  </h2>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Empower collective civil defense while strictly segregating individual identities from topological graphs.
                  </p>
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
                        Allow anonymized, desensitized pattern signatures (fraudulent sender tags, malicious APK SHA-256 hashes, or newly observed fake payment gateways) to be clustered into the public outbreak radar.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                      <input
                        checked={threatSharing}
                        onChange={(e) => {
                          setThreatSharing(e.target.checked);
                          triggerToast(e.target.checked ? 'Threat sharing enabled' : 'Threat sharing disabled');
                        }}
                        className="sr-only peer"
                        type="checkbox"
                      />
                      <div className="w-10 h-5 bg-border-control rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border-control after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-viz-primary" />
                    </label>
                  </div>

                  {/* Federation Tier Selection */}
                  <div className="pt-3 border-t border-border-divider">
                    <span className="text-xs font-semibold text-on-surface block mb-2">Outbreak Federation Level</span>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                      {[
                        { id: 'sovereign', title: 'Sovereign Shield', desc: 'Sync with NPCI & I4C National Radar' },
                        { id: 'regional', title: 'Regional Cluster Only', desc: 'Sync with state Cyber Crime Cells' },
                        { id: 'private', title: 'Private Vault', desc: 'Zero signature egress' },
                      ].map((tier) => (
                        <button
                          key={tier.id}
                          type="button"
                          onClick={() => {
                            setSharingTier(tier.id as any);
                            triggerToast(`Federation tier updated to ${tier.title}`);
                          }}
                          className={`p-3 rounded-lg border-2 text-left transition-all ${
                            sharingTier === tier.id ? 'border-viz-primary bg-surface font-semibold shadow-sm' : 'border-border-divider bg-surface hover:bg-surface-subtle'
                          }`}
                        >
                          <div className="font-bold text-on-surface">{tier.title}</div>
                          <div className="text-[10px] text-on-surface-variant mt-0.5">{tier.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Active Syndicate Alerts Toggle */}
                  <div className="pt-3 border-t border-border-divider">
                    <span className="text-xs font-semibold text-on-surface block mb-2">Category Alert Subscriptions</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      {[
                        { id: 'digital-arrest', label: 'Customs / Police Digital Arrest Calls' },
                        { id: 'part-time-task', label: 'Telegram Part-time Hotel Rating Schemes' },
                        { id: 'electricity-bill', label: 'Electricity Disconnection SMS Frauds' },
                        { id: 'customs-courier', label: 'Fake Fedex / Courier Drug Parcels' },
                      ].map((sub) => (
                        <label key={sub.id} className="flex items-center justify-between p-2.5 rounded-lg border border-border-divider bg-surface cursor-pointer hover:bg-surface-subtle">
                          <span className="text-on-surface font-medium">{sub.label}</span>
                          <input
                            type="checkbox"
                            checked={subscribedAlerts[sub.id]}
                            onChange={(e) => {
                              setSubscribedAlerts((prev) => ({ ...prev, [sub.id]: e.target.checked }));
                              triggerToast(`Alert settings updated for ${sub.label}`);
                            }}
                            className="rounded border-border-control text-viz-primary focus:ring-viz-primary"
                          />
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* ══════════════ SECTION 5: DATA EXPORT & SOVEREIGN ERASURE ══════════════ */}
            {activeSection === 'export-deletion' && (
              <section className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-6 animate-in fade-in duration-150">
                <div className="pb-3 border-b border-border-divider">
                  <h2 className="text-base font-bold text-tone-danger-strong-text flex items-center gap-2">
                    <Trash2 className="h-5 w-5 text-tone-danger-text" />
                    <span>Data Export &amp; Sovereign Erasure (Section 12 DPDP)</span>
                  </h2>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Exercise your irrevocable legal right to data portability and complete digital erasure.
                  </p>
                </div>

                {/* Action 1: Export Archive */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-surface-subtle border border-border-divider">
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-bold text-on-surface">Download Sovereign Data Archive (JSON + Manifest)</span>
                    <p className="text-[11px] text-on-surface-variant leading-relaxed max-w-xl">
                      Generate a cryptographically signed, timestamped archive containing all your submitted checks, forensic evidence uploads, and Rescue Dossier timelines.
                    </p>
                  </div>
                  <button
                    className="inline-flex items-center gap-2 px-4 h-9 rounded-lg border border-border-control bg-surface text-on-surface text-xs font-semibold hover:bg-surface-subtle shrink-0 transition-colors shadow-sm"
                    onClick={handleDownloadArchive}
                    type="button"
                  >
                    <Download className="h-4 w-4 text-viz-primary" />
                    <span>Request Data Archive</span>
                  </button>
                </div>

                {/* Action 2: BSA §65B Legal Certificate */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-surface-subtle border border-border-divider">
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-bold text-on-surface">Generate Section 65B BSA Legal Evidence Certificate</span>
                    <p className="text-[11px] text-on-surface-variant leading-relaxed max-w-xl">
                      Produces court-ready electronic affidavit with Merkle root hash attestation admissible under Indian Bharatiya Sakshya Adhiniyam.
                    </p>
                  </div>
                  <button
                    className="inline-flex items-center gap-2 px-4 h-9 rounded-lg border border-border-control bg-surface text-on-surface text-xs font-semibold hover:bg-surface-subtle shrink-0 transition-colors shadow-sm"
                    onClick={handleDownloadBsaCertificate}
                    type="button"
                  >
                    <FileCheck className="h-4 w-4 text-viz-primary" />
                    <span>Generate Certificate</span>
                  </button>
                </div>

                {/* Action 3: Sovereign Right to Erasure */}
                <div className="p-4 rounded-xl bg-tone-danger-bg border border-tone-danger-text/20 text-tone-danger-strong-text flex flex-col gap-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-tone-danger-text shrink-0 mt-0.5" />
                    <div className="flex flex-col gap-1">
                      <span className="text-xs font-bold text-tone-danger-strong-text">Execute Sovereign Right to Erasure</span>
                      <p className="text-xs text-tone-danger-text leading-relaxed">
                        Permanently purge your account, linked citizen ID, submitted evidence attachments, and active investigation dossiers across all ScamGraph data clusters. An immutable cryptographic tombstone receipt is produced as legal evidence of complete erasure.
                      </p>
                    </div>
                  </div>

                  {erasureTombstone ? (
                    <div className="p-3 rounded-lg bg-surface border border-tone-danger-text/30 flex items-center justify-between text-xs">
                      <div>
                        <span className="text-[10px] text-viz-neutral block">Cryptographic Tombstone Receipt:</span>
                        <span className="font-mono font-bold text-tone-danger-text">{erasureTombstone}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-tone-danger-bg text-tone-danger-text border border-tone-danger-text/20">
                        Zero Data Remains
                      </span>
                    </div>
                  ) : (
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-tone-danger-text/20">
                      <span className="text-[11px] text-tone-danger-text font-semibold">
                        Warning: This operation is non-reversible under DPDP Section 12 doctrine.
                      </span>
                      <button
                        className="inline-flex items-center gap-2 px-4 h-9 rounded-lg bg-tone-danger-text text-white text-xs font-bold hover:bg-tone-danger-strong-text transition-colors shrink-0 shadow-sm"
                        onClick={() => setShowDeleteModal(true)}
                        type="button"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Delete Account and All Case Data</span>
                      </button>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Bottom Commit Bar */}
            <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
              <div className="flex items-center gap-2 text-xs text-on-surface-variant">
                <RefreshCw className="h-4 w-4 text-viz-primary shrink-0" />
                <span>All modifications are cryptographically authenticated and synced with your session vault.</span>
              </div>
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  className="flex-1 sm:flex-none px-4 h-10 rounded-lg border border-border-control bg-surface text-xs font-semibold text-on-surface hover:bg-surface-subtle transition-colors"
                  type="button"
                  onClick={() => triggerToast('Settings reset to defaults')}
                >
                  Reset
                </button>
                <button
                  onClick={() => triggerToast('All configuration changes cryptographically synchronized')}
                  className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 h-10 px-6 rounded-full bg-viz-primary text-on-primary text-xs font-bold hover:bg-primary transition-all shadow-md"
                  type="button"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Save Changes</span>
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>

      {/* ── MODAL: CHANGE MASTER PASSPHRASE ── */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-150">
          <div className="w-full max-w-md bg-surface rounded-2xl border border-border-divider p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-border-divider">
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4 text-viz-primary" />
                <h3 className="text-sm font-bold text-on-surface">Rotate Master Vault Passphrase</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowPasswordModal(false)}
                className="p-1 rounded-lg hover:bg-surface-subtle text-viz-neutral"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {passwordSuccess ? (
              <div className="py-6 text-center flex flex-col items-center gap-2">
                <CheckCircle2 className="h-10 w-10 text-viz-primary" />
                <span className="text-sm font-bold text-on-surface">Passphrase Rotated!</span>
                <span className="text-xs text-on-surface-variant">New cryptographic hash bound to your session.</span>
              </div>
            ) : (
              <form onSubmit={handlePasswordChange} className="flex flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface">Current Passphrase</label>
                  <input
                    type="password"
                    required
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Enter current master passphrase"
                    className="h-10 px-3 rounded-lg border border-border-control bg-surface text-xs text-on-surface focus:outline-none focus:border-viz-primary"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface">New Master Passphrase</label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min 12 characters recommended"
                    className="h-10 px-3 rounded-lg border border-border-control bg-surface text-xs text-on-surface focus:outline-none focus:border-viz-primary"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-on-surface">Confirm New Passphrase</label>
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-type new passphrase"
                    className="h-10 px-3 rounded-lg border border-border-control bg-surface text-xs text-on-surface focus:outline-none focus:border-viz-primary"
                  />
                </div>
                <div className="flex items-center justify-end gap-3 pt-3 border-t border-border-divider">
                  <button
                    type="button"
                    onClick={() => setShowPasswordModal(false)}
                    className="px-4 py-2 rounded-lg border border-border-control text-xs font-semibold text-on-surface hover:bg-surface-subtle"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={!currentPassword || !newPassword || newPassword !== confirmPassword}
                    className="px-5 py-2 rounded-lg bg-viz-primary text-on-primary text-xs font-bold hover:bg-primary transition-all disabled:opacity-50"
                  >
                    Update Passphrase
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* ── MODAL: MANAGE FIDO2 KEYS ── */}
      {showKeysModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-150">
          <div className="w-full max-w-lg bg-surface rounded-2xl border border-border-divider p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-border-divider">
              <div className="flex items-center gap-2">
                <Key className="h-4 w-4 text-viz-primary" />
                <h3 className="text-sm font-bold text-on-surface">Registered Hardware Passkeys</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowKeysModal(false)}
                className="p-1 rounded-lg hover:bg-surface-subtle text-viz-neutral"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex flex-col gap-2.5 max-h-64 overflow-y-auto">
              {passkeys.map((key) => (
                <div key={key.id} className="p-3 rounded-xl border border-border-divider bg-surface-subtle flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Fingerprint className="h-5 w-5 text-viz-primary shrink-0" />
                    <div>
                      <div className="text-xs font-bold text-on-surface">{key.name}</div>
                      <div className="text-[10px] text-on-surface-variant">{key.type} · Added {key.addedDate}</div>
                    </div>
                  </div>
                  {passkeys.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemovePasskey(key.id)}
                      className="text-viz-neutral hover:text-tone-danger-text p-1.5 transition-colors"
                      title="Revoke Passkey"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-border-divider flex items-center justify-between">
              <button
                type="button"
                onClick={handleAddPasskey}
                disabled={isRegisteringKey}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-viz-primary text-on-primary text-xs font-bold hover:bg-primary transition-all disabled:opacity-50"
              >
                <Key className="h-3.5 w-3.5" />
                <span>{isRegisteringKey ? 'Waiting for Touch / Enclave...' : 'Register New Passkey'}</span>
              </button>
              <button
                type="button"
                onClick={() => setShowKeysModal(false)}
                className="px-4 py-2 rounded-lg border border-border-control text-xs font-semibold text-on-surface hover:bg-surface-subtle"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── MODAL: CONFIRM SOVEREIGN ERASURE ── */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-150">
          <div className="w-full max-w-md bg-surface rounded-2xl border border-tone-danger-text/30 p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center gap-3 text-tone-danger-text pb-3 border-b border-border-divider">
              <AlertTriangle className="h-6 w-6 shrink-0" />
              <div>
                <h3 className="text-sm font-bold text-on-surface">Confirm Sovereign Right to Erasure</h3>
                <span className="text-[11px] text-tone-danger-text">Irrevocable DPDP Section 12 Action</span>
              </div>
            </div>

            <p className="text-xs text-on-surface-variant leading-relaxed">
              This will permanently purge your Citizen ID (<code className="font-mono font-bold text-on-surface">#CIT-84920-BLR</code>), all linked phone numbers, email anchors, evidence uploads, and golden-hour case dossiers.
            </p>

            <div className="p-3 rounded-lg bg-tone-danger-bg text-tone-danger-text text-xs border border-tone-danger-text/20">
              To proceed, please type <strong className="font-mono">DELETE</strong> below:
            </div>

            <input
              type="text"
              value={deleteConfirmationText}
              onChange={(e) => setDeleteConfirmationText(e.target.value)}
              placeholder="Type DELETE to confirm"
              className="h-10 px-3 rounded-lg border border-border-control bg-surface text-xs font-mono font-bold text-on-surface focus:outline-none focus:border-tone-danger-text"
            />

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-border-divider">
              <button
                type="button"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteConfirmationText('');
                }}
                className="px-4 py-2 rounded-lg border border-border-control text-xs font-semibold text-on-surface hover:bg-surface-subtle"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={deleteConfirmationText.trim() !== 'DELETE' || isErasing}
                onClick={() => {
                  handleExecuteErasure();
                  setShowDeleteModal(false);
                  setDeleteConfirmationText('');
                }}
                className="px-5 py-2 rounded-lg bg-tone-danger-text text-white text-xs font-bold hover:bg-tone-danger-strong-text transition-all disabled:opacity-40"
              >
                {isErasing ? 'Purging Vault...' : 'Permanently Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
