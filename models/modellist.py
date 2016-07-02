# coding: utf8
# A list of common models
config_modellist = {
    "Netgear": {
        "WGT634U":{"target":"brcm47xx-legacy", "profile":"WGT634U"},
        "WNDR3700v1":{"target":"ar71xx", "profile":"WNDR3700"},
        "WNDR3700v2":{"target":"ar71xx", "profile":"WNDR3700"},
    },
    "\"TP-Link\"":{
        "WR741":{"target":"ar71xx", "profile":"TLWR741"},
        "WR841":{"target":"ar71xx", "profile":"TLWR841"},
        "WR842":{"target":"ar71xx", "profile":"TLWR842"},
        "WR1043ND":{"target":"ar71xx", "profile":"TLWR1043"},
        "WDR3600":{"target":"ar71xx", "profile":"TLWDR4300"},
        "WDR4300":{"target":"ar71xx", "profile":"TLWDR4300"},
        "WDR4310":{"target":"ar71xx", "profile":"TLWDR4300"},
    },
    "Ubiquiti":{
        "Nanostation Loco M2/M5":{"target":"ar71xx", "profile":"UBNT"},
        "Nanostation M2/M5":{"target":"ar71xx", "profile":"UBNT"},
        "Routerstation":{"target":"ar71xx", "profile":"UBNTRS"},
        "Routerstation Pro":{"target":"ar71xx", "profile":"UBNTRSPRO"},
        "Litestation LS-SR71":{"target":"ar71xx", "profile":"UBNT"},
    },
    "X86":{
        "Generic":{"target":"x86-generic", "profile":"Generic"},
        "Virtualbox":{"target":"x86-generic", "profile":"Generic"},
        "Vmware":{"target":"x86-generic", "profile":"Generic"},
        "KVM Guest":{"target":"x86-kvm_guest"},
    },
}
