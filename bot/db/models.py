import datetime
from typing import Optional

from sqlalchemy import BigInteger, Date
from sqlalchemy.orm import Mapped, mapped_column

from bot.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    status: Mapped[bool] = mapped_column(default=True)
    schedule_status: Mapped[bool] = mapped_column(default=True)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    schedule_status: Mapped[bool] = mapped_column(default=True)


class WarStatistic(Base):
    __tablename__ = "war_statistics"

    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    day: Mapped[int]

    # Personnel
    personnel_units: Mapped[Optional[int]] = mapped_column(default=0)
    personnel_units_inc: Mapped[Optional[int]] = mapped_column(default=0)

    # Equipment
    tanks: Mapped[Optional[int]] = mapped_column(default=0)
    tanks_inc: Mapped[Optional[int]] = mapped_column(default=0)

    armoured_fighting_vehicles: Mapped[Optional[int]] = mapped_column(default=0)
    armoured_fighting_vehicles_inc: Mapped[Optional[int]] = mapped_column(default=0)

    artillery_systems: Mapped[Optional[int]] = mapped_column(default=0)
    artillery_systems_inc: Mapped[Optional[int]] = mapped_column(default=0)

    mlrs: Mapped[Optional[int]] = mapped_column(default=0)
    mlrs_inc: Mapped[Optional[int]] = mapped_column(default=0)

    aa_warfare_systems: Mapped[Optional[int]] = mapped_column(default=0)
    aa_warfare_systems_inc: Mapped[Optional[int]] = mapped_column(default=0)

    planes: Mapped[Optional[int]] = mapped_column(default=0)
    planes_inc: Mapped[Optional[int]] = mapped_column(default=0)

    helicopters: Mapped[Optional[int]] = mapped_column(default=0)
    helicopters_inc: Mapped[Optional[int]] = mapped_column(default=0)

    vehicles_fuel_tanks: Mapped[Optional[int]] = mapped_column(default=0)
    vehicles_fuel_tanks_inc: Mapped[Optional[int]] = mapped_column(default=0)

    warships_cutters: Mapped[Optional[int]] = mapped_column(default=0)
    warships_cutters_inc: Mapped[Optional[int]] = mapped_column(default=0)

    cruise_missiles: Mapped[Optional[int]] = mapped_column(default=0)
    cruise_missiles_inc: Mapped[Optional[int]] = mapped_column(default=0)

    uav_systems: Mapped[Optional[int]] = mapped_column(default=0)
    uav_systems_inc: Mapped[Optional[int]] = mapped_column(default=0)

    special_military_equip: Mapped[Optional[int]] = mapped_column(default=0)
    special_military_equip_inc: Mapped[Optional[int]] = mapped_column(default=0)

    atgm_srbm_systems: Mapped[Optional[int]] = mapped_column(default=0)
    atgm_srbm_systems_inc: Mapped[Optional[int]] = mapped_column(default=0)

    submarines: Mapped[Optional[int]] = mapped_column(default=0)
    submarines_inc: Mapped[Optional[int]] = mapped_column(default=0)
