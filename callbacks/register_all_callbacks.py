# callbacks/register_all_callbacks.py
"""
Register All Callbacks - FIXES MISSING CALLBACK ERRORS
This ensures all callbacks are properly registered with Dash
"""

import logging
logger = logging.getLogger(__name__)

def register_all_missing_callbacks():
    """Register all callbacks that might be missing"""
    try:
        # Import and register public layout callbacks
        try:
            from layouts.public_layout_uniform import register_public_layout_callbacks
            register_public_layout_callbacks()
            logger.info("✅ Public layout callbacks registered")
        except ImportError:
            logger.warning("⚠️ Public layout callbacks not available")
        except Exception as e:
            logger.error(f"❌ Error registering public layout callbacks: {e}")
        
        # Import and register other callback modules if they exist
        callback_modules = [
            'callbacks.unified_dashboard_callbacks',
            'callbacks.public_landing_callbacks'
        ]
        
        for module_name in callback_modules:
            try:
                module = __import__(module_name, fromlist=[''])
                if hasattr(module, 'register_callbacks'):
                    module.register_callbacks()
                    logger.info(f"✅ Registered callbacks from {module_name}")
            except ImportError:
                logger.debug(f"⚠️ Module {module_name} not available")
            except Exception as e:
                logger.warning(f"⚠️ Could not register callbacks from {module_name}: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error in register_all_missing_callbacks: {e}")

# Auto-register when imported
register_all_missing_callbacks()
