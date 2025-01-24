import logging
import os
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

class Logger:
    _logger = None

    @staticmethod
    def get_logger(name):
        
        if Logger._logger:
            return Logger._logger

        # Create log directory
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Clean old logs
        Logger.clean_old_logs(log_dir)

        # Create logger
        logger = logging.getLogger('B4BA')
        logger.setLevel(logging.DEBUG)

        # Create file handler with date in filename
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'b4ba_{current_date}.log')
        
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter with module name
        formatter = logging.Formatter(
            '%(asctime)s - [%(module)s] - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        Logger._logger = logger
        return logger

    @staticmethod
    def clean_old_logs(log_dir):
        """Clean log files older than 30 days"""
        current_time = time.time()
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            try:
                file_time = os.path.getmtime(filepath)
                if current_time - file_time > 30 * 24 * 60 * 60:  # 30 days
                    os.remove(filepath)
            except Exception as e:
                logging.error(f"Failed to clean log file: {e}")
