from enum import auto, Enum, Flag, IntEnum, KEEP
from functools import reduce


class DLC(Flag, boundary=KEEP):
    VANILLA = auto()
    SUNKEN_TREASURES = auto()
    BOTANICA = auto()
    THE_PASSAGE = auto()
    SEAT_OF_POWER = auto()
    BRIGHT_HARVEST = auto()
    LAND_OF_LIONS = auto()
#    DOCKLANDS = auto()
    TOURIST_SEASON = auto()
#    THE_HIGH_LIFE = auto()
#    SEEDS_OF_CHANGE = auto()
    EMPIRE_OF_THE_SKIES = auto()
#    NEW_WORLD_RISING = auto()

    @property
    def guid(self) -> int:
        global _DLC_GUIDS
        return _DLC_GUIDS[self]


_DLC_GUIDS = {
    DLC.VANILLA: 0,
    DLC.SUNKEN_TREASURES: 410040,
    DLC.BOTANICA: 410041,
    DLC.THE_PASSAGE: 410042,
    DLC.SEAT_OF_POWER: 410059,
    DLC.BRIGHT_HARVEST: 410070,
    DLC.LAND_OF_LIONS: 410071,
    #    DLC.DOCKLANDS: 410083,
    DLC.TOURIST_SEASON: 410084,
    #    DLC.THE_HIGH_LIFE: 410085,
    #    DLC.SEEDS_OF_CHANGE: 24961,
    DLC.EMPIRE_OF_THE_SKIES: 24962,
    #    DLC.NEW_WORLD_RISING: 24963,
}

ALL_DLC = reduce(DLC.__or__, DLC.__members__.values())


class ProductType(Enum):
    META = auto()
    STAGE = auto()
    WORKFORCE = auto()
    GOOD = auto()
    SERVICE = auto()

    @property
    def full_name(self) -> str:
        global _PRODUCT_TYPE_NAMES
        return _PRODUCT_TYPE_NAMES[self]


_PRODUCT_TYPE_NAMES = {
    ProductType.META: "Meta",
    ProductType.STAGE: "Stage",
    ProductType.WORKFORCE: "Workforce",
    ProductType.GOOD: "Good",
    ProductType.SERVICE: "Service",
}


class Region(Flag, boundary=KEEP):
    OW = auto()
    NW = auto()
    AR = auto()
    EN = auto()

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

    @property
    def is_unique(self) -> bool:
        return self in Region.__members__.values()


_REGION_NAMES = {
    Region.OW: "Old World",
    Region.NW: "New World",
    Region.AR: "The Arctic",
    Region.EN: "Enbesa",
}

NO_REGION = Region(0)

START_REGION = Region.OW

ALL_REGIONS = reduce(Region.__or__, Region.__members__.values())


class RequirementType(Enum):
    NONE = 0
    PRODUCT = auto()
    UNLOCK = auto()


class Session(IntEnum):
    OW = auto()
    NW = auto()
    CT = auto()
    AR = auto()
    EN = auto()

    @property
    def full_name(self) -> str:
        global _SESSION_NAMES
        return _SESSION_NAMES[self]

    @property
    def guid(self) -> int:
        global _SESSION_GUIDS
        return _SESSION_GUIDS[self]

    @property
    def region(self) -> Region:
        global _SESSION_REGIONS
        return _SESSION_REGIONS[self]


_SESSION_NAMES = {
    Session.OW: "Old World",
    Session.NW: "New World",
    Session.CT: "Cape Trelawney",
    Session.AR: "The Arctic",
    Session.EN: "Enbesa",
}

_SESSION_GUIDS = {
    Session.OW: 180023,
    Session.NW: 180025,
    Session.CT: 110934,
    Session.AR: 180045,
    Session.EN: 112132,
}


_SESSION_REGIONS = {
    Session.OW: Region.OW,
    Session.NW: Region.NW,
    Session.CT: Region.OW,
    Session.AR: Region.AR,
    Session.EN: Region.EN,
}


class TriggerType(IntEnum):
    SESSION_ENTER = auto()
    POPULATION = auto()
    COUNTER = auto()
    UNLOCK = auto()
    DLC = auto()
    ANY = auto()
    ALL = auto()
    TRUE = auto()
    FALSE = auto()


class UnlockType(Flag, boundary=KEEP):
    UNLOCK = 0
    META = auto()
    BUILDING = auto()
    FACTORY = auto()
    UPGRADE = auto()
    RESIDENCE = auto()
