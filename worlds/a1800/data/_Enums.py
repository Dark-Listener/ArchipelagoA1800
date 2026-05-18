from enum import auto, Enum, Flag, KEEP


class DLC(Enum):
    VANILLA = auto()


class ProductType(Enum):
    META = auto()
    WORKFORCE = auto()
    GOOD = auto()
    SERVICE = auto()


class Region(Flag, boundary=KEEP):
    OW = auto()
    NW = auto()
    EN = auto()
    AR = auto()

    @property
    def full_name(self) -> str:
        global _REGION_NAMES

        out_name = ""
        for region, full_name in _REGION_NAMES.items():
            if region in self:
                if out_name:
                    out_name += "|"
                out_name += full_name
        return out_name


_REGION_NAMES = {
    Region.OW: "Old World",
    Region.NW: "New World",
    Region.EN: "Enbesa",
    Region.AR: "Arctic",
}

NO_REGION = Region(0)

ALL_REGIONS = Region.OW | Region.NW | Region.EN | Region.AR


class RequirementType(Enum):
    NONE = 0
    PRODUCT = auto()
    UNLOCK = auto()


class UnlockType(Flag, boundary=KEEP):
    UNLOCK = 0
    BUILDING = auto()
    FACTORY = auto()
    UPGRADE = auto()
    RESIDENCE = auto()
