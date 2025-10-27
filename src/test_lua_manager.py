"""
Unit tests for Lua Manager

Tests Lua build system integration with LuaRocks, busted, luacheck, and stylua.
"""

import unittest
from pathlib import Path
from lua_manager import LuaManager
from build_manager_factory import BuildManagerFactory, BuildSystem


class TestLuaManager(unittest.TestCase):
    """Test Lua manager functionality"""

    def test_lua_manager_registered(self):
        """Verify Lua manager is registered in factory"""
        factory = BuildManagerFactory.get_instance()
        self.assertIn(BuildSystem.LUA, factory.get_registered_systems())

    def test_lua_manager_creation(self):
        """Test creating Lua manager via factory"""
        factory = BuildManagerFactory.get_instance()
        manager = factory.create(BuildSystem.LUA, project_dir="/tmp/test_lua")
        self.assertIsInstance(manager, LuaManager)

    def test_rockspec_detection(self):
        """Test rockspec file detection"""
        # Create temp project directory with rockspec
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock rockspec file
            rockspec_path = Path(tmpdir) / "myproject-1.0.rockspec"
            rockspec_path.write_text("""
package = "myproject"
version = "1.0-1"
source = {
   url = "..."
}
description = {
   summary = "Test project"
}
dependencies = {
   "lua >= 5.1"
}
build = {
   type = "builtin"
}
""")

            manager = LuaManager(tmpdir)
            self.assertTrue(manager.detect())
            self.assertIsNotNone(manager.rockspec_file)
            self.assertEqual(manager.rockspec_file.name, "myproject-1.0.rockspec")

    def test_lua_file_detection(self):
        """Test detection via .lua files"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create src directory with Lua files
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            (src_dir / "main.lua").write_text("print('hello')")

            manager = LuaManager(tmpdir)
            self.assertTrue(manager.detect())

    def test_init_lua_detection(self):
        """Test detection via init.lua"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "init.lua").write_text("return {}")

            manager = LuaManager(tmpdir)
            self.assertTrue(manager.detect())

    def test_project_info_parsing(self):
        """Test rockspec metadata parsing"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            rockspec = Path(tmpdir) / "testproj-2.0.rockspec"
            rockspec.write_text("""
package = "testproj"
version = "2.0-1"
description = {
   summary = "A test Lua project"
}
""")

            manager = LuaManager(tmpdir)
            info = manager.get_project_info()

            self.assertEqual(info["name"], "testproj")
            self.assertEqual(info["version"], "2.0-1")
            self.assertEqual(info["description"], "A test Lua project")

    def test_no_detection_empty_dir(self):
        """Test no detection in empty directory"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LuaManager(tmpdir)
            self.assertFalse(manager.detect())


if __name__ == "__main__":
    unittest.main()
