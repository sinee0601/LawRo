"""
로깅 설정 모듈
통합 로깅 시스템 구성
"""
import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LoggerSetup:
    """로거 설정 클래스"""
    
    @staticmethod
    def setup_logger(
        name: str = "chatbot_service",
        level: str = "INFO",
        log_file: Optional[str] = None,
        enable_console: bool = True
    ) -> logging.Logger:
        """
        로거 설정
        
        Args:
            name: 로거 이름
            level: 로그 레벨
            log_file: 로그 파일 경로 (None이면 파일 로깅 비활성화)
            enable_console: 콘솔 출력 활성화 여부
        
        Returns:
            설정된 로거 인스턴스
        """
        logger = logging.getLogger(name)
        
        # 기존 핸들러 제거
        logger.handlers.clear()
        
        # 로그 레벨 설정
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # 포매터 설정
        detailed_format = (
            "%(asctime)s | %(name)s | %(levelname)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        )
        simple_format = "%(asctime)s | %(levelname)s | %(message)s"
        
        # 콘솔 핸들러
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            
            # 컬러 포매터 적용 (개발 환경에서만)
            if sys.stdout.isatty():
                console_formatter = ColoredFormatter(simple_format)
            else:
                console_formatter = logging.Formatter(simple_format)
            
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # 파일 핸들러
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            
            file_formatter = logging.Formatter(detailed_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # 중복 로그 방지
        logger.propagate = False
        
        return logger


# 전역 로거 인스턴스
def get_logger(name: str = "chatbot_service") -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)


# 기본 로거 설정
def setup_default_logging():
    """기본 로깅 설정"""
    import os
    
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE")
    
    return LoggerSetup.setup_logger(
        name="chatbot_service",
        level=log_level,
        log_file=log_file,
        enable_console=True
    )