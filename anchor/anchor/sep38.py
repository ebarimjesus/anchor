from typing import List, Optional, Union
from decimal import Decimal
from polaris.integrations import QuoteIntegration
from polaris.sep10.token import SEP10Token
from polaris.models import DeliveryMethod, OffChainAsset, Asset
from rest_framework.request import Request
from .rates import get_estimated_rate

class AnchorQuote(QuoteIntegration):
    def get_prices(
        self,
        token: SEP10Token,
        request: Request,
        sell_asset: Union[Asset, OffChainAsset],
        sell_amount: Decimal,
        buy_assets: List[Union[Asset, OffChainAsset]],
        sell_delivery_method: Optional[DeliveryMethod] = None,
        buy_delivery_method: Optional[DeliveryMethod] = None,
        country_code: Optional[str] = None,
        *args,
        **kwargs,
    ) -> List[Decimal]:
        prices = []
        for buy_asset in buy_assets:
            try:
                prices.append(
                    get_estimated_rate(
                        sell_asset,
                        buy_asset,
                        sell_amount=sell_amount
                    )
                )
            except RequestException:
                raise RuntimeError("unable to fetch prices")
        return prices

    def get_price(
        self,
        token: SEP10Token,
        request: Request,
        sell_asset: Union[Asset, OffChainAsset],
        buy_asset: Union[Asset, OffChainAsset],
        buy_amount: Optional[Decimal] = None,
        sell_amount: Optional[Decimal] = None,
        sell_delivery_method: Optional[DeliveryMethod] = None,
        buy_delivery_method: Optional[DeliveryMethod] = None,
        country_code: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Decimal:
        try:
            return get_estimated_rate(
                sell_asset,
                buy_asset,
                sell_amount=sell_amount,
                buy_amount=buy_amount
            )
        except RequestException:
            raise RuntimeError("unable to fetch price")


    def post_quote(
        self, token: SEP10Token, request: Request, quote: Quote, *args, **kwargs,
    ) -> Quote:
        if quote.requested_expire_after and not approve_expiration(
            quote.requested_expire_after
        ):
            raise ValueError("the requested expiration cannot be provided")
        try:
            rate, expiration = get_firm_quote(quote)
            quote.price = rate
            quote.expires_at = expiration
        except RequestException:
            raise RuntimeError("unable to fetch price for quote")
        return quote

        