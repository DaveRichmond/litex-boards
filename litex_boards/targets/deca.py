#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 David Richmond <dave@prstat.org>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import deca

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG -----------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        clk50 = platform.request("clk50")

        self.submodules.pll = pll = Max10PLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        platform = deca.Platform()
        # SoCCore ----------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
                ident = "LiteX SoC on Terasic DECA",
                ident_version = True,
                **kwargs)

        # CRG --------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # LEDs -------------------------------------------------------------
        self.submodules.leds = LedChaser(
                pads = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build --------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Terasic DECA")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load", action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk_freq", default=50e6, help="System clock frequency (default 50MHz)")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
            sys_clk_freq = int(float(args.sys_clk_freq)),
            **soc_sdram_argdict(args))
    #soc.platform.add_extension(deca._serial_bbb_io)
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__": 
    main()
