from pysatochip.JCconstants import STATE_UNINITIALIZED, STATE_SEALED, STATE_UNSEALED

# Constants
BG_MAIN_MENU = "#21283b"
BG_BUTTON = "#e1e1e0"
BG_HOVER_BUTTON = "grey"
BUTTON_TEXT_COLOR = "white"
DEFAULT_BG_COLOR = "whitesmoke"
HIGHLIGHT_COLOR = "#D3D3D3"
MAIN_MENU_COLOR = "#202738"
BUTTON_COLOR = "#e1e1e0"
HOVER_COLOR = "grey"
TEXT_COLOR = "black"

ICON_PATH = "./pictures_db/"


"""Satodime"""

# COIN_LIST = [
#     "Bitcoin",
#     "Ethereum",
#     "Bitcoin Cash",
#     "Litecoin",
#     "Polygon",
#     "Counterparty"
# ]

COIN_DICT = {
    "Bitcoin": 0x80000000,
    "Ethereum": 0x8000003c,
    "Bitcoin Cash": 0x80000091,
    "Litecoin": 0x80000002,
    "Polygon": 0x800003c6,
    "Counterparty": 0x80000009,
}

COIN_DECIMALS_DICT = {
    "BTC": 8,
    "ETH": 6,
    "BCH": 6,
    "LTC": 6,
    "POL": 2,
    "XCP": 3,

    "USD": 2,
    "EUR": 2,

    "BTCTEST": 8,
    "ETHTEST": 6,
    "BCHTEST": 6,
    "LTCTEST": 6,
    "POLTEST": 2,
    "XCPTEST": 3,
}


STATUS_DIC = {
STATE_UNINITIALIZED: "uninitialized",
STATE_SEALED: "sealed",
STATE_UNSEALED: "unsealed"
}

STATUS_COLOR_DIC = {
STATE_UNINITIALIZED: "grey",
STATE_SEALED: "green",
STATE_UNSEALED: "red"
}

# some known address for debugging/testing ui
DEBUG_ADDR = {
    'BTC': 'bc1ql49ydapnjafl5t2cp9zqpjwe6pdgmxy98859v2',  # whale
    'BCH': '1PUwPCNqKiC6La8wtbJEAhnBvtc8gdw19h',  # whale
    'LTC': 'ltc1qr07zu594qf63xm7l7x6pu3a2v39m2z6hh5pp4t', # whale
    'XCP': '1Do5kUZrTyZyoPJKtk4wCuXBkt5BDRhQJ4',

    'ETH': '0xd5b06c8c83e78e92747d12a11fcd0b03002d48cf',
    # 'ETH': '0x86b4d38e451c707e4914ffceab9479e3a8685f98',
    # 'ETH': '0xE71a126D41d167Ce3CA048cCce3F61Fa83274535',  # cryptopunk
    # 'ETH': '0xed1bf53Ea7fD8a290A3172B6c00F1Fb3657D538F',  # usdt
    # 'ETH': '0x2c4ebd4b21736e992f3efeb55de37ae66457199d',  # grolex nft

    # 'POL': '0x8db853Aa2f01AF401e10dd77657434536735aC62',
    # 'POL': '0x86d22A8219De3683CF188778CDAdEE62D1442033',
    'POL': '0xE976c3052Df18cc2Dc878b9bc3191Bba68Ef3d80',  # DolZ nft
    # 'POL': '0x440D4955a914D5e29F861aC024A608aE41c56cB6',  # PookyBall nft contract
    # 'POL': '0xd7f1cbca340c831d77c0d8d3dc843a07873ade44',  # PookyBall nft vault
    # 'POL': '0xF977814e90dA44bFA03b6295A0616a897441aceC',  # Binance hot wallet with USDT
}

"""Seedkeeper"""

TYPE_MASTERSEED = 0x10
TYPE_BIP39_MNEMONIC = 0x30
TYPE_ELECTRUM_MNEMONIC = 0x40
TYPE_PUBKEY = 0x70
TYPE_PASSWORD = 0x90
TYPE_2FA_SECRET = 0xB0
TYPE_DATA = 0xC0
TYPE_DESCRIPTOR = 0xC1

TYPE_DIC = {
    0x10: 'Masterseed',
    0x30: 'BIP39 mnemonic',
    0x40: 'Electrum mnemonic',
    0x50: 'Shamir Secret Share',
    0x60: 'Private Key',
    0x70: 'Public Key',
    0x71: 'Authenticated Public Key',
    0x80: 'Symmetric Key',
    0x90: 'Password',
    0x91: 'Master Password',
    0xA0: 'Certificate',
    0xB0: '2FA secret',
    0xC0: 'Data',
    0xC1: 'Wallet descriptor'
}

INS_DIC = {
    0x40: 'Create PIN',
    0x42: 'Verify PIN',
    0x44: 'Change PIN',
    0x46: 'Unblock PIN',
    0xA0: 'Generate masterseed',
    0xA5: 'Reset secret',
    0xAE: 'Generate 2FA Secret',
    0xA1: 'Import secret',
    0xA1A: 'Import plain secret',
    0xA1B: 'Import encrypted secret',
    0xA2: 'Export secret',
    0xA2A: 'Export plain secret',
    0xA2B: 'Export encrypted secret',
    0xFF: 'RESET TO FACTORY'
}

RES_DIC = {
    0x9000: 'OK',
    0x63C0: 'PIN failed',
    0x9C03: 'Operation not allowed',
    0x9C04: 'Setup not done',
    0x9C05: 'Feature unsupported',
    0x9C01: 'No memory left',
    0x9C08: 'Secret not found',
    0x9C10: 'Incorrect P1',
    0x9C11: 'Incorrect P2',
    0x9C0F: 'Invalid parameter',
    0x9C0B: 'Invalid signature',
    0x9C0C: 'Identity blocked',
    0x9CFF: 'Internal error',
    0x9C30: 'Lock error',
    0x9C31: 'Export not allowed',
    0x9C32: 'Import data too long',
    0x9C33: 'Wrong MAC during import',
    0x0000: 'Unexpected error'
}
