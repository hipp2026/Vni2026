import json
from datetime import datetime
from vnstock import stock_quote

# Lấy dữ liệu toàn bộ cổ phiếu HOSE + HNX + UPCOM (khoảng 1600-1700 mã)
# vnstock hỗ trợ lấy tất cả mà không cần list symbols
df = stock_quote(market='ALL')  # Hoặc dùng ticker_overview() nếu cần thêm field

# Tính giá trị giao dịch (tỷ VND): price * volume / 1000000000 (volume vnstock là lot = 100 cp)
df['value'] = (df['price'] * df['volume'] * 100) / 1_000_000_000  # GTGD tỷ VND

# Sắp xếp để lấy top
top_in = df[df['change_percent'] > 0].sort_values(by=['value'], ascending=False).head(10)
top_out = df[df['change_percent'] < 0].sort_values(by=['value'], ascending=False).head(10)

# Chuyển sang list dict cho JSON
def df_to_list(df_part):
    return df_part[['symbol', 'price', 'volume', 'change_percent', 'value']].round({'change_percent': 2, 'value': 1}).to_dict(orient='records')

data = {
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "top_in": df_to_list(top_in),
    "top_out": df_to_list(top_out)
}

# Ghi ra data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Đã cập nhật data.json thành công với dữ liệu thực!")