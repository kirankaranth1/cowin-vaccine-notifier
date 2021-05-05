# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = vaccine_centers_from_dict(json.loads(json_string))

from enum import Enum
from uuid import UUID
from typing import List, Any, TypeVar, Callable, Type, cast
from datetime import datetime
import dateutil.parser
import math


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    try:
        x = math.floor(x)
    except:
        print("floor failed")
    if x < 1:
        x = 0
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Session:
    session_id: UUID
    date: str
    available_capacity: int
    min_age_limit: int
    vaccine: str
    slots: List[str]

    def __init__(self, session_id: UUID, date: str, available_capacity: int, min_age_limit: int, vaccine: str, slots: List[str]) -> None:
        self.session_id = session_id
        self.date = date
        self.available_capacity = available_capacity
        self.min_age_limit = min_age_limit
        self.vaccine = vaccine
        self.slots = slots

    @staticmethod
    def from_dict(obj: Any) -> 'Session':
        assert isinstance(obj, dict)
        session_id = UUID(obj.get("session_id"))
        date = from_str(obj.get("date"))
        available_capacity = from_int(obj.get("available_capacity"))
        min_age_limit = from_int(obj.get("min_age_limit"))
        vaccine = from_str(obj.get("vaccine"))
        slots = from_list(str, obj.get("slots"))
        return Session(session_id, date, available_capacity, min_age_limit, vaccine, slots)

    def to_dict(self) -> dict:
        result: dict = {}
        result["session_id"] = str(self.session_id)
        result["date"] = from_str(self.date)
        result["available_capacity"] = from_int(self.available_capacity)
        result["min_age_limit"] = from_int(self.min_age_limit)
        result["vaccine"] = from_str(self.vaccine)
        #result["slots"] = from_list(lambda x: to_enum(Slot, x), self.slots)
        return result


class Center:
    center_id: int
    name: str
    state_name: str
    district_name: str
    block_name: str
    pincode: int
    lat: int
    long: int
    center_from: datetime
    to: datetime
    fee_type: str
    sessions: List[Session]
    total_capacity: int
    min_age_cumulative: int
    vaccine: str

    def __init__(self, center_id: int, name: str, state_name: str, district_name: str, block_name: str, pincode: int, lat: int, long: int, center_from: datetime, to: datetime, fee_type: str, sessions: List[Session]) -> None:
        self.center_id = center_id
        self.name = name
        self.state_name = state_name
        self.district_name = district_name
        self.block_name = block_name
        self.pincode = pincode
        self.lat = lat
        self.long = long
        self.center_from = center_from
        self.to = to
        self.fee_type = fee_type
        self.sessions = sessions
        self.total_capacity = sum(x.available_capacity for x in sessions)
        self.min_age_cumulative = min(x.min_age_limit for x in sessions)
        vaccines = set()
        for s in sessions:
            if s.vaccine and s.vaccine != '':
                vaccines.add(s.vaccine)
        if len(vaccines) > 0:
            self.vaccine = ','.join(list(vaccines))
        else:
            self.vaccine = 'No data'


    @staticmethod
    def from_dict(obj: Any) -> 'Center':
        assert isinstance(obj, dict)
        center_id = from_int(obj.get("center_id"))
        name = from_str(obj.get("name"))
        state_name = from_str(obj.get("state_name"))
        district_name = from_str(obj.get("district_name"))
        block_name = from_str(obj.get("block_name"))
        pincode = from_int(obj.get("pincode"))
        lat = from_int(obj.get("lat"))
        long = from_int(obj.get("long"))
        center_from = from_datetime(obj.get("from"))
        to = from_datetime(obj.get("to"))
        fee_type = from_str(obj.get("fee_type"))
        sessions = from_list(Session.from_dict, obj.get("sessions"))
        return Center(center_id, name, state_name, district_name, block_name, pincode, lat, long, center_from, to, fee_type, sessions)

    def to_dict(self) -> dict:
        result: dict = {}
        result["center_id"] = from_int(self.center_id)
        result["name"] = from_str(self.name)
        result["state_name"] = from_str(self.state_name)
        result["district_name"] = from_str(self.district_name)
        result["block_name"] = from_str(self.block_name)
        result["pincode"] = from_int(self.pincode)
        result["lat"] = from_int(self.lat)
        result["long"] = from_int(self.long)
        result["from"] = self.center_from.isoformat()
        result["to"] = self.to.isoformat()
        result["fee_type"] = from_str(self.fee_type)
        result["sessions"] = from_list(lambda x: to_class(Session, x), self.sessions)
        return result


class VaccineCenters:
    centers: List[Center]

    def __init__(self, centers: List[Center]) -> None:
        self.centers = centers

    @staticmethod
    def from_dict(obj: Any) -> 'VaccineCenters':
        assert isinstance(obj, dict)
        centers = from_list(Center.from_dict, obj.get("centers"))
        return VaccineCenters(centers)

    def to_dict(self) -> dict:
        result: dict = {}
        result["centers"] = from_list(lambda x: to_class(Center, x), self.centers)
        return result


def vaccine_centers_from_dict(s: Any) -> VaccineCenters:
    return VaccineCenters.from_dict(s)


def vaccine_centers_to_dict(x: VaccineCenters) -> Any:
    return to_class(VaccineCenters, x)
