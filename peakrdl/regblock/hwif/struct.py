from typing import Union, List, TYPE_CHECKING

from systemrdl.node import Node, AddressableNode, FieldNode, SignalNode

from .base import HwifBase

if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class StructHwif(HwifBase):

    def __init__(self, exporter:'RegblockExporter', top_node:Node, package_name:str):
        super().__init__(exporter, top_node, package_name)

        self.has_input_struct = None
        self.has_output_struct = None
        self._indent_level = 0


    def get_package_declaration(self) -> str:
        lines = []

        lines.append(f"package {self.package_name};")
        self._indent_level += 1
        self.has_input_struct = self._do_struct_addressable(lines, self.top_node, is_input=True)
        self.has_output_struct = self._do_struct_addressable(lines, self.top_node, is_input=False)
        self._indent_level -= 1
        lines.append("")
        lines.append(f"endpackage")

        return "\n".join(lines)


    @property
    def port_declaration(self) -> str:
        """
        Returns the declaration string for all I/O ports in the hwif group
        """

        # Assume get_package_declaration() is always called prior to this
        assert self.has_input_struct is not None
        assert self.has_output_struct is not None

        lines = []
        if self.has_input_struct:
            lines.append(f"input {self.package_name}::{self._get_struct_name(self.top_node, is_input=True)} hwif_in")
        if self.has_output_struct:
            lines.append(f"output {self.package_name}::{self._get_struct_name(self.top_node, is_input=False)} hwif_out")

        return ",\n".join(lines)

    #---------------------------------------------------------------------------
    # Struct generation functions
    #---------------------------------------------------------------------------
    @property
    def _indent(self) -> str:
        return "    " * self._indent_level

    def _get_node_array_suffix(self, node:AddressableNode) -> str:
        if node.is_array:
            return "".join([f'[{dim}]' for dim in node.array_dimensions])
        return ""

    def _get_struct_name(self, node:Node, is_input:bool = True) -> str:
        base = node.get_rel_path(
            self.top_node.parent,
            hier_separator="__",
            array_suffix="x",
            empty_array_suffix="x"
        )
        if is_input:
            return f'{base}_in_t'
        return f'{base}_out_t'

    def _do_struct_addressable(self, lines:list, node:AddressableNode, is_input:bool = True) -> bool:

        struct_children = []

        # Generate structs for children first
        for child in node.children():
            if isinstance(child, AddressableNode):
                if self._do_struct_addressable(lines, child, is_input):
                    struct_children.append(child)
            elif isinstance(child, FieldNode):
                if self._do_struct_field(lines, child, is_input):
                    struct_children.append(child)
            elif is_input and isinstance(child, SignalNode):
                # No child struct needed here
                # TODO: Skip if this is a top-level child
                struct_children.append(child)

        # Generate this addressable node's struct
        if struct_children:
            lines.append("")
            lines.append(f"{self._indent}// {node.get_rel_path(self.top_node.parent)}")
            lines.append(f"{self._indent}typedef struct {{")
            self._indent_level += 1
            for child in struct_children:
                if isinstance(child, AddressableNode):
                    lines.append(f"{self._indent}{self._get_struct_name(child, is_input)} {child.inst_name}{self._get_node_array_suffix(child)};")
                elif isinstance(child, FieldNode):
                    lines.append(f"{self._indent}{self._get_struct_name(child, is_input)} {child.inst_name};")
                elif isinstance(child, SignalNode):
                    if child.width == 1:
                        lines.append(f"{self._indent}logic {child.inst_name};")
                    else:
                        lines.append(f"{self._indent}logic [{child.msb}:{child.lsb}] {child.inst_name};")

            self._indent_level -= 1
            lines.append(f"{self._indent}}} {self._get_struct_name(node, is_input)};")

        return bool(struct_children)

    def _do_struct_field(self, lines:list, node:FieldNode, is_input:bool = True) -> bool:
        contents = []

        if is_input:
            contents = self._get_struct_input_field_contents(node)
        else:
            contents = self._get_struct_output_field_contents(node)

        if contents:
            lines.append("")
            lines.append(f"{self._indent}// {node.get_rel_path(self.top_node.parent)}")
            lines.append(f"{self._indent}typedef struct {{")
            self._indent_level += 1
            for member in contents:
                lines.append(self._indent + member)
            self._indent_level -= 1
            lines.append(f"{self._indent}}} {self._get_struct_name(node, is_input)};")

        return bool(contents)

    def _get_struct_input_field_contents(self, node:FieldNode) -> List[str]:
        contents = []

        # Provide input to field's value if it is writable by hw
        if self.has_value_input(node):
            if node.width == 1:
                contents.append("logic value;")
            else:
                contents.append(f"logic [{node.width-1}:0] value;")

        # TODO:
        """
        we/wel
            if either is boolean, and true
            not part of external hwif if reference
            mutually exclusive
        hwclr/hwset
            if either is boolean, and true
            not part of external hwif if reference
        incr/decr
            if counter=true, generate BOTH
        incrvalue/decrvalue
            if either incrwidth/decrwidth are set
        signals!
            any signal instances instantiated in the scope
        """

        return contents

    def _get_struct_output_field_contents(self, node:FieldNode) -> List[str]:
        contents = []

        # Expose field's value if it is readable by hw
        if self.has_value_output(node):
            if node.width == 1:
                contents.append("logic value;")
            else:
                contents.append(f"logic [{node.width-1}:0] value;")

        # TODO:
        """
        bitwise reductions
            if anded, ored, xored == True, output a signal
        swmod/swacc
            event strobes
        Are there was_written/was_read strobes too?
        """

        return contents
