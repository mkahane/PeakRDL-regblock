{% extends "cpuif/base_tmpl.sv" %}
{%- import "utils_tmpl.sv" as utils with context %}

{% block body %}
// Request
{%- call utils.AlwaysFF(cpuif_reset) %}
         case (axi_wr_state)
                C_AXI_STATE_IDLE : begin
                    if (S_AXI_AWVALID && S_AXI_WVALID) begin
                        axi_wr_state <= C_AXI_STATE_DATA;
                    end

                    axi_awready <= 'b0;
                    axi_wready <= 'b0;
                    axi_bresp <= 'd0;
                    axi_bvalid <= 'b0;

                    slv_reg_wr_addr <= 'h0;
                end
                C_AXI_STATE_DATA : begin
                    axi_wr_state <= C_AXI_STATE_RESP;

                    axi_awready <= 'b1;
                    axi_wready <= 'b1;
                    axi_bresp <= 'd0;
                    axi_bvalid <= 'b0;

                    slv_reg_wr_addr <= S_AXI_AWADDR[C_ADDR_LSB+:C_REG_ADDR_BITS];
                end
                C_AXI_STATE_RESP : begin
                    if (S_AXI_BREADY && axi_bvalid) begin
                        axi_wr_state <= C_AXI_STATE_IDLE;
                        axi_bvalid <= 'b0;
                    end else begin
                        axi_bvalid <= 'b1;
                    end

                    axi_awready <= 'b0;
                    axi_wready <= 'b0;
                    axi_bresp <= 'd0;

                    slv_reg_wr_addr <= 'h0;
                end
                default : begin
                    axi_wr_state <= C_AXI_STATE_IDLE;
                end
            endcase // axi_wr_state
        end
    end


    assign slv_reg_wren = axi_wready && axi_awready;

{%- endcall %}

{%- endblock body%}
