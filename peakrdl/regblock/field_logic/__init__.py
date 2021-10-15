import math
from typing import TYPE_CHECKING, List

from systemrdl.node import Node, AddressableNode, RegNode, FieldNode, RegfileNode

if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class FieldLogic:
    def __init__(self, exporter:'RegblockExporter', top_node:Node):
        self.exporter = exporter
        self.top_node = top_node

        self._indent_level = 0

    def get_storage_struct(self) -> str:
        lines = []
        self._do_struct(lines, self.top_node, is_top=True)

        # Only declare the storage struct if it exists
        if lines:
            lines.append(f"{self._indent}field_storage_t storage_d;")
        return "\n".join(lines)

    def get_storage_reset_implementation(self) -> str:
        lines = []
        self.emit_reset_values(lines, self.top_node)
        return "\n".join(lines)

    def get_storage_next_state_implementation(self) -> str:
        lines = []
        self.emit_storage(lines, self.top_node)
        return "\n".join(lines)

    def assign_default_nextstate(self) -> str:
        lines = []
        self.emit_default_nextstate(lines, self.top_node)
        return "\n".join(lines)

    def get_write_demux(self, addr_to_reg_map, cpuif_wr_data) -> str:
        lines = []
        self.emit_case_demux(lines, self.top_node, addr_to_reg_map, cpuif_wr_data)
        return "\n".join(lines)

    def clear_pulses(self, addr_to_reg_map) -> str:
        lines = []
        self.emit_clear_pulses(lines, self.top_node, addr_to_reg_map)
        return "\n".join(lines)



    #---------------------------------------------------------------------------
    # Field utility functions
    #---------------------------------------------------------------------------
    def get_storage_identifier(self, obj: FieldNode):
        assert obj.implements_storage

        return "TODO: implement get_storage_identifier()"


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

    def _do_struct(self, lines:List[str], node:AddressableNode, is_top:bool = False) -> bool:
        # Collect struct members first
        contents = []
        self._indent_level += 1
        for child in node.children():
            if isinstance(child, RegNode):
                self._do_reg_struct(contents, child)
            elif isinstance(child, AddressableNode):
                self._do_struct(contents, child)
        self._indent_level -= 1

        # If struct is not empty, emit a struct!
        if contents:
            if is_top:
                lines.append(f"{self._indent}typedef struct {{")
            else:
                lines.append(f"{self._indent}struct {{")

            lines.extend(contents)

            if is_top:
                lines.append(f"{self._indent}}} field_storage_t;")
            else:
                lines.append(f"{self._indent}}} {node.inst_name}{self._get_node_array_suffix(node)};")

    def emit_reset_values(self, lines:List[str], node:AddressableNode):
        for child in node.children(unroll=True):
            if isinstance(child, RegNode):
                for field in child.fields():
                    if(field.implements_storage):
                        hier = field.get_path()
                        tokens = hier.split(".")
                        tokens[0] = "hwif_out"
                        tokens.append("value")
                        storage_elem = ".".join(tokens)
                        lines.append(f"{self._indent}{storage_elem} <= {field.get_property('reset')};" )

            elif isinstance(child, RegfileNode):
                self.emit_reset_values(lines, child)


    def emit_storage(self, lines:List[str], node:AddressableNode):
        for child in node.children(unroll=True):
            if isinstance(child, RegNode):
                for field in child.fields():
                    if(field.implements_storage):
                        hier = field.get_path()
                        storage_tokens = hier.split(".")
                        d_tokens = hier.split(".")
                        storage_tokens[0] = "hwif_out"
                        d_tokens[0] = "storage_d"
                        storage_tokens.append("value")
                        storage_elem = ".".join(storage_tokens)
                        d_elem = ".".join(d_tokens)
                        lines.append(f"{self._indent}{storage_elem} <= {d_elem};" )
            elif isinstance(child, RegfileNode):
                self.emit_storage(lines, child)

    def emit_default_nextstate(self, lines:List[str], node:AddressableNode):
        for child in node.children(unroll=True):
            if isinstance(child, RegNode):
                for field in child.fields():
                    if(field.implements_storage):
                        hier = field.get_path()
                        storage_tokens = hier.split(".")
                        d_tokens = hier.split(".")
                        storage_tokens[0] = "hwif_out"
                        d_tokens[0] = "storage_d"
                        storage_elem = ".".join(storage_tokens)
                        d_elem = ".".join(d_tokens)

                        if(field.get_property("singlepulse")):
                            lines.append(f"{self._indent}{d_elem} = '0 //clear after pulse" )
                        else:
                            lines.append(f"{self._indent}{d_elem} = {storage_elem} //retain state" )
            elif isinstance(child, RegfileNode):
                self.emit_default_nextstate(lines, child)





    def emit_case_demux(self, lines:List[str], node:AddressableNode, addr_to_reg_map, cpuif_wr_data):

        #is this guaranteed to be ordered
        for key in addr_to_reg_map:
            li = addr_to_reg_map[key]
            for elem in li:
                if not elem.has_sw_writable:
                    continue

                self._indent_level += 1
                lines.append(f"{self._indent}'d{key}:")
                for field in elem.fields():
                    if(field.is_sw_writable and field.implements_storage):
                        hier =  field.get_path()
                        tokens = hier.split(".")
                        tokens[0] = "storage_d"
                        storage_elem = ".".join(tokens)

                        self._indent_level += 1
                        lines.append(f"{self._indent}{storage_elem} = {cpuif_wr_data}[{field.high}:{field.low}]")
                        self._indent_level -= 1

                self._indent_level -= 1





    def _do_reg_struct(self, lines:List[str], node:RegNode) -> None:

        fields = []
        for field in node.fields():
            if field.implements_storage:
                fields.append(field)

        if not fields:
            return

        lines.append(f"{self._indent}struct {{")
        self._indent_level += 1
        for field in fields:
            if field.width == 1:
                lines.append(f"{self._indent}logic {field.inst_name};")
            else:
                lines.append(f"{self._indent}logic [{field.width-1}:0] {field.inst_name};")
        self._indent_level -= 1
        lines.append(f"{self._indent}}} {node.inst_name}{self._get_node_array_suffix(node)};")
