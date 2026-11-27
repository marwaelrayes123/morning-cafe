"""Page views. Kept thin: read request -> call a service -> render or redirect."""

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.menu.services import MenuService
from apps.ordering.builder import DraftError
from apps.orders.models import Order
from apps.orders.services import OrderService
from apps.payments.gateway import APPROVED_TEST_CARD, DECLINED_TEST_CARD
from apps.payments.models import Payment
from apps.payments.services import PaymentService

from .draft_session import DraftSession
from .forms import PaymentForm

PREP_STAGES = [
    "Grinding the beans",
    "Pulling the espresso",
    "Steaming the milk",
    "Adding the finishing touch",
]


def home(request):
    """Welcome page: short intro and a button to the menu."""
    steps = [
        ("☕", "Pick a coffee", "Choose your favourite and how you like it."),
        ("🥛", "Make it yours", "Pick your milk, a syrup and the size of your cup."),
        ("💳", "Pay (pretend)", "Check out with a fake card. No real money."),
    ]
    return render(request, "web/home.html", {"steps": steps})


# --- Menu -------------------------------------------------------------------


def menu(request):
    """Step 1: all coffee types."""
    return render(request, "web/menu.html", {"coffees": MenuService.coffees()})


def coffee_detail(request, slug):
    """Step 2: the sub-categories (variants) of one coffee type."""
    coffee = get_object_or_404(MenuService.coffee_with_variants(), slug=slug)
    return render(request, "web/coffee.html", {"coffee": coffee, "variants": coffee.available_variants})


# --- Building the order (kept in the session) --------------------------------
# Order of steps: variant -> milk (if it contains milk) -> syrup (if allowed) -> size -> review.


def _next_step(variant, selection) -> str:
    """The first step the customer still has to do."""
    if variant.contains_milk and not selection.milk:
        return "web:order_milk"
    if variant.allows_syrup and selection.syrup is None:
        return "web:order_syrup"
    if not selection.size:
        return "web:order_size"
    return "web:order_review"


def _current_variant(selection):
    return MenuService.variants().filter(slug=selection.variant).first()


@require_POST
def order_start(request):
    """A variant was chosen: start a new draft and go to the next step."""
    variant = get_object_or_404(MenuService.variants(), slug=request.POST.get("variant"))
    draft = DraftSession(request.session)
    draft.start(variant.slug)
    return redirect(_next_step(variant, draft.get()))


@require_http_methods(["GET", "POST"])
def order_milk(request):
    """Step 3a: type of milk (only for coffees that contain milk)."""
    draft = DraftSession(request.session)
    variant = _current_variant(draft.get())
    if variant is None:
        return _restart(request, "Please choose a coffee first.")
    if not variant.contains_milk:
        return redirect(_next_step(variant, draft.get()))

    if request.method == "POST":
        milk = MenuService.milks().filter(slug=request.POST.get("milk")).first()
        if milk is None:
            messages.error(request, "Please choose a type of milk.")
            return redirect("web:order_milk")
        draft.set_milk(milk.slug)
        return redirect(_next_step(variant, draft.get()))

    return render(request, "web/milk.html", {"variant": variant, "milks": MenuService.milks()})


@require_http_methods(["GET", "POST"])
def order_syrup(request):
    """Step 3b: optional flavour syrup."""
    draft = DraftSession(request.session)
    selection = draft.get()
    variant = _current_variant(selection)
    if variant is None:
        return _restart(request, "Please choose a coffee first.")
    if not variant.allows_syrup:
        return redirect(_next_step(variant, selection))
    if variant.contains_milk and not selection.milk:
        return redirect("web:order_milk")

    if request.method == "POST":
        slug = request.POST.get("syrup", "")
        if slug and not MenuService.syrups().filter(slug=slug).exists():
            messages.error(request, "Please choose a syrup.")
            return redirect("web:order_syrup")
        draft.set_syrup(slug)  # "" means no syrup
        return redirect(_next_step(variant, draft.get()))

    context = {"variant": variant, "syrups": MenuService.syrups(), "selected": selection.syrup}
    return render(request, "web/syrup.html", context)


