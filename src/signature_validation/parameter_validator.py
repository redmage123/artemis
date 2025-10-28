#!/usr/bin/env python3
"""
Parameter Validation Logic

WHY: Validates function call arguments against signatures
RESPONSIBILITY: Check parameter counts, types, and keyword arguments
PATTERNS: Strategy pattern for validation, guard clauses for early returns
"""

import ast
from typing import List, Dict, Optional
from signature_validation.models import SignatureIssue, FunctionInfo
from signature_validation.type_validator import TypeChecker, TypeInferrer


class ParameterValidator:
    """
    Validates function call parameters

    WHY: Comprehensive parameter validation including counts and types
    RESPONSIBILITY: Validate all aspects of function calls
    PATTERNS: Strategy pattern, guard clauses
    """

    def __init__(self, function_info: Dict[str, FunctionInfo], verbose: bool = False):
        """
        Initialize parameter validator

        Args:
            function_info: Dictionary of function metadata
            verbose: Enable verbose output
        """
        self.function_info = function_info
        self.verbose = verbose
        self.type_checker = TypeChecker()
        self.type_inferrer = TypeInferrer(function_info)
        self.issues: List[SignatureIssue] = []

    def validate_call(
        self,
        call_node: ast.Call,
        file_path: str
    ) -> List[SignatureIssue]:
        """
        Validate a single function call

        WHY: Check parameter counts, types, and keyword arguments
        RESPONSIBILITY: Orchestrate all call validation checks
        PATTERNS: Guard clauses for early returns

        Args:
            call_node: Function call AST node
            file_path: Path to source file

        Returns:
            List of validation issues
        """
        self.issues = []

        # Get function name
        func_name = self._get_function_name(call_node.func)

        # Guard clause: function not defined in this file
        if not func_name or func_name not in self.function_info:
            return self.issues

        func_info = self.function_info[func_name]

        # Count positional arguments
        num_positional = len(call_node.args)

        # Extract keyword arguments
        kwarg_dict = {kw.arg: kw.value for kw in call_node.keywords if kw.arg}

        # Check if call has **kwargs
        has_star_kwargs = any(kw.arg is None for kw in call_node.keywords)

        # Validate based on function signature
        if func_info.has_varkw or has_star_kwargs:
            # Only validate types for dynamic calls
            self._validate_argument_types(
                call_node, func_info, file_path, num_positional, kwarg_dict
            )
        else:
            # Full validation for static calls
            self._validate_argument_count(
                call_node, func_info, file_path, func_name, num_positional
            )
            self._validate_required_arguments(
                call_node, func_info, file_path, func_name, num_positional, kwarg_dict
            )
            self._validate_keyword_arguments(
                call_node, func_info, file_path, func_name, kwarg_dict
            )
            self._validate_argument_types(
                call_node, func_info, file_path, num_positional, kwarg_dict
            )

        return self.issues

    def _validate_argument_count(
        self,
        call_node: ast.Call,
        func_info: FunctionInfo,
        file_path: str,
        func_name: str,
        num_positional: int
    ) -> None:
        """
        Validate number of positional arguments

        WHY: Detect too many arguments errors
        RESPONSIBILITY: Check positional argument count
        PATTERNS: Guard clause for early return

        Args:
            call_node: Function call node
            func_info: Function metadata
            file_path: Source file path
            func_name: Function name
            num_positional: Number of positional args provided
        """
        # Guard clause: function accepts *args
        if func_info.has_varargs:
            return

        # Guard clause: argument count is valid
        if num_positional <= len(func_info.args):
            return

        self.issues.append(SignatureIssue(
            file_path=file_path,
            line_number=call_node.lineno,
            function_name=func_name,
            issue_type='too_many_args',
            message=f"Too many arguments to {func_name}(): expected {len(func_info.args)}, got {num_positional}",
            severity='critical',
            suggestion=f"Remove {num_positional - len(func_info.args)} argument(s)"
        ))

    def _validate_required_arguments(
        self,
        call_node: ast.Call,
        func_info: FunctionInfo,
        file_path: str,
        func_name: str,
        num_positional: int,
        kwarg_dict: Dict[str, ast.AST]
    ) -> None:
        """
        Validate all required arguments are provided

        WHY: Detect missing required arguments
        RESPONSIBILITY: Check for missing required parameters
        PATTERNS: Set operations for efficient comparison

        Args:
            call_node: Function call node
            func_info: Function metadata
            file_path: Source file path
            func_name: Function name
            num_positional: Number of positional args provided
            kwarg_dict: Dictionary of keyword arguments
        """
        num_defaults = len(func_info.defaults)
        num_required = len(func_info.args) - num_defaults

        # Calculate provided and required arguments
        provided_args = set(func_info.args[:num_positional]) | set(kwarg_dict.keys())
        required_args = set(func_info.args[:num_required])
        missing_args = required_args - provided_args

        # Guard clause: all required arguments provided
        if not missing_args:
            return

        self.issues.append(SignatureIssue(
            file_path=file_path,
            line_number=call_node.lineno,
            function_name=func_name,
            issue_type='missing_required',
            message=f"Missing required arguments to {func_name}(): {', '.join(sorted(missing_args))}",
            severity='critical',
            suggestion=f"Add missing arguments: {', '.join(sorted(missing_args))}"
        ))

    def _validate_keyword_arguments(
        self,
        call_node: ast.Call,
        func_info: FunctionInfo,
        file_path: str,
        func_name: str,
        kwarg_dict: Dict[str, ast.AST]
    ) -> None:
        """
        Validate keyword arguments are recognized

        WHY: Detect unknown keyword arguments
        RESPONSIBILITY: Check for invalid keyword parameters
        PATTERNS: Set operations for efficient comparison

        Args:
            call_node: Function call node
            func_info: Function metadata
            file_path: Source file path
            func_name: Function name
            kwarg_dict: Dictionary of keyword arguments
        """
        all_valid_kwargs = set(func_info.args) | set(func_info.kwonly)
        unknown_kwargs = set(kwarg_dict.keys()) - all_valid_kwargs

        # Guard clause: all kwargs are valid
        if not unknown_kwargs:
            return

        self.issues.append(SignatureIssue(
            file_path=file_path,
            line_number=call_node.lineno,
            function_name=func_name,
            issue_type='unknown_kwarg',
            message=f"Unknown keyword argument(s) to {func_name}(): {', '.join(sorted(unknown_kwargs))}",
            severity='critical',
            suggestion=f"Valid keyword arguments: {', '.join(sorted(all_valid_kwargs))}"
        ))

    def _validate_argument_types(
        self,
        call_node: ast.Call,
        func_info: FunctionInfo,
        file_path: str,
        num_positional: int,
        kwarg_dict: Dict[str, ast.AST]
    ) -> None:
        """
        Validate argument types against type hints

        WHY: Catch type mismatches before runtime
        RESPONSIBILITY: Check all argument types
        PATTERNS: Separate validation for positional and keyword args

        Args:
            call_node: Function call node
            func_info: Function metadata
            file_path: Source file path
            num_positional: Number of positional args
            kwarg_dict: Dictionary of keyword arguments
        """
        # Validate positional argument types
        self._validate_positional_types(
            call_node, func_info, file_path, num_positional
        )

        # Validate keyword argument types
        self._validate_keyword_types(
            call_node, func_info, file_path, kwarg_dict
        )

    def _validate_positional_types(
        self,
        call_node: ast.Call,
        func_info: FunctionInfo,
        file_path: str,
        num_positional: int
    ) -> None:
        """
        Validate positional argument types

        WHY: Type checking for positional parameters
        RESPONSIBILITY: Check positional argument types
        PATTERNS: Guard clauses for early returns

        Args:
            call_node: Function call node
            func_info: Function metadata
            file_path: Source file path
            num_positional: Number of positional args
        """
        for i, arg_node in enumerate(call_node.args):
            # Guard clause: beyond function parameters
            if i >= len(func_info.args):
                break

            param_name = func_info.args[i]
            expected_type = func_info.arg_types.get(param_name)

            # Guard clause: no type hint
            if not expected_type:
                continue

            actual_type = self.type_inferrer.infer_type_from_node(arg_node)

            # Guard clause: types are compatible
            if self.type_checker.are_types_compatible(expected_type, actual_type):
                continue

            self.issues.append(SignatureIssue(
                file_path=file_path,
                line_number=call_node.lineno,
                function_name=func_info.name,
                issue_type='type_mismatch',
                message=f"Type mismatch for argument '{param_name}' in {func_info.name}(): expected {expected_type}, got {actual_type}",
                severity='warning',
                suggestion=f"Convert to {expected_type} or update type hint"
            ))

    def _validate_keyword_types(
        self,
        call_node: ast.Call,
        func_info: FunctionInfo,
        file_path: str,
        kwarg_dict: Dict[str, ast.AST]
    ) -> None:
        """
        Validate keyword argument types

        WHY: Type checking for keyword parameters
        RESPONSIBILITY: Check keyword argument types
        PATTERNS: Guard clauses for early returns

        Args:
            call_node: Function call node
            func_info: Function metadata
            file_path: Source file path
            kwarg_dict: Dictionary of keyword arguments
        """
        for kwarg_name, kwarg_value in kwarg_dict.items():
            expected_type = func_info.arg_types.get(kwarg_name)

            # Guard clause: no type hint
            if not expected_type:
                continue

            actual_type = self.type_inferrer.infer_type_from_node(kwarg_value)

            # Guard clause: types are compatible
            if self.type_checker.are_types_compatible(expected_type, actual_type):
                continue

            self.issues.append(SignatureIssue(
                file_path=file_path,
                line_number=call_node.lineno,
                function_name=func_info.name,
                issue_type='type_mismatch',
                message=f"Type mismatch for keyword argument '{kwarg_name}' in {func_info.name}(): expected {expected_type}, got {actual_type}",
                severity='warning',
                suggestion=f"Convert to {expected_type} or update type hint"
            ))

    def _get_function_name(self, func_node: ast.AST) -> Optional[str]:
        """
        Extract function name from call node

        WHY: Get callable identifier for validation
        RESPONSIBILITY: Parse function names from AST
        PATTERNS: Dispatch table pattern

        Args:
            func_node: Function AST node

        Returns:
            Function name or None
        """
        # Dictionary dispatch pattern for function name extraction
        name_extractors = {
            ast.Name: lambda node: node.id,
            ast.Attribute: lambda node: node.attr,
        }

        for node_type, extractor in name_extractors.items():
            if isinstance(func_node, node_type):
                return extractor(func_node)

        return None


