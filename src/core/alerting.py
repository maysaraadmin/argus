"""
Real-time alerting system for Argus MVP
Implements pattern detection and notification system
"""
import json
import uuid
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class PatternType(Enum):
    """Types of patterns to detect"""
    ENTITY_CONNECTION = "entity_connection"
    TRANSACTION_PATTERN = "transaction_pattern"
    TEMPORAL_PATTERN = "temporal_pattern"
    GEOGRAPHIC_PATTERN = "geographic_pattern"
    ATTRIBUTE_PATTERN = "attribute_pattern"
    NETWORK_PATTERN = "network_pattern"

class AlertChannel(Enum):
    """Alert notification channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"

@dataclass
class AlertRule:
    """Alert rule definition"""
    id: str
    name: str
    description: str
    pattern_type: PatternType
    conditions: Dict[str, Any]
    severity: AlertSeverity
    enabled: bool = True
    created_by: str = ""
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    entities: List[str]  # Entity IDs involved
    relationships: List[str]  # Relationship IDs involved
    evidence: Dict[str, Any]  # Evidence that triggered alert
    triggered_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.triggered_at is None:
            self.triggered_at = datetime.now()

@dataclass
class AlertSubscription:
    """User subscription to alerts"""
    user_id: str
    rule_ids: Set[str]  # Specific rules to follow
    severity_levels: Set[AlertSeverity]  # Minimum severity to notify
    channels: Set[AlertChannel]  # Notification channels
    enabled: bool = True

class PatternDetector:
    """Base class for pattern detection"""
    
    def detect(self, data: Dict[str, Any], rule: AlertRule) -> Optional[Dict[str, Any]]:
        """Detect pattern based on rule conditions"""
        raise NotImplementedError

class EntityConnectionDetector(PatternDetector):
    """Detects connections between specific entities"""
    
    def detect(self, data: Dict[str, Any], rule: AlertRule) -> Optional[Dict[str, Any]]:
        conditions = rule.conditions
        
        # Check if specific entities are connected
        required_entities = conditions.get('entities', [])
        max_hops = conditions.get('max_hops', 3)
        
        if len(required_entities) < 2:
            return None
        
        # Check if all required entities exist in the graph
        graph = data.get('graph')
        if not graph:
            return None
        
        # Find paths between entities
        connected_entities = set()
        evidence = {
            'connections': [],
            'paths': []
        }
        
        for i, entity1 in enumerate(required_entities):
            for entity2 in required_entities[i+1:]:
                try:
                    # Try to find path between entities
                    if graph.has_node(entity1) and graph.has_node(entity2):
                        path = list(nx.shortest_path(graph, entity1, entity2))
                        if len(path) - 1 <= max_hops:
                            connected_entities.add(entity1)
                            connected_entities.add(entity2)
                            evidence['paths'].append({
                                'from': entity1,
                                'to': entity2,
                                'path': path,
                                'hops': len(path) - 1
                            })
                except nx.NetworkXNoPath:
                    continue
        
        # Check if all entities are connected
        if len(connected_entities) == len(required_entities):
            return {
                'detected': True,
                'evidence': evidence,
                'entities': list(connected_entities)
            }
        
        return None

class TransactionPatternDetector(PatternDetector):
    """Detects suspicious transaction patterns"""
    
    def detect(self, data: Dict[str, Any], rule: AlertRule) -> Optional[Dict[str, Any]]:
        conditions = rule.conditions
        
        # Check transaction patterns
        min_amount = conditions.get('min_amount')
        max_amount = conditions.get('max_amount')
        time_window = conditions.get('time_window_hours', 24)
        transaction_count = conditions.get('transaction_count', 5)
        
        transactions = data.get('transactions', [])
        if not transactions:
            return None
        
        # Filter transactions by amount
        filtered_transactions = []
        for tx in transactions:
            amount = tx.get('amount', 0)
            if min_amount and amount < min_amount:
                continue
            if max_amount and amount > max_amount:
                continue
            filtered_transactions.append(tx)
        
        # Check for patterns in time window
        suspicious_patterns = []
        current_time = datetime.now()
        window_start = current_time - timedelta(hours=time_window)
        
        # Group by account or entity
        account_groups = defaultdict(list)
        for tx in filtered_transactions:
            tx_time = datetime.fromisoformat(tx.get('date', ''))
            if tx_time >= window_start:
                account = tx.get('from_account') or tx.get('to_account')
                account_groups[account].append(tx)
        
        # Check for high-frequency transactions
        for account, txs in account_groups.items():
            if len(txs) >= transaction_count:
                total_amount = sum(tx.get('amount', 0) for tx in txs)
                suspicious_patterns.append({
                    'account': account,
                    'transaction_count': len(txs),
                    'total_amount': total_amount,
                    'time_window_hours': time_window,
                    'transactions': txs
                })
        
        if suspicious_patterns:
            return {
                'detected': True,
                'evidence': {
                    'patterns': suspicious_patterns,
                    'total_patterns': len(suspicious_patterns)
                }
            }
        
        return None

class TemporalPatternDetector(PatternDetector):
    """Detects temporal patterns in events"""
    
    def detect(self, data: Dict[str, Any], rule: AlertRule) -> Optional[Dict[str, Any]]:
        conditions = rule.conditions
        
        # Check temporal patterns
        event_types = conditions.get('event_types', [])
        time_window = conditions.get('time_window_hours', 24)
        min_events = conditions.get('min_events', 3)
        
        events = data.get('events', [])
        if not events:
            return None
        
        # Filter events by type
        filtered_events = []
        for event in events:
            if event_types and event.get('type') not in event_types:
                continue
            filtered_events.append(event)
        
        # Check for patterns in time window
        current_time = datetime.now()
        window_start = current_time - timedelta(hours=time_window)
        
        recent_events = [
            event for event in filtered_events
            if datetime.fromisoformat(event.get('timestamp', '')) >= window_start
        ]
        
        if len(recent_events) >= min_events:
            return {
                'detected': True,
                'evidence': {
                    'event_count': len(recent_events),
                    'time_window_hours': time_window,
                    'events': recent_events
                }
            }
        
        return None

class AlertingManager:
    """Manages alerting system"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.subscriptions: Dict[str, AlertSubscription] = {}  # user_id -> subscription
        self.detectors: Dict[PatternType, PatternDetector] = {
            PatternType.ENTITY_CONNECTION: EntityConnectionDetector(),
            PatternType.TRANSACTION_PATTERN: TransactionPatternDetector(),
            PatternType.TEMPORAL_PATTERN: TemporalPatternDetector(),
        }
        self.notification_handlers: Dict[AlertChannel, Callable] = {
            AlertChannel.IN_APP: self._in_app_notification,
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def create_rule(self, name: str, description: str, pattern_type: PatternType,
                   conditions: Dict[str, Any], severity: AlertSeverity,
                   created_by: str) -> str:
        """Create a new alert rule"""
        rule = AlertRule(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            pattern_type=pattern_type,
            conditions=conditions,
            severity=severity,
            created_by=created_by
        )
        
        self.rules[rule.id] = rule
        logger.info(f"Created alert rule {rule.id}: {name}")
        return rule.id
    
    def update_rule(self, rule_id: str, **kwargs) -> bool:
        """Update an existing alert rule"""
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        logger.info(f"Updated alert rule {rule_id}")
        return True
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        if rule_id not in self.rules:
            return False
        
        del self.rules[rule_id]
        logger.info(f"Deleted alert rule {rule_id}")
        return True
    
    def create_subscription(self, user_id: str, rule_ids: Set[str] = None,
                         severity_levels: Set[AlertSeverity] = None,
                         channels: Set[AlertChannel] = None) -> str:
        """Create alert subscription for user"""
        subscription = AlertSubscription(
            user_id=user_id,
            rule_ids=rule_ids or set(),
            severity_levels=severity_levels or {AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL},
            channels=channels or {AlertChannel.IN_APP}
        )
        
        self.subscriptions[user_id] = subscription
        logger.info(f"Created alert subscription for user {user_id}")
        return user_id
    
    def start_monitoring(self, data_provider: Callable[[], Dict[str, Any]], 
                       check_interval: int = 60):
        """Start real-time monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(data_provider, check_interval),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Started real-time alert monitoring")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Stopped real-time alert monitoring")
    
    def _monitoring_loop(self, data_provider: Callable, check_interval: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                data = data_provider()
                self._check_rules(data)
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)
    
    def _check_rules(self, data: Dict[str, Any]):
        """Check all enabled rules against current data"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # Check cooldown period (avoid spam)
            if rule.last_triggered:
                cooldown = rule.conditions.get('cooldown_minutes', 60)
                if datetime.now() - rule.last_triggered < timedelta(minutes=cooldown):
                    continue
            
            # Run pattern detection
            detector = self.detectors.get(rule.pattern_type)
            if not detector:
                continue
            
            result = detector.detect(data, rule)
            if result and result.get('detected'):
                self._trigger_alert(rule, result)
    
    def _trigger_alert(self, rule: AlertRule, evidence: Dict[str, Any]):
        """Trigger an alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            title=f"Alert: {rule.name}",
            description=rule.description,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            entities=evidence.get('entities', []),
            relationships=evidence.get('relationships', []),
            evidence=evidence.get('evidence', {}),
            triggered_at=datetime.now()
        )
        
        self.alerts[alert.id] = alert
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        logger.warning(f"Triggered alert {alert.id} for rule {rule.name}")
        
        # Send notifications
        self._send_notifications(alert)
    
    def _send_notifications(self, alert: Alert):
        """Send alert notifications to subscribed users"""
        for user_id, subscription in self.subscriptions.items():
            if not subscription.enabled:
                continue
            
            # Check if user is subscribed to this rule
            if subscription.rule_ids and alert.rule_id not in subscription.rule_ids:
                continue
            
            # Check severity level
            if alert.severity not in subscription.severity_levels:
                continue
            
            # Send through each channel
            for channel in subscription.channels:
                handler = self.notification_handlers.get(channel)
                if handler:
                    try:
                        handler(user_id, alert)
                    except Exception as e:
                        logger.error(f"Failed to send notification via {channel}: {e}")
    
    def _in_app_notification(self, user_id: str, alert: Alert):
        """In-app notification handler"""
        # This would integrate with the UI to show notifications
        logger.info(f"In-app notification for user {user_id}: {alert.title}")
    
    def acknowledge_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now()
        if notes:
            alert.notes = notes
        
        logger.info(f"Acknowledged alert {alert_id} by user {user_id}")
        return True
    
    def resolve_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Resolve an alert"""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_by = user_id
        alert.resolved_at = datetime.now()
        if notes:
            alert.notes = notes
        
        logger.info(f"Resolved alert {alert_id} by user {user_id}")
        return True
    
    def get_active_alerts(self, user_id: Optional[str] = None) -> List[Alert]:
        """Get active alerts (optionally filtered by user)"""
        alerts = [alert for alert in self.alerts.values() if alert.status == AlertStatus.ACTIVE]
        
        if user_id:
            subscription = self.subscriptions.get(user_id)
            if subscription:
                # Filter by user's subscription
                filtered_alerts = []
                for alert in alerts:
                    if (not subscription.rule_ids or alert.rule_id in subscription.rule_ids) and \
                       alert.severity in subscription.severity_levels:
                        filtered_alerts.append(alert)
                alerts = filtered_alerts
        
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)
    
    def get_alert_history(self, user_id: Optional[str] = None, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Alert]:
        """Get alert history"""
        alerts = list(self.alerts.values())
        
        if user_id:
            subscription = self.subscriptions.get(user_id)
            if subscription:
                alerts = [alert for alert in alerts 
                         if (not subscription.rule_ids or alert.rule_id in subscription.rule_ids) and \
                            alert.severity in subscription.severity_levels]
        
        if start_date:
            alerts = [alert for alert in alerts if alert.triggered_at >= start_date]
        
        if end_date:
            alerts = [alert for alert in alerts if alert.triggered_at <= end_date]
        
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)

# Import NetworkX for graph operations
import networkx as nx

# Global alerting manager instance
alerting_manager = AlertingManager()
