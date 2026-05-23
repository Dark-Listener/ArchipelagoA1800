from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator

from ._Enums import ALL_REGIONS, DLC, NO_REGION, ProductType, Region


@dataclass
class A1800Product:
    name: str
    dlc: DLC
    region: Region
    guid: int
    type: ProductType


_a1800_products: list[A1800Product] = [
    ################################################################################################################
    ### VANILLA                                                                                                  ###
    ################################################################################################################
    A1800Product("Sea Travel", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Settling", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Riot Control", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Healthcare", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Railway", DLC.VANILLA, Region.OW | Region.NW, 0, ProductType.META),
    A1800Product("Oil Harbour", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Oil Field", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Oil Transport", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Settling", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Riot Control", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Healthcare", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Oil Harbour", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Oil Field", DLC.VANILLA, Region.NW, 0, ProductType.META),

    A1800Product("Victory", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),

    A1800Product("Farmers", DLC.VANILLA, Region.OW, 15000000, ProductType.WORKFORCE),
    A1800Product("Workers", DLC.VANILLA, Region.OW, 15000001, ProductType.WORKFORCE),
    A1800Product("Artisans", DLC.VANILLA, Region.OW, 15000002, ProductType.WORKFORCE),
    A1800Product("Engineers", DLC.VANILLA, Region.OW, 15000003, ProductType.WORKFORCE),
    A1800Product("Investors", DLC.VANILLA, Region.OW, 15000004, ProductType.WORKFORCE),
    A1800Product("Jornaleros", DLC.VANILLA, Region.NW, 15000005, ProductType.WORKFORCE),
    A1800Product("Obreros", DLC.VANILLA, Region.NW, 15000006, ProductType.WORKFORCE),

    A1800Product("Wood", DLC.VANILLA, ALL_REGIONS, 120008, ProductType.GOOD),
    A1800Product("Timber", DLC.VANILLA, ALL_REGIONS, 1010196, ProductType.GOOD),
    A1800Product("Fish", DLC.VANILLA, ALL_REGIONS, 1010200, ProductType.GOOD),
    A1800Product("Wool", DLC.VANILLA, ALL_REGIONS, 1010197, ProductType.GOOD),
    A1800Product("Work Clothes", DLC.VANILLA, ALL_REGIONS, 1010237, ProductType.GOOD),
    A1800Product("Potatoes", DLC.VANILLA, ALL_REGIONS, 1010195, ProductType.GOOD),
    A1800Product("Schnapps", DLC.VANILLA, ALL_REGIONS, 1010216, ProductType.GOOD),
    A1800Product("Clay", DLC.VANILLA, ALL_REGIONS, 1010201, ProductType.GOOD),
    A1800Product("Bricks", DLC.VANILLA, ALL_REGIONS, 1010205, ProductType.GOOD),
    A1800Product("Pigs", DLC.VANILLA, ALL_REGIONS, 1010199, ProductType.GOOD),
    A1800Product("Sausages", DLC.VANILLA, ALL_REGIONS, 1010238, ProductType.GOOD),
    A1800Product("Grain", DLC.VANILLA, ALL_REGIONS, 1010192, ProductType.GOOD),
    A1800Product("Flour", DLC.VANILLA, ALL_REGIONS, 1010235, ProductType.GOOD),
    A1800Product("Bread", DLC.VANILLA, ALL_REGIONS, 1010213, ProductType.GOOD),
    A1800Product("Sails", DLC.VANILLA, ALL_REGIONS, 1010210, ProductType.GOOD),
    A1800Product("Coal", DLC.VANILLA, ALL_REGIONS, 1010226, ProductType.GOOD),
    A1800Product("Iron", DLC.VANILLA, ALL_REGIONS, 1010227, ProductType.GOOD),
    A1800Product("Steel", DLC.VANILLA, ALL_REGIONS, 1010219, ProductType.GOOD),
    A1800Product("Steel Beams", DLC.VANILLA, ALL_REGIONS, 1010218, ProductType.GOOD),
    A1800Product("Tallow", DLC.VANILLA, ALL_REGIONS, 1010234, ProductType.GOOD),
    A1800Product("Soap", DLC.VANILLA, ALL_REGIONS, 1010203, ProductType.GOOD),
    A1800Product("Weapons", DLC.VANILLA, ALL_REGIONS, 1010221, ProductType.GOOD),
    A1800Product("Hops", DLC.VANILLA, ALL_REGIONS, 1010194, ProductType.GOOD),
    A1800Product("Malt", DLC.VANILLA, ALL_REGIONS, 1010236, ProductType.GOOD),
    A1800Product("Beer", DLC.VANILLA, ALL_REGIONS, 1010214, ProductType.GOOD),
    A1800Product("Quartz Sand", DLC.VANILLA, ALL_REGIONS, 1010228, ProductType.GOOD),
    A1800Product("Glass", DLC.VANILLA, ALL_REGIONS, 1010241, ProductType.GOOD),
    A1800Product("Windows", DLC.VANILLA, ALL_REGIONS, 1010207, ProductType.GOOD),
    A1800Product("Beef", DLC.VANILLA, ALL_REGIONS, 1010193, ProductType.GOOD),
    A1800Product("Red Peppers", DLC.VANILLA, ALL_REGIONS, 1010198, ProductType.GOOD),
    A1800Product("Goulash", DLC.VANILLA, ALL_REGIONS, 1010215, ProductType.GOOD),
    A1800Product("Canned Food", DLC.VANILLA, ALL_REGIONS, 1010217, ProductType.GOOD),
    A1800Product("Sewing Machines", DLC.VANILLA, ALL_REGIONS, 1010206, ProductType.GOOD),
    A1800Product("Furs", DLC.VANILLA, ALL_REGIONS, 1010209, ProductType.GOOD),
    A1800Product("Cotton", DLC.VANILLA, ALL_REGIONS, 1010253, ProductType.GOOD),
    A1800Product("Cotton Fabric", DLC.VANILLA, ALL_REGIONS, 1010240, ProductType.GOOD),
    A1800Product("Fur Coats", DLC.VANILLA, ALL_REGIONS, 1010247, ProductType.GOOD),
    A1800Product("Cement", DLC.VANILLA, ALL_REGIONS, 1010231, ProductType.GOOD),
    A1800Product("Reinforced Concrete", DLC.VANILLA, ALL_REGIONS, 1010202, ProductType.GOOD),
    A1800Product("Oil", DLC.VANILLA, Region.OW, 1010566, ProductType.GOOD),
    A1800Product("Zinc", DLC.VANILLA, ALL_REGIONS, 1010229, ProductType.GOOD),
    A1800Product("Copper", DLC.VANILLA, ALL_REGIONS, 1010230, ProductType.GOOD),
    A1800Product("Brass", DLC.VANILLA, ALL_REGIONS, 1010204, ProductType.GOOD),
    A1800Product("Spectacles", DLC.VANILLA, ALL_REGIONS, 120030, ProductType.GOOD),
    A1800Product("Caoutchouc", DLC.VANILLA, ALL_REGIONS, 1010255, ProductType.GOOD),
    A1800Product("Penny Farthings", DLC.VANILLA, ALL_REGIONS, 1010245, ProductType.GOOD),
    A1800Product("Steam Motors", DLC.VANILLA, ALL_REGIONS, 1010224, ProductType.GOOD),
    A1800Product("Saltpetre", DLC.VANILLA, ALL_REGIONS, 1010232, ProductType.GOOD),
    A1800Product("Dynamite", DLC.VANILLA, ALL_REGIONS, 1010222, ProductType.GOOD),
    A1800Product("Advanced Weapons", DLC.VANILLA, ALL_REGIONS, 1010223, ProductType.GOOD),
    A1800Product("Gold Ore", DLC.VANILLA, ALL_REGIONS, 1010233, ProductType.GOOD),
    A1800Product("Gold", DLC.VANILLA, ALL_REGIONS, 1010249, ProductType.GOOD),
    A1800Product("Pocket Watches", DLC.VANILLA, ALL_REGIONS, 1010246, ProductType.GOOD),
    A1800Product("Filaments", DLC.VANILLA, ALL_REGIONS, 1010243, ProductType.GOOD),
    A1800Product("Light Bulbs", DLC.VANILLA, ALL_REGIONS, 1010208, ProductType.GOOD),
    A1800Product("Grapes", DLC.VANILLA, ALL_REGIONS, 120014, ProductType.GOOD),
    A1800Product("Champagne", DLC.VANILLA, ALL_REGIONS, 120016, ProductType.GOOD),
    A1800Product("Wood Veneers", DLC.VANILLA, ALL_REGIONS, 1010242, ProductType.GOOD),
    A1800Product("Pearls", DLC.VANILLA, ALL_REGIONS, 1010256, ProductType.GOOD),
    A1800Product("Jewellery", DLC.VANILLA, ALL_REGIONS, 1010250, ProductType.GOOD),
    A1800Product("Gramophones", DLC.VANILLA, ALL_REGIONS, 1010248, ProductType.GOOD),
    A1800Product("Chassis", DLC.VANILLA, ALL_REGIONS, 1010211, ProductType.GOOD),
    A1800Product("Steam Carriages", DLC.VANILLA, ALL_REGIONS, 1010225, ProductType.GOOD),

    A1800Product("Fish Oil", DLC.VANILLA, ALL_REGIONS, 120042, ProductType.GOOD),
    A1800Product("Plantains", DLC.VANILLA, ALL_REGIONS, 120041, ProductType.GOOD),
    A1800Product("Fried Plantains", DLC.VANILLA, ALL_REGIONS, 120033, ProductType.GOOD),
    A1800Product("Sugar Cane", DLC.VANILLA, ALL_REGIONS, 1010251, ProductType.GOOD),
    A1800Product("Rum", DLC.VANILLA, ALL_REGIONS, 1010257, ProductType.GOOD),
    A1800Product("Alpaca Wool", DLC.VANILLA, ALL_REGIONS, 120036, ProductType.GOOD),
    A1800Product("Ponchos", DLC.VANILLA, ALL_REGIONS, 120043, ProductType.GOOD),
    A1800Product("Corn", DLC.VANILLA, ALL_REGIONS, 120034, ProductType.GOOD),
    A1800Product("Tortillas", DLC.VANILLA, ALL_REGIONS, 120035, ProductType.GOOD),
    A1800Product("Coffee Beans", DLC.VANILLA, ALL_REGIONS, 120031, ProductType.GOOD),
    A1800Product("Coffee", DLC.VANILLA, ALL_REGIONS, 120032, ProductType.GOOD),
    A1800Product("Felt", DLC.VANILLA, ALL_REGIONS, 120044, ProductType.GOOD),
    A1800Product("Bombins", DLC.VANILLA, ALL_REGIONS, 120037, ProductType.GOOD),
    A1800Product("Oil", DLC.VANILLA, Region.NW, 1010566, ProductType.GOOD),
    A1800Product("Tobacco", DLC.VANILLA, ALL_REGIONS, 1010252, ProductType.GOOD),
    A1800Product("Cigars", DLC.VANILLA, ALL_REGIONS, 1010259, ProductType.GOOD),
    A1800Product("Cocoa", DLC.VANILLA, ALL_REGIONS, 1010254, ProductType.GOOD),
    A1800Product("Sugar", DLC.VANILLA, ALL_REGIONS, 1010239, ProductType.GOOD),
    A1800Product("Chocolate", DLC.VANILLA, ALL_REGIONS, 1010258, ProductType.GOOD),

    A1800Product("Market", DLC.VANILLA, Region.OW, 120020, ProductType.SERVICE),
    A1800Product("Pub", DLC.VANILLA, Region.OW, 1010349, ProductType.SERVICE),
    A1800Product("Church", DLC.VANILLA, Region.OW, 1010350, ProductType.SERVICE),
    A1800Product("School", DLC.VANILLA, Region.OW, 1010351, ProductType.SERVICE),
    A1800Product("Variety Theatre", DLC.VANILLA, Region.OW, 1010352, ProductType.SERVICE),
    A1800Product("Zoo", DLC.VANILLA, Region.OW, 601485, ProductType.SERVICE),
    A1800Product("University", DLC.VANILLA, Region.OW, 1010353, ProductType.SERVICE),
    A1800Product("Museum", DLC.VANILLA, Region.OW, 133535, ProductType.SERVICE),
    A1800Product("Electricity", DLC.VANILLA, Region.OW, 120022, ProductType.SERVICE),
    A1800Product("Bank", DLC.VANILLA, Region.OW, 1010356, ProductType.SERVICE),
    A1800Product("Members Club", DLC.VANILLA, Region.OW, 1010355, ProductType.SERVICE),
    A1800Product("World's Fair", DLC.VANILLA, Region.OW, 133536, ProductType.SERVICE),
    A1800Product("Market", DLC.VANILLA, Region.NW, 120020, ProductType.SERVICE),
    A1800Product("Chapel", DLC.VANILLA, Region.NW, 1010350, ProductType.SERVICE),
    A1800Product("Boxing Arena", DLC.VANILLA, Region.NW, 1010349, ProductType.SERVICE),

    ################################################################################################################
    ### SUNKEN_TREASURES                                                                                         ###
    ################################################################################################################
    A1800Product("Scrap", DLC.SUNKEN_TREASURES, ALL_REGIONS, 112518, ProductType.GOOD),
    A1800Product("Nice Scrap", DLC.SUNKEN_TREASURES, ALL_REGIONS, 112520, ProductType.GOOD),
    A1800Product("Special Scrap", DLC.SUNKEN_TREASURES, ALL_REGIONS, 112523, ProductType.GOOD),
]

_a1800_populations = [product for product in _a1800_products if product.type == ProductType.WORKFORCE]

# Assure populations only have a single region flag
for population in _a1800_products:
    if population.type == ProductType.WORKFORCE:
        assert population.region in Region.__members__.values(), \
            f"Population {population.name} has multiple regions: {population.region}"


class _Products:
    _initialized: bool = False

    def init(self, enabled_dlcs: set[DLC]) -> None:
        global _a1800_products, _a1800_populations

        self._a1800_products = [product for product in _a1800_products if product.dlc in enabled_dlcs]
        self._a1800_populations = [population for population in _a1800_populations if population.dlc in enabled_dlcs]

        self._initialized = True

    def get_products(self) -> Sequence[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return self._a1800_products

    def find_products(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return (product for product in self._a1800_products if product.name == name and region in product.region)

    def get_populations(self) -> Sequence[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return self._a1800_populations

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return (population for population in self._a1800_populations if population.name == name and region in population.region)


PRODUCTS = _Products()
