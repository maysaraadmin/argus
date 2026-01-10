"""
Backward traceability system for Argus MVP
Implements full document linking and source tracking
"""
import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os

logger = logging.getLogger(__name__)

class SourceType(Enum):
    """Types of data sources"""
    FILE = "file"
    DATABASE = "database"
    API = "api"
    MANUAL = "manual"
    EMAIL = "email"
    WEB = "web"
    DOCUMENT = "document"

class DocumentType(Enum):
    """Types of documents"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    IMAGE = "image"
    TEXT = "text"
    EMAIL = "email"

class ConfidenceLevel(Enum):
    """Confidence levels for source verification"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4

@dataclass
class SourceDocument:
    """Source document reference"""
    id: str
    name: str
    source_type: SourceType
    document_type: DocumentType
    file_path: Optional[str]
    url: Optional[str]
    database_connection: Optional[str]
    api_endpoint: Optional[str]
    checksum: Optional[str]
    size_bytes: Optional[int]
    created_at: datetime
    modified_at: datetime
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DataExtraction:
    """Record of data extraction from source"""
    id: str
    source_document_id: str
    extraction_method: str  # "manual", "automated", "ocr", "api"
    extracted_at: datetime
    extractor_user_id: Optional[str]
    confidence_level: ConfidenceLevel
    raw_data: str  # Original extracted text/data
    processed_data: Dict[str, Any]  # Structured data
    page_number: Optional[int]
    line_number: Optional[int]
    coordinates: Optional[Dict[str, float]]  # For documents with layout
    extraction_notes: Optional[str]
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.extracted_at is None:
            self.extracted_at = datetime.now()

@dataclass
class EntityTrace:
    """Trace record linking entity to its sources"""
    id: str
    entity_id: str
    entity_type: str
    field_name: str
    field_value: str
    extraction_id: str
    confidence_level: ConfidenceLevel
    verification_status: str  # "unverified", "verified", "disputed"
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class RelationshipTrace:
    """Trace record linking relationship to its sources"""
    id: str
    relationship_id: str
    relationship_type: str
    source_entity_id: str
    target_entity_id: str
    extraction_id: str
    confidence_level: ConfidenceLevel
    verification_status: str
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

