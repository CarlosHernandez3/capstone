from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date

class Employment(BaseModel):
    employer_name: str
    start_date: Optional[date] = None
    pay_frequency: Optional[Literal["weekly","biweekly","semimonthly","monthly"]] = None
    annual_salary_claimed: Optional[float] = None
