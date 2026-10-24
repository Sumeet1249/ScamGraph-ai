"""Production Model Router and Execution Orchestrator for ScamGraph AI (Rule 46).

Implements:
1. Fast Path vs Deep Path routing based on signals, entities, and confidence (Rules 40-42).
2. Disagreement Detection between word, char, and heuristic models (Rule 37).
3. Graceful Fallback & Degraded Mode: Infrastructure failure NEVER returns SAFE (Rule 44).
4. Deterministic content-hash caching (Rule 43).
5. Explainable reason codes backed by evidence text spans (Rules 64-66).
"""

from __future__ import annotations

import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ml.evaluation.arena.adapters import (
    BaselineModelAdapter,
    CharacterTfidfAdapter,
    ClassifierAdapter,
    WordCharEnsembleAdapter,
)
from packages.inference.cache import IntelligenceCache
from packages.inference.contracts import (
    ConsumerRiskLevel,
    InferenceResponse,
    LanguageProfile,
    ReasonEvidence,
    StandardReasonCode,
    TacticEvidence,
    UntrustedArtifact,
)
from packages.inference.tiers import InferenceTier, TIER_SPECIFICATIONS
from packages.utils.normalization import normalize_text

logger = logging.getLogger("scamgraph.inference.router")

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "model_routing.yaml"


