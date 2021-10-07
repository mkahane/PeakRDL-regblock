{% extends "cpuif/base_tmpl.sv" %}
{%- import "utils_tmpl.sv" as utils with context %}

{% block body %}

    enum { 
        C_AXI_STATE_IDLE, 
        C_AXI_STATE_DATA, 
        C_AXI_STATE_RESP}
    axi_wr_state, axi_rd_state;

    logic[31:0] slv_reg_wr_addr;
    logic[31:0] slv_reg_rd_addr;
    logic slv_reg_wren;
    logic[31:0] reg_data_out;

// Request
{%- call utils.AlwaysFF(cpuif_reset) %}
         case (axi_wr_state)
                C_AXI_STATE_IDLE : begin
                    if (s_axi4lite.AWVALID && s_axi4lite.WVALID) begin
                        axi_wr_state <= C_AXI_STATE_DATA;
                    end

                    s_axi4lite.AWREADY <= 'b0;
                    s_axi4lite.WREADY<= 'b0;
                    s_axi4lite.BRESP <= 'd0;
                    s_axi4lite.BVALID <= 'b0;

                    slv_reg_wr_addr <= 'h0;
                end
                C_AXI_STATE_DATA : begin
                    axi_wr_state <= C_AXI_STATE_RESP;

                    s_axi4lite.AWREADY <= 'b1;
                    s_axi4lite.WREADY <= 'b1;
                    s_axi4lite.BRESP <= 'd0;
                    s_axi4lite.BVALID <= 'b0;

                    slv_reg_wr_addr <= s_axi4lite.AWADDR;
                end
                C_AXI_STATE_RESP : begin
                    if (s_axi4lite.BREADY && s_axi4lite.BVALID) begin
                        axi_wr_state <= C_AXI_STATE_IDLE;
                        s_axi4lite.BVALID <= 'b0;
                    end else begin
                        s_axi4lite.BVALID <= 'b1;
                    end

                    s_axi4lite.AWREADY <= 'b0;
                    s_axi4lite.WREADY <= 'b0;
                    s_axi4lite.BRESP <= 'd0;

                    slv_reg_wr_addr <= 'h0;
                end
                default : begin
                    axi_wr_state <= C_AXI_STATE_IDLE;
                end
            endcase // axi_wr_state


{%- endcall %}

assign slv_reg_wren = s_axi4lite.WREADY && s_axi4lite.AWREADY;

{%- endblock body%}
