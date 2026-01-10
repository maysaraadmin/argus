import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import re
from datetime import datetime
from collections import defaultdict

from argus.config import config
from argus.logging import get_logger
from argus.exceptions import EntityResolutionError

try:
    from fuzzywuzzy import fuzz
    import recordlinkage
    from recordlinkage.preprocessing import clean
    from sklearn.cluster import DBSCAN
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    MISSING_DEPS = str(e)

@dataclass
class MatchResult:
    entity1_id: str
    entity2_id: str
    similarity_score: float
    match_type: str
    confidence: float
    match_details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.match_details is None:
            self.match_details = {}

@dataclass
class ResolutionConfig:
    similarity_threshold: float = 0.85
    possible_match_threshold: float = 0.65
    non_match_threshold: float = 0.3
    weights: Dict[str, float] = None
    blocking_methods: List[str] = None
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "name": 0.4,
                "dob": 0.3,
                "address": 0.2,
                "phone": 0.1
            }
        if self.blocking_methods is None:
            self.blocking_methods = ["phonetic", "exact", "range"]

class SimilarityCalculator(ABC):
    """Abstract base class for similarity calculation algorithms"""
    
    @abstractmethod
    def calculate(self, value1: Any, value2: Any) -> float:
        """Calculate similarity between two values"""
        pass

class StringSimilarityCalculator(SimilarityCalculator):
    """String similarity using various algorithms"""
    
    def __init__(self, method: str = "jarowinkler"):
        self.method = method
        if not DEPENDENCIES_AVAILABLE:
            raise EntityResolutionError(f"Missing dependencies: {MISSING_DEPS}")
    
    def calculate(self, value1: str, value2: str) -> float:
        """Calculate string similarity"""
        if not value1 or not value2:
            return 0.0
        
        v1, v2 = str(value1).lower().strip(), str(value2).lower().strip()
        
        if self.method == "jarowinkler":
            return fuzz.ratio(v1, v2) / 100.0
        elif self.method == "token_sort":
            return fuzz.token_sort_ratio(v1, v2) / 100.0
        elif self.method == "partial":
            return fuzz.partial_ratio(v1, v2) / 100.0
        else:
            return fuzz.ratio(v1, v2) / 100.0

class NumericSimilarityCalculator(SimilarityCalculator):
    """Numeric similarity using Gaussian distribution"""
    
    def __init__(self, scale: float = 10.0):
        self.scale = scale
    
    def calculate(self, value1: float, value2: float) -> float:
        """Calculate numeric similarity"""
        if value1 is None or value2 is None:
            return 0.0
        
        diff = abs(float(value1) - float(value2))
        return np.exp(-(diff ** 2) / (2 * self.scale ** 2))

