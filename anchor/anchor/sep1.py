from rest_framework.request import Request

# Define the dictionary outside of the function
CONFIG_DATA = {
    # ACCOUNTS
    "ACCOUNTS": [
        "GBZAC3UPMX3QI4346PRRNE77QORHFO2V4CVDICI6DUVJJSD3QHO7RFAF",
        "GD72XP6N3LQFP4C27GUDV22LBYASGACAIEME64IEGKNU2HGO6RIALLRR",
        "GBRTM5TWRKX2DCOH6OETIA45NJJXGVP6QB7JJ754QFAO62XG2XMCDBAA"
    ],

    # SIGNING_KEY
    "SIGNING_KEY": "GCLCIGPIF52BY3ASVR4QBLCZ7BHDYZRTAT75UYPSR4EXTI5KLUXHS2YG",

    # FEDERATION_SERVER
    "FEDERATION_SERVER": "https://zingypay.com/federation",

    # NETWORK_PASSPHRASE
    "NETWORK_PASSPHRASE": 'Public Global Stellar Network ; September 2015',

    # TRANSFER_SERVER_SEP0024
    "TRANSFER_SERVER_SEP0024": "https://zingypay.com/sep24",

    # WEB_AUTH_ENDPOINT
    "WEB_AUTH_ENDPOINT": "https://zingypay.com/auth",

    # DIRECT_PAYMENT_SERVER
    "DIRECT_PAYMENT_SERVER": "https://zingypay.com/sep31",

    # KYC_SERVER
    "KYC_SERVER": "https://zingypay.com/kyc",

    # QUOTE_SERVER
    "QUOTE_SERVER": "https://zingypay.com/sep38",

    # Currency Definitions (CURRENCIES)
    "CURRENCIES": [
        {
            "code": "AFRO",
            "issuer": "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV",
            "status": "live",
            "display_decimals": 7,
            "is_asset_anchored": True,
            "anchor_asset_type": "crypto",
            "fixed_number": 900000000000,
            "desc": "Afro is the ‘One Africa’ Digital Currency designed to facilitate glocal trade among Africa’s economies to forestall over dependence on the USD, Euro, Etc.; while also showcasing and promoting the afro culture which is the bedrock of all extant humanity.",
            "image": "https://res.cloudinary.com/dp7civtid/image/upload/v1692079822/AFRO_TOKEN_ndqlai.png"
        },
        {
            "code": "LIFE",
            "issuer": "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV",
            "status": "live",
            "display_decimals": 7,
            "is_asset_anchored": True,
            "anchor_asset_type": "crypto",
            "fixed_number": 100000000000,
            "desc": "Life is Zingypay's glocally facing currency to facilitate glocal trade amongst individuals, businesses, organizations, and governments for fast, seamless, and cheap transactions. It is created to enhance lives on the planet.",
            "image": "https://res.cloudinary.com/dp7civtid/image/upload/v1690689235/life_y29ju9.png"
        },
        {
            "code": "NATURE",
            "issuer": "GBUYO263AYAZZKZI5ZCZFCPIGC42JVCGAOIP2CBBCUP2UTCEUIPIE2VV",
            "status": "live",
            "display_decimals": 7,
            "is_asset_anchored": True,
            "anchor_asset_type": "crypto",
            "fixed_number": 10000000000,
            "desc": "NATURE is Zingypay's asset created to cater to the environment, and nature's reengineering and conservation. 'Replenish the earth' is the mantra. More info in the White Paper.",
            "image": "https://res.cloudinary.com/dp7civtid/image/upload/v1690650612/nature_pzqdla.png"
        }
    ],

    # DOCUMENTATION
    "DOCUMENTATION": {
        "ORG_NAME": "Zingypay Glocal Services Co. Ltd.",
        "ORG_URL": "https://zingypay.com",
        "ORG_LOGO": "https://res.cloudinary.com/dp7civtid/image/upload/v1690775741/zingypay-logo.png",
        "ORG_DESCRIPTION": "A glocal payment platform built to facilitate instant glocal transactions with a throughput of 50,000 transactions per second utilizing the Telepay Protocol for fiat, and the decentralize Stellar Blockchain for fiat/crypto on/off-ramp transactions.",
        "ORG_OFFICIAL_EMAIL": "info@zingypay.com",
        "ORG_SUPPORT_EMAIL": "support@zingypay.com",
    },

    # PRINCIPALS
    "PRINCIPALS": [
        {
            "name": "Ebarim Godsend",
            "email": "ebarim@zingypay.com",
            "twitter": "@edenlife247",
            "keybase": "aniquel"
        }
    ]
}

# Function to return the TOML contents
def return_toml_contents(request, *args, **kwargs):
    return CONFIG_DATA

