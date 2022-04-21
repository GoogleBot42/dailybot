#!/usr/bin/env python3
# coding=utf-8

# Quotes from various historical versions of the Linux kernel

'''
Copyright (C) 2021 Flisk <flisk@fastmail.de>
Copyright (C) 2021 drastik.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import random


class Module:
    def __init__(self):
        self.commands = ['kernel']
        self.manual = {
            "desc": (
                "Post quotes from various historical versions of the"
                " Linux kernel http://www.schwarzvogel.de/software/misc.html"
            ),
            "bot_commands": {
                "usage": lambda x: f"{x}kernel"
            }
        }


# Taken from the Kernelcookies fortune file curated by Tobias
# Klausmann. These are quotes from various historical versions of the
# Linux kernel.
talk = [
  "/* This card is _fucking_ hot... */",
  # linux-2.6.6/drivers/net/sunhme.c

  "If you don't see why, please stay the fuck away from my code.",
  # Rusty, in linux-2.6.6/Documentation/DocBook/kernel-locking.tmpl

  "/* Fuck, we are miserable poor guys... */",
  # linux-2.6.6/net/xfrm/xfrm_algo.c

  "/* Ugly, ugly fucker. */",
  # linux-2.6.6/include/linux/netfilter_ipv4/ipt_limit.h

  "/* Remember: \"Different name, same old buggy as shit hardware.\" */",
  # linux-2.6.6/drivers/net/sunhme.c

  "/* This is total bullshit: */",
  # linux-2.6.6/drivers/video/sis/init301.c

  "/* The HME is the biggest piece of shit I have ever seen. */",
  # linux-2.6.6/drivers/scsi/esp.h

  "printk(\"WE HAVE A BUG HERE!!! stk=0x%p\\n\", stk);",
  # linux-2.6.6/drivers/block/cciss_scsi.c

  "printk(\"%s: huh ? Who issued this format command ?\\n\")",
  # linux-2.6.6/drivers/block/ps2esdi.c

  "printk(\"whoops, seeking 0\\n\");",
  # linux-2.6.6/drivers/block/swim3.c

  "printk(\"GSCD: magic ...\\n\");",
  # linux-2.6.6/drivers/cdrom/gscd.c

  "printk(\" (Read error)\");        /* Bitch about the problem. */",
  # linux-2.6.6/drivers/cdrom/mcd.c

  "printk(\" Speed now 1x\");        /* Pull my finger! */",
  # linux-2.6.6/drivers/cdrom/mcd.c

  "panic(\"Alas, I survived.\\n\");",
  # linux-2.6.6/arch/ppc64/kernel/rtas.c

  "panic(\"smp_callin() AAAAaaaaahhhh....\\n\");",
  # linux-2.6.6/arch/parisc/kernel/smp.c

  "panic(\"Yeee, unsupported cache architecture.\");",
  # linux-2.6.6/arch/mips/mm/cache.c

  "panic(\"\\n\");",
  # linux-2.6.6/arch/mips/tx4927/common/tx4927_irq.c

  "panic(\"%s called.  This Does Not Happen (TM).\", __FUNCTION__);",
  # linux-2.6.6/arch/mips/mm-64/tlb-dbg-r4k.c

  "printk (KERN_ERR \"%s: Oops - your private data area is hosed!\\n\", ...)",
  # linux-2.6.6/drivers/net/ewrk3.c

  "rio_dprintk (RIO_DEBUG_ROUTE, \"LIES! DAMN LIES! %d LIES!\\n\",Lies);",
  # linux-2.6.6/drivers/char/rio/rioroute.c

  "printk(\"NONONONOO!!!!\\n\");",
  # linux-2.6.6/drivers/atm/zatm.c

  "printk(\"@#*$!!!!  (%08x)\\n\", ...)",
  # linux-2.6.6/drivers/atm/zatm.c

  "fs_dprintk (FS_DEBUG_INIT, \"Ha! Initialized OK!\\n\");",
  # linux-2.6.6/drivers/atm/firestream.c

  "DPRINTK(\"strange things happen ...\\n\");",
  # linux-2.6.6/drivers/atm/eni.c

  "printk(KERN_WARNING \"Hey who turned the DMA off?\\n\");",
  # linux-2.6.6/drivers/net/wan/z85230.c

  "printk(KERN_DEBUG \"%s: BUG... transmitter died. Kicking it.\\n\",...)",
  # linux-2.6.6/drivers/net/acenic.c

  "printk(KERN_ERR \"%s: Something Wicked happened! %4.4x.\\n\",...);",
  # linux-2.6.6/drivers/net/sundance.c

  "DPRINTK(\"FAILURE, CAPUT\\n\");",
  # linux-2.6.6/drivers/net/tokenring/ibmtr.c

  "Dprintk(\"oh dear, we are idle\\n\");",
  # linux-2.6.6/drivers/net/ns83820.c

  "printk(KERN_DEBUG \"%s: burped during tx load.\\n\", dev->name)",
  # linux-2.6.6/drivers/net/3c501.c

  "printk(KERN_DEBUG \"%s: I'm broken.\\n\", dev->name);",
  # linux-2.6.6/drivers/net/plip.c

  "printk(\"%s: TDR is ga-ga (status %04x)\\n\", ...);",
  # linux-2.6.6/drivers/net/eexpress.c

  "printk(\"3c505 is sulking\\n\");",
  # linux-2.6.6/drivers/net/3c505.c

  "printk(KERN_ERR \"happy meal: Transceiver and a coke please.\");",
  # linux-2.6.6/drivers/net/sunhme.c

  "printk(\"Churning and Burning -\");",
  # linux-2.6.6/drivers/char/lcd.c

  "printk (KERN_DEBUG \"Somebody wants the port\\n\");",
  # linux-2.6.6/drivers/parport/parport_pc.c

  "printk(KERN_WARNING MYNAM \": (time to go bang on somebodies door)\\n\");",
  # linux-2.6.6/drivers/message/fusion/mptctl.c

  "printk(\"NULL POINTER IDIOT\\n\");",
  # linux-2.6.6/drivers/media/dvb/dvb-core/dvb_filter.c

  "dprintk(5, KERN_DEBUG \"Jotti is een held!\\n\");",
  # linux-2.6.6/drivers/media/video/zoran_card.c

  "printk(KERN_CRIT \"Whee.. Swapped out page in kernel page table\\n\");",
  # linux-2.6.6/mm/vmalloc.c

  "printk(\"----------- [cut here ] --------- [please bite here ] ---------\\n\");",
  # linux-2.6.6/arch/x86_64/kernel/traps.

  "printk (KERN_ALERT \"You are screwed! \" ...);",
  # linux-2.6.6/arch/i386/kernel/efi.c

  "printk(\"you lose buddy boy...\\n\");",
  # linux-2.6.6/arch/sparc/kernel/traps.c

  "printk (\"Barf\\n\");",
  # linux-2.6.6/arch/v850/kernel/module.c

  "printk(KERN_EMERG \"PCI: Tell willy he's wrong\\n\");",
  # linux-2.6.6/arch/parisc/kernel/pci.c

  "printk(KERN_ERR \"Danger Will Robinson: failed to re-trigger IRQ%d\\n\", irq);",
  # linux-2.6.6/arch/arm/common/sa1111.c

  "printk(\"; crashing the system because you wanted it\\n\");",
  # linux-2.6.6/fs/hpfs/super.c

  "panic(\"sun_82072_fd_inb: How did I get here?\");",
  # linux-2.2.16/include/asm-sparc/floppy.h

  "printk(KERN_ERR \"msp3400: chip reset failed, penguin on i2c bus?\\n\");",
  # linux-2.2.16/drivers/char/msp3400.c

  "die_if_kernel(\"Whee... Hello Mr. Penguin\", current->tss.kregs);",
  # linux-2.2.16/arch/sparc/kernel/traps.c

  "die_if_kernel(\"Penguin instruction from Penguin mode??!?!\", regs);",
  # linux-2.2.16/arch/sparc/kernel/traps.c

  "printk(\"Entering UltraSMPenguin Mode...\\n\");",
  # linux-2.2.16/arch/sparc64/kernel/smp.c

  "panic(\"mother...\");",
  # linux-2.2.16/drivers/block/cpqarray.c

  "panic(\"Foooooooood fight!\");",
  # linux-2.2.16/drivers/scsi/aha1542.c

  "panic(\"huh?\\n\");",
  # linux-2.2.16/arch/i386/kernel/smp.c

  "panic(\"Oh boy, that early out of memory?\");",
  # linux-2.2.16/arch/mips/mm/init.c

  "panic(\"CPU too expensive - making holiday in the ANDES!\");",
  # linux-2.2.16/arch/mips/kernel/traps.c

  "printk(\"Illegal format on cdrom.  Pester manufacturer.\\n\"); ",
  # linux-2.2.16/fs/isofs/inode.c

  "/* Fuck me gently with a chainsaw... */",
  # linux-2.0.38/arch/sparc/kernel/ptrace.c

  "/* Binary compatibility is good American knowhow fuckin' up. */",
  # linux-2.2.16/arch/sparc/kernel/sunos_ioctl.c

  "/* Am I fucking pedantic or what? */",
  # linux-2.2.16/drivers/scsi/qlogicpti.h

  "panic(\"Aarggh: attempting to free lock with active wait queue - shoot Andy\");",
  # linux-2.0.38/fs/locks.c

  "panic(\"bad_user_access_length executed (not cool, dude)\");",
  # linux-2.0.38/kernel/panic.c

  "printk(\"ufs_read_super: fucking Sun blows me\\n\");",
  # linux-2.0.38/fs/ufs/ufs_super.c

  "printk(\"autofs: Out of inode numbers -- what the heck did you do??\\n\"); ",
  # linux-2.0.38/fs/autofs/root.c

  "HARDFAIL(\"Not enough magic.\");",
  # linux-2.4.0-test2/drivers/block/nbd.c

  "#ifdef STUPIDLY_TRUST_BROKEN_PCMD_ENA_BIT",
  # linux-2.4.0-test2/drivers/ide/cmd640.c

  "/* Fuck.  The f-word is here so you can grep for it :-)  */",
  # linux-2.4.3/include/asm-mips/mmu_context.h

  "panic (\"No CPUs found.  System halted.\\n\");",
  # linux-2.4.3/arch/parisc/kernel/setup.c

  "printk(\"What? oldfid != cii->c_fid. Call 911.\\n\");",
  # linux-2.4.3/fs/coda/cnode.c

  "printk(\"Cool stuff's happening!\\n\")",
  # linux-2.4.3/fs/jffs/intrep.c

  "printk(\"MASQUERADE: No route: Rusty's brain broke!\\n\");",
  # linux-2.4.3/net/ipv4/netfilter/ipt_MASQUERADE.c

  "printk(\"CPU[%d]: Sending penguins to jail...\",smp_processor_id());",
  # linux-2.4.8/arch/sparc64/kernel/smp.c

  "printk(\"CPU[%d]: Giving pardon to imprisoned penguins\\n\", smp_processor_id());",
  # linux-2.4.8/arch/sparc64/kernel/smp.c

  "printk (KERN_INFO \"NM256: Congratulations. You're not running Eunice.\\n\");",
  # linux-2.6.19/sound/oss/nm256_audio.c

  "printk (KERN_ERR \"NM256: Fire in the hole! Unknown status 0x%x\\n\", ...);",
  # linux-2.6.19/sound/oss/nm256_audio.c

  "printk(\"Pretending it's a 3/80, but very afraid...\\n\");",
  # linux-2.6.19/arch/m68k/sun3x/prom.c

  "printk(\"IOP: oh my god, they killed the ISM IOP!\\n\");",
  # linux-2.6.19/arch/m68k/mac/iop.c

  "printk(\"starfire_translate: Are you kidding me?\\n\");",
  # linux-2.6.19/arch/sparc64/kernel/starfire.c

  "raw_printk(\"Oops: bitten by watchdog\\n\");",
  # linux-2.6.19/arch/cris/arch-v32/kernel/time.c

  "prom_printf(\"No VAC. Get some bucks and buy a real computer.\");",
  # linux-2.6.19/arch/sparc/mm/sun4c.c

  "printk(KERN_ERR \"happy meal: Eieee, rx config register gets greasy fries.\\n\");",
  # linux-2.6.19/drivers/net/sunhme.c

  "dprintk(\"NFSD: laundromat service - starting\\n\");"
  # linux-2.6.19/fs/nfsd/nfs4state.c
]


def main(i, irc):
    msg = f"{i.nickname}: {random.SystemRandom().choice(talk)}"
    irc.privmsg(i.channel, msg)
