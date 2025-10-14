from pydantic import BaseModel
from typing import Optional

class PaystubItem(BaseModel):
    net_pay: float
    ytd_gross: Optional[float] = None
    ytd_net: Optional[float] = None
    employer_name_on_stub: Optional[str] = None
    hours: Optional[float] = None
    taxes_withheld: Optional[float] = None
