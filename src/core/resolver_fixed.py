def __init__(self, config: Optional[ResolutionConfig] = None):
        if not DEPENDENCIES_AVAILABLE:
            raise EntityResolutionError(f"Missing dependencies: {MISSING_DEPS}")
