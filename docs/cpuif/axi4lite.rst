.. _cpuif_axi4lite:

AMBA AXI4-Lite
==============

Implements the register block using an
`AMBA AXI4-Lite <https://developer.arm.com/documentation/ihi0022/e/AMBA-AXI4-Lite-Interface-Specification>`_
CPU interface.

The AXI4-Lite CPU interface comes in two i/o port flavors:

SystemVerilog Interface
    Class: :class:`peakrdl.regblock.cpuif.axi4lite.AXI4Lite_Cpuif`

    Interface Definition: :download:`axi4lite_intf.sv <../../tests/lib/cpuifs/axi4lite/axi4lite_intf.sv>`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    Class: :class:`peakrdl.regblock.cpuif.axi4lite.AXI4Lite_Cpuif_flattened`


Pipelined Performance
---------------------
This implementation of the AXI4-Lite interface supports transaction pipelining
which can significantly improve performance of back-to-back transfers.

In order to support transaction pipelining, the CPU interface will accept multiple
concurrent transactions. The number of outstanding transactions allowed is automatically
determined based on the register file pipeline depth (affected by retiming options),
and influences the depth of the internal transaction response skid buffer.
