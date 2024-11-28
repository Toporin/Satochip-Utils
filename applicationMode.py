from enum import Enum


class ApplicationMode(Enum):
    Normal = 0
    FactoryResetV1 = 1
    FactoryResetV2 = 2
    SeedkeeperBackup = 3