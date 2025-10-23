#!/usr/bin/env python3
"""
MVP Semantic Template Mapper

Automatically maps natural language requirements to template selections.
Analyzes requirements and selects optimal template combinations.

Usage:
    python mvp_semantic_mapper.py "SaaS landing page with email capture"
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TemplateMetadata:
    """Template metadata from index.yaml and meta.yml"""
    id: str
    name: str
    path: str
    layer_type: str  # api, ui, infra, data, composite
    frameworks: List[str]
    tags: List[str]
    version: str
    status: str
    description: str
    cost_estimate_tokens: int
    outputs: Optional[List[Dict[str, str]]] = None
    variables_schema: Optional[Dict[str, Any]] = None


@dataclass
class TemplateMatch:
    """Template match with confidence score"""
    template: TemplateMetadata
    confidence: float
    matched_keywords: List[str]
    reasons: List[str]


@dataclass
class RequirementAnalysis:
    """Analyzed requirement with extracted entities"""
    raw_requirement: str
    entities: List[str]  # What (user, product, email, etc.)
    actions: List[str]  # What to do (capture, store, authenticate, etc.)
    technologies: List[str]  # Explicit tech mentions (FastAPI, React, etc.)
    patterns: List[str]  # Design patterns (CRUD, auth, landing, etc.)
    infrastructure: List[str]  # Deploy, database, cache, etc.
    
    # Semantic categories
    needs_frontend: bool = False
    needs_backend: bool = False
    needs_database: bool = False
    needs_auth: bool = False
    needs_deployment: bool = False
    needs_payments: bool = False
    needs_realtime: bool = False


class SemanticTemplateMapper:
    """Maps natural language requirements to templates"""
    
    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Path("templates/mvp")
        self.templates: List[TemplateMetadata] = []
        self.template_index: Dict[str, TemplateMetadata] = {}
        
        # Keyword dictionaries for semantic analysis
        self.keyword_mappings = {
            'frontend': [
                'landing', 'page', 'ui', 'website', 'react',
                'interface', 'form', 'dashboard'
            ],
            'backend': [
                'api', 'server', 'endpoint', 'service',
                'backend', 'fastapi'
            ],
            'database': [
                'store', 'save', 'persist', 'database',
                'data', 'record', 'user'
            ],
            'auth': [
                'login', 'signup', 'register', 'authenticate',
                'auth', 'user', 'password'
            ],
            'deployment': [
                'deploy', 'host', 'railway', 'production', 'serve'
            ],
            'payments': [
                'payment', 'stripe', 'checkout', 'subscription',
                'billing', 'saas'
            ],
            'realtime': [
                'realtime', 'live', 'websocket', 'streaming',
                'notification'
            ],
            'crud': [
                'create', 'read', 'update', 'delete', 'crud',
                'manage', 'list'
            ],
            'analytics': [
                'analytics', 'tracking', 'ga4', 'google analytics',
                'mixpanel', 'amplitude', 'metrics', 'events',
                'monitor', 'measure', 'track'
            ],
        }        # Action verbs
        self.action_verbs = {
            'capture', 'collect', 'store', 'save', 'create', 'build', 'generate',
            'authenticate', 'authorize', 'login', 'signup', 'register',
            'display', 'show', 'render', 'visualize',
            'process', 'handle', 'manage', 'track',
            'deploy', 'host', 'serve', 'run',
        }
        
        # Entity nouns
        self.entity_nouns = {
            'user', 'customer', 'email', 'data', 'product', 'order',
            'payment', 'subscription', 'account', 'profile',
            'landing', 'page', 'dashboard', 'form', 'api', 'service',
        }
        
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from templates/mvp/index.yaml"""
        index_file = self.templates_dir / "index.yaml"
        
        if not index_file.exists():
            print(f"⚠️  Template index not found: {index_file}")
            return
        
        with open(index_file, 'r') as f:
            index_data = yaml.safe_load(f)
        
        for template_data in index_data.get('templates', []):
            template = TemplateMetadata(
                id=template_data['id'],
                name=template_data['name'],
                path=template_data['path'],
                layer_type=template_data['layer_type'],
                frameworks=template_data.get('frameworks', []),
                tags=template_data.get('tags', []),
                version=template_data['version'],
                status=template_data['status'],
                description=template_data.get('description', ''),
                cost_estimate_tokens=template_data.get('cost_estimate_tokens', 0),
            )
            
            # Load additional metadata from meta.yml if it exists
            template_path = self.templates_dir / template_data['path']
            meta_file = template_path / "meta.yml"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    meta_data = yaml.safe_load(f)
                    template.outputs = meta_data.get('outputs', [])
            
            self.templates.append(template)
            self.template_index[template.id] = template
        
        print(f"✅ Loaded {len(self.templates)} templates from {index_file}")
    
    def analyze_requirement(self, requirement: str) -> RequirementAnalysis:
        """Analyze natural language requirement and extract semantic information"""
        req_lower = requirement.lower()
        words = set(re.findall(r'\b\w+\b', req_lower))
        
        analysis = RequirementAnalysis(
            raw_requirement=requirement,
            entities=[],
            actions=[],
            technologies=[],
            patterns=[],
            infrastructure=[],
        )
        
        # Extract entities (nouns)
        analysis.entities = [word for word in words if word in self.entity_nouns]
        
        # Extract actions (verbs)
        analysis.actions = [word for word in words if word in self.action_verbs]
        
        # Extract technologies
        tech_patterns = {
            'fastapi': 'FastAPI',
            'react': 'React',
            'stripe': 'Stripe',
            'postgresql': 'PostgreSQL',
            'railway': 'Railway',
        }
        for pattern, tech in tech_patterns.items():
            if pattern in req_lower:
                analysis.technologies.append(tech)
        
        # Detect patterns
        if any(word in req_lower for word in ['crud', 'create', 'read', 'update', 'delete']):
            analysis.patterns.append('CRUD')
        if any(word in req_lower for word in ['landing', 'homepage', 'hero']):
            analysis.patterns.append('Landing Page')
        if any(word in req_lower for word in ['auth', 'login', 'signup', 'register']):
            analysis.patterns.append('Authentication')
        
        # Semantic categorization
        analysis.needs_frontend = any(
            word in req_lower for word in self.keyword_mappings['frontend']
        )
        analysis.needs_backend = any(
            word in req_lower for word in self.keyword_mappings['backend']
        ) or analysis.needs_frontend  # Frontend usually needs backend
        
        analysis.needs_database = any(
            word in req_lower for word in self.keyword_mappings['database']
        )
        analysis.needs_auth = any(
            word in req_lower for word in self.keyword_mappings['auth']
        )
        analysis.needs_deployment = any(
            word in req_lower
            for word in self.keyword_mappings['deployment']
        )
        analysis.needs_payments = any(
            word in req_lower for word in self.keyword_mappings['payments']
        )
        analysis.needs_realtime = any(
            word in req_lower for word in self.keyword_mappings['realtime']
        )
        
        # Add analytics detection
        needs_analytics = any(
            word in req_lower for word in self.keyword_mappings['analytics']
        )
        if needs_analytics:
            analysis.infrastructure.append('analytics')
        
        return analysis
    
    def score_template_match(
        self,
        template: TemplateMetadata,
        analysis: RequirementAnalysis
    ) -> Tuple[float, List[str], List[str]]:
        """
        Score how well a template matches the requirement analysis.
        
        Returns:
            (confidence_score, matched_keywords, reasons)
        """
        score = 0.0
        matched_keywords = []
        reasons = []
        
        req_lower = analysis.raw_requirement.lower()
        
        # Check layer type alignment
        layer_scores = {
            'ui': 30 if analysis.needs_frontend else 0,
            'api': 30 if analysis.needs_backend else 0,
            'infra': 25 if analysis.needs_deployment else 0,
        }
        if template.layer_type in layer_scores:
            layer_score = layer_scores[template.layer_type]
            if layer_score > 0:
                score += layer_score
                reasons.append(f"{template.layer_type} layer matches requirement")
        
        # Check tags match
        for tag in template.tags:
            if tag.lower() in req_lower:
                score += 15
                matched_keywords.append(tag)
                reasons.append(f"Tag '{tag}' found in requirement")
        
        # Check frameworks match
        for framework in template.frameworks:
            if framework.lower() in req_lower or framework in analysis.technologies:
                score += 10
                matched_keywords.append(framework)
                reasons.append(f"Framework '{framework}' mentioned")
        
        # Check description similarity
        desc_lower = template.description.lower()
        desc_words = set(re.findall(r'\b\w+\b', desc_lower))
        req_words = set(re.findall(r'\b\w+\b', req_lower))
        common_words = desc_words & req_words
        
        # Remove common words (the, a, an, etc.)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with'}
        meaningful_common = common_words - stop_words
        
        if meaningful_common:
            word_match_score = min(len(meaningful_common) * 5, 20)
            score += word_match_score
            matched_keywords.extend(list(meaningful_common)[:3])
            reasons.append(f"{len(meaningful_common)} keywords match description")
        
        # Specific template logic
        if template.id == 'tpl-frontend-react-landing':
            if 'landing' in req_lower or 'page' in req_lower or 'hero' in req_lower:
                score += 20
                reasons.append("Landing page template for landing/page requirement")
        
        if template.id == 'tpl-backend-fastapi-crud':
            if any(word in req_lower for word in ['crud', 'api', 'store', 'save', 'manage']):
                score += 20
                reasons.append("CRUD template for data operations")
        
        if template.id == 'tpl-backend-fastapi-auth':
            if analysis.needs_auth:
                score += 25
                reasons.append("Auth template for authentication requirement")
        
        if template.id == 'tpl-infra-railway-service':
            if analysis.needs_deployment:
                score += 20
                reasons.append("Railway template for deployment")
        
        # Analytics templates - boost score significantly if analytics detected
        if template.id in ['tpl-analytics-ga4', 'tpl-analytics-mixpanel',
                          'tpl-analytics-amplitude']:
            if 'analytics' in analysis.infrastructure:
                score += 50  # Big boost for analytics match
                reasons.append("Analytics template for tracking requirement")
            
            # Specific platform matching
            if template.id == 'tpl-analytics-ga4':
                if any(word in req_lower for word in ['ga4', 'google']):
                    score += 30
                    reasons.append("GA4 template for Google Analytics")
            elif template.id == 'tpl-analytics-mixpanel':
                if 'mixpanel' in req_lower:
                    score += 30
                    reasons.append("Mixpanel template requested")
            elif template.id == 'tpl-analytics-amplitude':
                if 'amplitude' in req_lower:
                    score += 30
                    reasons.append("Amplitude template requested")
        
        # Normalize score to 0-100
        confidence = min(score, 100.0)
        
        return confidence, matched_keywords, reasons
    
    def find_matching_templates(
        self,
        requirement: str,
        min_confidence: float = 20.0,
        max_results: int = 10
    ) -> List[TemplateMatch]:
        """Find templates that match the requirement"""
        analysis = self.analyze_requirement(requirement)
        
        matches = []
        for template in self.templates:
            confidence, keywords, reasons = self.score_template_match(template, analysis)
            
            if confidence >= min_confidence:
                match = TemplateMatch(
                    template=template,
                    confidence=confidence,
                    matched_keywords=keywords,
                    reasons=reasons
                )
                matches.append(match)
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches[:max_results]
    
    def suggest_template_combination(self, requirement: str) -> Dict[str, Any]:
        """
        Suggest a combination of templates for the requirement.
        
        Returns structured recommendation with templates grouped by layer.
        """
        analysis = self.analyze_requirement(requirement)
        matches = self.find_matching_templates(requirement, min_confidence=15.0)
        
        # Group templates by layer type
        layers = defaultdict(list)
        for match in matches:
            layers[match.template.layer_type].append(match)
        
        # Build recommendation
        recommendation = {
            'requirement': requirement,
            'analysis': {
                'needs_frontend': analysis.needs_frontend,
                'needs_backend': analysis.needs_backend,
                'needs_database': analysis.needs_database,
                'needs_auth': analysis.needs_auth,
                'needs_deployment': analysis.needs_deployment,
                'needs_analytics': 'analytics' in analysis.infrastructure,
                'entities': analysis.entities,
                'actions': analysis.actions,
                'patterns': analysis.patterns,
            },
            'templates': {
                'ui': layers.get('ui', []),
                'api': layers.get('api', []),
                'infra': layers.get('infra', []),
                'analytics': layers.get('analytics', []),
                'composite': layers.get('composite', []),
            },
            'total_templates': len(matches),
            'total_cost_tokens': sum(
                m.template.cost_estimate_tokens for m in matches[:5]
            ),
            'estimated_time_minutes': sum(
                m.template.cost_estimate_tokens for m in matches[:5]
            ) // 200,
        }
        
        return recommendation
    
    def generate_parameter_suggestions(
        self,
        template: TemplateMetadata,
        requirement: str
    ) -> Dict[str, Any]:
        """Generate suggested parameters for a template based on requirement"""
        analysis = self.analyze_requirement(requirement)
        
        suggestions = {}
        
        # For CRUD template
        if template.id == 'tpl-backend-fastapi-crud':
            # Extract potential model name
            if 'user' in analysis.entities or 'user' in requirement.lower():
                suggestions['model_name'] = 'User'
                suggestions['table_name'] = 'users'
            elif 'email' in analysis.entities:
                suggestions['model_name'] = 'Email'
                suggestions['table_name'] = 'emails'
            else:
                suggestions['model_name'] = 'Item'
                suggestions['table_name'] = 'items'
            
            # Suggest fields based on requirement
            fields = []
            if 'email' in requirement.lower():
                fields.append({
                    'name': 'email',
                    'type': 'String',
                    'unique': True,
                    'indexed': True,
                })
            if 'name' in requirement.lower() or 'user' in requirement.lower():
                fields.append({
                    'name': 'full_name',
                    'type': 'String',
                    'nullable': True,
                })
            
            if fields:
                suggestions['fields'] = fields
        
        # For landing page template
        if template.id == 'tpl-frontend-react-landing':
            suggestions['app_name'] = 'My App'
            suggestions['tagline'] = 'Build something amazing'
            if 'email' in requirement.lower() or 'waitlist' in requirement.lower():
                suggestions['include_email_capture'] = True
        
        return suggestions


