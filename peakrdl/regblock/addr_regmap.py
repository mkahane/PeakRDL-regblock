import re
import math
from typing import TYPE_CHECKING, List

from systemrdl.node import Node, AddressableNode, RegNode, FieldNode, RegfileNode

if TYPE_CHECKING:
    from .exporter import RegblockExporter

class AddrRegmap:
    def __init__(self, exporter:'RegblockExporter', top_node:AddressableNode):
        self.exporter = exporter
        self.top_node = top_node


    #This does not handle register fields that overlap addresses
    def gen_mux_map(self, node, addr_width, data_width, addr_to_reg_map):

        for child in node.children(unroll=True):

            if isinstance(child, RegNode):
                if(child.has_sw_readable):
                    mux_address = (child.absolute_address * 8) >> (int)(math.log2(addr_width))
                    if mux_address in addr_to_reg_map:
                        addr_to_reg_map[mux_address].append(child)
                    else:
                        newlist = []
                        newlist.append(child)
                        addr_to_reg_map[mux_address] = newlist


            elif isinstance(child, RegfileNode):
                self.gen_mux_map(child, addr_width, data_width, addr_to_reg_map)
