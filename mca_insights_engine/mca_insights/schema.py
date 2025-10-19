from dataclasses import dataclass
from typing import Optional

@dataclass
class Company:
    CIN: str
    Company_Name: str
    Company_Class: str
    Date_of_Incorporation: str
    Authorized_Capital: float
    Paidup_Capital: float
    Company_Status: str
    NIC_Code: str
    Registered_Address: str
    RoC: str
    State: str
