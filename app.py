import streamlit as st
import akshare as ak
import pandas as pd


# ========== 工具函数 ==========
def get_financials(stock_code):
    """获取三大财务报表"""
    profit = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
    balance = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
    cashflow = ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表")
    return profit, balance, cashflow


# ========== 12条排雷规则（示例实现 3 条，其余可扩展） ==========
def rule_1_stable_growth(profit):
    """营业收入、净利润是否保持稳定增长"""
    try:
        income = profit.loc[profit['报表项目'] == '营业总收入'].iloc[:, 1:].astype(float)
        net_profit = profit.loc[profit['报表项目'] == '净利润'].iloc[:, 1:].astype(float)
        if income.pct_change(axis=1).min().min() > -0.2 and net_profit.pct_change(axis=1).min().min() > -0.2:
            return "✅ 稳定增长"
        else:
            return "❌ 波动过大"
    except:
        return "⚠️ 数据不足"


def rule_2_liquidity(balance):
    """流动资产 < 流动负债"""
    try:
        ca = float(balance.loc[balance['报表项目'] == '流动资产合计'].iloc[0, 1])
        cl = float(balance.loc[balance['报表项目'] == '流动负债合计'].iloc[0, 1])
        return "❌ 流动性风险" if ca < cl else "✅ 正常"
    except:
        return "⚠️ 数据不足"


def rule_3_debt_risk(balance):
    """A vs B+C 规则"""
    try:
        cash = float(balance.loc[balance['报表项目'] == '货币资金'].iloc[0, 1])
        fin_assets = float(balance.loc[balance['报表项目'] == '交易性金融资产'].iloc[0, 1])
        A = cash + fin_assets

        short_debt = float(balance.loc[balance['报表项目'] == '短期借款'].iloc[0, 1])
        current_noncurrent = float(balance.loc[balance['报表项目'] == '一年内到期的非流动负债'].iloc[0, 1])
        B = short_debt + current_noncurrent

        long_debt = float(balance.loc[balance['报表项目'] == '长期借款'].iloc[0, 1])
        bonds = float(balance.loc[balance['报表项目'] == '应付债券'].iloc[0, 1])
        C = long_debt + bonds

        if A < B:
            return "❌ 资金链紧张"
        elif A < (B + C):
            return "⚠️ 偿债压力大"
        else:
            return "✅ 安全"
    except:
        return "⚠️ 数据不足"


# TODO: 继续实现 rule_4 ~ rule_12（存货、应收账款、商誉、质押比例...）


# ========== 总控函数 ==========
def check_risks(stock_code: str):
    report = {}
    try:
        profit, balance, cashflow = get_financials(stock_code)

        report["业绩趋势"] = rule_1_stable_growth(profit)
        report["流动性"] = rule_2_liquidity(balance)
        report["偿债能力"] = rule_3_debt_risk(balance)

        # 可扩展更多规则
        # report["存货占比"] = rule_4_inventory(...)
        # ...

    except Exception as e:
        report["错误"] = f"数据抓取失败: {e}"

    # 最终结论
    if any("❌" in v for v in report.values()):
        report["最终结论"] = "高风险，建议排除"
    elif any("⚠️" in v for v in report.values()):
        report["最终结论"] = "中风险，需谨慎"
    else:
        report["最终结论"] = "低风险，可进一步研究"

    return report


# ========== Streamlit 网页 ==========
st.title("股票排雷检测器（Beta）")
stock_code = st.text_input("请输入股票代码（如 600519）", "")

if stock_code:
    st.write("正在分析，请稍等...")
    result = check_risks(stock_code)
    st.subheader("检测结果")
    df = pd.DataFrame(list(result.items()), columns=["检测项", "结论"])
    st.table(df)
