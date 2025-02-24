// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// Write enable and data arbitration logic for register slice conforming to Comportibility guide.

module prim_subreg_arb #(
  parameter int DW       = 32  ,
  parameter     SWACCESS = "RW"  // {RW, RO, WO, W1C, W1S, W0C, RC}
) (
  // From SW: valid for RW, WO, W1C, W1S, W0C, RC.
  // In case of RC, top connects read pulse to we.
  input          we,
  input [DW-1:0] wd,

  // From HW: valid for HRW, HWO.
  input          de,
  input [DW-1:0] d,

  // From register: actual reg value.
  input [DW-1:0] q,

  // To register: actual write enable and write data.
  output logic          wr_en,
  output logic [DW-1:0] wr_data
);

  if ((SWACCESS == "RW") || (SWACCESS == "WO")) begin : gen_w
    assign wr_en   = we | de;
    assign wr_data = (we == 1'b1) ? wd : d; // SW higher priority
    // Unused q - Prevent lint errors.
    logic [DW-1:0] unused_q;
    assign unused_q = q;
  end else if (SWACCESS == "RO") begin : gen_ro
    assign wr_en   = de;
    assign wr_data = d;
    // Unused we, wd, q - Prevent lint errors.
    logic          unused_we;
    logic [DW-1:0] unused_wd;
    logic [DW-1:0] unused_q;
    assign unused_we = we;
    assign unused_wd = wd;
    assign unused_q  = q;
  end else if (SWACCESS == "W1S") begin : gen_w1s
    // If SWACCESS is W1S, then assume hw tries to clear.
    // So, give a chance HW to clear when SW tries to set.
    // If both try to set/clr at the same bit pos, SW wins.
    assign wr_en   = we | de;
    assign wr_data = (de ? d : q) | (we ? wd : '0);
  end else if (SWACCESS == "W1C") begin : gen_w1c
    // If SWACCESS is W1C, then assume hw tries to set.
    // So, give a chance HW to set when SW tries to clear.
    // If both try to set/clr at the same bit pos, SW wins.
    assign wr_en   = we | de;
    assign wr_data = (de ? d : q) & (we ? ~wd : '1);
  end else if (SWACCESS == "W0C") begin : gen_w0c
    assign wr_en   = we | de;
    assign wr_data = (de ? d : q) & (we ? wd : '1);
  end else if (SWACCESS == "RC") begin : gen_rc
    // This swtype is not recommended but exists for compatibility.
    // WARN: we signal is actually read signal not write enable.
    assign wr_en  = we | de;
    assign wr_data = (de ? d : q) & (we ? '0 : '1);
    // Unused wd - Prevent lint errors.
    logic [DW-1:0] unused_wd;
    assign unused_wd = wd;
  end else if (SWACCESS == "W1SS") begin : gen_w1ss
    // If SWACCESS is W1SS, writing is ilegal if the bit is set
    assign wr_en   = (q == 1)? 0: we | de;
    assign wr_data = (de ? d : q) | (we ? wd : '0);
  end else if (SWACCESS == "W1CS") begin : gen_w1cs
    // If SWACCESS is W1CS, writing is ilegal if the bit is 0
    assign wr_en   = (q == 0)? 0: we | de;
    assign wr_data = (de ? d : q) & (we ? ~wd : '1);
  end else begin : gen_hw
    assign wr_en   = de;
    assign wr_data = d;
    // Unused we, wd, q - Prevent lint errors.
    logic          unused_we;
    logic [DW-1:0] unused_wd;
    logic [DW-1:0] unused_q;
    assign unused_we = we;
    assign unused_wd = wd;
    assign unused_q  = q;
  end

endmodule
