#!/usr/bin/env python
# Made (mostly) by gemini 2025-04-11
# Functions to standardize error messages
# SECTION : Imports
import datetime
import os
import sys
import logging

import traceback
# !SECTION

# SECTION : Functions definitions
# SECTION Logger
def log_message(message, script_name, exit_code=None):
    """
    Logs a message to the console and optionally to a log file,
    Exits the script if specified.
    Messages types are determined by the object name. 
    Example error_message, info_message, warning_message, debug_message.
    that are passed to the function

    Args:
        message (str): The message to log.
        script_name (str): The name of the script.
        exit_code (int): The exit code to use when calling sys.exit().
    """
    script_name = script_name
    # Basic console output (always do this)
    # print(message)

    # Determine message type from the object name
    message_type = "unknown"
    object_name = [name for name, obj in globals().items() if obj is message]
    if object_name:
        object_name_lower = object_name[0].lower()
        if "error" in object_name_lower:
            message_type = "error"
        elif "info" in object_name_lower:
            message_type = "info"
        elif "warning" in object_name_lower:
            message_type = "warning"
        elif "debug" in object_name_lower:
            message_type = "debug"

    # Defining log file name
    script_name_noextension = os.path.splitext(script_name)[0]
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{script_name_noextension}.log"

    # logging configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_name, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True  # Added force=True for cleaner re-configuration
    )
    
    # print(message)
    
    if message_type == "info":
        logging.info(message)
    elif message_type == "debug":
        logging.debug(message)
    elif message_type == "warning":
        logging.warning(message)
    elif message_type == "error":
        logging.error(message)
        logging.error("Exception traceback:")
        logging.error(traceback.format_exc())
    else:
        logging.info(f"LOG: {message}") # Default logging if type is unknown

    if exit_code:
        sys.exit(exit_code)
# !SECTION

# SECTION standardize error messages
def processing_error_message(script_name, file_path, identifier = None, e = None):
        # Defining log file name
        script_name_noextension = os.path.splitext(script_name)[0]
        log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{script_name_noextension}.log"
        
        script_name = script_name
        error_message = f"Error while processing result file: {file_path}.\n"    
        error_message += f"\t\tScript name: {script_name}.\n" 
        if e: 
            error_message += f"\t\tError: {e}.\n"
        if identifier:
            error_message += f"\t\tIdentifier {identifier}.\n"
        error_message += f"\t\tCheck log: {log_file_name}\n\n"
        # print(error_message)
        return error_message
    

def processing_result_message(script_name, file_path, identifier = None, e  = None):
    info_message = f"Processing result file: {file_path}.\n"
    info_message += f"\t\tScript name: {script_name}.\n"
    if identifier:
        info_message += f"\t\tIdentifier {identifier}.\n"
    if e: 
        info_message += f"\t\tError: {e}.\n"
    return info_message
    
# !SECTION
        
# SECTION : Example main 
# Example in main
# if __name__ == "__main__":
#     try:
#         # ... your main logic ...
#     except FileNotFoundError:
#         log_error_and_exit("Input file not found.", log_file="main.log")
#     except Exception as e:
#         log_error_and_exit(f"An unexpected error occurred: {e}", log_file="main.log")

# TODO 
# script_name = os.path.basename(__file__)
# script_name_noextension = os.path.splitext(script_name)[0]

# !SECTION