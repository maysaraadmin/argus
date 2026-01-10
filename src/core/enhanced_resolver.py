"""
Enhanced entity resolution system for Argus MVP
Implements advanced matching algorithms and user interaction
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import re
import logging
from difflib import SequenceMatcher
import jellyfish
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import Levenshtein

logger = logging.getLogger(__name__)

@dataclass
class MatchCandidate:
    """Match candidate with confidence score"""
    entity1_id: str
    entity2_id: str
    entity1_data: Dict[str, Any]
    entity2_data: Dict[str, Any]
    confidence_score: float
    match_type: str
    match_details: Dict[str, Any] = field(default_factory=dict)
    user_decision: Optional[str] = None  # "confirm", "reject", "defer"
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

@dataclass
class MatchingRule:
    """Matching rule configuration"""
    field_name: str
    matching_type: str  # "exact", "fuzzy", "phonetic", "numeric"
    weight: float
    threshold: float
    enabled: bool = True
    preprocessing: List[str] = field(default_factory=list)  # "lowercase", "remove_spaces", etc.

class EnhancedEntityResolver:
    """Enhanced entity resolution with advanced algorithms"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.matching_rules = self._setup_default_rules()
        self.blocking_keys = set()
        self.match_candidates: List[MatchCandidate] = []
        self.processed_entities: Dict[str, Dict[str, Any]] = {}
        
    def _setup_default_rules(self) -> List[MatchingRule]:
        """Setup default matching rules"""
        return [
            MatchingRule("name", "fuzzy", 0.4, 0.8, True, ["lowercase", "remove_special_chars"]),
            MatchingRule("email", "exact", 0.3, 1.0, True, ["lowercase"]),
            MatchingRule("phone", "exact", 0.2, 0.9, True, ["normalize_phone"]),
            MatchingRule("address", "fuzzy", 0.2, 0.7, True, ["lowercase", "standardize_address"]),
            MatchingRule("dob", "exact", 0.1, 1.0, True, []),
            MatchingRule("ssn", "exact", 0.1, 1.0, True, []),
            MatchingRule("passport", "exact", 0.1, 1.0, True, []),
        ]
    
    def preprocess_field(self, value: str, preprocessing: List[str]) -> str:
        """Preprocess field value based on rules"""
        if not value or not isinstance(value, str):
            return str(value) if value else ""
        
        processed = value
        
        for step in preprocessing:
            if step == "lowercase":
                processed = processed.lower()
            elif step == "uppercase":
                processed = processed.upper()
            elif step == "remove_spaces":
                processed = processed.replace(" ", "")
            elif step == "remove_special_chars":
                processed = re.sub(r'[^\w\s]', '', processed)
            elif step == "standardize_address":
                processed = self._standardize_address(processed)
            elif step == "normalize_phone":
                processed = self._normalize_phone(processed)
            elif step == "remove_punctuation":
                processed = re.sub(r'[^\w\s]', '', processed)
        
        return processed.strip()
    
    def _standardize_address(self, address: str) -> str:
        """Standardize address format"""
        if not address:
            return ""
        
        # Common address abbreviations
        abbreviations = {
            'st': 'street',
            'rd': 'road',
            'ave': 'avenue',
            'blvd': 'boulevard',
            'apt': 'apartment',
            'suite': 'suite',
            'ste': 'suite'
        }
        
        # Replace abbreviations
        words = address.lower().split()
        standardized = []
        for word in words:
            if word in abbreviations:
                standardized.append(abbreviations[word])
            else:
                standardized.append(word)
        
        return ' '.join(standardized)
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Handle country codes and area codes
        if len(digits_only) == 10:
            # US format: (XXX) XXX-XXXX
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) > 10:
            # International format: +XX XXX XXX XXX
            if digits_only.startswith('1'):
                return f"+{digits_only[0]} ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
            else:
                return f"+{digits_only[:2]} {digits_only[2:5]} {digits_only[5:8]} {digits_only[8:]}"
        
        return digits_only
    
    def exact_match(self, value1: str, value2: str) -> float:
        """Exact string matching"""
        if not value1 or not value2:
            return 0.0
        
        return 1.0 if value1 == value2 else 0.0
    
    def fuzzy_match_jaro_winkler(self, value1: str, value2: str) -> float:
        """Jaro-Winkler fuzzy matching"""
        if not value1 or not value2:
            return 0.0
        
        return jellyfish.jaro_winkler_similarity(value1, value2)
    
    def fuzzy_match_levenshtein(self, value1: str, value2: str) -> float:
        """Levenshtein distance fuzzy matching"""
        if not value1 or not value2:
            return 0.0
        
        max_len = max(len(value1), len(value2))
        if max_len == 0:
            return 1.0
        
        distance = Levenshtein.distance(value1, value2)
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    def fuzzy_match_difflib(self, value1: str, value2: str) -> float:
        """Difflib sequence matching"""
        if not value1 or not value2:
            return 0.0
        
        return SequenceMatcher(None, value1, value2).ratio()
    
    def phonetic_match(self, value1: str, value2: str) -> float:
        """Phonetic matching using Soundex"""
        if not value1 or not value2:
            return 0.0
        
        soundex1 = jellyfish.soundex(value1)
        soundex2 = jellyfish.soundex(value2)
        
        return 1.0 if soundex1 == soundex2 else 0.0
    
    def numeric_match(self, value1: Any, value2: Any, tolerance: float = 0.1) -> float:
        """Numeric matching with tolerance"""
        try:
            num1 = float(str(value1).replace(',', '').replace('$', ''))
            num2 = float(str(value2).replace(',', '').replace('$', ''))
            
            if num1 == 0 and num2 == 0:
                return 1.0
            
            diff = abs(num1 - num2)
            max_val = max(abs(num1), abs(num2))
            
            if max_val == 0:
                return 1.0
            
            similarity = 1.0 - (diff / max_val)
            return max(0.0, similarity)
            
        except (ValueError, TypeError):
            return 0.0
    
    def calculate_field_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any], 
                              rule: MatchingRule) -> float:
        """Calculate similarity for a specific field"""
        value1 = entity1.get(rule.field_name, "")
        value2 = entity2.get(rule.field_name, "")
        
        # Preprocess values
        proc_value1 = self.preprocess_field(str(value1), rule.preprocessing)
        proc_value2 = self.preprocess_field(str(value2), rule.preprocessing)
        
        # Apply matching algorithm
        if rule.matching_type == "exact":
            similarity = self.exact_match(proc_value1, proc_value2)
        elif rule.matching_type == "fuzzy":
            # Use Jaro-Winkler for names, Levenshtein for others
            if rule.field_name == "name":
                similarity = self.fuzzy_match_jaro_winkler(proc_value1, proc_value2)
            else:
                similarity = self.fuzzy_match_levenshtein(proc_value1, proc_value2)
        elif rule.matching_type == "phonetic":
            similarity = self.phonetic_match(proc_value1, proc_value2)
        elif rule.matching_type == "numeric":
            similarity = self.numeric_match(value1, value2)
        else:
            similarity = 0.0
        
        # Apply threshold
        return similarity if similarity >= rule.threshold else 0.0
    
    def calculate_entity_similarity(self, entity1: Dict[str, Any], 
                              entity2: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Calculate overall similarity between two entities"""
        total_score = 0.0
        total_weight = 0.0
        field_scores = {}
        
        for rule in self.matching_rules:
            if not rule.enabled:
                continue
            
            # Calculate field similarity
            field_sim = self.calculate_field_similarity(entity1, entity2, rule)
            field_weighted_score = field_sim * rule.weight
            
            total_score += field_weighted_score
            total_weight += rule.weight
            
            field_scores[rule.field_name] = {
                'similarity': field_sim,
                'weight': rule.weight,
                'weighted_score': field_weighted_score,
                'threshold': rule.threshold,
                'matched': field_sim >= rule.threshold
            }
        
        # Normalize total score
        overall_similarity = total_score / total_weight if total_weight > 0 else 0.0
        
        # Determine match type
        if overall_similarity >= 0.9:
            match_type = "high_confidence"
        elif overall_similarity >= 0.7:
            match_type = "medium_confidence"
        elif overall_similarity >= 0.5:
            match_type = "low_confidence"
        else:
            match_type = "no_match"
        
        match_details = {
            'field_scores': field_scores,
            'total_score': total_score,
            'total_weight': total_weight,
            'overall_similarity': overall_similarity,
            'match_type': match_type
        }
        
        return overall_similarity, match_details
    
    def blocking(self, entities: List[Dict[str, Any]]) -> List[List[str]]:
        """Apply blocking to reduce comparison pairs"""
        blocks = {}
        
        for entity in entities:
            # Create blocking keys
            blocking_keys = []
            
            # Name-based blocking
            name = entity.get('name', '').lower()
            if name:
                # First letter blocking
                blocking_keys.append(name[0] if name else '')
                # First two letters blocking
                blocking_keys.append(name[:2] if len(name) >= 2 else name)
                # Soundex blocking
                blocking_keys.append(jellyfish.soundex(name))
            
            # Email domain blocking
            email = entity.get('email', '').lower()
            if email and '@' in email:
                domain = email.split('@')[1]
                blocking_keys.append(domain)
            
            # Phone area code blocking
            phone = entity.get('phone', '')
            if phone and len(phone) >= 3:
                area_code = re.sub(r'\D', '', phone)[:3]
                blocking_keys.append(area_code)
            
            # Add entity to blocks
            for key in blocking_keys:
                if key not in blocks:
                    blocks[key] = []
                blocks[key].append(entity.get('id'))
        
        return list(blocks.values())
    
    def find_potential_matches(self, entities: List[Dict[str, Any]], 
                           target_entity: Dict[str, Any]) -> List[MatchCandidate]:
        """Find potential matches for a target entity"""
        candidates = []
        
        for entity in entities:
            if entity.get('id') == target_entity.get('id'):
                continue
            
            similarity, match_details = self.calculate_entity_similarity(target_entity, entity)
            
            if similarity > 0.5:  # Minimum threshold for consideration
                candidate = MatchCandidate(
                    entity1_id=target_entity.get('id'),
                    entity2_id=entity.get('id'),
                    entity1_data=target_entity,
                    entity2_data=entity,
                    confidence_score=similarity,
                    match_type=match_details['match_type'],
                    match_details=match_details
                )
                candidates.append(candidate)
        
        # Sort by confidence score
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        return candidates
    
    def resolve_batch(self, entities: List[Dict[str, Any]]) -> List[MatchCandidate]:
        """Resolve entities in batch with blocking and matching"""
        logger.info(f"Starting batch resolution for {len(entities)} entities")
        
        # Apply blocking
        blocks = self.blocking(entities)
        
        all_candidates = []
        total_comparisons = 0
        
        # Compare within blocks
        for block in blocks:
            if len(block) < 2:
                continue
            
            # Get entities in this block
            block_entities = [e for e in entities if e.get('id') in block]
            
            # Compare all pairs in block
            for i, entity1 in enumerate(block_entities):
                for entity2 in block_entities[i+1:]:
                    similarity, match_details = self.calculate_entity_similarity(entity1, entity2)
                    
                    if similarity > 0.5:  # Minimum threshold
                        candidate = MatchCandidate(
                            entity1_id=entity1.get('id'),
                            entity2_id=entity2.get('id'),
                            entity1_data=entity1,
                            entity2_data=entity2,
                            confidence_score=similarity,
                            match_type=match_details['match_type'],
                            match_details=match_details
                        )
                        all_candidates.append(candidate)
                    
                    total_comparisons += 1
        
        logger.info(f"Completed {total_comparisons} comparisons, found {len(all_candidates)} candidates")
        
        # Sort by confidence score
        all_candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        self.match_candidates = all_candidates
        
        return all_candidates
    
    def confirm_match(self, candidate_id: str, user_id: str, action: str) -> bool:
        """Confirm or reject a match candidate"""
        for candidate in self.match_candidates:
            # Create unique identifier for candidate
            candidate_identifier = f"{candidate.entity1_id}_{candidate.entity2_id}"
            if candidate_identifier == candidate_id:
                candidate.user_decision = action
                candidate.reviewed_at = datetime.now()
                candidate.reviewed_by = user_id
                logger.info(f"Match {candidate_identifier} {action} by user {user_id}")
                return True
        
        return False
    
    def merge_entities(self, entity1_id: str, entity2_id: str, 
                     merge_strategy: str = "prefer_entity1") -> Dict[str, Any]:
        """Merge two entities"""
        # Find entities in processed data
        entity1 = self.processed_entities.get(entity1_id)
        entity2 = self.processed_entities.get(entity2_id)
        
        if not entity1 or not entity2:
            raise ValueError("One or both entities not found")
        
        # Create merged entity
        merged_entity = {
            'id': f"merged_{entity1_id}_{entity2_id}",
            'original_ids': [entity1_id, entity2_id],
            'merge_strategy': merge_strategy,
            'merged_at': datetime.now().isoformat(),
            'type': entity1.get('type', entity2.get('type')),
            'attributes': {}
        }
        
        # Merge attributes based on strategy
        all_attributes = set()
        all_attributes.update(entity1.get('attributes', {}).keys())
        all_attributes.update(entity2.get('attributes', {}).keys())
        
        for attr in all_attributes:
            val1 = entity1.get('attributes', {}).get(attr)
            val2 = entity2.get('attributes', {}).get(attr)
            
            if merge_strategy == "prefer_entity1":
                merged_entity['attributes'][attr] = val1 if val1 is not None else val2
            elif merge_strategy == "prefer_entity2":
                merged_entity['attributes'][attr] = val2 if val2 is not None else val1
            elif merge_strategy == "combine":
                if val1 is not None and val2 is not None:
                    if val1 == val2:
                        merged_entity['attributes'][attr] = val1
                    else:
                        # Store both values
                        merged_entity['attributes'][attr] = {
                            'entity1_value': val1,
                            'entity2_value': val2,
                            'conflict': True
                        }
                elif val1 is not None:
                    merged_entity['attributes'][attr] = val1
                elif val2 is not None:
                    merged_entity['attributes'][attr] = val2
            elif merge_strategy == "most_recent":
                # Use most recent (simplified - would need timestamps)
                merged_entity['attributes'][attr] = val1 if val1 is not None else val2
        
        # Preserve relationships (would need to be updated in graph)
        merged_entity['relationships'] = {
            'entity1_relationships': entity1.get('relationships', []),
            'entity2_relationships': entity2.get('relationships', [])
        }
        
        logger.info(f"Merged entities {entity1_id} and {entity2_id} using strategy {merge_strategy}")
        return merged_entity
    
    def get_match_statistics(self) -> Dict[str, Any]:
        """Get statistics about match candidates"""
        if not self.match_candidates:
            return {}
        
        total_candidates = len(self.match_candidates)
        confirmed = len([c for c in self.match_candidates if c.user_decision == "confirm"])
        rejected = len([c for c in self.match_candidates if c.user_decision == "reject"])
        pending = len([c for c in self.match_candidates if c.user_decision is None])
        
        # Confidence distribution
        high_conf = len([c for c in self.match_candidates if c.match_type == "high_confidence"])
        med_conf = len([c for c in self.match_candidates if c.match_type == "medium_confidence"])
        low_conf = len([c for c in self.match_candidates if c.match_type == "low_confidence"])
        
        return {
            'total_candidates': total_candidates,
            'confirmed': confirmed,
            'rejected': rejected,
            'pending': pending,
            'confirmation_rate': confirmed / total_candidates if total_candidates > 0 else 0,
            'confidence_distribution': {
                'high': high_conf,
                'medium': med_conf,
                'low': low_conf
            },
            'average_confidence': np.mean([c.confidence_score for c in self.match_candidates]),
            'median_confidence': np.median([c.confidence_score for c in self.match_candidates])
        }
    
    def export_matches(self, format: str = "csv") -> str:
        """Export match candidates for review"""
        if not self.match_candidates:
            return ""
        
        # Convert to DataFrame
        data = []
        for candidate in self.match_candidates:
            data.append({
                'Entity1_ID': candidate.entity1_id,
                'Entity2_ID': candidate.entity2_id,
                'Confidence_Score': candidate.confidence_score,
                'Match_Type': candidate.match_type,
                'User_Decision': candidate.user_decision or 'Pending',
                'Reviewed_At': candidate.reviewed_at.isoformat() if candidate.reviewed_at else '',
                'Reviewed_By': candidate.reviewed_by or '',
                'Entity1_Name': candidate.entity1_data.get('name', ''),
                'Entity2_Name': candidate.entity2_data.get('name', ''),
                'Entity1_Type': candidate.entity1_data.get('type', ''),
                'Entity2_Type': candidate.entity2_data.get('type', '')
            })
        
        df = pd.DataFrame(data)
        
        if format == "csv":
            return df.to_csv(index=False)
        elif format == "json":
            return df.to_json(orient='records', indent=2)
        elif format == "excel":
            return df.to_excel(index=False)
        
        return ""

# Global enhanced resolver instance
enhanced_resolver = EnhancedEntityResolver()
