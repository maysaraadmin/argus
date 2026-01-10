"""
Plug-in architecture for Argus MVP
Provides extensibility for custom connectors, analytics, and visualizations
"""
import importlib
import inspect
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PluginType(Enum):
    """Types of plugins"""
    DATA_CONNECTOR = "data_connector"
    ANALYTICS = "analytics"
    VISUALIZATION = "visualization"
    WORKFLOW = "workflow"
    NOTIFICATION = "notification"

class PluginStatus(Enum):
    """Plugin status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    LOADING = "loading"

@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    config_schema: Dict[str, Any]
    entry_point: str
    status: PluginStatus = PluginStatus.INACTIVE

class Plugin(ABC):
    """Base plugin class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        pass

class DataConnectorPlugin(Plugin):
    """Base class for data connector plugins"""
    
    @abstractmethod
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """Connect to data source"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from data source"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to data source"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get data schema"""
        pass
    
    @abstractmethod
    def extract_data(self, query: Optional[str] = None, 
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Extract data from source"""
        pass

class AnalyticsPlugin(Plugin):
    """Base class for analytics plugins"""
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return results"""
        pass
    
    @abstractmethod
    def get_supported_data_types(self) -> List[str]:
        """Get supported data types"""
        pass

class VisualizationPlugin(Plugin):
    """Base class for visualization plugins"""
    
    @abstractmethod
    def render(self, data: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Render visualization and return HTML/JS"""
        pass
    
    @abstractmethod
    def get_supported_chart_types(self) -> List[str]:
        """Get supported chart types"""
        pass

class WorkflowPlugin(Plugin):
    """Base class for workflow plugins"""
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow step"""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema"""
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema"""
        pass

class NotificationPlugin(Plugin):
    """Base class for notification plugins"""
    
    @abstractmethod
    def send_notification(self, message: str, recipients: List[str],
                       metadata: Dict[str, Any]) -> bool:
        """Send notification"""
        pass
    
    @abstractmethod
    def test_notification(self) -> bool:
        """Test notification sending"""
        pass

class PluginManager:
    """Manages plugin lifecycle and registry"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        
        # Ensure plugin directory exists
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Load existing plugins
        self._discover_plugins()
        self._load_plugin_configs()
    
    def _discover_plugins(self):
        """Discover plugins in plugin directory"""
        if not os.path.exists(self.plugin_dir):
            return
        
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            # Check if it's a plugin directory with manifest
            if os.path.isdir(plugin_path):
                manifest_path = os.path.join(plugin_path, "plugin.json")
                if os.path.exists(manifest_path):
                    self._load_plugin_manifest(manifest_path, plugin_path)
    
    def _load_plugin_manifest(self, manifest_path: str, plugin_path: str):
        """Load plugin manifest"""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            metadata = PluginMetadata(
                name=manifest['name'],
                version=manifest['version'],
                description=manifest['description'],
                author=manifest['author'],
                plugin_type=PluginType(manifest['type']),
                dependencies=manifest.get('dependencies', []),
                config_schema=manifest.get('config_schema', {}),
                entry_point=manifest['entry_point']
            )
            
            self.plugin_metadata[metadata.name] = metadata
            logger.info(f"Discovered plugin: {metadata.name} v{metadata.version}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin manifest {manifest_path}: {e}")
    
    def _load_plugin_configs(self):
        """Load plugin configurations"""
        config_path = os.path.join(self.plugin_dir, "configs.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.plugin_configs = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load plugin configs: {e}")
    
    def install_plugin(self, plugin_path: str) -> bool:
        """Install a new plugin from file or directory"""
        try:
            # This would handle plugin installation from zip file, git repo, etc.
            # For now, assume it's already extracted
            if os.path.isdir(plugin_path):
                # Copy to plugins directory
                import shutil
                plugin_name = os.path.basename(plugin_path)
                target_path = os.path.join(self.plugin_dir, plugin_name)
                
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                
                shutil.copytree(plugin_path, target_path)
                
                # Load manifest
                manifest_path = os.path.join(target_path, "plugin.json")
                if os.path.exists(manifest_path):
                    self._load_plugin_manifest(manifest_path, target_path)
                    logger.info(f"Installed plugin: {plugin_name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to install plugin: {e}")
            return False
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        if plugin_name not in self.plugin_metadata:
            logger.error(f"Plugin {plugin_name} not found")
            return False
        
        metadata = self.plugin_metadata[plugin_name]
        
        # Check dependencies
        for dep in metadata.dependencies:
            if dep not in self.plugins:
                logger.error(f"Plugin {plugin_name} requires dependency {dep}")
                return False
        
        try:
            # Load plugin module
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            entry_point = metadata.entry_point
            
            # Add plugin directory to Python path
            import sys
            if plugin_path not in sys.path:
                sys.path.insert(0, plugin_path)
            
            # Import plugin module
            module = importlib.import_module(entry_point)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"No plugin class found in {plugin_name}")
                return False
            
            # Get plugin configuration
            config = self.plugin_configs.get(plugin_name, {})
            
            # Initialize plugin
            plugin = plugin_class(config)
            
            # Initialize plugin
            if plugin.initialize():
                self.plugins[plugin_name] = plugin
                metadata.status = PluginStatus.ACTIVE
                logger.info(f"Loaded plugin: {plugin_name}")
                
                # Register hooks
                self._register_plugin_hooks(plugin_name, plugin)
                
                return True
            else:
                metadata.status = PluginStatus.ERROR
                logger.error(f"Failed to initialize plugin: {plugin_name}")
                return False
                
        except Exception as e:
            metadata.status = PluginStatus.ERROR
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            
            # Cleanup plugin
            plugin.cleanup()
            
            # Remove from registry
            del self.plugins[plugin_name]
            
            # Update status
            if plugin_name in self.plugin_metadata:
                self.plugin_metadata[plugin_name].status = PluginStatus.INACTIVE
            
            # Unregister hooks
            self._unregister_plugin_hooks(plugin_name)
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get loaded plugin instance"""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """Get all loaded plugins of a specific type"""
        return [
            plugin for plugin in self.plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]
    
    def get_available_plugins(self) -> List[PluginMetadata]:
        """Get all available plugins (loaded and unloaded)"""
        return list(self.plugin_metadata.values())
    
    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Configure a plugin"""
        if plugin_name not in self.plugin_metadata:
            return False
        
        # Validate config against schema
        metadata = self.plugin_metadata[plugin_name]
        schema = metadata.config_schema
        
        if schema and not self._validate_config(config, schema):
            logger.error(f"Invalid configuration for plugin {plugin_name}")
            return False
        
        # Save configuration
        self.plugin_configs[plugin_name] = config
        
        # Update plugin if loaded
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.config = config
            
            # Reinitialize if needed
            try:
                plugin.cleanup()
                plugin.initialize()
            except Exception as e:
                logger.error(f"Failed to reinitialize plugin {plugin_name}: {e}")
                return False
        
        # Save to file
        self._save_plugin_configs()
        
        logger.info(f"Configured plugin: {plugin_name}")
        return True
    
    def _validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate configuration against schema"""
        # Simple validation - could use jsonschema for more complex validation
        for key, spec in schema.items():
            if spec.get('required', False) and key not in config:
                return False
            
            if key in config:
                expected_type = spec.get('type')
                if expected_type and not isinstance(config[key], expected_type):
                    return False
        
        return True
    
    def _save_plugin_configs(self):
        """Save plugin configurations to file"""
        try:
            config_path = os.path.join(self.plugin_dir, "configs.json")
            with open(config_path, 'w') as f:
                json.dump(self.plugin_configs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin configs: {e}")
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """Execute all callbacks for a hook"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook callback failed: {e}")
    
    def _register_plugin_hooks(self, plugin_name: str, plugin: Plugin):
        """Register plugin hooks"""
        # Check if plugin has hook methods
        for method_name in dir(plugin):
            if method_name.startswith('hook_'):
                hook_name = method_name[5:]  # Remove 'hook_' prefix
                callback = getattr(plugin, method_name)
                if callable(callback):
                    self.register_hook(hook_name, callback)
    
    def _unregister_plugin_hooks(self, plugin_name: str):
        """Unregister plugin hooks"""
        # Remove all hooks from this plugin
        hooks_to_remove = []
        for hook_name, callbacks in self.hooks.items():
            self.hooks[hook_name] = [
                callback for callback in callbacks
                if not hasattr(callback, '__self__') or 
                callback.__self__.__class__.__name__ != plugin_name
            ]
            
            if not self.hooks[hook_name]:
                hooks_to_remove.append(hook_name)
        
        for hook_name in hooks_to_remove:
            del self.hooks[hook_name]

# Global plugin manager instance
plugin_manager = PluginManager()

# Example plugin implementations
class CSVConnectorPlugin(DataConnectorPlugin):
    """Example CSV data connector plugin"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="csv_connector",
            version="1.0.0",
            description="CSV file data connector",
            author="Argus Team",
            plugin_type=PluginType.DATA_CONNECTOR,
            dependencies=[],
            config_schema={
                "file_path": {"type": str, "required": True},
                "delimiter": {"type": str, "required": False, "default": ","},
                "encoding": {"type": str, "required": False, "default": "utf-8"}
            },
            entry_point="csv_connector"
        )
    
    def initialize(self) -> bool:
        return True
    
    def cleanup(self) -> bool:
        return True
    
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        self.file_path = connection_params['file_path']
        self.delimiter = connection_params.get('delimiter', ',')
        self.encoding = connection_params.get('encoding', 'utf-8')
        return os.path.exists(self.file_path)
    
    def disconnect(self) -> bool:
        return True
    
    def test_connection(self) -> bool:
        return os.path.exists(self.file_path)
    
    def get_schema(self) -> Dict[str, Any]:
        import pandas as pd
        try:
            df = pd.read_csv(self.file_path, nrows=1)
            return {
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def extract_data(self, query: Optional[str] = None, 
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        import pandas as pd
        try:
            df = pd.read_csv(self.file_path, delimiter=self.delimiter, encoding=self.encoding)
            if limit:
                df = df.head(limit)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to extract CSV data: {e}")
            return []

class CentralityAnalyticsPlugin(AnalyticsPlugin):
    """Example centrality analytics plugin"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="centrality_analytics",
            version="1.0.0",
            description="Network centrality analysis",
            author="Argus Team",
            plugin_type=PluginType.ANALYTICS,
            dependencies=["networkx"],
            config_schema={},
            entry_point="centrality_analytics"
        )
    
    def initialize(self) -> bool:
        return True
    
    def cleanup(self) -> bool:
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        import networkx as nx
        
        graph = data.get('graph')
        if not graph or not isinstance(graph, nx.Graph):
            return {"error": "Invalid graph data"}
        
        results = {}
        
        # Calculate centrality measures
        results['degree_centrality'] = nx.degree_centrality(graph)
        results['betweenness_centrality'] = nx.betweenness_centrality(graph)
        results['closeness_centrality'] = nx.closeness_centrality(graph)
        results['eigenvector_centrality'] = nx.eigenvector_centrality(graph)
        
        # Find most central nodes
        if results['degree_centrality']:
            most_central = max(results['degree_centrality'].items(), key=lambda x: x[1])
            results['most_central_node'] = {
                'node': most_central[0],
                'centrality_score': most_central[1]
            }
        
        return results
    
    def get_supported_data_types(self) -> List[str]:
        return ["networkx_graph", "graph_data"]
