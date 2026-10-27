"""
AI/ML Engine for Societal Innovation Platform
Implements:
1. NLP Classification of Societal Problems (TF-IDF + Calibrated Classifier)
2. Semantic Duplicate Detection & Related Problem Identification (Cosine Similarity)
3. Multi-Criteria University & Expert Matching (Domain Affinity + Keyword Relevance + Proximity)
4. Dynamic Urgency & Priority Scoring
5. Explainability Pipeline for Academic Demonstrations & Viva
"""

import re
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

from app.training_data import TRAINING_DATA, DOMAINS, UNIVERSITIES

# High-urgency alert vocabulary for societal impact
CRITICAL_KEYWORDS = {
    "fatal", "death", "outbreak", "poison", "poisoning", "collapse", "epidemic",
    "drowning", "fluorosis", "arsenic", "contamination", "crisis", "starvation",
    "emergency", "subsidence", "landslide", "electrocution", "flash flood"
}

HIGH_KEYWORDS = {
    "severe", "acute", "shortage", "malnutrition", "dropout", "drought",
    "infestation", "overflowing", "hazardous", "polluted", "loss", "broken",
    "unemployment", "damage", "potholes", "disease"
}


class SocietalAIEngine:
    def __init__(self):
        self.domains = DOMAINS
        self.universities = UNIVERSITIES
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            stop_words='english',
            sublinear_tf=True
        )
        self.classifier = LogisticRegression(C=2.5, max_iter=500, random_state=42)
        self.is_trained = False
        self._train()

    def _train(self):
        """Train classifier and vectorizer on initial training dataset."""
        corpus = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]

        X_tfidf = self.vectorizer.fit_transform(corpus)
        self.classifier.fit(X_tfidf, labels)
        self.is_trained = True

    def clean_text(self, text: str) -> str:
        """Preprocess text: lowercasing and basic punctuation cleanup."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def predict_domain(self, text: str) -> Dict[str, Any]:
        """
        Predict societal problem domain and return confidence scores for all classes.
        """
        cleaned = self.clean_text(text)
        vec = self.vectorizer.transform([cleaned])
        probas = self.classifier.predict_proba(vec)[0]
        classes = self.classifier.classes_

        class_probs = []
        for c, p in zip(classes, probas):
            class_probs.append({
                "domain": c,
                "confidence": round(float(p) * 100, 2)
            })

        # Sort descending by confidence
        class_probs.sort(key=lambda x: x["confidence"], reverse=True)

        top_domain = class_probs[0]["domain"]
        top_confidence = class_probs[0]["confidence"]

        # Feature explanation (top TF-IDF words extracted)
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        row = vec.toarray()[0]
        top_indices = np.argsort(row)[::-1]
        active_terms = []
        for idx in top_indices:
            if row[idx] > 0:
                active_terms.append({
                    "term": feature_names[idx],
                    "weight": round(float(row[idx]), 3)
                })
            if len(active_terms) >= 8:
                break

        return {
            "predicted_domain": top_domain,
            "confidence": top_confidence,
            "all_probabilities": class_probs,
            "key_features": active_terms
        }

    def detect_duplicates(self, new_text: str, existing_problems: List[Dict[str, Any]], threshold: float = 0.35) -> Dict[str, Any]:
        """
        Compute TF-IDF Cosine Similarity against existing database problems.
        Flags potential duplicates and closely related societal issues.
        """
        if not existing_problems:
            return {
                "has_duplicates": False,
                "matches": [],
                "highest_similarity": 0.0
            }

        # Build corpus of existing problem titles + descriptions
        existing_corpus = [
            f"{p.get('title', '')} {p.get('description', '')}"
            for p in existing_problems
        ]

        # Vectorize both
        all_texts = existing_corpus + [new_text]
        tfidf_matrix = self.vectorizer.transform(all_texts)

        # Vector of new problem is the last row
        new_vec = tfidf_matrix[-1]
        existing_matrix = tfidf_matrix[:-1]

        # Cosine similarity
        sim_scores = cosine_similarity(new_vec, existing_matrix)[0]

        matches = []
        for i, score in enumerate(sim_scores):
            similarity_pct = round(float(score) * 100, 2)
            if score >= threshold:
                matched_p = existing_problems[i]
                status_label = "Duplicate" if score >= 0.65 else "Related"
                matches.append({
                    "problem_id": matched_p.get("id"),
                    "title": matched_p.get("title"),
                    "category": matched_p.get("domain", matched_p.get("category")),
                    "state": matched_p.get("state", "Jharkhand"),
                    "district": matched_p.get("district"),
                    "similarity": similarity_pct,
                    "type": status_label
                })

        matches.sort(key=lambda x: x["similarity"], reverse=True)

        return {
            "has_duplicates": len([m for m in matches if m["similarity"] >= 65.0]) > 0,
            "duplicate_count": len([m for m in matches if m["similarity"] >= 65.0]),
            "related_count": len([m for m in matches if m["similarity"] < 65.0]),
            "highest_similarity": matches[0]["similarity"] if matches else 0.0,
            "matches": matches[:5]
        }

    def match_universities(self, text: str, domain: str, district: str = None, state: str = None) -> List[Dict[str, Any]]:
        """
        Multi-criteria institutional recommendation:
        1. Domain alignment score (45%)
        2. Keyword & research semantic match (40%)
        3. Regional proximity to affected district/state (15%)
        """
        cleaned = self.clean_text(text)
        words = set(cleaned.split())

        ranked_universities = []
        for uni in self.universities:
            # Domain match score
            if domain in uni["primary_domains"]:
                domain_score = 100.0 if domain == uni["primary_domains"][0] else 85.0
            else:
                domain_score = 25.0

            # Keyword match score
            keyword_hits = []
            for kw in uni["expertise_keywords"]:
                if kw in cleaned or any(kw in w for w in words):
                    keyword_hits.append(kw)

            keyword_score = min(len(keyword_hits) * 22.0, 100.0)
            if not keyword_hits:
                keyword_score = 15.0

            # Geographic proximity score
            uni_state = uni.get("state", "Jharkhand")
            district_match = False
            state_match = False

            if state and state.strip():
                state_match = (state.strip().lower() == uni_state.lower())
            else:
                # If state not provided (legacy call), treat as regional if district matches or fallback
                state_match = True

            if district and district.strip() and state_match:
                dist_clean = district.strip().lower()
                for d in uni.get("districts", []):
                    if dist_clean in d.lower() or d.lower() in dist_clean:
                        district_match = True
                        break

            if district_match:
                geo_score = 100.0
            elif state_match:
                geo_score = 60.0
            else:
                # Nationwide remote partner: honest cross-state alignment score
                geo_score = 25.0

            # Composite weighted match score
            composite = (domain_score * 0.45) + (keyword_score * 0.40) + (geo_score * 0.15)
            composite = round(min(composite, 99.0), 1)

            rationale = []
            if domain in uni["primary_domains"]:
                rationale.append(f"Primary center for {domain}")
            if keyword_hits:
                rationale.append(f"Specialized in {', '.join(keyword_hits[:3])}")
            if district_match:
                rationale.append(f"Active presence in {district}")
            elif state_match:
                rationale.append(f"Regional state presence ({uni_state})")
            else:
                rationale.append(f"National research partner (Remote alignment; based in {uni_state})")

            ranked_universities.append({
                "university_id": uni["id"],
                "name": uni["name"],
                "match_score": composite,
                "domain_score": domain_score,
                "keyword_score": keyword_score,
                "matched_keywords": keyword_hits,
                "faculty_lead": uni["faculty_lead"],
                "departments": uni["departments"],
                "rationale": " • ".join(rationale) if rationale else "General engineering & scientific expertise"
            })

        ranked_universities.sort(key=lambda x: x["match_score"], reverse=True)
        return ranked_universities[:4]

    def calculate_priority(self, text: str, reported_urgency: str = "Medium",
                           population_impact: str = "Community", duplicate_count: int = 0) -> Dict[str, Any]:
        """
        Calculate composite priority index (0-100) and severity level:
        CRITICAL (>=75), HIGH (>=50), MEDIUM (>=30), LOW (<30)
        """
        score = 0
        factors = []
        cleaned = self.clean_text(text)

        # 1. Critical keyword detection (+25)
        crit_found = [w for w in CRITICAL_KEYWORDS if w in cleaned]
        high_found = [w for w in HIGH_KEYWORDS if w in cleaned]

        if crit_found:
            score += 30
            factors.append(f"Critical hazards detected: {', '.join(crit_found[:3])}")
        elif high_found:
            score += 18
            factors.append(f"High-severity indicators: {', '.join(high_found[:3])}")
        else:
            score += 8

        # 2. Citizen reported urgency (+10 to +30)
        urg_map = {"Critical": 30, "High": 22, "Medium": 14, "Low": 6}
        urg_score = urg_map.get(reported_urgency, 14)
        score += urg_score
        factors.append(f"Reported urgency: {reported_urgency} (+{urg_score} pts)")

        # 3. Population scale (+8 to +25)
        pop_map = {
            "Entire District": 25,
            "Multiple Villages / Block": 18,
            "Village / Town Ward": 12,
            "Community": 10,
            "Individual / Single Facility": 6
        }
        pop_score = pop_map.get(population_impact, 10)
        score += pop_score
        factors.append(f"Scale of impact: {population_impact} (+{pop_score} pts)")

        # 4. Multi-reporter cluster boost (+5 per duplicate, up to +15)
        if duplicate_count > 0:
            cluster_boost = min(duplicate_count * 5, 15)
            score += cluster_boost
            factors.append(f"Multi-citizen cluster (+{cluster_boost} pts from {duplicate_count} related reports)")

        score = min(max(score, 10), 100)

        if score >= 75:
            level = "CRITICAL"
            badge_color = "red"
        elif score >= 50:
            level = "HIGH"
            badge_color = "amber"
        elif score >= 30:
            level = "MEDIUM"
            badge_color = "blue"
        else:
            level = "LOW"
            badge_color = "gray"

        return {
            "priority_score": score,
            "priority_level": level,
            "badge_color": badge_color,
            "factors": factors
        }

    def full_problem_analysis(self, title: str, description: str, district: str = "",
                              state: str = "Jharkhand",
                              reported_urgency: str = "Medium", population_impact: str = "Community",
                              existing_problems: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Unified AI pipeline executed upon submission or live demo.
        """
        full_text = f"{title}. {description}"
        if existing_problems is None:
            existing_problems = []

        # 1. NLP Classification
        nlp_res = self.predict_domain(full_text)
        predicted_domain = nlp_res["predicted_domain"]

        # 2. Semantic Duplicate Detection
        dup_res = self.detect_duplicates(full_text, existing_problems)

        # 3. AI University Recommendation
        uni_matches = self.match_universities(full_text, predicted_domain, district=district, state=state)

        # 4. Priority Calculation
        priority_res = self.calculate_priority(
            full_text,
            reported_urgency=reported_urgency,
            population_impact=population_impact,
            duplicate_count=dup_res.get("duplicate_count", 0)
        )

        return {
            "nlp_classification": nlp_res,
            "duplicate_detection": dup_res,
            "recommended_universities": uni_matches,
            "priority": priority_res
        }


# Singleton engine instance
ai_engine = SocietalAIEngine()
