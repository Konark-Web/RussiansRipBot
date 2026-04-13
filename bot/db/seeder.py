import asyncio
import logging
import aiohttp
from datetime import datetime

log = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from bot.config_loader import load_config
from bot.db.models import WarStatistic
from bot.db.repositories.statistics_repository import StatisticsRepository

API_URL = "https://russianwarship.rip/api/v2/statistics"

async def fetch_history(session: aiohttp.ClientSession, offset: int = 0):
    params = {"offset": offset, "limit": 50}
    timeout = aiohttp.ClientTimeout(total=30)
    async with session.get(API_URL, params=params, timeout=timeout) as response:
        response.raise_for_status()
        data = await response.json()
        return data["data"]["records"]

def map_record_to_db(record: dict) -> dict:
    stats = record["stats"]
    inc = record["increase"]
    
    return {
        "date": datetime.strptime(record["date"], "%Y-%m-%d").date(),
        "day": record["day"],
        "personnel_units": stats["personnel_units"],
        "personnel_units_inc": inc["personnel_units"],
        "tanks": stats["tanks"],
        "tanks_inc": inc["tanks"],
        "armoured_fighting_vehicles": stats["armoured_fighting_vehicles"],
        "armoured_fighting_vehicles_inc": inc["armoured_fighting_vehicles"],
        "artillery_systems": stats["artillery_systems"],
        "artillery_systems_inc": inc["artillery_systems"],
        "mlrs": stats["mlrs"],
        "mlrs_inc": inc["mlrs"],
        "aa_warfare_systems": stats["aa_warfare_systems"],
        "aa_warfare_systems_inc": inc["aa_warfare_systems"],
        "planes": stats["planes"],
        "planes_inc": inc["planes"],
        "helicopters": stats["helicopters"],
        "helicopters_inc": inc["helicopters"],
        "vehicles_fuel_tanks": stats["vehicles_fuel_tanks"],
        "vehicles_fuel_tanks_inc": inc["vehicles_fuel_tanks"],
        "warships_cutters": stats["warships_cutters"],
        "warships_cutters_inc": inc["warships_cutters"],
        "cruise_missiles": stats["cruise_missiles"],
        "cruise_missiles_inc": inc["cruise_missiles"],
        "uav_systems": stats["uav_systems"],
        "uav_systems_inc": inc["uav_systems"],
        "special_military_equip": stats["special_military_equip"],
        "special_military_equip_inc": inc["special_military_equip"],
        "atgm_srbm_systems": stats["atgm_srbm_systems"],
        "atgm_srbm_systems_inc": inc["atgm_srbm_systems"],
        "submarines": stats["submarines"],
        "submarines_inc": inc["submarines"],
    }

async def run_seeder():
    config = load_config()
    db_url = (
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}"
        f"@{config.db.host}/{config.db.db_name}"
    )
    
    # Force use localhost for seeder if needed
    if "rus_bot_db" in db_url:
        db_url = db_url.replace("rus_bot_db", "localhost:32705")

    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with aiohttp.ClientSession() as http:
        offset = 0
        total_inserted = 0
        
        while True:
            log.info("Fetching history with offset %d...", offset)
            records = await fetch_history(http, offset)
            if not records:
                break
            
            mapped_data = [map_record_to_db(r) for r in records]
            
            async with async_session() as db_session:
                repo = StatisticsRepository()
                await repo.insert_bulk(db_session, mapped_data)
            
            total_inserted += len(records)
            offset += 50
            
            # Small delay to respect API limits
            await asyncio.sleep(0.5)

        log.info("Seeding completed! Inserted %d days of history.", total_inserted)
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_seeder())
