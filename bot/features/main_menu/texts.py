import html


def build_greeting_text(first_name: str | None) -> str:
    name = (first_name or "друг").strip() or "друг"
    safe_name = html.escape(name)
    return (
        f"👋 Добро пожаловать, {safe_name}!\n"
        "🤖 Я - бот финансовый помощник!\n\n"
        "❤️ Приятного использования!"
    )


def build_home_text(budget_name: str) -> str:
    safe_name = html.escape(budget_name)
    return f"<b>🏠 HOME</b>\n<i>💼 Бюджет \"{safe_name}\"</i>"


def build_first_run_text() -> str:
    return "<b>Первый запуск</b>\nЧто делаем?"


def build_section_text(title: str, hint: str) -> str:
    return f"<b>{html.escape(title)}</b>\n{html.escape(hint)}"


def build_breadcrumbs(prefix: str, current: str) -> str:
    return f"<i>{html.escape(prefix)} / </i><b><i>{html.escape(current)}</i></b>"
