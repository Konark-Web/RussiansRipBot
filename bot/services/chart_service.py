import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

_BLUE = "#0057B8"
_YELLOW = "#FFD700"
_BG = "#1a1a2e"
_TEXT = "#e0e0e0"
_GRID = "#2a2a4a"

_MONTHS_UK = ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер",
               "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"]


class ChartService:
    def generate_monthly_chart(
        self, label: str, year: int, monthly_data: dict[int, int]
    ) -> io.BytesIO:
        months = list(monthly_data.keys())
        values = list(monthly_data.values())
        month_labels = [_MONTHS_UK[m - 1] for m in months]

        fig, ax = plt.subplots(figsize=(11, 5))
        fig.patch.set_facecolor(_BG)
        ax.set_facecolor(_BG)

        # Fill under line
        ax.fill_between(months, values, alpha=0.15, color=_BLUE)

        # Line + markers
        ax.plot(months, values, color=_BLUE, linewidth=2.5, zorder=3)
        ax.scatter(months, values, color=_YELLOW, s=60, zorder=4)

        # Value labels above each point
        def fmt(v: int) -> str:
            if v >= 1_000_000:
                return f"{v / 1_000_000:.1f}M"
            if v >= 1_000:
                return f"{v / 1_000:.1f}K"
            return str(v)

        for m, v in zip(months, values):
            ax.text(
                m, v + max(values) * 0.03,
                fmt(v),
                ha="center", va="bottom",
                color=_TEXT, fontsize=9, fontweight="bold",
            )

        ax.set_title(f"{label} — {year}", color=_TEXT, fontsize=14, fontweight="bold", pad=12)
        ax.set_xticks(months)
        ax.set_xticklabels(month_labels, color=_TEXT, fontsize=11)
        ax.tick_params(axis="y", colors=_TEXT)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(int(x))))
        ax.set_xlim(months[0] - 0.3, months[-1] + 0.3)
        ax.set_ylim(0, max(values) * 1.2)

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis="y", color=_GRID, linestyle="--", linewidth=0.7, zorder=0)
        ax.grid(axis="x", color=_GRID, linestyle=":", linewidth=0.5, zorder=0)

        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=_BG, dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf
