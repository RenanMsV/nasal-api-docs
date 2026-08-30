# Copyright (C) 2012 Adrian Musceac
# Copyright (C) 2019-2026 RenanMsV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for the TypeInferenceEngine."""

from nasal_api_docs.type_inference import (
    TYPE_SCALAR,
    TYPE_BOOL,
    TYPE_NIL,
    TYPE_VECTOR,
    TYPE_HASH,
    TYPE_FUNC,
    TYPE_NODE,
    TYPE_VOID,
    TYPE_UNKNOWN,
    infer_return_type,
    infer_arg_types,
)


def test_empty_comments():
    """No comments should yield unknown."""
    assert infer_return_type([]) == TYPE_UNKNOWN


def test_comments_with_no_hints():
    """Comments without type hints should yield unknown."""
    comments = [
        "This module provide basic functions",
        "helper functions",
        "==============================================================================",
    ]
    assert infer_return_type(comments) == TYPE_UNKNOWN


# --- Void indicators ---

def test_destructor():
    """'class destructor' should infer void."""
    assert infer_return_type(["class destructor"]) == TYPE_VOID


def test_arrow_set():
    """'-> set' should infer void."""
    assert infer_return_type(["door.enable(bool) ->  set ./enabled"]) == TYPE_VOID


def test_arrow_move():
    """'-> move' should infer void."""
    assert infer_return_type(["door.close() ->  move to closed state"]) == TYPE_VOID


def test_arrow_destroy():
    """'-> destroy' should infer void."""
    assert infer_return_type(["something -> destroy the object"]) == TYPE_VOID


def test_removelistener():
    """'removelistener' should infer void."""
    assert infer_return_type(["removelistener(me.switchL)"]) == TYPE_VOID


# --- Scalar ---

def test_arrow_return_double():
    """'-> return ... double' should infer scalar."""
    assert infer_return_type([
        "double door.getpos() ->  return current position as double",
    ]) == TYPE_SCALAR


def test_returns_double():
    """'returns a double' should infer scalar."""
    assert infer_return_type(["returns a double"]) == TYPE_SCALAR


def test_returns_number():
    """'returns a number' should infer scalar."""
    assert infer_return_type(["returns a number"]) == TYPE_SCALAR


def test_returns_elevation():
    """'returns elevation' should infer scalar."""
    assert infer_return_type(["returns elevation in meter"]) == TYPE_SCALAR


def test_returns_distance():
    """'returns distance' should infer scalar."""
    assert infer_return_type(["returns distance in m"]) == TYPE_SCALAR


def test_returns_speed():
    """'returns speed' should infer scalar."""
    assert infer_return_type(["returns speed [kt]"]) == TYPE_SCALAR


def test_returns_string():
    """'returns a string' should infer scalar (strings are scalar in Nasal)."""
    assert infer_return_type(["returns a string"]) == TYPE_SCALAR


def test_returns_path():
    """'returns a path' should infer scalar."""
    assert infer_return_type(["returns tile path string"]) == TYPE_SCALAR


def test_returns_angle():
    """'returns an angle' should infer scalar."""
    assert infer_return_type(["returns angle normalized"]) == TYPE_SCALAR


# --- Bool ---

def test_returns_bool():
    """'returns a bool' should infer bool."""
    assert infer_return_type(["returns a bool"]) == TYPE_BOOL


def test_returns_boolean():
    """'returns a boolean' should infer bool."""
    assert infer_return_type(["returns a boolean"]) == TYPE_BOOL


def test_returns_true_false():
    """'returns true/false' should infer bool."""
    assert infer_return_type(["returns true/false"]) == TYPE_BOOL


def test_returns_true_or_false():
    """'returns true or false' should infer bool."""
    assert infer_return_type(["returns true or false"]) == TYPE_BOOL


def test_returns_true():
    """'returns true' should infer bool."""
    assert infer_return_type(["returns true"]) == TYPE_BOOL


def test_returns_false():
    """'returns false' should infer bool."""
    assert infer_return_type(["returns false"]) == TYPE_BOOL


def test_returns_whether():
    """'returns whether' should infer bool."""
    assert infer_return_type(["returns whether coords are defined"]) == TYPE_BOOL


# --- Nil ---

def test_returns_nil():
    """'returns nil' should infer nil."""
    assert infer_return_type(["returns nil"]) == TYPE_NIL


def test_returns_nothing():
    """'returns nothing' should infer void."""
    assert infer_return_type(["returns nothing"]) == TYPE_VOID


# --- Vector ---

def test_returns_vector():
    """'returns a vector' should infer vector."""
    assert infer_return_type(["returns a vector"]) == TYPE_VECTOR


def test_returns_array():
    """'returns an array' should infer vector."""
    assert infer_return_type(["returns an array"]) == TYPE_VECTOR


def test_returns_list():
    """'returns a list' should infer vector."""
    assert infer_return_type(["returns a list"]) == TYPE_VECTOR


# --- Hash ---

