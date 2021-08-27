from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from ..exporter import RegblockExporter
    from ..signals import SignalBase

class CpuifBase:
    template_path = "cpuif/base_tmpl.sv"

    def __init__(self, exporter:'RegblockExporter',
        cpuif_reset:'SignalBase',
        cpuif_wr_valid:'SignalBase',
        cpuif_rd_data: 'SignalBase',
        data_width:int=32, addr_width:int=32
    ):
        self.exporter = exporter
        self.cpuif_reset = cpuif_reset
        self.cpuif_wr_valid = cpuif_wr_valid
        self.cpuif_rd_data= cpuif_rd_data
        self.data_width = data_width
        self.addr_width = addr_width

    @property
    def port_declaration(self) -> str:
        raise NotImplementedError()

    def get_implementation(self) -> str:
        context = {
            "cpuif": self,
            "cpuif_reset": self.cpuif_reset,
            "cpuif_wr_valid": self.cpuif_wr_valid,
            "cpuif_rd_data": self.cpuif_rd_data,
            "data_width": self.data_width,
            "addr_width": self.addr_width,
        }


        template = self.exporter.jj_env.get_template(self.template_path)
        return template.render(context)