@require_http_methods(["GET", "POST"])
def order_size(request):
    """Step 3c: cup size."""
    draft = DraftSession(request.session)
    selection = draft.get()
    variant = _current_variant(selection)
    if variant is None:
        return _restart(request, "Please choose a coffee first.")
    previous = _next_step(variant, selection)
    if previous in ("web:order_milk", "web:order_syrup"):
        return redirect(previous)

    if request.method == "POST":
        size = MenuService.sizes().filter(slug=request.POST.get("size")).first()
        if size is None:
            messages.error(request, "Please choose a size.")
            return redirect("web:order_size")
        draft.set_size(size.slug)
        return redirect("web:order_review")

    context = {
        "variant": variant,
        "milk": MenuService.milks().filter(slug=selection.milk).first(),
        "syrup": MenuService.syrups().filter(slug=selection.syrup).first() if selection.syrup else None,
        "sizes": MenuService.sizes(),
    }
    return render(request, "web/size.html", context)


@require_http_methods(["GET", "POST"])
def order_review(request):
    """Step 4: tell the price. "Agree & pay" places the order."""
    draft = DraftSession(request.session)
    selection = draft.get()
    try:
        priced = OrderService.prepare(selection.variant, selection.milk, selection.size, selection.syrup)
    except DraftError as error:
        return _restart(request, str(error))

    if request.method == "POST":
        order = OrderService.place_order(priced)
        draft.clear()
        return redirect("web:order_pay", number=order.number)

    return render(request, "web/review.html", {"priced": priced})


# --- Paying and picking up -----------------------------------------------------


@require_http_methods(["GET", "POST"])
def order_pay(request, number):
    """Step 5: fake card payment."""
    order = get_object_or_404(Order, number=number)
    if order.is_paid:
        return redirect("web:order_preparing", number=order.number)

    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment = PaymentService().pay(
            order,
            customer_name=form.cleaned_data["customer_name"],
            card_number=form.cleaned_data["card_number"],
        )
        if payment.status == Payment.Status.APPROVED:
            return redirect("web:order_preparing", number=order.number)
        form.add_error(None, "Your card was declined. Please try another card.")

    context = {
        "order": order,
        "form": form,
        "approved_card": _pretty_card(APPROVED_TEST_CARD),
        "declined_card": _pretty_card(DECLINED_TEST_CARD),
    }
    return render(request, "web/pay.html", context)


def order_preparing(request, number):
    """Step 6a: animation while the barista makes the coffee."""
    order = get_object_or_404(Order, number=number)
    if not order.is_paid:
        return redirect("web:order_pay", number=order.number)
    if order.is_ready():
        return redirect("web:order_ready", number=order.number)

    total = settings.COFFEE_PREP_SECONDS
    stage_length = total / len(PREP_STAGES)
    stages = [(label, round(i * stage_length, 2)) for i, label in enumerate(PREP_STAGES)]
    context = {
        "order": order,
        "prep_seconds": total,
        "remaining": order.seconds_until_ready(),
        "elapsed": total - order.seconds_until_ready(),
        "stages": stages,
    }
    return render(request, "web/preparing.html", context)


def order_ready(request, number):
    """Step 6b: the coffee is ready to pick up."""
    order = get_object_or_404(Order, number=number)
    if not order.is_paid:
        return redirect("web:order_pay", number=order.number)
    if not order.is_ready():
        return redirect("web:order_preparing", number=order.number)
    return render(request, "web/ready.html", {"order": order})


# --- Helpers -------------------------------------------------------------------


def _restart(request, message: str):
    messages.info(request, message)
    return redirect("web:menu")


def _pretty_card(number: str) -> str:
    return " ".join(number[i : i + 4] for i in range(0, len(number), 4))
