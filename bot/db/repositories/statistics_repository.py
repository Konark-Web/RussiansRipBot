import datetime

from sqlalchemy import extract, insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import WarStatistic

INC_FIELDS = [
    "personnel_units_inc",
    "tanks_inc",
    "armoured_fighting_vehicles_inc",
    "artillery_systems_inc",
    "mlrs_inc",
    "aa_warfare_systems_inc",
    "planes_inc",
    "helicopters_inc",
    "vehicles_fuel_tanks_inc",
    "warships_cutters_inc",
    "cruise_missiles_inc",
    "uav_systems_inc",
    "special_military_equip_inc",
    "atgm_srbm_systems_inc",
    "submarines_inc",
]


class StatisticsRepository:
    async def insert_bulk(self, session: AsyncSession, data: list[dict]):
        if not data:
            return
        await session.execute(insert(WarStatistic).values(data))
        await session.commit()

    async def get_count(self, session: AsyncSession) -> int:
        result = await session.execute(select(func.count(WarStatistic.date)))
        return result.scalar() or 0

    async def get_max_increments(self, session: AsyncSession) -> dict[str, int]:
        cols = [func.max(getattr(WarStatistic, f)).label(f) for f in INC_FIELDS]
        result = await session.execute(select(*cols))
        row = result.one()
        return {f: (getattr(row, f) or 0) for f in INC_FIELDS}

    async def get_averages(self, session: AsyncSession) -> dict[str, float]:
        cols = [func.avg(getattr(WarStatistic, f)).label(f) for f in INC_FIELDS]
        result = await session.execute(select(*cols))
        row = result.one()
        return {f: round(getattr(row, f) or 0, 1) for f in INC_FIELDS}

    async def get_available_years(self, session: AsyncSession) -> list[int]:
        """Returns sorted list of years present in the table."""
        year_col = extract("year", WarStatistic.date)
        stmt = select(year_col.label("year")).group_by(year_col).order_by(year_col)
        result = await session.execute(stmt)
        return [int(row.year) for row in result.all()]

    async def get_monthly_stats(
        self, session: AsyncSession, field: str, year: int
    ) -> dict[int, int]:
        """Returns {month: total_inc} for a given field and year."""
        col = getattr(WarStatistic, field)
        month_col = extract("month", WarStatistic.date)
        year_col = extract("year", WarStatistic.date)
        stmt = (
            select(month_col.label("month"), func.sum(col).label("total"))
            .where(year_col == year)
            .group_by(month_col)
            .order_by(month_col)
        )
        result = await session.execute(stmt)
        return {int(row.month): int(row.total or 0) for row in result.all()}

    async def get_latest_totals(self, session: AsyncSession) -> dict[str, int]:
        """Returns the cumulative totals from the most recent record."""
        cumulative_fields = [f.removesuffix("_inc") for f in INC_FIELDS]
        stmt = select(WarStatistic).order_by(WarStatistic.date.desc()).limit(1)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return {}
        return {f: (getattr(row, f) or 0) for f in cumulative_fields}

    async def get_avg_increments_last_days(
        self, session: AsyncSession, days: int = 30
    ) -> dict[str, float]:
        """Returns average daily increments over the last N days."""
        from sqlalchemy import desc
        subq = (
            select(WarStatistic)
            .order_by(desc(WarStatistic.date))
            .limit(days)
            .subquery()
        )
        cols = [func.avg(subq.c[f]).label(f) for f in INC_FIELDS]
        result = await session.execute(select(*cols))
        row = result.one()
        return {f: float(getattr(row, f) or 0) for f in INC_FIELDS}

    async def get_records(
        self, session: AsyncSession
    ) -> list[tuple[str, int, datetime.date]]:
        """For each inc field returns (field_name, max_value, date_of_record).
        Uses UNION ALL — single round-trip instead of N queries."""
        from sqlalchemy import literal, union_all

        subqueries = [
            select(
                literal(field).label("field"),
                getattr(WarStatistic, field).label("value"),
                WarStatistic.date,
            )
            .order_by(getattr(WarStatistic, field).desc())
            .limit(1)
            for field in INC_FIELDS
        ]
        result = await session.execute(union_all(*subqueries))
        return [
            (row.field, row.value, row.date)
            for row in result.all()
            if row.value
        ]
