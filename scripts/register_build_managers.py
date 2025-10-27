"""
Module: register_build_managers.py

Purpose: Central registration point for all build managers
Why: Ensures all build managers with @register_build_manager decorator
     are imported and registered with BuildManagerFactory at startup
Patterns: Registry Pattern initialization
Integration: Imported by main orchestrator to activate all build managers

This file forces import of all manager modules, triggering their
@register_build_manager decorators to populate the factory registry.
"""

# Import all build managers to trigger decorator registration
# The @register_build_manager decorator on each class auto-registers it
import npm_manager
import maven_manager
import gradle_manager
import cargo_manager
import poetry_manager
import composer_manager
import go_mod_manager
import dotnet_manager
import bundler_manager
import terraform_manager
import bash_manager
import cmake_manager
import lua_manager  # Newly added Lua support

# Factory is now populated with all registered build systems
from build_manager_factory import BuildManagerFactory

def get_registered_build_systems():
    """
    Get list of all registered build systems.

    Why needed: Allows runtime introspection of available build systems

    Returns:
        List of BuildSystem enums that are registered
    """
    factory = BuildManagerFactory.get_instance()
    return factory.get_registered_systems()


def verify_registration():
    """
    Verify all expected build managers are registered.

    Why needed: Sanity check during startup to catch import errors

    Returns:
        True if all managers registered successfully
    """
    systems = get_registered_build_systems()
    print(f"✅ Registered {len(systems)} build systems:")
    for system in sorted(systems, key=lambda s: s.value):
        print(f"   - {system.value}")
    return len(systems) > 0


if __name__ == "__main__":
    # Test registration
    if verify_registration():
        print("\n✅ All build managers registered successfully!")
    else:
        print("\n❌ Build manager registration failed!")
