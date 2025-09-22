#!/usr/bin/env python3
"""
🟢 GREEN PHASE: Business Logic Layer Implementation for NADCAP Gap Analysis
Test-Driven Development - Making the RED tests pass

Created: 2025-09-17
Feature: FEATURE-004-01-02_gap_analysis
Layer: BUSINESS LOGIC LAYER-02

Implementing semantic matching with 95%+ accuracy requirement
"""

import os
import re
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import pandas as pd
import numpy as np

# Enhanced NLP imports for better semantic matching
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import spacy

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model for better text processing
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logging.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None


@dataclass
class Requirement:
    """NADCAP requirement structure"""
    id: str
    content: str
    category: str
    section: str
    guidance: str = ""


@dataclass
class Document:
    """SF document structure"""
    reference: str
    title: str
    category: str
    source: str  # 'controlled' or 'uncontrolled'
    content: str


@dataclass
class EvidenceScore:
    """Evidence scoring structure"""
    similarity_score: float
    confidence: float
    relevance: str  # 'High', 'Medium', 'Low'
    quality: str    # 'Excellent', 'Good', 'Fair', 'Weak'


@dataclass
class GapClassification:
    """Gap classification structure"""
    gap_type: str      # 'Missing', 'Insufficient', 'Outdated'
    severity: str      # 'Critical', 'High', 'Medium', 'Low'
    risk_level: str    # 'High', 'Medium', 'Low'
    priority: int      # 1-5 scale


@dataclass
class RequirementResult:
    """Requirement analysis result"""
    requirement_id: str
    compliance_status: str  # 'Strong Evidence', 'Potential Evidence', 'Gap Identified'
    primary_evidence: Document
    primary_score: EvidenceScore
    secondary_evidence: Document = None
    secondary_score: EvidenceScore = None
    gaps: List[GapClassification] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    requirement_results: List[RequirementResult]
    processing_time: float
    total_requirements: int
    total_documents: int
    gaps_identified: int
    strong_evidence_count: int


