from django.apps import AppConfig

class AnchorConfig(AppConfig):
    name = 'anchor'

    def ready(self):
        from polaris.integrations import register_integrations
        from .sep1 import return_toml_contents
        from .sep12 import AnchorCustomer
        from .deposit import AnchorDeposit
        from .withdraw import AnchorWithdraw

        register_integrations(
            toml=return_toml_contents,
            customer=AnchorCustomer(),
            deposit=AnchorDeposit(),
            withdrawal=AnchorWithdraw(),
        )

