{% extends "cpuif/base_tmpl.sv" %}
{%- import "utils_tmpl.sv" as utils with context %}

{% block body %}

enum {
    C_AXI_STATE_IDLE,
    C_AXI_STATE_DATA,
    C_AXI_STATE_RESP
} axi_wr_state, axi_rd_state;

logic[29:0] slv_reg_wr_addr;
logic[29:0] slv_reg_rd_addr;
logic slv_reg_wren;
logic[31:0] reg_data_out;


// =================================================================
// AXI Write Handler
// =================================================================
{%- call utils.AlwaysFF(cpuif_reset) %}
if (rst) begin
    axi_wr_state <= C_AXI_STATE_IDLE;
    s_axi4lite.AWREADY <= 'b0;
    s_axi4lite.WREADY <= 'b0;
    s_axi4lite.BRESP <= 'd0;
    s_axi4lite.BVALID  <= 'b0;
    slv_reg_wr_addr <= 'h0;
end else begin
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

            slv_reg_wr_addr <= s_axi4lite.AWADDR[31:2];
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
end
{%- endcall %}

assign slv_reg_wren = s_axi4lite.WREADY && s_axi4lite.AWREADY;



// =================================================================
// AXI Read Handler
// =================================================================
{%- call utils.AlwaysFF(cpuif_reset) %}
if (rst) begin

    axi_rd_state <= C_AXI_STATE_IDLE;

    s_axi4lite.ARREADY <= 'b0;
    s_axi4lite.RVALID  <= 'b0;
    s_axi4lite.RRESP   <= 'd0;

    slv_reg_rd_addr    <= 'h0;

end else begin
    case (axi_rd_state)
        C_AXI_STATE_IDLE : begin
            if (s_axi4lite.ARVALID) begin
                axi_rd_state <= C_AXI_STATE_DATA;
            end

            s_axi4lite.ARREADY <= 'b0;
            s_axi4lite.RVALID  <= 'b0;
            s_axi4lite.RRESP   <= 'd0;
        end
        C_AXI_STATE_DATA : begin
            axi_rd_state       <= C_AXI_STATE_RESP;

            s_axi4lite.ARREADY <= 'b1;
            s_axi4lite.RVALID  <= 'b0;
            s_axi4lite.RRESP   <= 'd0;

            slv_reg_rd_addr <= s_axi4lite.ARADDR[31:2];
        end
        C_AXI_STATE_RESP : begin
            if (s_axi4lite.RREADY && s_axi4lite.RVALID) begin
                axi_rd_state <= C_AXI_STATE_IDLE;
                s_axi4lite.RVALID <= 'b0;
            end else begin
                s_axi4lite.RVALID <= 'b1;
            end
            s_axi4lite.RRESP <= 'd0;
            s_axi4lite.ARREADY <= 'b0;
        end
        default : begin
            axi_rd_state <= C_AXI_STATE_IDLE;
        end
    endcase // axi_rd_state
end

{%- endcall %}


{%- endblock body%}
