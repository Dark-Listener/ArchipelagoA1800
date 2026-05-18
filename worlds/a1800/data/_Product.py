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
    A1800Product("Sea Travel", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Riot Control", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Healthcare", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Victory", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),

    A1800Product("Farmers", DLC.VANILLA, Region.OW, 15000000, ProductType.WORKFORCE),
    A1800Product("Workers", DLC.VANILLA, Region.OW, 15000001, ProductType.WORKFORCE),
    A1800Product("Artisans", DLC.VANILLA, Region.OW, 15000002, ProductType.WORKFORCE),

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

    A1800Product("Market", DLC.VANILLA, Region.OW, 120020, ProductType.SERVICE),
    A1800Product("Pub", DLC.VANILLA, Region.OW, 1010349, ProductType.SERVICE),
    A1800Product("Church", DLC.VANILLA, Region.OW, 1010350, ProductType.SERVICE),
    A1800Product("School", DLC.VANILLA, Region.OW, 1010351, ProductType.SERVICE),
]


def get_products() -> Sequence[A1800Product]:
    global _a1800_products
    return _a1800_products


def find_products(name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
    global _a1800_products
    return (product for product in _a1800_products if product.name == name and region in product.region)


_a1800_populations = [product for product in _a1800_products if product.type == ProductType.WORKFORCE]

# Assure populations only have a single region flag
for population in _a1800_populations:
    assert population.region in Region.__members__.values()


def find_populations(name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
    global _a1800_populations
    return (population for population in _a1800_populations if population.name == name and region in population.region)
