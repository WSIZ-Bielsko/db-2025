from pydantic import BaseModel


# PremiumACSystem

class Room(BaseModel):
    # table name = roomz
    room_name: str  # acts as primary key
    capacity_seats: int
    ac_power_kw: float
    room_area: float
    cooling_cost_per_hour: float
