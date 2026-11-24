"""PaymentService: charge an order through the gateway and record the result."""

from django.db import transaction

from apps.orders.models import Order
from apps.orders.services import OrderService

from .gateway import PaymentGateway, get_payment_gateway
from .models import Payment


class PaymentError(Exception):
    """The order cannot be paid (e.g. it is already paid)."""


class PaymentService:
    def __init__(self, gateway: PaymentGateway | None = None) -> None:
        self.gateway = gateway or get_payment_gateway()

    @transaction.atomic
    def pay(self, order: Order, *, customer_name: str, card_number: str) -> Payment:
        """Charge the order. Approved -> order paid. Declined -> order failed (customer can retry)."""
        if order.is_paid:
            raise PaymentError("This order is already paid.")

        result = self.gateway.charge(
            amount=order.total,
            card_number=card_number,
            description=f"Morning Cafe {order.number}",
        )
        payment = Payment.objects.create(
            order=order,
            status=Payment.Status.APPROVED if result.approved else Payment.Status.DECLINED,
            amount=order.total,
            card_last4=card_number[-4:],
            reference=result.reference,
        )
        if result.approved:
            OrderService.mark_paid(order, customer_name)
        else:
            OrderService.mark_failed(order)
        return payment
