# resume_matcher.py
"""
AI-powered Resume-Job Matching Engine
Used by recruiter_engine.py to match candidates to job postings
"""

import re
import logging
from typing import Dict, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Optional: sentence-transformers for semantic scoring
# Falls back gracefully if not installed
# ──────────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer, util
    _ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    SEMANTIC_AVAILABLE = True
    logger.info("✅ Sentence-transformer loaded for resume matching")
except Exception as e:
    _ST_MODEL = None
    SEMANTIC_AVAILABLE = False
    logger.warning(f"⚠️  Semantic matching unavailable: {e}")


# ──────────────────────────────────────────────
# Skill taxonomy (extend as needed)
# ──────────────────────────────────────────────
SKILL_SYNONYMS = {
    "js": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "ci/cd": "ci cd",
    "rest": "rest api",
    "oop": "object oriented programming",
}

EDUCATION_LEVELS = {
    "phd": 5, "ph.d": 5, "doctorate": 5,
    "mba": 4, "m.b.a": 4,
    "master": 4, "msc": 4, "m.sc": 4, "m.tech": 4, "mtech": 4, "me": 4,
    "bachelor": 3, "bsc": 3, "b.sc": 3, "b.tech": 3, "btech": 3, "be": 3, "b.e": 3, "ba": 3,
    "diploma": 2, "associate": 2,
    "high school": 1, "12th": 1, "hsc": 1,
}


