# this platform/target assumes you have the daughterboard that qmtech supply
# it provides ethernet, sdcard, vga, buttons and leds. The mainboard
# button unfortunately conflicts with the sd_cmd signal :(

import os
import argparse

from migen import *
from litex_boards.platforms import qmtech_a7ddr3
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII

from litevideo.terminal.core import Terminal

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys,      sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,    4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs,4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,   200e6)
        pll.create_clkout(self.cd_eth,      25e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # ignore sys_clk to pll.clkin path created by SoC's rst
        
        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)
        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)

class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=int(100e6), with_ethernet=False, with_etherbone=False, eth_ip="192.168.1.50", ident_version=True, **kwargs):
        platform = qmtech_a7ddr3.Platform(toolchain=toolchain)

        # SoCCore ---------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, 
                ident = "LiteX SoC on QMTech A7 DDR3",
                ident_version=ident_version,
                **kwargs)

        # CRG -------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 ------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(
                    platform.request("ddram"),
                    memtype = "DDR3",
                    nphases = 4,
                    sys_clk_freq = sys_clk_freq)
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                    phy = self.ddrphy,
                    module = MT41K128M16(sys_clk_freq, "1:4"),
                    origin = self.mem_map["main_ram"],
                    size = kwargs.get("max_sdram_size", 0x40000000),
                    l2_cache_size = kwargs.get("l2_size", 8192),
                    l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                    l2_cache_reverse = True)

        # Ethernet/Etherbone ----------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYMII(
                    clock_pads = self.platform.request("eth_clocks"),
                    pads = self.platform.request("eth"))
            self.add_csr("ethphy")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # LEDs ------------------------------------------------------------------
        self.submodules.leds = LedChaser(
                pads = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

# Build -------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on QMTech Artix 7 DDR3")
    parser.add_argument("--toolchain",  default="vivado", help="Toolchain use to build (default: vivado)")
    parser.add_argument("--build",      action="store_true", help="build bitstream")
    parser.add_argument("--load",       action="store_true", help="load bitstream")
    parser.add_argument("--sys-clk-freq", default=50e6, help="System clock frequency (default: 50MHz)")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet", action="store_true", help="Enable ethernet")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Eneable etherbone")
    parser.add_argument("--eth-ip",         default="192.168.1.50", type=str, help="Ethernet/Etherbone IP address")
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDcard support")
    sdopts.add_argument("--with-sdcard", action="store_true", help="Enable SDcard support")
    parser.add_argument("--no-ident-version", action="store_false", help="Disable build time output")
    builder_args(parser)
    soc_sdram_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
            toochain        =args.toolchain,
            sys_clk_freq    =int(float(args.sys_clk_freq)),
            with_ethernet   =args.with_ethernet, 
            with_etherbone  =args.with_etherbone,
            eth_ip          = args.eth_ip,
            ident_version   = args.no_ident_version,
            **soc_sdram_argdict(args))
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args) if args.toolchain == "vivado" else {}
    builder.build(**builder_kwargs, run=args.build)
    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()

