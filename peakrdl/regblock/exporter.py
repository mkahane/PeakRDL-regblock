import os
from typing import TYPE_CHECKING

import jinja2 as jj
from systemrdl.node import Node, RootNode

from .addr_decode import AddressDecode
from .addr_regmap import AddrRegmap
from .field_logic import FieldLogic
from .dereferencer import Dereferencer
from .readback_mux import ReadbackMux
from .signals import InferredSignal

from .cpuif.axi4lite import AXI4LITE_Cpuif
from .hwif.struct import StructHwif

class RegblockExporter:
    def __init__(self, **kwargs):
        user_template_dir = kwargs.pop("user_template_dir", None)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        if user_template_dir:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(user_template_dir),
                jj.FileSystemLoader(os.path.dirname(__file__)),
                jj.PrefixLoader({
                    'user': jj.FileSystemLoader(user_template_dir),
                    'base': jj.FileSystemLoader(os.path.dirname(__file__)),
                }, delimiter=":")
            ])
        else:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(os.path.dirname(__file__)),
                jj.PrefixLoader({
                    'base': jj.FileSystemLoader(os.path.dirname(__file__)),
                }, delimiter=":")
            ])

        self.jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
        )


    def export(self, node:Node, output_relpath, **kwargs):
        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        cpuif_cls = kwargs.pop("cpuif_cls", AXI4LITE_Cpuif)
        hwif_cls = kwargs.pop("hwif_cls", StructHwif)
        module_name = kwargs.pop("module_name", node.inst_name + "_reg")
        package_name = kwargs.pop("package_name", module_name + "_pkg")

        #TODO
        addr_width = 32
        data_width = 32

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])



        # TODO: Scan design...

        # TODO: derive this from somewhere
        cpuif_reset = InferredSignal("rst")
        cpuif_wr_valid = InferredSignal("WVALID")
        cpuif_rd_data = InferredSignal("RDATA")
        reset_signals = [cpuif_reset]



        cpuif = cpuif_cls(
            self,
            cpuif_reset=cpuif_reset, # TODO:
            cpuif_wr_valid=cpuif_wr_valid, # TODO:
            cpuif_rd_data=cpuif_rd_data, # TODO:
            data_width=data_width,
            addr_width=addr_width
        )

        hwif = hwif_cls(
            self,
            top_node=node,
            package_name=package_name,
        )

        address_decode = AddressDecode(self, node)
        field_logic = FieldLogic(self, node)
        readback_mux = ReadbackMux(self, node)
        dereferencer = Dereferencer(self, hwif, field_logic, node)
        addr_regmap = AddrRegmap(self, node)

        addr_to_reg_map = {}
        addr_regmap.gen_mux_map(node, addr_width, data_width, addr_to_reg_map)



        # Build Jinja template context
        context = {
            "module_name": module_name,
            "package_name": package_name,
            "data_width": 64, # TODO:
            "addr_width": 32, # TODO:
            "reset_signals": reset_signals,
            "cpuif_reset": cpuif_reset,
            "cpuif_wr_valid": cpuif_wr_valid,
            "cpuif_rd_data": cpuif_rd_data,
            "user_signals": [], # TODO:
            "interrupts": [], # TODO:
            "cpuif": cpuif,
            "hwif": hwif,
            "address_decode": address_decode,
            "field_logic": field_logic,
            "readback_mux": readback_mux,
            "addr_to_reg_map" :addr_to_reg_map
        }

        output_package_path = output_relpath + package_name + ".sv"
        template = self.jj_env.get_template("pkg_tmpl.sv")
        stream = template.stream(context)
        stream.dump(output_package_path)

        output_module_path = output_relpath + module_name + ".sv"
        template = self.jj_env.get_template("module_tmpl.sv")
        stream = template.stream(context)
        stream.dump(output_module_path)


