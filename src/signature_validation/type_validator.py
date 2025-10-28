#!/usr/bin/env python3
"""
Type Validation Logic

WHY: Centralized type compatibility and hint extraction
RESPONSIBILITY: Handle all type checking and type hint parsing
PATTERNS: Strategy pattern for type inference, dispatch tables for AST parsing
"""

import ast
from typing import Optional, Dict, Callable


class TypeChecker:
    """
    Helper class for type checking

    WHY: Centralizes type compatibility checking logic
    RESPONSIBILITY: Type compatibility validation and hint extraction
    PATTERNS: Strategy pattern, dispatch table pattern
    """

    # Built-in type compatibility mappings
    TYPE_COMPATIBILITY: Dict[str, set] = {
        'int': {'int', 'float', 'complex', 'bool'},
        'float': {'float', 'complex'},
        'str': {'str'},
        'bool': {'bool', 'int'},
        'list': {'list', 'List'},
        'dict': {'dict', 'Dict'},
        'tuple': {'tuple', 'Tuple'},
        'set': {'set', 'Set'},
    }

    @classmethod
    def are_types_compatible(cls, expected: str, actual: str) -> bool:
        """
        Check if two types are compatible

        WHY: Handles type compatibility including subtype relationships
        RESPONSIBILITY: Determine type compatibility
        PATTERNS: Guard clauses for early returns

        Args:
            expected: Expected type string
            actual: Actual type string

        Returns:
            True if types are compatible
        """
        # Guard clause: no type hints means no validation needed
        if not expected or not actual:
            return True

        # Guard clause: exact match
        if expected == actual:
            return True

        # Check compatibility map
        if expected in cls.TYPE_COMPATIBILITY:
            return actual in cls.TYPE_COMPATIBILITY[expected]

        # Handle Optional types
        if 'Optional[' in expected:
            inner_type = expected.replace('Optional[', '').replace(']', '')
            if actual == 'None' or cls.are_types_compatible(inner_type, actual):
                return True

        # Handle Union types
        if 'Union[' in expected:
            types = expected.replace('Union[', '').replace(']', '').split(',')
            types = [t.strip() for t in types]
            return any(cls.are_types_compatible(t, actual) for t in types)

        return False

    @classmethod
    def extract_type_from_annotation(cls, annotation: ast.AST) -> Optional[str]:
        """
        Extract type string from AST annotation node

        WHY: Converts AST annotation nodes to readable type strings
        RESPONSIBILITY: Parse AST type annotations
        PATTERNS: Dispatch table pattern for type extraction

        Args:
            annotation: AST annotation node

        Returns:
            Type string or None if extraction fails
        """
        # Guard clause: early return for None
        if annotation is None:
            return None

        # Dictionary dispatch pattern for type extraction
        type_extractors: Dict[type, Callable[[ast.AST], Optional[str]]] = {
            ast.Name: lambda node: node.id,
            ast.Constant: lambda node: str(node.value),
            ast.Subscript: cls._extract_subscript_type,
            ast.Tuple: cls._extract_tuple_type,
            ast.Attribute: lambda node: node.attr,
        }

        for node_type, extractor in type_extractors.items():
            if isinstance(annotation, node_type):
                return extractor(annotation)

        return None

    @classmethod
    def _extract_subscript_type(cls, annotation: ast.Subscript) -> Optional[str]:
        """
        Extract type from subscript annotation (e.g., List[int])

        WHY: Handle generic type annotations
        RESPONSIBILITY: Parse subscripted types
        PATTERNS: Recursive extraction

        Args:
            annotation: Subscript AST node

        Returns:
            Formatted type string
        """
        value = cls.extract_type_from_annotation(annotation.value)
        slice_type = cls.extract_type_from_annotation(annotation.slice)
        return f"{value}[{slice_type}]" if slice_type else value

    @classmethod
    def _extract_tuple_type(cls, annotation: ast.Tuple) -> str:
        """
        Extract type from tuple annotation (e.g., Union[int, str])

        WHY: Handle Union and tuple type annotations
        RESPONSIBILITY: Parse tuple types
        PATTERNS: List comprehension with filtering

        Args:
            annotation: Tuple AST node

        Returns:
            Comma-separated type string
        """
        types = [cls.extract_type_from_annotation(elt) for elt in annotation.elts]
        return ', '.join(t for t in types if t)


class TypeInferrer:
    """
    Infer types from AST nodes

    WHY: Best-effort static type inference for validation
    RESPONSIBILITY: Determine types from AST expressions
    PATTERNS: Strategy pattern with dispatch table
    """

    def __init__(self, function_info: Dict[str, 'FunctionInfo']):
        """
        Initialize type inferrer

        Args:
            function_info: Dictionary of function metadata
        """
        self.function_info = function_info

    def infer_type_from_node(self, node: ast.AST) -> str:
        """
        Infer type from AST node

        WHY: Best-effort static type inference for validation
        RESPONSIBILITY: Map AST nodes to type strings
        PATTERNS: Dispatch table pattern

        Args:
            node: AST node to analyze

        Returns:
            Inferred type string
        """
        # Dictionary dispatch pattern for type inference
        type_inferrers: Dict[type, Callable[[ast.AST], str]] = {
            ast.Constant: self._infer_constant_type,
            ast.Num: self._infer_num_type,
            ast.Str: lambda _: 'str',
            ast.List: lambda _: 'list',
            ast.Dict: lambda _: 'dict',
            ast.Tuple: lambda _: 'tuple',
            ast.Set: lambda _: 'set',
            ast.Call: self._infer_call_type,
        }

        for node_type, inferrer in type_inferrers.items():
            if isinstance(node, node_type):
                return inferrer(node)

        return 'Unknown'

    def _infer_constant_type(self, node: ast.Constant) -> str:
        """Infer type from Constant node (Python 3.8+)"""
        return type(node.value).__name__

    def _infer_num_type(self, node: ast.Num) -> str:
        """Infer type from Num node (older Python versions)"""
        return 'int' if isinstance(node.n, int) else 'float'

    def _infer_call_type(self, node: ast.Call) -> str:
        """
        Infer type from function call

        WHY: Track return types through function calls
        RESPONSIBILITY: Determine call expression types
        PATTERNS: Guard clauses

        Args:
            node: Call AST node

        Returns:
            Inferred return type
        """
        func_name = self._get_function_name(node.func)

        # Guard clause: unknown function
        if not func_name:
            return 'Unknown'

        # Check if it's a type constructor
        if func_name in {'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple', 'set'}:
            return func_name

        # Check if we have return type info
        if func_name in self.function_info:
            return self.function_info[func_name].return_type or 'Unknown'

        return 'Unknown'

    def _get_function_name(self, func_node: ast.AST) -> Optional[str]:
        """
        Extract function name from call node

        WHY: Get callable identifier for type lookup
        RESPONSIBILITY: Parse function names from AST
        PATTERNS: Dispatch table pattern

        Args:
            func_node: Function AST node

        Returns:
            Function name or None
        """
        # Dictionary dispatch pattern for function name extraction
        name_extractors: Dict[type, Callable[[ast.AST], str]] = {
            ast.Name: lambda node: node.id,
            ast.Attribute: lambda node: node.attr,
        }

        for node_type, extractor in name_extractors.items():
            if isinstance(func_node, node_type):
                return extractor(func_node)

        return None
