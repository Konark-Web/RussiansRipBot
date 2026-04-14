from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

STATS_URL = "https://russianwarship.rip/api/v2/statistics/latest"
HISTORY_URL = "https://russianwarship.rip/api/v2/statistics"


class StatisticsService:
    """Fetches war statistics from the public API (non-blocking for the event loop)."""

    async def fetch_daily_message_html(self, max_increments: dict[str, int] | None = None) -> str:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as http:
            async with http.get(STATS_URL) as response:
                response.raise_for_status()
                body: dict[str, Any] = await response.json()
        return self._format_statistics_html(body["data"], max_increments or {})

    async def fetch_weekly_message_html(self) -> str:
        # We need the last 7 days of increases.
        now = datetime.now(timezone.utc)
        date_to = now.strftime("%Y-%m-%d")
        date_from = (now - timedelta(days=6)).strftime("%Y-%m-%d")

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as http:
            params = {"date_from": date_from, "date_to": date_to}
            async with http.get(HISTORY_URL, params=params) as response:
                response.raise_for_status()
                body: dict[str, Any] = await response.json()

        records = body["data"]["records"]
        return self._format_weekly_statistics_html(records, date_from, date_to)

    def _format_statistics_html(self, response_data: dict[str, Any], max_increments: dict[str, int]) -> str:
        day_war = response_data["day"]
        date = response_data["date"]
        stats = response_data["stats"]
        inc = response_data["increase"]

        def get_stat(key: str, label: str) -> str:
            val = stats.get(key, 0)
            increase = inc.get(key, 0)
            inc_text = f" (+ {increase})" if increase else ""
            return f"{label}: {val}{inc_text}"

        names_for_rus = [
            "Зробило жест доброї волі ☠️",
            "Хороших русскіх ☠️",
            "На концерті Кобзона ☠️",
            "Особового складу ☠️",
        ]
        rus_label = random.choice(names_for_rus)

        lines = [
            f"<b>{day_war} ДЕНЬ ВІЙНИ ({date})</b>",
            "",
            get_stat("personnel_units", rus_label),
            get_stat("tanks", "Танків"),
            get_stat("armoured_fighting_vehicles", "ББМ"),
            get_stat("artillery_systems", "Арт. систем"),
            get_stat("mlrs", "РСЗВ"),
            get_stat("aa_warfare_systems", "Засобів ППО"),
            get_stat("planes", "Літаків"),
            get_stat("helicopters", "Гелікоптерів"),
            get_stat("vehicles_fuel_tanks", "Автотехніки"),
            get_stat("warships_cutters", "Морського транспорту"),
            get_stat("uav_systems", "БПЛА"),
            get_stat("special_military_equip", "Спец. техніки"),
            get_stat("atgm_srbm_systems", "ОТРК/ТРК"),
            get_stat("cruise_missiles", "Крилатих ракет"),
            "",
            "<i>Не забувайте донатити ЗСУ! -> /donate</i>",
            "<i>СЛАВА УКРАЇНІ 🇺🇦, СЛАВА НАЦІЇ і піздєц російській федерації 🐖</i>",
        ]

        records = self._detect_records(inc, max_increments)
        if records:
            lines.append("")
            lines.extend(records)

        return "\n".join(lines)

    # Used in daily stats: "🔥 РЕКОРД! Знищено найбільшу кількість <label>: 34!"
    _RECORD_LABELS: dict[str, str] = {
        "personnel_units_inc": "хороших русських за день",
        "tanks_inc": "танків за день",
        "armoured_fighting_vehicles_inc": "ББМ за день",
        "artillery_systems_inc": "арт. систем за день",
        "mlrs_inc": "РСЗВ за день",
        "aa_warfare_systems_inc": "засобів ППО за день",
        "planes_inc": "літаків за день",
        "helicopters_inc": "гелікоптерів за день",
        "vehicles_fuel_tanks_inc": "одиниць автотехніки за день",
        "warships_cutters_inc": "кораблів та катерів за день",
        "cruise_missiles_inc": "крилатих ракет за день",
        "uav_systems_inc": "БПЛА за день",
        "special_military_equip_inc": "одиниць спец. техніки за день",
        "atgm_srbm_systems_inc": "ПТРК/ОТРК за день",
        "submarines_inc": "підводних човнів за день",
    }

    # Used in /records and /average: "34 — танків"
    _CATEGORY_LABELS: dict[str, str] = {
        "personnel_units_inc": "хороших русських",
        "tanks_inc": "танків",
        "armoured_fighting_vehicles_inc": "ББМ",
        "artillery_systems_inc": "арт. систем",
        "mlrs_inc": "РСЗВ",
        "aa_warfare_systems_inc": "засобів ППО",
        "planes_inc": "літаків",
        "helicopters_inc": "гелікоптерів",
        "vehicles_fuel_tanks_inc": "одиниць автотехніки",
        "warships_cutters_inc": "кораблів та катерів",
        "cruise_missiles_inc": "крилатих ракет",
        "uav_systems_inc": "БПЛА",
        "special_military_equip_inc": "одиниць спец. техніки",
        "atgm_srbm_systems_inc": "ПТРК/ОТРК",
        "submarines_inc": "підводних човнів",
    }

    def _detect_records(self, inc: dict[str, Any], max_increments: dict[str, int]) -> list[str]:
        if not max_increments:
            return []

        def fmt(val: int) -> str:
            return f"{val:,}".replace(",", " ")

        records = []
        for db_key, label in self._RECORD_LABELS.items():
            api_key = db_key.removesuffix("_inc")
            today_val = inc.get(api_key, 0)
            prev_max = max_increments.get(db_key, 0)
            if today_val > 0 and today_val >= prev_max:
                records.append(f"🔥 <b>РЕКОРД!</b> Знищено найбільшу кількість {label}: <b>{fmt(today_val)}</b>!")

        return records

    def format_averages_html(self, averages: dict[str, float]) -> str:
        def fmt(val: float) -> str:
            return f"{int(val):,}".replace(",", " ")

        lines = [
            "<b>📊 СЕРЕДНІ ВТРАТИ ЗА ДЕНЬ</b>",
            "<i>Середньодобові втрати армії рф за весь час:</i>",
            "",
        ]
        for field, label in self._CATEGORY_LABELS.items():
            val = averages.get(field, 0)
            if val > 0:
                lines.append(f"<b>{fmt(val)}</b> — {label}")

        lines.extend(["", "<i>СЛАВА ЗСУ! 🇺🇦</i>"])
        return "\n".join(lines)

    def format_records_html(self, records: list[tuple[str, int, object]]) -> str:
        def fmt(val: int) -> str:
            return f"{val:,}".replace(",", " ")

        lines = ["<b>🏆 РЕКОРДИ ЗА ВЕСЬ ЧАС</b>", "<i>Найбільші втрати за один день:</i>", ""]
        for field, value, date in records:
            label = self._CATEGORY_LABELS.get(field)
            if label:
                lines.append(f"<b>{fmt(value)}</b> — {label} ({date})")

        lines.extend(["", "<i>СЛАВА ЗСУ! 🇺🇦</i>"])
        return "\n".join(lines)

    # Next round-number milestones per cumulative field
    _MILESTONES: dict[str, list[int]] = {
        "personnel_units":              [1_000_000, 1_250_000, 1_500_000, 1_750_000, 2_000_000,
                                         2_500_000, 3_000_000, 4_000_000, 5_000_000],
        "tanks":                        [10_000, 12_000, 15_000, 20_000, 25_000, 30_000, 50_000],
        "armoured_fighting_vehicles":   [25_000, 30_000, 40_000, 50_000, 75_000, 100_000],
        "artillery_systems":            [25_000, 30_000, 40_000, 50_000, 75_000, 100_000],
        "mlrs":                         [1_500, 2_000, 3_000, 4_000, 5_000, 10_000],
        "aa_warfare_systems":           [1_000, 1_500, 2_000, 3_000, 5_000, 10_000],
        "planes":                       [500, 750, 1_000, 1_500, 2_000, 3_000],
        "helicopters":                  [400, 500, 750, 1_000, 1_500, 2_000],
        "uav_systems":                  [25_000, 30_000, 50_000, 75_000, 100_000, 200_000, 500_000],
        "cruise_missiles":              [3_000, 4_000, 5_000, 7_500, 10_000, 15_000],
        "vehicles_fuel_tanks":          [50_000, 75_000, 100_000, 150_000, 200_000],
        "special_military_equip":       [10_000, 15_000, 20_000, 30_000, 50_000],
        "warships_cutters":             [50, 100, 150, 200, 300],
        "submarines":                   [5, 10, 15, 20],
    }

    _MILESTONE_LABELS: dict[str, str] = {
        "personnel_units":              "хороших русських",
        "tanks":                        "танків",
        "armoured_fighting_vehicles":   "ББМ",
        "artillery_systems":            "арт. систем",
        "mlrs":                         "РСЗВ",
        "aa_warfare_systems":           "засобів ППО",
        "planes":                       "літаків",
        "helicopters":                  "гелікоптерів",
        "uav_systems":                  "БПЛА",
        "cruise_missiles":              "крилатих ракет",
        "vehicles_fuel_tanks":          "одиниць автотехніки",
        "special_military_equip":       "одиниць спец. техніки",
        "warships_cutters":             "кораблів та катерів",
        "submarines":                   "підводних човнів",
    }

    def format_milestones_html(
        self,
        totals: dict[str, int],
        avg_inc: dict[str, float],
    ) -> str:
        def fmt(val: int) -> str:
            return f"{val:,}".replace(",", " ")

        lines = [
            "<b>🎯 ПРОГНОЗ ДО ЮВІЛЕЇВ</b>",
            "<i>Скільки залишилось до круглих чисел (темп: останні 30 днів):</i>",
            "",
        ]

        found = False
        for field, milestones in self._MILESTONES.items():
            current = totals.get(field, 0)
            inc_field = f"{field}_inc"
            daily_avg = avg_inc.get(inc_field, 0)
            label = self._MILESTONE_LABELS.get(field, field)

            next_milestone = next((m for m in milestones if m > current), None)
            if next_milestone is None:
                continue

            remaining = next_milestone - current
            if daily_avg > 0:
                days_left = int(remaining / daily_avg)
                pace_text = f"~{days_left} днів"
            else:
                pace_text = "темп невідомий"

            lines.append(
                f"До <b>{fmt(next_milestone)}</b> {label}: "
                f"залишилось <b>{fmt(remaining)}</b> "
                f"<i>({pace_text})</i>"
            )
            found = True

        if not found:
            lines.append("<i>Всі відомі ювілеї вже досягнуті 🎉</i>")

        lines.extend(["", "<i>СЛАВА ЗСУ! 🇺🇦</i>"])
        return "\n".join(lines)

    def _format_weekly_statistics_html(self, records: list, date_from: str, date_to: str) -> str:
        weekly_inc = {}

        # Categories to sum up
        categories = [
            ("personnel_units", "особового складу"),
            ("tanks", "танків"),
            ("armoured_fighting_vehicles", "ББМ"),
            ("artillery_systems", "арт. систем"),
            ("mlrs", "РСЗВ"),
            ("aa_warfare_systems", "засобів ППО"),
            ("planes", "літаків"),
            ("helicopters", "гелікоптерів"),
            ("vehicles_fuel_tanks", "автотехніки та автоцистерн"),
            ("warships_cutters", "кораблів та катерів"),
            ("uav_systems", "БПЛА"),
            ("special_military_equip", "спец. техніки"),
            ("submarines", "підводних човнів"),
            ("cruise_missiles", "крилатих ракет"),
        ]

        for record in records:
            inc = record["increase"]
            for key, _ in categories:
                weekly_inc[key] = weekly_inc.get(key, 0) + inc.get(key, 0)

        def fmt(val: int) -> str:
            return f"{val:,}".replace(",", " ")

        lines = [
            f"<b>📊 ТИЖНЕВИЙ ЗВІТ ({date_from} — {date_to})</b>",
            "<i>За цей тиждень армія рф стала меншою на:</i>",
            "",
        ]

        for key, label in categories:
            val = weekly_inc.get(key, 0)
            if val > 0:
                lines.append(f"<b>{fmt(val)}</b> — {label}")

        lines.extend([
            "",
            "<i>СЛАВА ЗСУ! 🇺🇦</i>",
            "<i>Донат на ЗСУ наближає перемогу -> /donate</i>"
        ])

        return "\n".join(lines)