class EntityResolver:
    """Main entity resolution class implementing the resolution pipeline"""
    
    def __init__(self, config: Optional[ResolutionConfig] = None):
        if not DEPENDENCIES_AVAILABLE:
            raise EntityResolutionError(f"Missing dependencies: {MISSING_DEPS}")
        
        self.logger = get_logger(__name__)
        self.config = config or ResolutionConfig()
        
        # Load configuration from system config
        if config is not None and hasattr(config, 'entity_resolution'):
            system_config = config.entity_resolution
            if system_config:
                self.config.similarity_threshold = system_config.similarity_threshold
                self.config.weights = system_config.weights
        
        # Initialize similarity calculators
        self.string_calculator = StringSimilarityCalculator()
        self.numeric_calculator = NumericSimilarityCalculator()
        
        # Blocking rules by entity type
        self.blocking_rules = {
            'person': ['first_letter_of_name', 'dob_year', 'country'],
            'organization': ['country', 'industry', 'type'],
            'location': ['country', 'type'],
            'event': ['date_year', 'country', 'type']
        }
        
        self.logger.info("EntityResolver initialized")
    
    def resolve_batch(self, entities: List[Dict]) -> List[MatchResult]:
        """Resolve entities in a batch"""
        df = pd.DataFrame(entities)
        
        # Clean data
        df_clean = self._clean_dataframe(df)
        
        # Apply blocking to reduce comparisons
        candidate_pairs = self._blocking(df_clean)
        
        # Calculate similarities
        similarity_matrix = self._calculate_similarities(df_clean, candidate_pairs)
        
        # Apply threshold
        matches = similarity_matrix[similarity_matrix['overall_similarity'] > self.similarity_threshold]
        
        # Cluster matches
        clusters = self._cluster_matches(matches, df_clean)
        
        # Convert to MatchResult objects
        results = []
        for cluster_id, entity_ids in clusters.items():
            if len(entity_ids) > 1:
                # Create matches within cluster
                for i in range(len(entity_ids)):
                    for j in range(i + 1, len(entity_ids)):
                        results.append(MatchResult(
                            entity1_id=entity_ids[i],
                            entity2_id=entity_ids[j],
                            similarity_score=0.95,  # Approximate
                            match_type="same_entity",
                            confidence=0.9
                        ))
        
        return results
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize dataframe"""
        df_clean = df.copy()
        
        # Clean string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].apply(
                lambda x: clean(str(x)) if pd.notnull(x) else x
            )
        
        return df_clean
    
    def _blocking(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply blocking to reduce comparison pairs"""
        indexer = recordlinkage.Index()
        
        # Simple blocking on first letter of name
        if 'name' in df.columns:
            df['name_first_letter'] = df['name'].str[0].str.lower()
            indexer.block('name_first_letter')
        
        # Block on country if available
        if 'country' in df.columns:
            indexer.block('country')
        
        return indexer.index(df)
    
    def _calculate_similarities(self, df: pd.DataFrame, candidate_pairs) -> pd.DataFrame:
        """Calculate similarity scores for candidate pairs"""
        compare = recordlinkage.Compare()
        
        # String comparisons
        if 'name' in df.columns:
            compare.string('name', 'name', 
                          method='jarowinkler', 
                          label='name_similarity')
        
        if 'address' in df.columns:
            compare.string('address', 'address',
                          method='levenshtein',
                          label='address_similarity',
                          threshold=0.8)
        
        # Numeric comparisons
        if 'age' in df.columns:
            compare.numeric('age', 'age',
                           method='gauss',
                           label='age_similarity',
                           offset=5, scale=10)
        
        # Compute similarities
        features = compare.compute(candidate_pairs, df)
        
        # Calculate overall similarity
        if len(features.columns) > 0:
            features['overall_similarity'] = features.mean(axis=1)
        else:
            features['overall_similarity'] = 0.0
        
        return features
    
    def _cluster_matches(self, matches: pd.DataFrame, df: pd.DataFrame) -> Dict[int, List[str]]:
        """Cluster matched entities"""
        if len(matches) == 0:
            return {}
        
        # Create similarity matrix for clustering
        entity_ids = list(set(matches.index.get_level_values(0).tolist() + 
                            matches.index.get_level_values(1).tolist()))
        
        # Create mapping
        id_to_idx = {eid: idx for idx, eid in enumerate(entity_ids)}
        
        # Initialize similarity matrix
        n = len(entity_ids)
        sim_matrix = np.eye(n)  # Self-similarity = 1
        
        # Fill matrix with similarity scores
        for (id1, id2), row in matches.iterrows():
            idx1 = id_to_idx[id1]
            idx2 = id_to_idx[id2]
            sim_matrix[idx1, idx2] = row['overall_similarity']
            sim_matrix[idx2, idx1] = row['overall_similarity']
        
        # Apply DBSCAN clustering
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='precomputed')
        # Convert similarity to distance
        distance_matrix = 1 - sim_matrix
        labels = clustering.fit_predict(distance_matrix)
        
        # Group entities by cluster
        clusters = {}
        for entity_id, idx in id_to_idx.items():
            cluster_id = labels[idx]
            if cluster_id != -1:  # -1 means noise in DBSCAN
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(entity_id)
        
        return clusters
    
    def resolve_single_pair(self, entity1: Dict, entity2: Dict) -> Tuple[float, bool]:
        """Check if two entities are the same"""
        score = 0.0
        weights = {'name': 0.4, 'dob': 0.3, 'address': 0.3}
        
        # Name matching
        if 'name' in entity1 and 'name' in entity2:
            name_score = fuzz.token_sort_ratio(
                str(entity1['name']),
                str(entity2['name'])
            ) / 100.0
            score += name_score * weights.get('name', 0.4)
        
        # Date of birth matching
        if 'dob' in entity1 and 'dob' in entity2:
            if entity1['dob'] == entity2['dob']:
                score += weights.get('dob', 0.3)
        
        # Address matching
        if 'address' in entity1 and 'address' in entity2:
            addr_score = fuzz.partial_ratio(
                str(entity1['address']),
                str(entity2['address'])
            ) / 100.0
            score += addr_score * weights.get('address', 0.3)
        
        return score, score > self.similarity_threshold
    
    def resolve_single_pair(self, entity1: Dict, entity2: Dict) -> MatchResult:
        """Enhanced single pair resolution with detailed results"""
        try:
            similarity_scores = {}
            total_score = 0.0
            total_weight = 0.0
            
            # Calculate similarity for each field
            for field, weight in self.config.weights.items():
                if field in entity1 and field in entity2:
                    value1, value2 = entity1[field], entity2[field]
                    
                    if isinstance(value1, str) and isinstance(value2, str):
                        similarity = self.string_calculator.calculate(value1, value2)
                    elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                        similarity = self.numeric_calculator.calculate(value1, value2)
                    elif value1 == value2:
                        similarity = 1.0
                    else:
                        similarity = 0.0
                    
                    similarity_scores[field] = similarity
                    total_score += similarity * weight
                    total_weight += weight
            
            # Normalize score
            overall_similarity = total_score / total_weight if total_weight > 0 else 0.0
            
            # Determine match type and confidence
            if overall_similarity >= self.config.similarity_threshold:
                match_type = "match"
                confidence = min(0.9, overall_similarity)
            elif overall_similarity >= self.config.possible_match_threshold:
                match_type = "possible_match"
                confidence = overall_similarity
            else:
                match_type = "non_match"
                confidence = 1.0 - overall_similarity
            
            return MatchResult(
                entity1_id=entity1.get('id', 'unknown'),
                entity2_id=entity2.get('id', 'unknown'),
                similarity_score=overall_similarity,
                match_type=match_type,
                confidence=confidence,
                match_details={
                    "field_similarities": similarity_scores,
                    "weights_used": self.config.weights,
                    "threshold": self.config.similarity_threshold
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in single pair resolution: {e}")
            raise EntityResolutionError(f"Single pair resolution failed: {e}", "resolve_single_pair")
    
    def find_duplicate_entities(self, entities: List[Dict], entity_type: Optional[str] = None) -> List[MatchResult]:
        """Find potential duplicate entities in a dataset"""
        try:
            # Filter by entity type if specified
            if entity_type:
                entities = [e for e in entities if e.get('type') == entity_type]
            
            # Resolve in batch
            matches = self.resolve_batch(entities)
            
            # Filter for high-confidence matches
            duplicates = [
                match for match in matches 
                if match.match_type == "match" and match.confidence >= 0.8
            ]
            
            self.logger.info(f"Found {len(duplicates)} duplicate pairs from {len(entities)} entities")
            return duplicates
            
        except Exception as e:
            self.logger.error(f"Error finding duplicates: {e}")
            raise EntityResolutionError(f"Duplicate detection failed: {e}", "find_duplicates")
    
    def canonicalize_entity(self, entities: List[Dict]) -> Dict:
        """Create a canonical entity from a cluster of duplicates"""
        if not entities:
            return {}
        
        try:
            # Start with the highest confidence entity as base
            base_entity = max(entities, key=lambda e: e.get('confidence', 0.0))
            canonical = base_entity.copy()
            
            # Merge attributes from all entities
            merged_attributes = defaultdict(list)
            for entity in entities:
                for key, value in entity.items():
                    if key not in ['id', 'confidence', 'source']:
                        merged_attributes[key].append(value)
            
            # Resolve conflicts for each attribute
            for attr, values in merged_attributes.items():
                if len(set(str(v) for v in values)) == 1:
                    # All values are the same
                    canonical[attr] = values[0]
                else:
                    # Choose the most frequent or highest confidence value
                    value_counts = defaultdict(int)
                    for i, value in enumerate(values):
                        weight = entities[i].get('confidence', 1.0)
                        value_counts[value] += weight
                    
                    canonical[attr] = max(value_counts, key=value_counts.get)
            
            # Add metadata
            canonical['sources'] = [e.get('source', 'unknown') for e in entities]
            canonical['duplicate_count'] = len(entities)
            canonical['canonicalized_at'] = datetime.utcnow().isoformat()
            
            return canonical
            
        except Exception as e:
            self.logger.error(f"Error canonicalizing entity: {e}")
            raise EntityResolutionError(f"Entity canonicalization failed: {e}", "canonicalize_entity")
    
    def get_resolution_statistics(self, matches: List[MatchResult]) -> Dict[str, Any]:
        """Get statistics about resolution results"""
        if not matches:
            return {"total_matches": 0}
        
        match_types = defaultdict(int)
        confidence_scores = []
        similarity_scores = []
        
        for match in matches:
            match_types[match.match_type] += 1
            confidence_scores.append(match.confidence)
            similarity_scores.append(match.similarity_score)
        
        return {
            "total_matches": len(matches),
            "match_types": dict(match_types),
            "avg_confidence": np.mean(confidence_scores) if confidence_scores else 0.0,
            "avg_similarity": np.mean(similarity_scores) if similarity_scores else 0.0,
            "high_confidence_matches": len([m for m in matches if m.confidence >= 0.8]),
            "possible_matches": match_types.get("possible_match", 0),
            "definite_matches": match_types.get("match", 0)
        }