def main():
    """CLI interface for semantic template mapper"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mvp_semantic_mapper.py <requirement>")
        print("\nExamples:")
        print('  python mvp_semantic_mapper.py "SaaS landing page with email capture"')
        print('  python mvp_semantic_mapper.py "REST API for user management"')
        print('  python mvp_semantic_mapper.py "Deploy FastAPI app to Railway"')
        sys.exit(1)
    
    requirement = " ".join(sys.argv[1:])
    
    print("=" * 80)
    print("🔍 MVP SEMANTIC TEMPLATE MAPPER")
    print("=" * 80)
    print(f"\n📋 Requirement: {requirement}\n")
    
    mapper = SemanticTemplateMapper()
    
    # Analyze requirement
    analysis = mapper.analyze_requirement(requirement)
    print("📊 Analysis:")
    print(f"  • Entities: {', '.join(analysis.entities) or 'None'}")
    print(f"  • Actions: {', '.join(analysis.actions) or 'None'}")
    print(f"  • Patterns: {', '.join(analysis.patterns) or 'None'}")
    print(f"  • Infrastructure: {', '.join(analysis.infrastructure) or 'None'}")
    print(f"  • Needs Frontend: {'Yes' if analysis.needs_frontend else 'No'}")
    print(f"  • Needs Backend: {'Yes' if analysis.needs_backend else 'No'}")
    print(f"  • Needs Database: {'Yes' if analysis.needs_database else 'No'}")
    print(f"  • Needs Auth: {'Yes' if analysis.needs_auth else 'No'}")
    needs_analytics = 'analytics' in analysis.infrastructure
    print(f"  • Needs Analytics: {'Yes' if needs_analytics else 'No'}")
    print()
    
    # Find matching templates
    matches = mapper.find_matching_templates(requirement, min_confidence=15.0)
    
    if not matches:
        print("❌ No matching templates found. Try rephrasing your requirement.")
        sys.exit(1)
    
    print(f"✅ Found {len(matches)} matching templates:\n")
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.template.name} ({match.template.id})")
        print(f"   Confidence: {match.confidence:.1f}%")
        print(f"   Layer: {match.template.layer_type}")
        print(f"   Cost: {match.template.cost_estimate_tokens} tokens")
        if match.matched_keywords:
            print(f"   Keywords: {', '.join(match.matched_keywords[:5])}")
        if match.reasons:
            print(f"   Reasons:")
            for reason in match.reasons[:3]:
                print(f"     • {reason}")
        print()
    
    # Generate recommendation
    recommendation = mapper.suggest_template_combination(requirement)
    
    print("=" * 80)
    print("💡 RECOMMENDED TEMPLATE COMBINATION")
    print("=" * 80)
    print(f"\nTotal Templates: {recommendation['total_templates']}")
    print(f"Estimated Cost: {recommendation['total_cost_tokens']} tokens")
    print(f"Estimated Time: ~{recommendation['estimated_time_minutes']} minutes")
    print()
    
    for layer_type, layer_matches in recommendation['templates'].items():
        if layer_matches:
            print(f"📦 {layer_type.upper()} Layer:")
            for match in layer_matches:
                print(f"  • {match.template.name} ({match.confidence:.1f}% confidence)")
            print()
    
    print("=" * 80)
    print("🚀 Next Steps:")
    print("=" * 80)
    print("1. Review the recommended templates above")
    print("2. Use mvp_generator.py to generate the project:")
    print(f'   python mvp_generator.py "{requirement}"')
    print()


if __name__ == "__main__":
    main()
