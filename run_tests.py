#!/usr/bin/env python3
"""
测试运行脚本

使用方式：
python run_tests.py                    # 运行所有测试
python run_tests.py --unit             # 只运行单元测试
python run_tests.py --integration      # 只运行集成测试
python run_tests.py --coverage         # 运行测试并生成覆盖率报告
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并处理输出"""
    print(f"\n🔄 {description}")
    print(f"执行命令: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误代码: {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Excel Converter 测试运行器")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 确保当前目录是项目根目录
    project_root = Path(__file__).parent
    print(f"📁 项目根目录: {project_root.absolute()}")
    
    # 基本pytest命令
    pytest_cmd = [sys.executable, "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    # 确定测试范围
    if args.unit:
        pytest_cmd.extend(["tests/test_config.py", "tests/test_validators.py"])
        description = "单元测试"
    elif args.integration:
        pytest_cmd.append("tests/test_integration.py")
        description = "集成测试"
    else:
        pytest_cmd.append("tests/")
        description = "所有测试"
    
    # 添加覆盖率选项
    if args.coverage:
        pytest_cmd.extend([
            "--cov=excel_converter",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
        description += " (包含覆盖率)"
    
    # 添加其他有用的选项
    pytest_cmd.extend([
        "--tb=short",  # 简化错误输出
        "-x",          # 第一个失败后停止
    ])
    
    print("🧪 Excel Converter 测试套件")
    print("=" * 60)
    
    # 运行测试
    success = run_command(pytest_cmd, description)
    
    if success:
        print("\n🎉 所有测试通过！")
        
        if args.coverage:
            print("\n📊 覆盖率报告已生成:")
            print("  - 终端报告: 上方显示")
            print("  - HTML报告: htmlcov/index.html")
            
    else:
        print("\n💥 测试失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main() 