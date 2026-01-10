"""
Fine-grained security system for Argus MVP
Implements cell-level access control similar to Gotham
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Permission levels for access control"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class ClearanceLevel(Enum):
    """Security clearance levels"""
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SECRET = 3
    TOP_SECRET = 4

@dataclass
class SecurityPolicy:
    """Security policy for field-level access control"""
    field_name: str
    required_clearance: ClearanceLevel
    required_permissions: Set[Permission]
    conditions: Optional[Dict[str, Any]] = None

@dataclass
class User:
    """User with security clearance and permissions"""
    user_id: str
    username: str
    clearance_level: ClearanceLevel
    permissions: Set[Permission]
    department: str
    active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class SecurityManager:
    """Manages security policies and access control"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.policies: Dict[str, List[SecurityPolicy]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Default security policies for different entity types
        self._setup_default_policies()
    
    def _setup_default_policies(self):
        """Setup default security policies"""
        # Person entity policies
        self.policies['person'] = [
            SecurityPolicy('name', ClearanceLevel.PUBLIC, {Permission.READ}),
            SecurityPolicy('dob', ClearanceLevel.INTERNAL, {Permission.READ}),
            SecurityPolicy('ssn', ClearanceLevel.SECRET, {Permission.READ}),
            SecurityPolicy('passport', ClearanceLevel.CONFIDENTIAL, {Permission.READ}),
            SecurityPolicy('address', ClearanceLevel.INTERNAL, {Permission.READ}),
            SecurityPolicy('phone', ClearanceLevel.INTERNAL, {Permission.READ}),
            SecurityPolicy('email', ClearanceLevel.PUBLIC, {Permission.READ}),
        ]
        
        # Organization entity policies
        self.policies['organization'] = [
            SecurityPolicy('name', ClearanceLevel.PUBLIC, {Permission.READ}),
            SecurityPolicy('registration_number', ClearanceLevel.CONFIDENTIAL, {Permission.READ}),
            SecurityPolicy('tax_id', ClearanceLevel.SECRET, {Permission.READ}),
            SecurityPolicy('address', ClearanceLevel.INTERNAL, {Permission.READ}),
            SecurityPolicy('phone', ClearanceLevel.PUBLIC, {Permission.READ}),
        ]
        
        # Transaction entity policies
        self.policies['transaction'] = [
            SecurityPolicy('amount', ClearanceLevel.INTERNAL, {Permission.READ}),
            SecurityPolicy('from_account', ClearanceLevel.CONFIDENTIAL, {Permission.READ}),
            SecurityPolicy('to_account', ClearanceLevel.CONFIDENTIAL, {Permission.READ}),
            SecurityPolicy('date', ClearanceLevel.INTERNAL, {Permission.READ}),
            SecurityPolicy('reference', ClearanceLevel.SECRET, {Permission.READ}),
        ]
    
    def add_user(self, user: User) -> bool:
        """Add a new user to the system"""
        try:
            self.users[user.user_id] = user
            self._log_action('USER_CREATED', user.user_id, {'username': user.username})
            return True
        except Exception as e:
            logger.error(f"Failed to add user {user.user_id}: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token"""
        user = None
        for u in self.users.values():
            if u.username == username and u.active:
                user = u
                break
        
        if not user:
            self._log_action('LOGIN_FAILED', None, {'username': username})
            return None
        
        # In production, use proper password hashing
        token = hashlib.sha256(f"{username}{datetime.now()}".encode()).hexdigest()
        
        self.session_tokens[token] = {
            'user_id': user.user_id,
            'username': user.username,
            'clearance_level': user.clearance_level,
            'permissions': user.permissions,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=8)
        }
        
        self._log_action('LOGIN_SUCCESS', user.user_id, {'username': username})
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user session"""
        if token not in self.session_tokens:
            return None
        
        session = self.session_tokens[token]
        if datetime.now() > session['expires_at']:
            del self.session_tokens[token]
            return None
        
        return session
    
    def can_access_field(self, token: str, entity_type: str, field_name: str, 
                       permission: Permission = Permission.READ) -> bool:
        """Check if user can access a specific field"""
        session = self.validate_token(token)
        if not session:
            return False
        
        if entity_type not in self.policies:
            return True  # No specific policy, allow access
        
        for policy in self.policies[entity_type]:
            if policy.field_name == field_name:
                # Check clearance level
                if session['clearance_level'].value < policy.required_clearance.value:
                    self._log_action('ACCESS_DENIED', session['user_id'], {
                        'entity_type': entity_type,
                        'field': field_name,
                        'reason': 'insufficient_clearance'
                    })
                    return False
                
                # Check permissions
                if permission not in policy.required_permissions:
                    self._log_action('ACCESS_DENIED', session['user_id'], {
                        'entity_type': entity_type,
                        'field': field_name,
                        'reason': 'insufficient_permission'
                    })
                    return False
                
                # Check conditions if any
                if policy.conditions:
                    if not self._check_conditions(session, policy.conditions):
                        self._log_action('ACCESS_DENIED', session['user_id'], {
                            'entity_type': entity_type,
                            'field': field_name,
                            'reason': 'condition_not_met'
                        })
                        return False
        
        return True
    
    def _check_conditions(self, session: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Check if user meets policy conditions"""
        for condition_key, condition_value in conditions.items():
            if condition_key == 'department':
                user = self.users[session['user_id']]
                if user.department != condition_value:
                    return False
            elif condition_key == 'time_range':
                current_time = datetime.now().time()
                start_time = condition_value.get('start')
                end_time = condition_value.get('end')
                if start_time and end_time:
                    if not (start_time <= current_time <= end_time):
                        return False
        
        return True
    
    def filter_entity_data(self, token: str, entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter entity data based on user permissions"""
        filtered_data = {}
        
        for field_name, field_value in data.items():
            if self.can_access_field(token, entity_type, field_name, Permission.READ):
                filtered_data[field_name] = field_value
            else:
                filtered_data[field_name] = '[REDACTED]'
        
        return filtered_data
    
    def _log_action(self, action: str, user_id: Optional[str], details: Dict[str, Any]):
        """Log security action for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details
        }
        self.audit_log.append(log_entry)
        logger.info(f"Security action: {action} by user {user_id}")
    
    def get_audit_log(self, token: str, start_date: Optional[datetime] = None, 
                    end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit log entries (admin only)"""
        session = self.validate_token(token)
        if not session or Permission.ADMIN not in session['permissions']:
            return []
        
        filtered_log = self.audit_log
        
        if start_date:
            filtered_log = [entry for entry in filtered_log 
                          if datetime.fromisoformat(entry['timestamp']) >= start_date]
        
        if end_date:
            filtered_log = [entry for entry in filtered_log 
                          if datetime.fromisoformat(entry['timestamp']) <= end_date]
        
        return filtered_log
    
    def logout(self, token: str):
        """Logout user and invalidate token"""
        if token in self.session_tokens:
            session = self.session_tokens[token]
            self._log_action('LOGOUT', session['user_id'], {'username': session['username']})
            del self.session_tokens[token]

# Global security manager instance
security_manager = SecurityManager()

# Setup default users for demo
def setup_demo_users():
    """Setup demo users with different clearance levels"""
    demo_users = [
        User(
            user_id="user_001",
            username="analyst_john",
            clearance_level=ClearanceLevel.INTERNAL,
            permissions={Permission.READ, Permission.WRITE},
            department="fraud_analysis"
        ),
        User(
            user_id="user_002", 
            username="ct_analyst",
            clearance_level=ClearanceLevel.SECRET,
            permissions={Permission.READ, Permission.WRITE, Permission.DELETE},
            department="counter_terrorism"
        ),
        User(
            user_id="user_003",
            username="admin",
            clearance_level=ClearanceLevel.TOP_SECRET,
            permissions={Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN},
            department="security"
        )
    ]
    
    for user in demo_users:
        security_manager.add_user(user)
