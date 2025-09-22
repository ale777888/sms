"""主菜单按钮处理。"""
from aiogram import Router
from aiogram.types import Message

from ..keyboards.countries import build_country_keyboard
from ..keyboards.projects import build_project_keyboard
from ..keyboards.orders import build_order_actions

router = Router(name="menu")


async def _mock_projects() -> list[tuple[int, str, float]]:
    return [
        (1001, "Telegram", 1.5),
        (1007, "Facebook", 1.8),
        (1013, "探探", 1.2),
        (1025, "Bumble", 2.0),
    ]


async def _mock_countries() -> list[tuple[str, str]]:
    return [
        ("chn", "中国"),
        ("usa", "美国"),
        ("vnm", "越南"),
        ("phl", "菲律宾"),
        ("mys", "马来西亚"),
        ("jpn", "日本"),
        ("tha", "泰国"),
    ]


@router.message(lambda msg: msg.text == "📲 取号")
async def handle_pick_country(message: Message) -> None:
    countries = await _mock_countries()
    await message.answer("请选择国家：", reply_markup=build_country_keyboard(countries))


@router.message(lambda msg: msg.text == "🧩 项目")
async def handle_list_projects(message: Message) -> None:
    projects = await _mock_projects()
    await message.answer(
        "请选择项目：",
        reply_markup=build_project_keyboard(projects, currency="CNY"),
    )


@router.message(lambda msg: msg.text == "🧾 订单")
async def handle_orders(message: Message) -> None:
    await message.answer(
        "暂无订单示例，后续阶段将接入真实数据。",
        reply_markup=build_order_actions(order_id=1, status="created"),
    )


@router.message(lambda msg: msg.text == "📩 收码")
async def handle_collect(message: Message) -> None:
    await message.answer("请选择需要收码的订单（功能开发中）。")


@router.message(lambda msg: msg.text == "💳 余额")
async def handle_wallet(message: Message) -> None:
    await message.answer("余额功能开发中，下一阶段将展示真实余额与明细。")


@router.message(lambda msg: msg.text == "🛒 充值")
async def handle_recharge(message: Message) -> None:
    await message.answer("充值申请功能将在下一阶段实现，包括 USDT(TRC20) 指引。")


@router.message(lambda msg: msg.text == "🌍 国家")
async def handle_country(message: Message) -> None:
    countries = await _mock_countries()
    await message.answer("常用国家：", reply_markup=build_country_keyboard(countries))


@router.message(lambda msg: msg.text == "🆘 帮助")
async def handle_help_hint(message: Message) -> None:
    await message.answer(
        "帮助中心建设中，请稍后再试。",
    )
