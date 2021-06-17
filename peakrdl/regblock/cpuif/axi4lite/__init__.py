from ..base import CpuifBase

class AXI4LITE_Cpuif(CpuifBase):
    template_path = "cpuif/axi4lite/axi4lite_tmpl.sv"

    @property
    def port_declaration(self) -> str:
        return "axi4lite_intf.slave s_axi4lite"

    def signal(self, name:str) -> str:
        return "s_axi4lite." + name


class AXI4LITE_Cpuif_flattened(AXI4LITE_Cpuif):
    @property
    def port_declaration(self) -> str:
        # TODO: Reference data/addr width from verilog parameter perhaps?
        lines = [
            "input  wire %s" % self.signal("AWVALID"),
            "output logic %s" % self.signal("AWREADY"),
            "input  wire [%d-1:0] %s" % (self.addr_width, self.signal("AWADDR")),
            "input  wire [1:0] %s" % self.signal("AWPROT"),
            "input  wire %s" % self.signal("WVALID"),
            "output logic %s" %self.signal("WREADY"),
            "input  wire [%d-1:0] %s" %(self.data_width, self.signal("WDATA")),
            "input  wire [%0d-1:0] %s" %(self.data_width/8, self.signal("WSTRB")),

            "output logic %s" %self.signal("BVALID"),
            "input  wire %s" %self.signal("BREADY"),
            "output logic [1:0] %s" %self.signal("BRESP"),

            "input  logic %s" %self.signal("ARVALID"),
            "output logic %s" %self.signal("ARREADY"),
            "input  wire [%d-1:0] %s" % (self.addr_width, self.signal("ARADDR")),
            "input  wire [1:0] %s" % self.signal("ARPROT"),

            "output logic %s" %self.signal("RVALID"),
            "input  wire %s" %self.signal("RREADY"),
            "output logic %s" %self.signal("RDATA"),
            "output logic [1:0] %s" %self.signal("RRESP"),

        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_axi4lite_" + name