class TraceabilityManager:
    """Manages traceability and source tracking"""
    
    def __init__(self, storage_path: str = "data/traceability"):
        self.storage_path = storage_path
        self.source_documents: Dict[str, SourceDocument] = {}
        self.extractions: Dict[str, DataExtraction] = {}
        self.entity_traces: Dict[str, List[EntityTrace]] = {}  # entity_id -> traces
        self.relationship_traces: Dict[str, List[RelationshipTrace]] = {}  # relationship_id -> traces
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def add_source_document(self, name: str, source_type: SourceType, 
                         document_type: DocumentType, file_path: Optional[str] = None,
                         url: Optional[str] = None, database_connection: Optional[str] = None,
                         api_endpoint: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new source document"""
        document_id = str(uuid.uuid4())
        
        # Calculate checksum if file exists
        checksum = None
        size_bytes = None
        if file_path and os.path.exists(file_path):
            checksum = self._calculate_file_checksum(file_path)
            size_bytes = os.path.getsize(file_path)
        
        document = SourceDocument(
            id=document_id,
            name=name,
            source_type=source_type,
            document_type=document_type,
            file_path=file_path,
            url=url,
            database_connection=database_connection,
            api_endpoint=api_endpoint,
            checksum=checksum,
            size_bytes=size_bytes,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.source_documents[document_id] = document
        self._save_data()
        
        logger.info(f"Added source document {document_id}: {name}")
        return document_id
    
    def extract_data(self, source_document_id: str, extraction_method: str,
                    raw_data: str, processed_data: Dict[str, Any],
                    extractor_user_id: Optional[str] = None,
                    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM,
                    page_number: Optional[int] = None,
                    line_number: Optional[int] = None,
                    coordinates: Optional[Dict[str, float]] = None,
                    extraction_notes: Optional[str] = None) -> str:
        """Extract data from source document"""
        if source_document_id not in self.source_documents:
            raise ValueError(f"Source document {source_document_id} not found")
        
        extraction_id = str(uuid.uuid4())
        
        extraction = DataExtraction(
            id=extraction_id,
            source_document_id=source_document_id,
            extraction_method=extraction_method,
            extracted_at=datetime.now(),
            extractor_user_id=extractor_user_id,
            confidence_level=confidence_level,
            raw_data=raw_data,
            processed_data=processed_data,
            page_number=page_number,
            line_number=line_number,
            coordinates=coordinates,
            extraction_notes=extraction_notes
        )
        
        self.extractions[extraction_id] = extraction
        self._save_data()
        
        logger.info(f"Extracted data {extraction_id} from document {source_document_id}")
        return extraction_id
    
    def trace_entity_field(self, entity_id: str, entity_type: str, field_name: str,
                         field_value: str, extraction_id: str,
                         confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM) -> str:
        """Create trace record for entity field"""
        trace_id = str(uuid.uuid4())
        
        trace = EntityTrace(
            id=trace_id,
            entity_id=entity_id,
            entity_type=entity_type,
            field_name=field_name,
            field_value=field_value,
            extraction_id=extraction_id,
            confidence_level=confidence_level,
            verification_status="unverified",
            notes=None,
            created_at=datetime.now()
        )
        
        if entity_id not in self.entity_traces:
            self.entity_traces[entity_id] = []
        
        self.entity_traces[entity_id].append(trace)
        self._save_data()
        
        logger.info(f"Created entity trace {trace_id} for {entity_id}.{field_name}")
        return trace_id
    
    def trace_relationship(self, relationship_id: str, relationship_type: str,
                        source_entity_id: str, target_entity_id: str,
                        extraction_id: str,
                        confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM) -> str:
        """Create trace record for relationship"""
        trace_id = str(uuid.uuid4())
        
        trace = RelationshipTrace(
            id=trace_id,
            relationship_id=relationship_id,
            relationship_type=relationship_type,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            extraction_id=extraction_id,
            confidence_level=confidence_level,
            verification_status="unverified",
            notes=None,
            created_at=datetime.now()
        )
        
        if relationship_id not in self.relationship_traces:
            self.relationship_traces[relationship_id] = []
        
        self.relationship_traces[relationship_id].append(trace)
        self._save_data()
        
        logger.info(f"Created relationship trace {trace_id} for {relationship_id}")
        return trace_id
    
    def get_entity_sources(self, entity_id: str, field_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get source documents for entity (optionally filtered by field)"""
        if entity_id not in self.entity_traces:
            return []
        
        sources = []
        for trace in self.entity_traces[entity_id]:
            if field_name and trace.field_name != field_name:
                continue
            
            extraction = self.extractions.get(trace.extraction_id)
            if not extraction:
                continue
            
            document = self.source_documents.get(extraction.source_document_id)
            if not document:
                continue
            
            source_info = {
                'trace_id': trace.id,
                'field_name': trace.field_name,
                'field_value': trace.field_value,
                'confidence_level': trace.confidence_level.value,
                'verification_status': trace.verification_status,
                'verified_by': trace.verified_by,
                'verified_at': trace.verified_at.isoformat() if trace.verified_at else None,
                'extraction': {
                    'id': extraction.id,
                    'method': extraction.extraction_method,
                    'extracted_at': extraction.extracted_at.isoformat(),
                    'extractor_user_id': extraction.extractor_user_id,
                    'page_number': extraction.page_number,
                    'line_number': extraction.line_number,
                    'coordinates': extraction.coordinates,
                    'notes': extraction.extraction_notes
                },
                'document': {
                    'id': document.id,
                    'name': document.name,
                    'source_type': document.source_type.value,
                    'document_type': document.document_type.value,
                    'file_path': document.file_path,
                    'url': document.url,
                    'checksum': document.checksum,
                    'size_bytes': document.size_bytes,
                    'created_at': document.created_at.isoformat(),
                    'metadata': document.metadata
                }
            }
            sources.append(source_info)
        
        return sources
    
    def get_relationship_sources(self, relationship_id: str) -> List[Dict[str, Any]]:
        """Get source documents for relationship"""
        if relationship_id not in self.relationship_traces:
            return []
        
        sources = []
        for trace in self.relationship_traces[relationship_id]:
            extraction = self.extractions.get(trace.extraction_id)
            if not extraction:
                continue
            
            document = self.source_documents.get(extraction.source_document_id)
            if not document:
                continue
            
            source_info = {
                'trace_id': trace.id,
                'relationship_type': trace.relationship_type,
                'confidence_level': trace.confidence_level.value,
                'verification_status': trace.verification_status,
                'verified_by': trace.verified_by,
                'verified_at': trace.verified_at.isoformat() if trace.verified_at else None,
                'extraction': {
                    'id': extraction.id,
                    'method': extraction.extraction_method,
                    'extracted_at': extraction.extracted_at.isoformat(),
                    'extractor_user_id': extraction.extractor_user_id,
                    'notes': extraction.extraction_notes
                },
                'document': {
                    'id': document.id,
                    'name': document.name,
                    'source_type': document.source_type.value,
                    'document_type': document.document_type.value,
                    'file_path': document.file_path,
                    'url': document.url,
                    'checksum': document.checksum,
                    'created_at': document.created_at.isoformat(),
                    'metadata': document.metadata
                }
            }
            sources.append(source_info)
        
        return sources
    
    def verify_trace(self, trace_id: str, user_id: str, verified: bool = True,
                   notes: Optional[str] = None) -> bool:
        """Verify or dispute a trace record"""
        # Search in entity traces
        for entity_traces in self.entity_traces.values():
            for trace in entity_traces:
                if trace.id == trace_id:
                    trace.verification_status = "verified" if verified else "disputed"
                    trace.verified_by = user_id
                    trace.verified_at = datetime.now()
                    if notes:
                        trace.notes = notes
                    self._save_data()
                    return True
        
        # Search in relationship traces
        for relationship_traces in self.relationship_traces.values():
            for trace in relationship_traces:
                if trace.id == trace_id:
                    trace.verification_status = "verified" if verified else "disputed"
                    trace.verified_by = user_id
                    trace.verified_at = datetime.now()
                    if notes:
                        trace.notes = notes
                    self._save_data()
                    return True
        
        return False
    
    def get_document_content(self, document_id: str) -> Optional[str]:
        """Get content of source document"""
        document = self.source_documents.get(document_id)
        if not document:
            return None
        
        if document.file_path and os.path.exists(document.file_path):
            try:
                with open(document.file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read document {document_id}: {e}")
        
        return None
    
    def search_sources(self, query: str, source_type: Optional[SourceType] = None) -> List[SourceDocument]:
        """Search source documents"""
        results = []
        query_lower = query.lower()
        
        for document in self.source_documents.values():
            if source_type and document.source_type != source_type:
                continue
            
            if (query_lower in document.name.lower() or 
                query_lower in str(document.metadata).lower()):
                results.append(document)
        
        return results
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return None
    
    def _save_data(self):
        """Save traceability data to files"""
        try:
            # Save source documents
            with open(f"{self.storage_path}/source_documents.json", 'w') as f:
                data = {k: asdict(v) for k, v in self.source_documents.items()}
                json.dump(data, f, indent=2, default=str)
            
            # Save extractions
            with open(f"{self.storage_path}/extractions.json", 'w') as f:
                data = {k: asdict(v) for k, v in self.extractions.items()}
                json.dump(data, f, indent=2, default=str)
            
            # Save entity traces
            with open(f"{self.storage_path}/entity_traces.json", 'w') as f:
                data = {k: [asdict(t) for t in v] for k, v in self.entity_traces.items()}
                json.dump(data, f, indent=2, default=str)
            
            # Save relationship traces
            with open(f"{self.storage_path}/relationship_traces.json", 'w') as f:
                data = {k: [asdict(t) for t in v] for k, v in self.relationship_traces.items()}
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save traceability data: {e}")
    
    def _load_data(self):
        """Load traceability data from files"""
        try:
            # Load source documents
            if os.path.exists(f"{self.storage_path}/source_documents.json"):
                with open(f"{self.storage_path}/source_documents.json", 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        v['source_type'] = SourceType(v['source_type'])
                        v['document_type'] = DocumentType(v['document_type'])
                        v['created_at'] = datetime.fromisoformat(v['created_at'])
                        v['modified_at'] = datetime.fromisoformat(v['modified_at'])
                        self.source_documents[k] = SourceDocument(**v)
            
            # Load extractions
            if os.path.exists(f"{self.storage_path}/extractions.json"):
                with open(f"{self.storage_path}/extractions.json", 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        v['confidence_level'] = ConfidenceLevel(v['confidence_level'])
                        v['extracted_at'] = datetime.fromisoformat(v['extracted_at'])
                        self.extractions[k] = DataExtraction(**v)
            
            # Load entity traces
            if os.path.exists(f"{self.storage_path}/entity_traces.json"):
                with open(f"{self.storage_path}/entity_traces.json", 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        traces = []
                        for trace_data in v:
                            trace_data['confidence_level'] = ConfidenceLevel(trace_data['confidence_level'])
                            trace_data['created_at'] = datetime.fromisoformat(trace_data['created_at'])
                            if trace_data.get('verified_at'):
                                trace_data['verified_at'] = datetime.fromisoformat(trace_data['verified_at'])
                            traces.append(EntityTrace(**trace_data))
                        self.entity_traces[k] = traces
            
            # Load relationship traces
            if os.path.exists(f"{self.storage_path}/relationship_traces.json"):
                with open(f"{self.storage_path}/relationship_traces.json", 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        traces = []
                        for trace_data in v:
                            trace_data['confidence_level'] = ConfidenceLevel(trace_data['confidence_level'])
                            trace_data['created_at'] = datetime.fromisoformat(trace_data['created_at'])
                            if trace_data.get('verified_at'):
                                trace_data['verified_at'] = datetime.fromisoformat(trace_data['verified_at'])
                            traces.append(RelationshipTrace(**trace_data))
                        self.relationship_traces[k] = traces
                        
        except Exception as e:
            logger.error(f"Failed to load traceability data: {e}")

# Global traceability manager instance
traceability_manager = TraceabilityManager()
