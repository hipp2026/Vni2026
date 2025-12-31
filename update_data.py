import json
from datetime import datetime
from vnstock import Vnstock

# Tạo instance Vnstock
stock_client = Vnstock().stock()

# Lấy danh sách tất cả mã chứng khoán
all_symbols = stock_client.listing().symbols_by_exchange()['ticker'].tolist()

# Lấy bảng giá realtime cho toàn bộ mã (có thể nhiều, nhưng vnstock hỗ trợ tốt)
df = stock_client.quote.price_board(all_symbols)

# Kiểm tra nếu df rỗng
if df.empty:
    print("Không lấy được dữ liệu - có thể ngoài giờ giao dịch hoặc lỗi tạm thời")
    exit()

# Đổi tên cột cho dễ dùng (tùy phiên bản, cột có thể là 'ticker', 'price', 'volume', 'change_pct' hoặc tương tự)
# Dựa trên vnstock mới: thường là 'ticker', 'close' (giá), 'lot' (volume lot), 'changePercent'
df.rename(columns={
    'ticker': 'symbol',
    'close': 'price',
    'lot': 'volume',
    'changePercent': 'change_percent'
}, inplace=True)

# Nếu cột không khớp, in ra để debug (chỉ lần đầu)
print(df.columns)  # Xóa dòng này sau khi chạy ổn

# Tính GTGD tỷ VND (volume là lot = 100 cp)
df['value'] = (df['price'] * df['volume'] * 100) / 1_000_000_000
df['value'] = df['value'].round(1)
df['change_percent'] = df['change_percent'].round(2)

# Top 10 tiền vào (tăng >0)
top_in = df[df['change_percent'] > 0].sort_values(by='value', ascending=False).head(10)

# Top 10 tiền ra (giảm <0)
top_out = df[df['change_percent'] < 0].sort_values(by='value', ascending=False).head(10)

# Chuyển sang list dict
def df_to_list(part):
    return part[['symbol', 'price', 'volume', 'change_percent', 'value']].to_dict(orient='records')

data = {
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "top_in": df_to_list(top_in),
    "top_out": df_to_list(top_out)
}

# Ghi data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Update thành công! Top in: {len(top_in)} mã, Top out: {len(top_out)} mã")