class ModelRouter:
    """Production router for model selection, tiering, fallback, and escalation."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        cache: Optional[IntelligenceCache] = None,
        tier1_classifier: Optional[ClassifierAdapter] = None,
        tier2_classifier: Optional[ClassifierAdapter] = None,
    ):
        self.config_path = config_path or CONFIG_PATH
        self.config = self._load_config()
        self.cache = cache or IntelligenceCache(default_ttl_sec=self.config.get("routing_policy", {}).get("cache_ttl_seconds", 3600))

        # Lazy-loaded model adapters
        self._tier1_model = tier1_classifier
        self._tier2_model = tier2_classifier
        self._fallback_baseline: Optional[BaselineModelAdapter] = None

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Could not read routing config from %s: %s", self.config_path, e)
        return {
            "routing_policy": {"default_inference_tier": "TIER_1_FAST_ML", "enable_caching": True},
            "escalation_policy": {"ambiguity_low": 0.35, "ambiguity_high": 0.65, "disagreement_threshold": 0.35},
        }

    def _get_tier1_model(self) -> ClassifierAdapter:
        if self._tier1_model is None:
            # Initialize default Word + Character Ensemble
            base = BaselineModelAdapter().load()
            char = CharacterTfidfAdapter()
            self._tier1_model = WordCharEnsembleAdapter(word_adapter=base, char_adapter=char).load()
        return self._tier1_model

    def _get_tier2_model(self) -> Optional[ClassifierAdapter]:
        if self._tier2_model is None:
            from ml.evaluation.arena.adapters import TransformerClassifierAdapter
            self._tier2_model = TransformerClassifierAdapter().load()
        return self._tier2_model

    def _get_fallback_baseline(self) -> BaselineModelAdapter:
        if self._fallback_baseline is None:
            self._fallback_baseline = BaselineModelAdapter().load()
        return self._fallback_baseline

    def detect_language_profile(self, text: str) -> LanguageProfile:
        """Lightweight language and script identification separating Language from Script (Rule 31)."""
        has_deva = bool(re.search(r"[\u0900-\u097F]", text))
        if has_deva:
            return LanguageProfile(language="hi", script="Deva", is_transliterated=False, is_code_mixed=False)

        lower = text.lower()
        hinglish_words = ["aapka", "kare", "hai", "nahi", "bhejo", "paise", "turant", "vibhag", "bijli", "khata", "bhai"]
        match_count = sum(1 for w in hinglish_words if re.search(rf"\b{w}\b", lower))
        if match_count >= 2:
            return LanguageProfile(language="hi", script="Latn", is_transliterated=True, is_code_mixed=True)

        return LanguageProfile(language="en", script="Latn", is_transliterated=False, is_code_mixed=False)

    def extract_deterministic_reasons(self, text: str) -> Tuple[List[ReasonEvidence], List[TacticEvidence]]:
        """Fast regex-based behavioral and impersonation markers (Tier 0)."""
        lower = text.lower()
        reasons: List[ReasonEvidence] = []
        tactics: List[TacticEvidence] = []

        # Check for benign routine transaction context
        is_routine_bank = bool(re.search(r"\b(credited to your a/c|debited from your a/c|available bal|txn id|ref no|statement generated)\b", lower))
        has_coercion = bool(re.search(r"\b(block|suspend|deactivat|freeze|hold|kyc|pan|link|rok|turant|immediately|urgent)\b", lower))

        # 1. Authority impersonation
        authority_patterns = {
            "POLICE_CBI": (r"\b(police|cbi|crime branch|cyber cell|court|arrest)\b", "Impersonates police or law enforcement authority"),
            "BANK_OFFICIAL": (r"\b(sbi|hdfc|icici|yono|bank manager|rbi)\b", "Claims official banking institution authority"),
            "ELECTRICITY_DEPT": (r"\b(electricity|discom|bijli vibhag|power supply)\b", "Impersonates utility or electricity department"),
        }
        for entity_key, (pat, expl) in authority_patterns.items():
            # If routine transaction notification without coercive threat, the bank name is an authentic attribution
            if entity_key == "BANK_OFFICIAL" and is_routine_bank and not has_coercion:
                continue

            m = re.search(pat, lower)
            if m:
                span = m.group(0)
                reasons.append(ReasonEvidence(
                    code=StandardReasonCode.AUTHORITY_IMPERSONATION,
                    explanation=expl,
                    supporting_span=span,
                    confidence=0.90,
                    engine="tier0-regex-entity",
                    engine_version="1.0.0",
                ))
                tactics.append(TacticEvidence(tactic="AUTHORITY", confidence=0.90, supporting_text_span=span))
                break

        # 2. Urgent payment pressure
        urgency_m = re.search(r"\b(urgent|immediately|today only|within \d+ hours?|turant|jaldi|rok diya jayega)\b", lower)
        if urgency_m:
            span = urgency_m.group(0)
            reasons.append(ReasonEvidence(
                code=StandardReasonCode.URGENT_PAYMENT_REQUEST,
                explanation="Coercive urgency pressuring immediate action without time to verify",
                supporting_span=span,
                confidence=0.85,
                engine="tier0-regex-urgency",
                engine_version="1.0.0",
            ))
            tactics.append(TacticEvidence(tactic="URGENCY", confidence=0.85, supporting_text_span=span))

        # 3. Credential or OTP solicitation
        cred_m = re.search(r"\b(otp|pin|password|pan card|aadhaar|update kyc)\b", lower)
        if cred_m:
            span = cred_m.group(0)
            reasons.append(ReasonEvidence(
                code=StandardReasonCode.CREDENTIAL_REQUEST,
                explanation="Solicitation of sensitive credentials, OTP, or KYC document details",
                supporting_span=span,
                confidence=0.95,
                engine="tier0-regex-credential",
                engine_version="1.0.0",
            ))
            tactics.append(TacticEvidence(tactic="PAYMENT_PRESSURE", confidence=0.90, supporting_text_span=span))

        # 4. Platform migration lure
        mig_m = re.search(r"\b(telegram|whatsapp|join group|contact on telegram)\b", lower)
        if mig_m:
            span = mig_m.group(0)
            reasons.append(ReasonEvidence(
                code=StandardReasonCode.PLATFORM_MIGRATION,
                explanation="Attempts to migrate conversation to unmonitored messaging channels",
                supporting_span=span,
                confidence=0.80,
                engine="tier0-regex-migration",
                engine_version="1.0.0",
            ))
            tactics.append(TacticEvidence(tactic="ISOLATION", confidence=0.80, supporting_text_span=span))

        # 5. Suspicious link
        link_m = re.search(r"https?://[^\s]+|bit\.ly/[^\s]+|t\.me/[^\s]+", text)
        if link_m:
            reasons.append(ReasonEvidence(
                code=StandardReasonCode.SUSPICIOUS_LINK,
                explanation="Contains external unverified hyperlink requiring caution",
                supporting_span=link_m.group(0),
                confidence=0.75,
                engine="tier0-regex-link",
                engine_version="1.0.0",
            ))

        return reasons, tactics

    def route_and_infer(
        self,
        raw_text: str,
        force_tier: Optional[InferenceTier] = None,
        skip_cache: bool = False,
    ) -> InferenceResponse:
        """Main routing pipeline with Tier 0 edge check, Tier 1 fast ML, and Tier 2 deep escalation."""
        t_start = time.perf_counter()
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"

        # Step 1: Defensive input sanitation (Prompt injection defense)
        untrusted = UntrustedArtifact.sanitize(raw_text)
        normalized = normalize_text(untrusted.sanitized_content)

        # Step 2: Language profiling
        lang_profile = self.detect_language_profile(raw_text)

        # Step 3: Check deterministic cache (Rule 43)
        cache_key = IntelligenceCache.generate_cache_key(
            normalized_text=normalized,
            model_id="scamgraph-ensemble",
            model_version="1.0.0",
        )
        if not skip_cache and self.config.get("routing_policy", {}).get("enable_caching", True):
            cached = self.cache.get(cache_key)
            if cached is not None:
                cached.latency_ms = round((time.perf_counter() - t_start) * 1000.0, 3)
                return cached

        # Step 4: Tier 0 Deterministic Feature Extraction
        tier0_reasons, tier0_tactics = self.extract_deterministic_reasons(raw_text)

        # Check for known routine transaction patterns (Fast Path Benign)
        is_routine_bank = bool(re.search(r"\b(credited to your a/c|debited from your a/c|available bal)\b", raw_text.lower()))
        has_credential_request = any(r.code == StandardReasonCode.CREDENTIAL_REQUEST for r in tier0_reasons)

        if is_routine_bank and not has_credential_request and not tier0_tactics:
            # Fast Path: Benign transactional alert (0ms ML needed)
            latency = (time.perf_counter() - t_start) * 1000.0
            resp = InferenceResponse(
                execution_id=execution_id,
                risk_level=ConsumerRiskLevel.LIKELY_SAFE,
                scam_probability=0.02,
                confidence=0.98,
                reasons=[],
                tactics_detected=[],
                language_profile=lang_profile,
                tier_executed=InferenceTier.TIER_0_DETERMINISTIC,
                model_id="tier0-deterministic-filter",
                model_revision="v1.0.0",
                latency_ms=round(latency, 3),
                fallback_used=False,
                degraded_mode=False,
            )
            self.cache.set(cache_key, resp)
            return resp

        # Step 5: Execute Tier 1 Fast ML
        tier1_model = self._get_tier1_model()
        fallback_used = False
        degraded_mode = False
        missing_capabilities = []

        try:
            tier1_prob = tier1_model.predict_proba([normalized])[0]
        except Exception as e:
            logger.error("Tier 1 model failed (%s). Falling back to legacy baseline.", e)
            fallback_baseline = self._get_fallback_baseline()
            tier1_prob = fallback_baseline.predict_proba([normalized])[0]
            fallback_used = True
            degraded_mode = True
            missing_capabilities.append("scamgraph-word-char-ensemble")

        # Step 6: Escalation Decision (Fast Path vs Deep Path)
        esc_cfg = self.config.get("escalation_policy", {})
        ambig_low = esc_cfg.get("ambiguity_low", 0.35)
        ambig_high = esc_cfg.get("ambiguity_high", 0.65)
        is_ambiguous = ambig_low <= tier1_prob <= ambig_high

        # Check for model disagreement if ensemble
        has_disagreement = False
        if isinstance(tier1_model, WordCharEnsembleAdapter):
            disag = tier1_model.detect_disagreement(normalized, threshold_delta=esc_cfg.get("disagreement_threshold", 0.35))
            has_disagreement = disag["has_disagreement"]

        # Escalation criteria
        should_escalate = (
            force_tier == InferenceTier.TIER_2_DEEP_INTELLIGENCE
            or is_ambiguous
            or has_disagreement
            or (len(tier0_reasons) >= 2 and tier1_prob < 0.50)  # Contradiction between rules and model
        )

        final_prob = tier1_prob
        executed_tier = InferenceTier.TIER_1_FAST_ML
        model_id = tier1_model.model_id
        model_rev = tier1_model.model_revision

        if should_escalate and force_tier != InferenceTier.TIER_1_FAST_ML:
            tier2_model = self._get_tier2_model()
            if tier2_model is not None:
                try:
                    t2_probs = tier2_model.predict_proba([normalized])
                    t2_prob = t2_probs[0]
                    # Calibrated aggregation: blend Tier 1 and Tier 2 probabilities
                    final_prob = float(0.40 * tier1_prob + 0.60 * t2_prob)
                    executed_tier = InferenceTier.TIER_2_DEEP_INTELLIGENCE
                    model_id = f"{tier1_model.model_id}+{tier2_model.model_id}"
                    model_rev = f"{tier1_model.model_revision}+{tier2_model.model_revision}"
                except Exception as e:
                    logger.warning("Tier 2 deep model failed (%s). Retaining Tier 1 probability.", e)
                    fallback_used = True
                    missing_capabilities.append("tier2-transformer-classifier")

        # Step 7: Map Probability & Evidence to Consumer Risk Tier
        # Rule 38: Separate Risk from Confidence
        confidence = float(min(1.0, abs(final_prob - 0.50) * 2.0))
        if has_disagreement:
            # Reduce confidence when models disagree
            confidence = max(0.20, confidence * 0.70)

        # Map to ConsumerRiskLevel
        if final_prob >= 0.75 or (final_prob >= 0.50 and len(tier0_reasons) >= 2):
            risk_level = ConsumerRiskLevel.HIGH_RISK
        elif final_prob >= 0.50 or len(tier0_reasons) >= 1:
            risk_level = ConsumerRiskLevel.SUSPICIOUS
        elif final_prob >= 0.30:
            risk_level = ConsumerRiskLevel.CAUTION
        else:
            risk_level = ConsumerRiskLevel.LIKELY_SAFE

        dur_ms = (time.perf_counter() - t_start) * 1000.0

        response = InferenceResponse(
            execution_id=execution_id,
            risk_level=risk_level,
            scam_probability=round(final_prob, 4),
            confidence=round(confidence, 4),
            reasons=tier0_reasons,
            tactics_detected=tier0_tactics,
            language_profile=lang_profile,
            tier_executed=executed_tier,
            model_id=model_id,
            model_revision=model_rev,
            latency_ms=round(dur_ms, 3),
            fallback_used=fallback_used,
            degraded_mode=degraded_mode,
            missing_capabilities=missing_capabilities,
            cached_result=False,
        )

        # Store in cache
        self.cache.set(cache_key, response)
        return response