class ResumeMatcher:
    """
    Match candidate resumes against job descriptions.
    Produces a composite score across:
      - Skills match  (40 %)
      - Experience    (25 %)
      - Education     (15 %)
      - Semantic/NLP  (20 %)
    """

    # Scoring weights
    WEIGHTS = {
        "skills":     0.40,
        "experience": 0.25,
        "education":  0.15,
        "semantic":   0.20,
    }

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def match_candidates_to_job(
        self,
        job: Dict,
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        Match a list of candidate profiles against a job.

        Args:
            job        : job document from MongoDB
            candidates : list of candidate user documents

        Returns:
            List of dicts with match scores added, sorted best-first.
        """
        results = []
        for candidate in candidates:
            try:
                result = self._score_candidate(candidate, job)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scoring candidate {candidate.get('_id')}: {e}")

        results.sort(key=lambda x: x["overallScore"], reverse=True)
        return results

    def calculate_match_score(
        self,
        resume_data: Dict,
        job: Dict
    ) -> Dict:
        """
        Score a single parsed resume against a job.
        Used by match_uploaded_resume route.
        """
        return self._score_candidate(resume_data, job)

    def match_by_text(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict:
        """
        Lightweight text-only match (no structured data needed).
        Called from /api/recruiter/match-resume in app.py.
        """
        resume_skills = self._extract_skills_from_text(resume_text)
        job_skills    = self._extract_skills_from_text(job_description)

        skills_score  = self._score_skills(resume_skills, job_skills)
        semantic_score = self._semantic_score(resume_text, job_description)
        exp_years      = self._extract_experience_years(resume_text)
        req_years      = self._extract_required_experience(job_description)
        exp_score      = self._score_experience(exp_years, req_years)

        overall = round(
            skills_score  * 0.45 +
            exp_score     * 0.25 +
            semantic_score * 0.30,
            1,
        )

        matched_skills  = list(set(resume_skills) & set(job_skills))
        missing_skills  = list(set(job_skills) - set(resume_skills))

        return {
            "matchScore":      overall,
            "skillsScore":     round(skills_score, 1),
            "experienceScore": round(exp_score, 1),
            "semanticScore":   round(semantic_score, 1),
            "matchedSkills":   matched_skills[:15],
            "missingSkills":   missing_skills[:10],
            "feedback":        self._generate_feedback(overall),
        }

    # ──────────────────────────────────────────
    # Internal scoring helpers
    # ──────────────────────────────────────────

    def _score_candidate(self, candidate: Dict, job: Dict) -> Dict:
        """Build a full score breakdown for one candidate vs one job."""

        # ── Skills ──────────────────────────────
        candidate_skills = self._normalise_skills(candidate.get("skills", []))
        job_skills       = self._normalise_skills(
            job.get("skills", []) +
            self._extract_skills_from_text(job.get("requirements", "")) +
            self._extract_skills_from_text(job.get("description", ""))
        )
        skills_score, matched_skills, missing_skills = self._score_skills_detailed(
            candidate_skills, job_skills
        )

        # ── Experience ──────────────────────────
        candidate_exp = self._get_experience_years(candidate)
        required_exp  = self._extract_required_experience(
            job.get("experience", "") + " " + job.get("requirements", "")
        )
        exp_score = self._score_experience(candidate_exp, required_exp)

        # ── Education ───────────────────────────
        candidate_edu = candidate.get("education", "")
        job_edu_req   = job.get("requirements", "") + " " + job.get("description", "")
        edu_score     = self._score_education(candidate_edu, job_edu_req)

        # ── Semantic (NLP) ───────────────────────
        candidate_text = self._build_candidate_text(candidate)
        job_text       = self._build_job_text(job)
        semantic_score = self._semantic_score(candidate_text, job_text)

        # ── Composite ────────────────────────────
        overall = round(
            skills_score  * self.WEIGHTS["skills"] +
            exp_score     * self.WEIGHTS["experience"] +
            edu_score     * self.WEIGHTS["education"] +
            semantic_score * self.WEIGHTS["semantic"],
            1,
        )

        return {
            # Candidate identifiers
            "candidateId":   str(candidate.get("_id", "")),
            "candidateName": candidate.get("name", "Unknown"),
            "email":         candidate.get("email", ""),
            "phone":         candidate.get("phone", ""),
            "location":      candidate.get("location", ""),
            "experience":    f"{candidate_exp} years" if candidate_exp else "Not specified",

            # Scores (0–100)
            "overallScore":    overall,
            "skillsMatch":     round(skills_score, 1),
            "experienceMatch": round(exp_score, 1),
            "educationMatch":  round(edu_score, 1),
            "semanticMatch":   round(semantic_score, 1),

            # Details
            "matchedSkills": matched_skills,
            "missingSkills": missing_skills,
            "tier":          self._assign_tier(overall),
            "recommendation": self._generate_feedback(overall),
        }

    # ── Skills ──────────────────────────────────

    def _normalise_skills(self, skills) -> List[str]:
        """Lower-case, de-duplicate, and apply synonyms."""
        result = []
        for skill in skills:
            s = str(skill).lower().strip()
            s = SKILL_SYNONYMS.get(s, s)
            if s:
                result.append(s)
        return list(set(result))

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Simple keyword extraction from free text."""
        if not text:
            return []
        text_lower = text.lower()

        known_skills = [
            # Programming languages
            "python", "java", "javascript", "typescript", "c++", "c#", "php",
            "ruby", "swift", "kotlin", "go", "rust", "scala", "r", "matlab",
            # Frontend
            "react", "vue", "angular", "html", "css", "tailwind", "bootstrap",
            "next.js", "nuxt",
            # Backend
            "node.js", "django", "flask", "spring boot", "express", "fastapi",
            "laravel", "rails",
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "cassandra", "firebase", "dynamodb",
            # Cloud / DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "ci cd", "jenkins", "github actions", "ansible",
            # ML / Data
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "opencv", "nlp",
            "data science", "data analysis", "tableau", "power bi",
            # Soft / General
            "git", "agile", "scrum", "rest api", "graphql", "microservices",
            "linux", "communication", "teamwork", "leadership",
        ]

        return [skill for skill in known_skills if skill in text_lower]

    def _score_skills(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """Return 0–100 skill match score."""
        if not job_skills:
            return 70.0
        if not candidate_skills:
            return 0.0
        matched = len(set(candidate_skills) & set(job_skills))
        return round(min(100, (matched / len(job_skills)) * 100), 1)

    def _score_skills_detailed(
        self,
        candidate_skills: List[str],
        job_skills: List[str],
    ) -> Tuple[float, List[str], List[str]]:
        """Return (score, matched_list, missing_list)."""
        if not job_skills:
            return 70.0, candidate_skills[:5], []
        matched  = list(set(candidate_skills) & set(job_skills))
        missing  = list(set(job_skills) - set(candidate_skills))
        score    = self._score_skills(candidate_skills, job_skills)
        return score, matched, missing

    # ── Experience ──────────────────────────────

    def _get_experience_years(self, candidate: Dict) -> int:
        """Extract numeric years of experience from candidate data."""
        exp = candidate.get("experience", 0)
        if isinstance(exp, (int, float)):
            return int(exp)
        return self._extract_experience_years(str(exp))

    def _extract_experience_years(self, text: str) -> int:
        """Parse years from text like '3 years', '5+ years exp', etc."""
        patterns = [
            r"(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)",
            r"experience[:\s]+(\d+)\+?\s*years?",
            r"(\d+)\+?\s*yrs?\s+(?:of\s+)?(?:experience|exp)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text.lower())
            if m:
                return int(m.group(1))
        return 0

    def _extract_required_experience(self, text: str) -> int:
        """Pull minimum required years from job text."""
        patterns = [
            r"(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)",
            r"minimum\s+(\d+)\s+years?",
            r"at\s+least\s+(\d+)\s+years?",
            r"(\d+)\s*-\s*\d+\s*years?",  # range like "3-5 years"
        ]
        years_found = []
        for pattern in patterns:
            for m in re.finditer(pattern, text.lower()):
                years_found.append(int(m.group(1)))
        return min(years_found) if years_found else 0

    def _score_experience(self, candidate_years: int, required_years: int) -> float:
        """Return 0–100 experience match score."""
        if required_years == 0:
            return 80.0
        if candidate_years >= required_years:
            bonus = min(10, (candidate_years - required_years) * 2)
            return min(100, 85 + bonus)
        ratio = candidate_years / required_years
        return round(ratio * 75, 1)

    # ── Education ───────────────────────────────

    def _score_education(self, candidate_edu: str, job_req: str) -> float:
        """Return 0–100 education match score."""
        candidate_level = self._get_education_level(candidate_edu)
        required_level  = self._get_required_education_level(job_req)

        if required_level == 0:
            return 80.0
        if candidate_level >= required_level:
            return 90.0 if candidate_level == required_level else 100.0
        gap = required_level - candidate_level
        return max(0, 80 - gap * 20)

    def _get_education_level(self, text: str) -> int:
        text_lower = text.lower()
        for keyword, level in sorted(EDUCATION_LEVELS.items(), key=lambda x: -x[1]):
            if keyword in text_lower:
                return level
        return 0

    def _get_required_education_level(self, text: str) -> int:
        text_lower = text.lower()
        for keyword, level in sorted(EDUCATION_LEVELS.items(), key=lambda x: -x[1]):
            if keyword in text_lower:
                return level
        return 0

    # ── Semantic ────────────────────────────────

    def _semantic_score(self, text1: str, text2: str) -> float:
        """Return 0–100 semantic similarity. Falls back to keyword overlap."""
        if not text1 or not text2:
            return 50.0

        if SEMANTIC_AVAILABLE:
            try:
                emb1 = _ST_MODEL.encode(text1[:512], convert_to_tensor=True)
                emb2 = _ST_MODEL.encode(text2[:512], convert_to_tensor=True)
                sim  = util.pytorch_cos_sim(emb1, emb2)[0][0].item()
                return round((sim + 1) / 2 * 100, 1)  # map [-1,1] → [0,100]
            except Exception as e:
                logger.warning(f"Semantic scoring error: {e}")

        # Fallback: Jaccard similarity on words
        words1 = set(re.findall(r'\b\w{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b\w{3,}\b', text2.lower()))
        if not words1 or not words2:
            return 50.0
        intersection = words1 & words2
        union        = words1 | words2
        return round((len(intersection) / len(union)) * 100, 1)

    # ── Misc helpers ────────────────────────────

    def _build_candidate_text(self, candidate: Dict) -> str:
        parts = [
            candidate.get("name", ""),
            " ".join(candidate.get("skills", [])),
            candidate.get("education", ""),
            candidate.get("summary", ""),
            str(candidate.get("experience", "")),
        ]
        return " ".join(filter(None, parts))

    def _build_job_text(self, job: Dict) -> str:
        parts = [
            job.get("title", ""),
            " ".join(job.get("skills", [])),
            job.get("description", ""),
            job.get("requirements", ""),
            job.get("experience", ""),
        ]
        return " ".join(filter(None, parts))

    def _assign_tier(self, score: float) -> str:
        if score >= 85: return "Excellent"
        if score >= 70: return "Strong"
        if score >= 55: return "Good"
        if score >= 40: return "Average"
        return "Below Average"

    def _generate_feedback(self, score: float) -> str:
        if score >= 85: return "Highly Recommended – Schedule interview immediately"
        if score >= 70: return "Recommended – Strong candidate, proceed with interview"
        if score >= 55: return "Consider – Good potential, review in detail"
        if score >= 40: return "Maybe – Requires careful evaluation"
        return "Not Recommended – Significant skill gaps"
