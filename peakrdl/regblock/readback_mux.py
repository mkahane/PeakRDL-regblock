import re
import math
from typing import TYPE_CHECKING, List

from systemrdl.node import Node, AddressableNode, RegNode, FieldNode, RegfileNode



if TYPE_CHECKING:
    from .exporter import RegblockExporter

class ReadbackMux:
    def __init__(self, exporter:'RegblockExporter', top_node:AddressableNode):
        self.exporter = exporter
        self.top_node = top_node

        self._indent_level = 0

    @property
    def _indent(self) -> str:
        return "    " * self._indent_level

    #TODO: This needs to handle fields that overlap addresses?
    def gen_mux_map(self, node, addr_width, data_width, addr_to_reg_map):

        for child in node.children(unroll=True):

            if isinstance(child, RegNode):
                if(child.has_sw_readable):
                    mux_address = (child.absolute_address * 8) >> (int)(math.log2(data_width))
                    if mux_address in addr_to_reg_map:
                        addr_to_reg_map[mux_address].append(child)
                    else:
                        newlist = []
                        newlist.append(child)
                        addr_to_reg_map[mux_address] = newlist

                   
            elif isinstance(child, RegfileNode):
                self.gen_mux_map(child, addr_width, data_width, addr_to_reg_map)


    def get_implementation(self, addr_width, data_width, rd_bus_name) -> str:
        lines = []
        lines.append(f"{self._indent}//Readback Mux")
        lines.append(f"{self._indent}always_comb begin")
        self._indent_level += 1
        lines.append(f"{self._indent}case (slv_reg_rd_addr)")
        # TODO: Count the number of readable registers
        readable_regs = 0;
        addr_to_reg_map = {}


        self.gen_mux_map(self.top_node, addr_width, data_width, addr_to_reg_map)

        #is this guaranteed to be ordered
        for key in addr_to_reg_map:
            li = addr_to_reg_map[key]
            for elem in li:
                self._indent_level += 1
                lines.append(f"{self._indent}'d{key}: begin")
                for field in elem.fields():
                    if(field.is_sw_readable):
                        hier =  field.get_path()
                        tokens = hier.split(".")
                        if(field.implements_storage):
                            tokens[0] = "storage"
                        else :
                            tokens[0] = "hwif_in"
                        storage_elem = ".".join(tokens)
                        self._indent_level += 1
                        lines.append(f"{self._indent}{rd_bus_name}[{field.high}:{field.low}] = {storage_elem}")
                        self._indent_level -= 1

                self._indent_level -= 1

        lines.append(f"{self._indent}endcase")
        self._indent_level -= 1
        lines.append(f"{self._indent}end // always_comb")

        lines.append(f"\n\n")


        return "\n".join(lines)


    #---------------------------------------------------------------------------
    @property
    def _indent(self) -> str:
        return "    " * self._indent_level
