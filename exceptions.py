import logging
from log_config import get_logger, SUCCESS, setup_logging
logger = get_logger(__name__)

####################################################################################################################
"""BASE EXCEPTIONS"""
####################################################################################################################

class SeedkeeperError(Exception):
    """Base exception class for Seedkeeper Tool."""
    def __init__(self, message="Error in Seedkeeper Tool"):
        super().__init__(message)
        logger.error("An error occurred in Seedkeeper Tool", exc_info=True)

####################################################################################################################
"""VIEW RELATED EXCEPTIONS"""
####################################################################################################################

class ViewError(SeedkeeperError):
    """Base exception class for View-related errors."""
    def __init__(self, message):
        super().__init__(message)
        logger.error("An error occurred in View", exc_info=True)

class InitializationError(ViewError):
    """Exception raised when View initialization fails."""
    def __init__(self, message="Error in view initialization"):
        super().__init__(message)

class AttributeInitializationError(ViewError):
    """Exception raised when there's an error initializing attributes."""
    def __init__(self, message="Error in attribute initialization"):
        super().__init__(message)

class ApplicationRestartError(ViewError):
    """Exception raised when there's an error restarting the application."""
    def __init__(self, message="Error in application restart"):
        super().__init__(message)

class FrameError(ViewError):
    """Exception raised for errors in frame operations."""
    def __init__(self, message="Error in frame operation"):
        super().__init__(message)

class FrameCreationError(FrameError):
    """Exception raised when there's an error creating or placing a frame."""
    def __init__(self, message="Error in frame creation"):
        super().__init__(message)

class FrameClearingError(FrameError):
    """Exception raised when there's an error clearing a frame."""
    def __init__(self, message="Error in frame clearing"):
        super().__init__(message)

class SecretFrameCreationError(FrameError):
    """Exception raised for errors in the secret frame creation process."""
    def __init__(self, message="Error in secret frame creation"):
        super().__init__(message)

class WelcomeFrameCreationError(FrameError):
    """Exception raised for errors in the welcome frame creation process."""
    def __init__(self, message="Error in welcome frame creation"):
        super().__init__(message)

class UIElementError(ViewError):
    """Exception raised for errors in creating or manipulating UI elements."""
    def __init__(self, message="Error in UI element"):
        super().__init__(message)

class WindowSetupError(UIElementError):
    """Exception raised when there's an error setting up the main window."""
    def __init__(self, message="Error in window setup"):
        super().__init__(message)

class MenuCreationError(UIElementError):
    """Exception raised when there's an error creating a menu."""
    def __init__(self, message="Error in menu creation"):
        super().__init__(message)

class MenuDeletionError(ViewError):
    """Exception raised when there's an error deleting a menu."""
    def __init__(self, message="Error in menu deletion"):
        super().__init__(message)

class CanvasCreationError(UIElementError):
    """Exception raised when there's an error creating a canvas."""
    def __init__(self, message="Error in canvas creation"):
        super().__init__(message)

class BackgroundPhotoError(UIElementError):
    """Exception raised when there's an error creating a background photo."""
    def __init__(self, message="Error in background photo creation"):
        super().__init__(message)

class LabelCreationError(UIElementError):
    """Exception raised when there's an error creating a label."""
    def __init__(self, message="Error in label creation"):
        super().__init__(message)

class EntryCreationError(UIElementError):
    """Exception raised when there's an error creating an entry."""
    def __init__(self, message="Error in entry creation"):
        super().__init__(message)

class HeaderCreationError(UIElementError):
    """Exception raised when there's an error creating a header."""
    def __init__(self, message="Error in header creation"):
        super().__init__(message)

class ButtonCreationError(UIElementError):
    """Exception raised when there's an error creating a button."""
    def __init__(self, message="Error in button creation"):
        super().__init__(message)

####################################################################################################################
"""CONTROLLER RELATED EXCEPTIONS"""
####################################################################################################################

class ControllerError(SeedkeeperError):
    """Base exception class for Controller-related errors."""
    def __init__(self, message="Error in Controller"):
        super().__init__(message)
        logger.error("An error occurred in Controller", exc_info=True)

class CardNotSuitableError(ControllerError):
    """Exception raised when the card is not present or is not suitable for the operation."""
    def __init__(self, message="Card not present or incompatible"):
        super().__init__(message)

class InvalidPinError(ControllerError):
    """Exception raised when the PIN does not meet the required criteria."""
    def __init__(self, message="Invalid PIN"):
        super().__init__(message)

class PinMismatchError(ControllerError):
    """Exception raised when the new PIN and confirmation PIN do not match."""
    def __init__(self, message="PIN mismatch"):
        super().__init__(message)

class PinChangeError(ControllerError):
    """Exception raised when there is an error during the PIN change process."""
    def __init__(self, message="Failed to change PIN"):
        super().__init__(message)

####################################################################################################################
"""CARD RELATED EXCEPTIONS"""
####################################################################################################################

class CardError(SeedkeeperError):
    """Exception raised for errors related to card operations."""
    def __init__(self, message="Error in card operation"):
        super().__init__(message)
        logger.error("An error occurred during card operation", exc_info=True)

####################################################################################################################
"""DATA PROCESSING EXCEPTIONS"""
####################################################################################################################

class SecretRetrievalError(ViewError):
    """Exception raised when there's an error retrieving secret details."""
    def __init__(self, message="Error in secret retrieval"):
        super().__init__(message)
        logger.error("An error occurred during secret retrieval", exc_info=True)

class SecretProcessingError(ViewError):
    """Exception raised when there's an error processing a secret."""
    def __init__(self, message="Error in secret processing"):
        super().__init__(message)
        logger.error("An error occurred during secret processing", exc_info=True)