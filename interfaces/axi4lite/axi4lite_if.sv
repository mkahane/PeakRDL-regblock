interface axi4lite_if #(
	parameter integer ADDR_WIDTH = 32,
	parameter integer DATA_WIDTH = 32
) (

  input logic ACLK,
  input logic ARESETN

)

  logic AWVALID;
  logic AWREADY;
  logic[ADDR_WIDTH-1:0] AWADDR;
  logic[1:0] AWPROT;

  logic WVALID;
  logic WREADY;
  logic [C_DATA_WIDTH-1:0] WDATA;
  logic [C_DATA_WIDTH/8-1:0] WSTRB;

  logic BVALID;
  logic BREADY;
  logic [1:0] BRESP;

  logic ARVALID;
  logic ARREADY;
  logic [C_ADDR_WIDTH-1:0] ARADDR;
  logic [2:0] ARPROT;

  logic RVALID;
  logic RREADY;
  logic [C_DATA_WIDTH-1:0] RDATA;
  logic [1:0] RRESP;

  modport MASTER (

    output AWVALID,
    input AWREADY,
    output AWADDR,
    output AWPROT,

    output WVALID,
    input WREADY,
    output WDATA,
    output WSTRB,

    input BVALID,
    output BREADY,
    input BRESP,

    output ARVALID,
    input  ARREADY,
    output ARADDR,
    output ARPROT,

    input  RVALID,
    output RREADY,
    input  RDATA,
    input  RRESP

  );

  modport SLAVE (

    input AWVALID,
    output AWREADY,
    input AWADDR,
    input AWPROT,

    input WVALID,
    output WREADY,
    input WDATA,
    input WSTRB,

    output BVALID,
    input BREADY,
    output BRESP,

    input ARVALID,
    output  ARREADY,
    input ARADDR,
    input ARPROT,

    output  RVALID,
    input RREADY,
    output  RDATA,
    output  RRESP

  );

endinterface