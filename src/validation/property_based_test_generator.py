#!/usr/bin/env python3
"""
Property-Based Test Generator

WHY: Generate tests from code invariants to catch edge cases
RESPONSIBILITY: Analyze code, extract properties, generate hypothesis tests
PATTERNS: Strategy pattern, Guard clauses

Reduces hallucinations by:
- Testing properties that should ALWAYS hold
- Finding edge cases regular tests miss
- Verifying mathematical invariants
- Checking boundary conditions automatically
"""

import ast
import re
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass

from artemis_logger import get_logger


@dataclass
class CodeProperty:
    """
    A property that should hold for code.

    Examples:
    - "result >= 0" (non-negative output)
    - "len(result) == len(input)" (size preservation)
    - "sorted(result) == result" (sorted output)
    """
    property_type: str  # "non_negative", "size_preserving", "sorted", "bounded", "custom"
    description: str
    test_strategy: str  # hypothesis strategy name
    assertion: str  # Python assertion code


@dataclass
class PropertyTestSuite:
    """Generated property-based test suite."""
    function_name: str
    properties: List[CodeProperty]
    test_code: str
    imports_needed: Set[str]


class PropertyBasedTestGenerator:
    """
    Generate property-based tests from code.

    WHY: Property-based tests find edge cases regular tests miss
    RESPONSIBILITY: Extract invariants, generate hypothesis tests
    PATTERNS: Strategy pattern for property extraction, Guard clauses
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize property-based test generator.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger("property_based_tests")

    def generate_tests(
        self,
        code: str,
        function_name: Optional[str] = None
    ) -> List[PropertyTestSuite]:
        """
        Generate property-based tests for code.

        WHY: Main entry point for test generation
        RESPONSIBILITY: Parse code, extract properties, generate tests

        Args:
            code: Python source code
            function_name: Specific function to test (None = all functions)

        Returns:
            List of PropertyTestSuite, one per function
        """
        self.logger.info(f"Generating property-based tests for {function_name or 'all functions'}")

        # Parse code into AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.logger.error(f"Failed to parse code: {e}")
            return []

        # Extract functions
        functions = self._extract_functions(tree)

        # Guard: No functions found
        if not functions:
            self.logger.warning("No functions found in code")
            return []

        # Filter to specific function if requested
        if function_name:
            functions = [f for f in functions if f.name == function_name]

        # Guard: Function not found
        if not functions:
            self.logger.warning(f"Function '{function_name}' not found")
            return []

        # Generate tests for each function
        test_suites = []
        for func in functions:
            suite = self._generate_test_suite_for_function(func, code)
            # Guard: Skip if no properties found
            if suite and suite.properties:
                test_suites.append(suite)

        return test_suites

    def _extract_functions(self, tree: ast.AST) -> List[ast.FunctionDef]:
        """Extract function definitions from AST."""
        functions = []

        for node in ast.walk(tree):
            # Guard: Not a function definition
            if not isinstance(node, ast.FunctionDef):
                continue

            # Guard: Skip private functions (start with _)
            if node.name.startswith('_'):
                continue

            functions.append(node)

        return functions

    def _generate_test_suite_for_function(
        self,
        func: ast.FunctionDef,
        source_code: str
    ) -> Optional[PropertyTestSuite]:
        """
        Generate property test suite for a single function.

        WHY: Main logic for test generation
        RESPONSIBILITY: Extract properties, generate test code
        PATTERNS: Guard clauses for early returns
        """
        self.logger.info(f"Analyzing function: {func.name}")

        # Extract properties from function
        properties = []

        # Property 1: Check return type hints
        type_properties = self._extract_type_properties(func)
        properties.extend(type_properties)

        # Property 2: Check docstring for invariants
        docstring_properties = self._extract_docstring_properties(func)
        properties.extend(docstring_properties)

        # Property 3: Analyze return statements
        return_properties = self._analyze_return_statements(func)
        properties.extend(return_properties)

        # Guard: No properties found
        if not properties:
            self.logger.info(f"No properties found for {func.name}")
            return None

        # Generate test code
        test_code = self._generate_hypothesis_test(func, properties)

        # Determine required imports
        imports_needed = self._determine_imports(properties)

        return PropertyTestSuite(
            function_name=func.name,
            properties=properties,
            test_code=test_code,
            imports_needed=imports_needed
        )

    def _extract_type_properties(self, func: ast.FunctionDef) -> List[CodeProperty]:
        """
        Extract properties from type hints.

        WHY: Type hints specify return type constraints
        RESPONSIBILITY: Convert type hints to property tests
        PATTERNS: Guard clauses, dispatch table
        """
        properties = []

        # Guard: No return annotation
        if not func.returns:
            return properties

        # Map type to property
        type_name = self._get_type_name(func.returns)

        # Dispatch table for type → property mapping
        type_property_map = {
            'int': self._create_int_property,
            'float': self._create_float_property,
            'str': self._create_str_property,
            'list': self._create_list_property,
            'dict': self._create_dict_property,
            'bool': self._create_bool_property,
        }

        # Get property creator for this type
        creator = type_property_map.get(type_name)

        # Guard: Unknown type
        if not creator:
            return properties

        # Create property
        prop = creator(func.name)
        if prop:
            properties.append(prop)

        return properties

    def _get_type_name(self, type_node: ast.AST) -> str:
        """Extract type name from type annotation node."""
        # Guard: Simple name
        if isinstance(type_node, ast.Name):
            return type_node.id

        # Guard: Subscript (e.g., List[int])
        if isinstance(type_node, ast.Subscript):
            if isinstance(type_node.value, ast.Name):
                return type_node.value.id

        return "unknown"

    def _create_int_property(self, func_name: str) -> CodeProperty:
        """Create property for int return type."""
        return CodeProperty(
            property_type="type_check",
            description=f"{func_name} returns an integer",
            test_strategy="integers()",
            assertion=f"assert isinstance(result, int)"
        )

    def _create_float_property(self, func_name: str) -> CodeProperty:
        """Create property for float return type."""
        return CodeProperty(
            property_type="type_check",
            description=f"{func_name} returns a float",
            test_strategy="floats(allow_nan=False, allow_infinity=False)",
            assertion=f"assert isinstance(result, float)"
        )

    def _create_str_property(self, func_name: str) -> CodeProperty:
        """Create property for str return type."""
        return CodeProperty(
            property_type="type_check",
            description=f"{func_name} returns a string",
            test_strategy="text()",
            assertion=f"assert isinstance(result, str)"
        )

    def _create_list_property(self, func_name: str) -> CodeProperty:
        """Create property for list return type."""
        return CodeProperty(
            property_type="type_check",
            description=f"{func_name} returns a list",
            test_strategy="lists(integers())",
            assertion=f"assert isinstance(result, list)"
        )

    def _create_dict_property(self, func_name: str) -> CodeProperty:
        """Create property for dict return type."""
        return CodeProperty(
            property_type="type_check",
            description=f"{func_name} returns a dict",
            test_strategy="dictionaries(text(), integers())",
            assertion=f"assert isinstance(result, dict)"
        )

    def _create_bool_property(self, func_name: str) -> CodeProperty:
        """Create property for bool return type."""
        return CodeProperty(
            property_type="type_check",
            description=f"{func_name} returns a boolean",
            test_strategy="booleans()",
            assertion=f"assert isinstance(result, bool)"
        )

    def _extract_docstring_properties(self, func: ast.FunctionDef) -> List[CodeProperty]:
        """
        Extract properties from docstring.

        WHY: Docstrings often describe invariants
        RESPONSIBILITY: Parse docstring for property hints
        PATTERNS: Guard clauses, regex patterns
        """
        properties = []

        # Guard: No docstring
        docstring = ast.get_docstring(func)
        if not docstring:
            return properties

        # Look for common property patterns in docstring
        property_patterns = {
            r'returns?\s+(?:a\s+)?non-negative': ('non_negative', 'assert result >= 0'),
            r'returns?\s+(?:a\s+)?positive': ('positive', 'assert result > 0'),
            r'always\s+returns?\s+(?:a\s+)?sorted': ('sorted', 'assert result == sorted(result)'),
            r'preserves?\s+(?:the\s+)?(?:length|size)': ('size_preserving', 'assert len(result) == len(input_data)'),
            r'idempotent': ('idempotent', 'assert func(result) == result'),
        }

        for pattern, (prop_type, assertion) in property_patterns.items():
            # Guard: Pattern not found
            if not re.search(pattern, docstring, re.IGNORECASE):
                continue

            properties.append(CodeProperty(
                property_type=prop_type,
                description=f"Property from docstring: {prop_type}",
                test_strategy="integers()" if 'non_negative' in prop_type or 'positive' in prop_type else "text()",
                assertion=assertion
            ))

        return properties

    def _analyze_return_statements(self, func: ast.FunctionDef) -> List[CodeProperty]:
        """
        Analyze return statements for patterns.

        WHY: Return patterns reveal invariants
        RESPONSIBILITY: Identify common patterns (max, min, comparison)
        PATTERNS: Guard clauses, dispatch table
        """
        properties = []

        # Dispatch table for function name → property mapping
        function_property_map = {
            'max': lambda: CodeProperty(
                property_type="bounded",
                description="Returns maximum value",
                test_strategy="lists(integers(), min_size=1)",
                assertion="assert result >= min(input_data)"
            ),
            'min': lambda: CodeProperty(
                property_type="bounded",
                description="Returns minimum value",
                test_strategy="lists(integers(), min_size=1)",
                assertion="assert result <= max(input_data)"
            ),
            'sorted': lambda: CodeProperty(
                property_type="sorted",
                description="Returns sorted result",
                test_strategy="lists(integers())",
                assertion="assert result == sorted(result)"
            ),
        }

        for node in ast.walk(func):
            # Guard: Not a return statement
            if not isinstance(node, ast.Return):
                continue

            # Guard: No value returned
            if not node.value:
                continue

            # Guard: Not a function call
            if not isinstance(node.value, ast.Call):
                continue

            # Guard: Function is not a Name node
            if not isinstance(node.value.func, ast.Name):
                continue

            # Get function name
            func_name = node.value.func.id

            # Get property creator from dispatch table
            creator = function_property_map.get(func_name)

            # Guard: Function not in our pattern map
            if not creator:
                continue

            # Create and add property
            properties.append(creator())

        return properties

    def _generate_hypothesis_test(
        self,
        func: ast.FunctionDef,
        properties: List[CodeProperty]
    ) -> str:
        """
        Generate hypothesis test code.

        WHY: Convert properties to executable tests
        RESPONSIBILITY: Format test code with proper hypothesis decorators
        """
        # Build parameter strategies
        param_strategies = self._build_parameter_strategies(func)

        # Build test function
        lines = [
            f"@given({param_strategies})",
            f"def test_{func.name}_properties({self._get_param_names(func)}):",
            f'    """Property-based tests for {func.name}."""',
        ]

        # Add property assertions
        for prop in properties:
            lines.append(f"    # Property: {prop.description}")
            lines.append(f"    result = {func.name}({self._get_param_names(func)})")
            lines.append(f"    {prop.assertion}")
            lines.append("")

        return "\n".join(lines)

    def _build_parameter_strategies(self, func: ast.FunctionDef) -> str:
        """Build hypothesis strategies for function parameters."""
        strategies = []

        for arg in func.args.args:
            # Guard: Skip 'self' parameter
            if arg.arg == 'self':
                continue

            # Get strategy based on type hint or default
            strategy = self._get_strategy_for_param(arg)
            strategies.append(f"{arg.arg}={strategy}")

        return ", ".join(strategies)

    def _get_strategy_for_param(self, arg: ast.arg) -> str:
        """Get hypothesis strategy for parameter."""
        # Guard: Has type annotation
        if arg.annotation:
            type_name = self._get_type_name(arg.annotation)

            # Dispatch table for type → strategy
            type_strategy_map = {
                'int': 'integers()',
                'float': 'floats(allow_nan=False)',
                'str': 'text()',
                'list': 'lists(integers())',
                'dict': 'dictionaries(text(), integers())',
                'bool': 'booleans()',
            }

            return type_strategy_map.get(type_name, 'integers()')

        # Default to integers if no type hint
        return 'integers()'

    def _get_param_names(self, func: ast.FunctionDef) -> str:
        """Get comma-separated parameter names."""
        param_names = [arg.arg for arg in func.args.args if arg.arg != 'self']
        return ", ".join(param_names)

    def _determine_imports(self, properties: List[CodeProperty]) -> Set[str]:
        """Determine required imports for test code."""
        imports = {'from hypothesis import given, strategies as st'}

        # Check if any properties need specific imports
        for prop in properties:
            # Guard: Needs sorted
            if 'sorted' in prop.assertion:
                imports.add('# No additional imports needed for sorted')

            # Guard: Needs list operations
            if 'len(' in prop.assertion:
                imports.add('# No additional imports needed for len')

        return imports
