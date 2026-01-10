"""
Collaborative workspaces for multi-user analysis
Implements shared case files, annotations, and team collaboration
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AnnotationType(Enum):
    """Types of annotations"""
    NOTE = "note"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    QUESTION = "question"
    ALERT = "alert"
    TAG = "tag"

class WorkspaceRole(Enum):
    """User roles in workspace"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"

@dataclass
class Annotation:
    """Annotation on data points"""
    id: str
    user_id: str
    entity_id: Optional[str]
    relationship_id: Optional[str]
    annotation_type: AnnotationType
    content: str
    confidence: Optional[float] = None
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    parent_id: Optional[str] = None  # For threaded discussions
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []

@dataclass
class WorkspaceMember:
    """Member of a workspace"""
    user_id: str
    role: WorkspaceRole
    joined_at: datetime = None
    
    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.now()

@dataclass
class CaseFile:
    """Shared case file for investigation"""
    id: str
    name: str
    description: str
    owner_id: str
    members: Dict[str, WorkspaceMember]
    entities: Set[str]  # Entity IDs included in case
    relationships: Set[str]  # Relationship IDs included in case
    annotations: List[Annotation]
    status: str = "active"
    priority: str = "medium"
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class CollaborationManager:
    """Manages collaborative workspaces and case files"""
    
    def __init__(self):
        self.workspaces: Dict[str, CaseFile] = {}
        self.user_workspaces: Dict[str, Set[str]] = {}  # user_id -> workspace_ids
        self.annotations: Dict[str, Annotation] = {}  # annotation_id -> annotation
        
    def create_workspace(self, name: str, description: str, owner_id: str) -> str:
        """Create a new workspace/case file"""
        workspace_id = str(uuid.uuid4())
        
        workspace = CaseFile(
            id=workspace_id,
            name=name,
            description=description,
            owner_id=owner_id,
            members={
                owner_id: WorkspaceMember(owner_id, WorkspaceRole.OWNER)
            },
            entities=set(),
            relationships=set(),
            annotations=[]
        )
        
        self.workspaces[workspace_id] = workspace
        
        # Track user's workspaces
        if owner_id not in self.user_workspaces:
            self.user_workspaces[owner_id] = set()
        self.user_workspaces[owner_id].add(workspace_id)
        
        logger.info(f"Created workspace {workspace_id} by user {owner_id}")
        return workspace_id
    
    def add_member(self, workspace_id: str, user_id: str, role: WorkspaceRole, 
                  added_by: str) -> bool:
        """Add a member to workspace"""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        
        # Check if user has permission to add members
        if not self._can_manage_members(workspace, added_by):
            return False
        
        workspace.members[user_id] = WorkspaceMember(user_id, role)
        
        # Track user's workspaces
        if user_id not in self.user_workspaces:
            self.user_workspaces[user_id] = set()
        self.user_workspaces[user_id].add(workspace_id)
        
        logger.info(f"Added user {user_id} to workspace {workspace_id} as {role.value}")
        return True
    
    def remove_member(self, workspace_id: str, user_id: str, removed_by: str) -> bool:
        """Remove a member from workspace"""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        
        # Check if user has permission to remove members
        if not self._can_manage_members(workspace, removed_by):
            return False
        
        # Cannot remove owner
        if workspace.members[user_id].role == WorkspaceRole.OWNER:
            return False
        
        del workspace.members[user_id]
        
        # Update user's workspace list
        if user_id in self.user_workspaces:
            self.user_workspaces[user_id].discard(workspace_id)
        
        logger.info(f"Removed user {user_id} from workspace {workspace_id}")
        return True
    
    def add_entity_to_workspace(self, workspace_id: str, entity_id: str, user_id: str) -> bool:
        """Add an entity to workspace"""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        
        # Check if user has permission to add entities
        if not self._can_edit_workspace(workspace, user_id):
            return False
        
        workspace.entities.add(entity_id)
        workspace.updated_at = datetime.now()
        
        logger.info(f"Added entity {entity_id} to workspace {workspace_id}")
        return True
    
    def add_relationship_to_workspace(self, workspace_id: str, relationship_id: str, 
                                  user_id: str) -> bool:
        """Add a relationship to workspace"""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        
        # Check if user has permission to add relationships
        if not self._can_edit_workspace(workspace, user_id):
            return False
        
        workspace.relationships.add(relationship_id)
        workspace.updated_at = datetime.now()
        
        logger.info(f"Added relationship {relationship_id} to workspace {workspace_id}")
        return True
    
    def add_annotation(self, workspace_id: str, user_id: str, entity_id: Optional[str],
                    relationship_id: Optional[str], annotation_type: AnnotationType,
                    content: str, confidence: Optional[float] = None,
                    tags: List[str] = None, parent_id: Optional[str] = None) -> str:
        """Add an annotation to entity or relationship"""
        if workspace_id not in self.workspaces:
            return ""
        
        workspace = self.workspaces[workspace_id]
        
        # Check if user has permission to annotate
        if not self._can_annotate_workspace(workspace, user_id):
            return ""
        
        annotation = Annotation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            entity_id=entity_id,
            relationship_id=relationship_id,
            annotation_type=annotation_type,
            content=content,
            confidence=confidence,
            tags=tags or [],
            parent_id=parent_id
        )
        
        workspace.annotations.append(annotation)
        self.annotations[annotation.id] = annotation
        workspace.updated_at = datetime.now()
        
        logger.info(f"Added annotation {annotation.id} to workspace {workspace_id}")
        return annotation.id
    
    def get_workspace(self, workspace_id: str, user_id: str) -> Optional[CaseFile]:
        """Get workspace if user has access"""
        if workspace_id not in self.workspaces:
            return None
        
        workspace = self.workspaces[workspace_id]
        
        # Check if user is a member
        if user_id not in workspace.members:
            return None
        
        return workspace
    
    def get_user_workspaces(self, user_id: str) -> List[CaseFile]:
        """Get all workspaces for a user"""
        if user_id not in self.user_workspaces:
            return []
        
        workspaces = []
        for workspace_id in self.user_workspaces[user_id]:
            if workspace_id in self.workspaces:
                workspaces.append(self.workspaces[workspace_id])
        
        return workspaces
    
    def get_annotations_for_entity(self, entity_id: str, user_id: str) -> List[Annotation]:
        """Get all annotations for an entity that user can see"""
        annotations = []
        
        for annotation in self.annotations.values():
            if annotation.entity_id == entity_id:
                # Check if user has access to the workspace containing this annotation
                workspace_id = self._find_annotation_workspace(annotation.id)
                if workspace_id and self._can_view_workspace(self.workspaces[workspace_id], user_id):
                    annotations.append(annotation)
        
        return sorted(annotations, key=lambda x: x.created_at)
    
    def get_annotations_for_relationship(self, relationship_id: str, user_id: str) -> List[Annotation]:
        """Get all annotations for a relationship that user can see"""
        annotations = []
        
        for annotation in self.annotations.values():
            if annotation.relationship_id == relationship_id:
                # Check if user has access to the workspace containing this annotation
                workspace_id = self._find_annotation_workspace(annotation.id)
                if workspace_id and self._can_view_workspace(self.workspaces[workspace_id], user_id):
                    annotations.append(annotation)
        
        return sorted(annotations, key=lambda x: x.created_at)
    
    def search_annotations(self, query: str, user_id: str, workspace_id: Optional[str] = None) -> List[Annotation]:
        """Search annotations by content"""
        results = []
        query_lower = query.lower()
        
        for annotation in self.annotations.values():
            # Check workspace access
            if workspace_id:
                if not self._annotation_in_workspace(annotation.id, workspace_id):
                    continue
            else:
                # Check any workspace access
                ws_id = self._find_annotation_workspace(annotation.id)
                if not ws_id or not self._can_view_workspace(self.workspaces[ws_id], user_id):
                    continue
            
            # Search content
            if query_lower in annotation.content.lower():
                results.append(annotation)
        
        return sorted(results, key=lambda x: x.created_at, reverse=True)
    
    def _can_manage_members(self, workspace: CaseFile, user_id: str) -> bool:
        """Check if user can manage workspace members"""
        if user_id not in workspace.members:
            return False
        
        member = workspace.members[user_id]
        return member.role in [WorkspaceRole.OWNER, WorkspaceRole.EDITOR]
    
    def _can_edit_workspace(self, workspace: CaseFile, user_id: str) -> bool:
        """Check if user can edit workspace"""
        if user_id not in workspace.members:
            return False
        
        member = workspace.members[user_id]
        return member.role in [WorkspaceRole.OWNER, WorkspaceRole.EDITOR]
    
    def _can_annotate_workspace(self, workspace: CaseFile, user_id: str) -> bool:
        """Check if user can annotate in workspace"""
        if user_id not in workspace.members:
            return False
        
        member = workspace.members[user_id]
        return member.role in [WorkspaceRole.OWNER, WorkspaceRole.EDITOR, WorkspaceRole.COMMENTER]
    
    def _can_view_workspace(self, workspace: CaseFile, user_id: str) -> bool:
        """Check if user can view workspace"""
        return user_id in workspace.members
    
    def _find_annotation_workspace(self, annotation_id: str) -> Optional[str]:
        """Find which workspace contains an annotation"""
        for workspace_id, workspace in self.workspaces.items():
            for annotation in workspace.annotations:
                if annotation.id == annotation_id:
                    return workspace_id
        return None
    
    def _annotation_in_workspace(self, annotation_id: str, workspace_id: str) -> bool:
        """Check if annotation is in specific workspace"""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        for annotation in workspace.annotations:
            if annotation.id == annotation_id:
                return True
        return False
    
    def export_workspace(self, workspace_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Export workspace data for backup or sharing"""
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None
        
        export_data = {
            'workspace': asdict(workspace),
            'exported_at': datetime.now().isoformat(),
            'exported_by': user_id
        }
        
        return export_data
    
    def import_workspace(self, export_data: Dict[str, Any], user_id: str) -> Optional[str]:
        """Import workspace data from export"""
        try:
            workspace_data = export_data['workspace']
            
            # Create new workspace
            new_workspace_id = self.create_workspace(
                workspace_data['name'],
                workspace_data['description'],
                user_id
            )
            
            workspace = self.workspaces[new_workspace_id]
            workspace.entities = set(workspace_data.get('entities', []))
            workspace.relationships = set(workspace_data.get('relationships', []))
            
            # Import annotations
            for annotation_data in workspace_data.get('annotations', []):
                annotation = Annotation(**annotation_data)
                workspace.annotations.append(annotation)
                self.annotations[annotation.id] = annotation
            
            logger.info(f"Imported workspace {new_workspace_id}")
            return new_workspace_id
            
        except Exception as e:
            logger.error(f"Failed to import workspace: {e}")
            return None

# Global collaboration manager instance
collaboration_manager = CollaborationManager()
