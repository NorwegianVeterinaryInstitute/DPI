#!/usr/bin/env python
# Made (mostly) by gemini 2025-04-11
# Functions to standardize error messages
# SECTION : Imports
import datetime
import logging
import os
import sys

import traceback
# !SECTION

# SECTION : Global state for logging setup to ensure it's done once per run
_log_file_name_global = None
_logger_setup_done = False
_configured_logger_name = None

# !SECTION


# SECTION : Functions definitions
# SECTION Logger
def setup_logger(script_name):
    """
    Configures logging for the application. Should be called once.
    Creates a unique log file for the script run.

    Args:
    script_name (str): The basename of the script calling this setup.
                        Used for naming the log file and the logger.

    Returns:
    tuple: (logging.Logger instance, str: log_file_name)
    """
    global _log_file_name_global, _logger_setup_done, _configured_logger_name

    if _logger_setup_done:
        if _configured_logger_name:
            return logging.getLogger(_configured_logger_name), _log_file_name_global
        else:
            # Should not happen if setup was marked done correctly
            print(
                "CRITICAL_ERROR: Logger setup marked done, but no logger name configured.",
                file=sys.stderr,
            )
            return None, None  # Or raise an exception

    # script_base_name = os.path.splitext(os.path.basename(calling_script_name_for_log_file_and_logger_name))[0]
    # _configured_logger_name = script_base_name

    _configured_logger_name = os.path.splitext(script_name)[0]
    _log_file_name_global = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{_configured_logger_name}.log"

    logger = logging.getLogger(_configured_logger_name)
    logger.setLevel(logging.DEBUG)  # Set the default level for the logger

    # Clear existing handlers for this logger instance to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler
    fh = logging.FileHandler(_log_file_name_global, mode="w")
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)

    # Optional: Console Handler (Uncomment and configure if needed for direct script runs)
    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.INFO) # Example: console shows INFO and above
    # ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    # logger.addHandler(ch)

    _logger_setup_done = True
    logger.info(
        f"Logging initialized for '{_configured_logger_name}'. Log file: {_log_file_name_global}"
    )
    return logger, _log_file_name_global


# !SECTION


# SECTION : Error handling
def log_message(message, level, exit_code=None):
    """
    Logs a message using a pre-configured logger.
    Exits the script if exit_code is specified.

    Args:
        message (str): The message to log.
        level (int): The logging level (e.g., logging.INFO, logging.ERROR).
        exit_code (int, optional): The exit code to use. Defaults to None.
    """
    # Uses global variables to check if logger is set up
    if not _logger_setup_done or not _configured_logger_name:
        print(
            f"LOGGER_NOT_SETUP [{logging.getLevelName(level)}]: {message}",
            file=sys.stderr,
        )
        if exit_code is not None:
            sys.exit(exit_code)
        return

    logger = logging.getLogger(_configured_logger_name)
    logger.log(level, message)

    if exit_code is not None:
        logger.log(
            logging.INFO,
            f"Exiting with code {exit_code} due to previous log at level {logging.getLevelName(level)}.",
        )
        sys.exit(exit_code)


# helper function to get the log file name
def get_log_file_name():
    """Returns the configured log file name. Returns a placeholder if logger not set up."""
    if not _logger_setup_done or _log_file_name_global is None:
        return "log_not_initialized.log"
    return _log_file_name_global


# !SECTION


# SECTION standardize error/info message string construction
def processing_error_message(script_name, file_path, identifier=None, e=None):
    """
    Formats an error message string.
    Includes traceback if 'e' is an exception.
    Uses the globally set log file name in the message.

    Args:
        script_name (str): The basename of the script.
        file_path (str): The path to the result file.
        identifier (str, optional): An identifier for the process. Defaults to None.
        e (Exception, optional): An exception object. Defaults to None.
    """

    error_parts = [
        f"Error while processing result file: {file_path}.",
        f"\t\tScript name: {script_name}.",
    ]
    if identifier:
        error_parts.append(f"\t\tIdentifier: {identifier}.")
    if e:
        error_parts.append(f"\t\tError: {str(e)}.")
        # Add traceback if 'e' is an exception and there's an active exception context
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type is not None:  # Checks if we are in an exception handler
            tb_str = "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )
            error_parts.append(f"\t\tTraceback:\n{tb_str}")
        elif isinstance(e, Exception) and hasattr(e, "__traceback__"):
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            error_parts.append(f"\t\tTraceback (from exception object):\n{tb_str}")

    log_fn = get_log_file_name()
    error_parts.append(f"\t\tCheck log: {log_fn}\n")
    return "\n".join(error_parts)


def processing_result_message(script_name, file_path, identifier=None):
    """
    Formats an informational message string.

    Args:
        script_name (str): The basename of the script.
        file_path (str): The path to the result file.
        identifier (str, optional): An identifier for the process. Defaults to None.
    """
    info_parts = [
        f"Processing result file: {file_path}.",
        f"\t\tScript name: {script_name}.",
    ]
    if identifier:
        info_parts.append(f"\t\tIdentifier: {identifier}.")
    return "\n".join(info_parts)


# !SECTION