def test_returns_hash():
    """'returns a hash' should infer hash."""
    assert infer_return_type(["returns a hash"]) == TYPE_HASH


def test_returns_dictionary():
    """'returns a dictionary' should infer hash."""
    assert infer_return_type(["returns a dictionary"]) == TYPE_HASH


# --- Func ---

def test_returns_func():
    """'returns a function' should infer func."""
    assert infer_return_type(["returns a function"]) == TYPE_FUNC


def test_returns_callback():
    """'returns a callback' should infer func."""
    assert infer_return_type(["returns a callback"]) == TYPE_FUNC


# --- Node ---

def test_returns_node():
    """'returns a node' should infer node."""
    assert infer_return_type(["returns a node"]) == TYPE_NODE


def test_returns_property_node():
    """'returns a property node' should infer node."""
    assert infer_return_type(["returns a property node"]) == TYPE_NODE


# --- Arrow return patterns ---

def test_arrow_return_as_scalar():
    """'-> return ... as scalar' should infer scalar."""
    assert infer_return_type(["-> return current position as double"]) == TYPE_SCALAR


def test_arrow_return_nil():
    """'-> return nil' should infer nil."""
    assert infer_return_type(["-> return nil"]) == TYPE_NIL


# --- Unknown fallback ---

def test_generic_comment_unknown():
    """Generic comments without type info should yield unknown."""
    assert infer_return_type(["helper functions"]) == TYPE_UNKNOWN


def test_mixed_comments_unknown():
    """Mixed comments without type hints should yield unknown."""
    assert infer_return_type([
        "This is a comment first line",
        "This is a comment third line",
    ]) == TYPE_UNKNOWN


# --- Arg type inference ---

def test_arg_types_empty_comments():
    """No comments should yield empty arg_types."""
    assert infer_arg_types([], ["a", "b"]) == ["", ""]


def test_arg_types_empty_args():
    """Empty args should yield empty list."""
    assert infer_arg_types(["some comment"], []) == []


def test_arg_types_inline_signature():
    """Inline signature like 'func_name(type)' should infer types."""
    comments = ["door.enable(bool)"]
    args = ["enabled"]
    assert infer_arg_types(comments, args) == [TYPE_BOOL]


def test_arg_types_inline_signature_multiple():
    """Inline signature with multiple types."""
    comments = ["func_name(scalar, hash)"]
    args = ["a", "b"]
    assert infer_arg_types(comments, args) == [TYPE_SCALAR, TYPE_HASH]


def test_arg_types_synopsis_angle_brackets():
    """SYNOPSIS '<type>' should infer types."""
    comments = ["Synopsis: <vector> <hash>"]
    args = ["a", "b"]
    assert infer_arg_types(comments, args) == [TYPE_VECTOR, TYPE_HASH]


def test_arg_types_synopsis_mixed():
    """SYNOPSIS with mapped and unmapped types."""
    comments = ["Synopsis: <scalar> <unknown_type>"]
    args = ["a", "b"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_SCALAR
    assert result[1] == "unknown_type"


def test_arg_types_description_pattern():
    """Description pattern 'param ... type' should infer types."""
    comments = ["n ... scalar anotherArgument ... hash"]
    args = ["n", "anotherArgument"]
    assert infer_arg_types(comments, args) == [TYPE_SCALAR, TYPE_HASH]


def test_arg_types_description_keyword():
    """Description with type keyword near param name."""
    comments = ["n ... vector"]
    args = ["n"]
    assert infer_arg_types(comments, args) == [TYPE_VECTOR]


def test_arg_types_default_value_scalar():
    """Default value hint should infer scalar."""
    comments = ["some comment"]
    args = ["count = 0"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_SCALAR


def test_arg_types_default_value_nil():
    """Default value hint should infer nil."""
    comments = ["some comment"]
    args = ["opt = nil"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_NIL


def test_arg_types_default_value_bool():
    """Default value hint should infer bool."""
    comments = ["some comment"]
    args = ["flag = true"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_BOOL


def test_arg_types_default_value_hash():
    """Default value hint should infer hash."""
    comments = ["some comment"]
    args = ["opts = {}"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_HASH


def test_arg_types_default_value_vector():
    """Default value hint should infer vector."""
    comments = ["some comment"]
    args = ["items = []"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_VECTOR


def test_arg_types_no_matches_empty():
    """No matching patterns should yield empty strings."""
    comments = ["just a generic comment with no type hints"]
    args = ["a", "b"]
    assert infer_arg_types(comments, args) == ["", ""]


def test_arg_types_all_strategies():
    """When inline signature provides all types, stop there."""
    comments = ["func(scalar, bool) some other text <hash>"]
    args = ["a", "b"]
    assert infer_arg_types(comments, args) == [TYPE_SCALAR, TYPE_BOOL]


def test_arg_types_partial_match():
    """Partial matches should leave remaining as empty string."""
    comments = ["func(scalar)"]
    args = ["a", "b"]
    result = infer_arg_types(comments, args)
    assert result[0] == TYPE_SCALAR
    assert result[1] == ""