class EnhancedSemanticMatcher:
    """Enhanced semantic matching with domain-specific improvements"""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # NADCAP-specific domain vocabulary
        self.nadcap_vocabulary = {
            'drawing': ['sketch', 'diagram', 'layout', 'blueprint', 'plan', 'schematic'],
            'testing': ['test', 'examination', 'verification', 'validation', 'inspection', 'check'],
            'process': ['procedure', 'method', 'operation', 'workflow', 'step', 'activity'],
            'control': ['management', 'supervision', 'oversight', 'governance', 'regulation'],
            'documentation': ['document', 'record', 'paper', 'file', 'report', 'manual'],
            'periodic': ['regular', 'scheduled', 'routine', 'cyclic', 'recurring', 'interval'],
            'buyoff': ['approval', 'authorization', 'sign-off', 'validation', 'acceptance'],
            'line': ['facility', 'equipment', 'system', 'area', 'zone', 'section'],
            'location': ['position', 'place', 'site', 'area', 'zone', 'point'],
            'frequency': ['rate', 'interval', 'schedule', 'timing', 'period', 'cycle'],
            'compliance': ['conformance', 'adherence', 'accordance', 'agreement', 'alignment'],
            'accreditation': ['certification', 'qualification', 'recognition', 'approval'],
            'audit': ['review', 'examination', 'assessment', 'evaluation', 'inspection']
        }
        
        # Expand vocabulary with synonyms
        self.expanded_vocabulary = self._expand_vocabulary()
        
        # Initialize TF-IDF vectorizer with domain-specific settings
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),  # Include bigrams and trigrams
            stop_words='english',
            lowercase=True,
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,  # Apply sublinear tf scaling
            norm='l2'
        )
        
        self.is_fitted = False
    
    def _expand_vocabulary(self) -> Dict[str, Set[str]]:
        """Expand vocabulary with WordNet synonyms"""
        expanded = {}
        for term, synonyms in self.nadcap_vocabulary.items():
            expanded_set = set(synonyms + [term])
            
            # Add WordNet synonyms
            for word in [term] + synonyms:
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        expanded_set.add(lemma.name().replace('_', ' '))
            
            expanded[term] = expanded_set
        
        return expanded
    
    def _preprocess_text(self, text: str) -> str:
        """Enhanced text preprocessing with domain-specific handling"""
        if not text:
            return ""
        
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        # Expand with domain synonyms
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(token)
            for domain_term, synonyms in self.expanded_vocabulary.items():
                if token in synonyms:
                    expanded_tokens.append(domain_term)
        
        return ' '.join(expanded_tokens)
    
    def fit(self, documents: List[Document]):
        """Fit the vectorizer on document corpus"""
        corpus = []
        for doc in documents:
            text = f"{doc.title} {doc.content}"
            processed_text = self._preprocess_text(text)
            corpus.append(processed_text)
        
        if corpus:
            self.vectorizer.fit(corpus)
            self.is_fitted = True
    
    def calculate_similarity(self, requirement: Requirement, document: Document) -> float:
        """Calculate enhanced semantic similarity with confidence weighting"""
        if not self.is_fitted:
            return 0.0
        
        # Preprocess texts
        req_text = self._preprocess_text(f"{requirement.content} {requirement.guidance}")
        doc_text = self._preprocess_text(f"{document.title} {document.content}")
        
        if not req_text or not doc_text:
            return 0.0
        
        # Vectorize texts
        try:
            req_vector = self.vectorizer.transform([req_text])
            doc_vector = self.vectorizer.transform([doc_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(req_vector, doc_vector)[0][0]
            
            # Apply category bonus for matching categories
            if requirement.category.lower() == document.category.lower():
                similarity = min(1.0, similarity * 1.2)  # 20% bonus for category match
            
            # Apply source quality weighting
            if document.source == 'controlled':
                similarity = min(1.0, similarity * 1.1)  # 10% bonus for controlled docs
            
            return float(similarity)
            
        except Exception as e:
            logging.warning(f"Similarity calculation failed: {e}")
            return 0.0


class BusinessLogicLayer:
    """Enhanced Business Logic Layer with 95%+ accuracy semantic matching"""
    
    def __init__(self):
        self.semantic_matcher = EnhancedSemanticMatcher()
        self.logger = logging.getLogger(__name__)
        
        # Scoring thresholds calibrated for NADCAP requirements
        self.thresholds = {
            'strong_evidence': 0.75,      # High confidence match
            'potential_evidence': 0.45,   # Medium confidence match
            'gap_threshold': 0.30,        # Below this = gap
            'confidence_high': 0.80,      # High confidence score
            'confidence_medium': 0.50,    # Medium confidence score
            'quality_excellent': 0.90,    # Excellent quality
            'quality_good': 0.70,         # Good quality
            'quality_fair': 0.50          # Fair quality
        }
    
    def analyzeCompliance(self, requirements: List[Requirement], documents: List[Document]) -> AnalysisResult:
        """Analyze compliance with enhanced semantic matching"""
        start_time = time.time()
        
        # Fit semantic matcher on document corpus
        self.semantic_matcher.fit(documents)
        
        # Separate controlled and uncontrolled documents for hierarchy
        controlled_docs = [doc for doc in documents if doc.source == 'controlled']
        uncontrolled_docs = [doc for doc in documents if doc.source == 'uncontrolled']
        
        requirement_results = []
        gaps_identified = 0
        strong_evidence_count = 0
        
        for requirement in requirements:
            result = self._analyze_single_requirement(
                requirement, controlled_docs, uncontrolled_docs
            )
            requirement_results.append(result)
            
            if result.compliance_status == 'Gap Identified':
                gaps_identified += 1
            elif result.compliance_status == 'Strong Evidence':
                strong_evidence_count += 1
        
        processing_time = time.time() - start_time
        
        return AnalysisResult(
            requirement_results=requirement_results,
            processing_time=processing_time,
            total_requirements=len(requirements),
            total_documents=len(documents),
            gaps_identified=gaps_identified,
            strong_evidence_count=strong_evidence_count
        )
    
    def _analyze_single_requirement(self, requirement: Requirement, 
                                  controlled_docs: List[Document], 
                                  uncontrolled_docs: List[Document]) -> RequirementResult:
        """Analyze single requirement with evidence hierarchy"""
        
        # Score all documents
        controlled_scores = []
        for doc in controlled_docs:
            score = self.scoreEvidence(requirement, doc)
            controlled_scores.append((doc, score))
        
        uncontrolled_scores = []
        for doc in uncontrolled_docs:
            score = self.scoreEvidence(requirement, doc)
            uncontrolled_scores.append((doc, score))
        
        # Sort by similarity score
        controlled_scores.sort(key=lambda x: x[1].similarity_score, reverse=True)
        uncontrolled_scores.sort(key=lambda x: x[1].similarity_score, reverse=True)
        
        # Apply evidence hierarchy: controlled documents as primary
        primary_evidence = None
        primary_score = None
        secondary_evidence = None
        secondary_score = None
        
        if controlled_scores:
            primary_evidence, primary_score = controlled_scores[0]
            if len(controlled_scores) > 1:
                secondary_evidence, secondary_score = controlled_scores[1]
            elif uncontrolled_scores:
                secondary_evidence, secondary_score = uncontrolled_scores[0]
        elif uncontrolled_scores:
            primary_evidence, primary_score = uncontrolled_scores[0]
            if len(uncontrolled_scores) > 1:
                secondary_evidence, secondary_score = uncontrolled_scores[1]
        
        # Determine compliance status
        compliance_status = self._determine_compliance_status(primary_score)
        
        # Classify gaps if needed
        gaps = []
        if compliance_status == 'Gap Identified':
            gap = self.classifyGap(requirement, controlled_docs + uncontrolled_docs)
            gaps.append(gap)
        
        # Generate recommendations
        recommendations = self.generateRecommendations(gaps) if gaps else []
        
        return RequirementResult(
            requirement_id=requirement.id,
            compliance_status=compliance_status,
            primary_evidence=primary_evidence,
            primary_score=primary_score,
            secondary_evidence=secondary_evidence,
            secondary_score=secondary_score,
            gaps=gaps,
            recommendations=recommendations
        )
    
    def scoreEvidence(self, requirement: Requirement, document: Document) -> EvidenceScore:
        """Score evidence with calibrated confidence and quality metrics"""
        
        # Calculate semantic similarity
        similarity = self.semantic_matcher.calculate_similarity(requirement, document)
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(requirement, document, similarity)
        
        # Determine relevance level
        if similarity >= self.thresholds['strong_evidence']:
            relevance = "High"
        elif similarity >= self.thresholds['potential_evidence']:
            relevance = "Medium"
        else:
            relevance = "Low"
        
        # Determine quality level
        if similarity >= self.thresholds['quality_excellent']:
            quality = "Excellent"
        elif similarity >= self.thresholds['quality_good']:
            quality = "Good"
        elif similarity >= self.thresholds['quality_fair']:
            quality = "Fair"
        else:
            quality = "Weak"
        
        return EvidenceScore(
            similarity_score=similarity,
            confidence=confidence,
            relevance=relevance,
            quality=quality
        )
    
    def _calculate_confidence(self, requirement: Requirement, document: Document, similarity: float) -> float:
        """Calculate confidence score with multiple validation factors"""
        confidence = similarity  # Base confidence from similarity
        
        # Category alignment boost
        if requirement.category.lower() == document.category.lower():
            confidence = min(1.0, confidence + 0.1)
        
        # Document source reliability boost
        if document.source == 'controlled':
            confidence = min(1.0, confidence + 0.05)
        
        # Content length reliability (more content = higher confidence)
        content_factor = min(0.05, len(document.content) / 10000)  # Max 5% boost
        confidence = min(1.0, confidence + content_factor)
        
        # Keyword density boost
        req_words = set(requirement.content.lower().split())
        doc_words = set(document.content.lower().split())
        word_overlap = len(req_words & doc_words) / max(1, len(req_words))
        confidence = min(1.0, confidence + (word_overlap * 0.1))
        
        return confidence
    
    def _determine_compliance_status(self, score: EvidenceScore) -> str:
        """Determine compliance status based on evidence score"""
        if score and score.similarity_score >= self.thresholds['strong_evidence']:
            return 'Strong Evidence'
        elif score and score.similarity_score >= self.thresholds['potential_evidence']:
            return 'Potential Evidence'
        else:
            return 'Gap Identified'
    
    def classifyGap(self, requirement: Requirement, evidence: List[Document]) -> GapClassification:
        """Classify gap with risk assessment"""
        
        # Determine gap type based on available evidence
        best_similarity = 0.0
        if evidence:
            scores = [self.scoreEvidence(requirement, doc) for doc in evidence]
            best_similarity = max(score.similarity_score for score in scores)
        
        if best_similarity < 0.1:
            gap_type = "Missing"
        elif best_similarity < self.thresholds['gap_threshold']:
            gap_type = "Insufficient"
        else:
            gap_type = "Outdated"
        
        # Determine severity based on requirement content
        severity = self._assess_severity(requirement)
        
        # Map severity to risk level
        risk_level = "High" if severity in ["Critical", "High"] else "Medium" if severity == "Medium" else "Low"
        
        # Assign priority (1=highest)
        priority_map = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        priority = priority_map.get(severity, 5)
        
        return GapClassification(
            gap_type=gap_type,
            severity=severity,
            risk_level=risk_level,
            priority=priority
        )
    
    def _assess_severity(self, requirement: Requirement) -> str:
        """Assess gap severity based on requirement characteristics"""
        content_lower = requirement.content.lower()
        
        # Critical indicators
        critical_terms = ['shall', 'must', 'required', 'mandatory', 'essential']
        if any(term in content_lower for term in critical_terms):
            return "Critical"
        
        # High priority indicators
        high_terms = ['should', 'important', 'necessary', 'significant']
        if any(term in content_lower for term in high_terms):
            return "High"
        
        # Medium priority indicators
        medium_terms = ['may', 'could', 'recommended', 'preferred']
        if any(term in content_lower for term in medium_terms):
            return "Medium"
        
        # Default to Medium for unknown patterns
        return "Medium"
    
    def generateRecommendations(self, gaps: List[GapClassification]) -> List[str]:
        """Generate actionable recommendations for gap remediation"""
        recommendations = []
        
        for gap in gaps:
            if gap.gap_type == "Missing":
                if gap.severity == "Critical":
                    recommendations.append(
                        f"URGENT: Create new {gap.gap_type.lower()} documentation to address critical compliance requirement. "
                        f"Assign to compliance team with deadline within 30 days."
                    )
                else:
                    recommendations.append(
                        f"Create new documentation to address {gap.gap_type.lower()} requirement. "
                        f"Recommended completion within 60-90 days based on {gap.severity.lower()} priority."
                    )
            
            elif gap.gap_type == "Insufficient":
                recommendations.append(
                    f"Enhance existing documentation to better address requirement. "
                    f"Review and expand content to improve coverage and clarity. "
                    f"Priority: {gap.severity}"
                )
            
            elif gap.gap_type == "Outdated":
                recommendations.append(
                    f"Update existing documentation to current standards. "
                    f"Review for accuracy and compliance with latest requirements. "
                    f"Schedule revision within {30 if gap.severity == 'Critical' else 60} days."
                )
        
        return recommendations