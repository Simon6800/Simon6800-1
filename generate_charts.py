#!/usr/bin/env python3
# generate_charts.py
# 需求：akshare, pandas, mplfinance
# 安装：pip install akshare pandas matplotlib mplfinance

import os
import sys
import pandas as pd
import akshare as ak
import mplfinance as mpf

csv_path = "top20_electronics.csv"   # 保证文件与脚本在同一目录
output_dir = "charts"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 读取 CSV，需确保第一列列名为 code
df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

def normalize_symbol(code):
    # A 股：以 6 开头为 sh，其它为 sz（适配主流）
    code = code.strip()
    if code.startswith("6") or code.startswith("9") or code.startswith("5") or code.startswith("7"):
        return "sh" + code
    else:
        return "sz" + code

def fetch_save_plot(code):
    symbol = normalize_symbol(code)
    try:
        # akshare: stock_zh_a_daily(symbol="sz000001")
        kline = ak.stock_zh_a_daily(symbol=symbol)
        if kline is None or kline.empty:
            print(f"[WARN] no kline for {symbol}")
            return
        kline.rename(columns={'date':'date'}, inplace=True)
        kline['date'] = pd.to_datetime(kline['date'])
        kline.set_index('date', inplace=True)
        kline.sort_index(inplace=True)
        # 计算均线列（可用于检查）
        kline['MA20'] = kline['close'].rolling(20).mean()
        kline['MA60'] = kline['close'].rolling(60).mean()
        kline['MA250'] = kline['close'].rolling(250).mean()

        # 截取最近 300 日绘图
        plot_df = kline.tail(300)[['open','high','low','close','volume']]

        mav = (20,60,250)
        savefile = os.path.join(output_dir, f"{code}.png")
        mpf.plot(plot_df, type='candle', mav=mav, volume=True,
                 title=f"{code} 日线（含 MA20/60/250）", style='yahoo',
                 savefig=dict(fname=savefile, dpi=150))
        print(f"[OK] Saved {savefile}")
    except Exception as e:
        print(f"[ERR] {code} -> {e}")

# 批量
for idx, row in df.iterrows():
    code = row['code'].strip()
    if code == "":
        continue
    fetch_save_plot(code)

print("Finished. Charts in:", output_dir)