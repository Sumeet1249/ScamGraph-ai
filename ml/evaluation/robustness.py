"""Defensive adversarial perturbation framework for testing model robustness."""

import random
import re
from typing import Callable, Dict, List, Tuple


# Common Indian English / Hinglish homoglyphs and evasive substitutions
HOMOGLYPH_MAP = {
    "a": ["@", "4", "а"],
    "b": ["8", "13", "b"],
    "e": ["3", "е"],
    "i": ["1", "!", "|", "і"],
    "o": ["0", "о"],
    "s": ["$", "5"],
    "t": ["7", "+"],
}

CURRENCY_VARIATIONS = [
    (r"\b(rs\.?|inr)\b", "₹"),
    (r"₹", "Rs."),
]


class AdversarialPerturbationGenerator:
    """Generates non-destructive derived adversarial evaluation variants."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def perturb_case(self, text: str) -> str:
        """Randomized capitalization (e.g. uRgEnT kYc uPdAtE)."""
        return "".join(c.upper() if self.rng.random() > 0.5 else c.lower() for c in text)

    def perturb_spacing(self, text: str) -> str:
        """Insert extra spaces into sensitive keywords or phone numbers."""
        words = text.split()
        if len(words) > 3:
            idx = self.rng.randint(0, len(words) - 1)
            # Insert spaces inside word
            w = words[idx]
            if len(w) > 3:
                words[idx] = " ".join(list(w))
        return " ".join(words)

    def perturb_homoglyphs(self, text: str, max_replacements: int = 3) -> str:
        """Replace standard Latin characters with visual homoglyphs or leetspeak."""
        chars = list(text)
        count = 0
        indices = list(range(len(chars)))
        self.rng.shuffle(indices)

        for i in indices:
            low = chars[i].lower()
            if low in HOMOGLYPH_MAP:
                chars[i] = self.rng.choice(HOMOGLYPH_MAP[low])
                count += 1
                if count >= max_replacements:
                    break
        return "".join(chars)

    def perturb_currency(self, text: str) -> str:
        """Swap currency symbols between ₹, Rs., and INR."""
        res = text
        for pat, repl in CURRENCY_VARIATIONS:
            if re.search(pat, res, flags=re.IGNORECASE):
                res = re.sub(pat, repl, res, count=1, flags=re.IGNORECASE)
                break
        return res

    def generate_all_variants(self, text: str) -> Dict[str, str]:
        """Generate all defensive adversarial transformations for a sample."""
        return {
            "case_variation": self.perturb_case(text),
            "spacing_perturbation": self.perturb_spacing(text),
            "homoglyph_substitution": self.perturb_homoglyphs(text),
            "currency_swap": self.perturb_currency(text),
        }
