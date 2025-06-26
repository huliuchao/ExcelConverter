"""Excel数据转换器主程序

程序入口点，提供命令行接口。
"""

import sys
from .cli import cli


def main():
    """主程序入口"""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()