class ReturnTypeValidator:
    """
    Validates return types against type hints

    WHY: Ensure functions return the type they promise
    RESPONSIBILITY: Check return statement types
    PATTERNS: Strategy pattern, guard clauses
    """

    def __init__(self, function_info: Dict[str, FunctionInfo], verbose: bool = False):
        """
        Initialize return type validator

        Args:
            function_info: Dictionary of function metadata
            verbose: Enable verbose output
        """
        self.function_info = function_info
        self.verbose = verbose
        self.type_checker = TypeChecker()
        self.type_inferrer = TypeInferrer(function_info)
        self.issues: List[SignatureIssue] = []

    def validate_returns(self, file_path: str) -> List[SignatureIssue]:
        """
        Validate all return statements against type hints

        WHY: Comprehensive return type checking
        RESPONSIBILITY: Check all return statements in all functions
        PATTERNS: Iterator pattern

        Args:
            file_path: Source file path

        Returns:
            List of validation issues
        """
        self.issues = []

        for func_name, func_info in self.function_info.items():
            # Guard clause: no return type hint
            if not func_info.return_type:
                continue

            for return_node in func_info.return_nodes:
                self._validate_single_return(
                    return_node, func_name, func_info, file_path
                )

        return self.issues

    def _validate_single_return(
        self,
        return_node: ast.Return,
        func_name: str,
        func_info: FunctionInfo,
        file_path: str
    ) -> None:
        """
        Validate a single return statement against type hint

        WHY: Check individual return for type correctness
        RESPONSIBILITY: Validate one return statement
        PATTERNS: Guard clause for early returns

        Args:
            return_node: Return statement node
            func_name: Function name
            func_info: Function metadata
            file_path: Source file path
        """
        # Guard clause: return with no value
        if return_node.value is None:
            self._check_none_return(return_node, func_name, func_info, file_path)
            return

        # Handle return with value
        self._check_typed_return(return_node, func_name, func_info, file_path)

    def _check_none_return(
        self,
        return_node: ast.Return,
        func_name: str,
        func_info: FunctionInfo,
        file_path: str
    ) -> None:
        """
        Check return statement with no value

        WHY: Validate empty returns against type hints
        RESPONSIBILITY: Check None returns
        PATTERNS: Guard clause for valid returns

        Args:
            return_node: Return statement node
            func_name: Function name
            func_info: Function metadata
            file_path: Source file path
        """
        # Guard clause: None is expected
        if func_info.return_type == 'None':
            return

        self.issues.append(SignatureIssue(
            file_path=file_path,
            line_number=return_node.lineno,
            function_name=func_name,
            issue_type='return_type_mismatch',
            message=f"Function {func_name}() returns None but type hint is {func_info.return_type}",
            severity='warning',
            suggestion=f"Add return value or change type hint to None"
        ))

    def _check_typed_return(
        self,
        return_node: ast.Return,
        func_name: str,
        func_info: FunctionInfo,
        file_path: str
    ) -> None:
        """
        Check return statement with a value

        WHY: Validate typed returns against type hints
        RESPONSIBILITY: Check valued returns
        PATTERNS: Guard clause for compatible types

        Args:
            return_node: Return statement node
            func_name: Function name
            func_info: Function metadata
            file_path: Source file path
        """
        actual_type = self.type_inferrer.infer_type_from_node(return_node.value)

        # Guard clause: types are compatible
        if self.type_checker.are_types_compatible(func_info.return_type, actual_type):
            return

        self.issues.append(SignatureIssue(
            file_path=file_path,
            line_number=return_node.lineno,
            function_name=func_name,
            issue_type='return_type_mismatch',
            message=f"Return type mismatch in {func_name}(): expected {func_info.return_type}, got {actual_type}",
            severity='warning',
            suggestion=f"Convert return value to {func_info.return_type} or update return type hint"
        ))
