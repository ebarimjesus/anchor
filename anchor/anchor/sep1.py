from rest_framework.request import Request

def return_toml_contents(request, *args, **kwargs):
    return {
        "DOCUMENTATION": {
            "ORG_NAME": "Zingypay Glocal Services Co. Ltd.",
            "ORG_URL": "https://zingypay.com",
            "ORG_LOGO": "https://res.cloudinary.com/dp7civtid/image/upload/v1690775741/zingypay-logo.png",
            "ORG_DESCRIPTION": "A glocal payment platform built to facilitate instant glocal transactions with a throughput of 50,000 transactions per second utilizing the Telepay Protocol for fiat, and the decentralize Stellar Blockchain for fiat/crypto on/off-ramp transactions.",
            "ORG_OFFICIAL_EMAIL": "info@zingypay.com",
            "ORG_SUPPORT_EMAIL": "support@zingypay.com"
        },
    }

