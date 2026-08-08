from enum import Enum


class PlanCode(str, Enum):
    GUEST = "GUEST"
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class BillingInterval(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
