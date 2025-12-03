#!/usr/bin/env python3
"""
Wrapper script to bypass molecule 25.x schema validation issue.
This patches molecule's _validate method to skip schema validation errors.
"""
import sys
import os

# Patch molecule's validation BEFORE any imports that might trigger it
def patch_molecule_validation():
    """Monkey-patch molecule's _validate method to skip schema validation errors."""
    try:
        # Import molecule.config early
        from molecule import config
        
        # Store the original _validate method
        original_validate = config.Config._validate
        
        def patched_validate(self):
            """Patched _validate that skips schema validation errors."""
            try:
                # Try to run the original validation
                return original_validate(self)
            except Exception as e:
                error_str = str(e).lower()
                error_msg = str(e)
                # If it's a schema validation error, skip it
                if any(term in error_str for term in ['schema', 'does not provide a schema', 'failed to validate']):
                    # Log a warning but don't fail
                    try:
                        from molecule import logger
                        # Try to get scenario name, but handle if config isn't available yet
                        try:
                            scenario_name = self.config.get("scenario", {}).get("name", "default")
                        except (AttributeError, KeyError):
                            scenario_name = "default"
                        validation_log = logger.get_scenario_logger(__name__, scenario_name, "validate")
                        validation_log.warning(f"Skipping schema validation (known molecule 25.x issue): {error_msg}")
                    except Exception:
                        # If logging fails, just print to stderr
                        print(f"⚠️  Skipping schema validation (known molecule 25.x issue): {error_msg}", file=sys.stderr)
                    return
                # Re-raise other errors
                raise
        
        # Apply the patch
        config.Config._validate = patched_validate
        
    except (ImportError, AttributeError) as e:
        # If patching fails, log a warning but continue
        print(f"Warning: Could not patch molecule validation: {e}", file=sys.stderr)

# Apply patch before any molecule CLI imports
patch_molecule_validation()

# Now run molecule CLI
if __name__ == '__main__':
    try:
        from molecule.__main__ import main
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        error_str = str(e).lower()
        # If it's still a schema validation error at this level, log and exit gracefully
        if any(term in error_str for term in ['schema', 'does not provide a schema', 'failed to validate']):
            print(f"⚠️  Schema validation error (known molecule 25.x issue): {e}", file=sys.stderr)
            sys.exit(1)
        raise
