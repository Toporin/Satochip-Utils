
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

"""Seedkeeper"""

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
