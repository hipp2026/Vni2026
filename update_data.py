import json
from datetime import datetime
from vnstock import ticker_overview

# Lấy dữ liệu realtime toàn thị trường (HOSE + HNX + UPCOM)
df = ticker_overview()

# Kiểm tra nếu df rỗng (ngoài giờ giao dịch hoặc lỗi)
if df.empty:
    print("Không lấy được dữ liệu - có thể ngoài giờ giao dịch")
    exit()

# Tính giá trị giao dịch (GTGD) tỷ VND
# price: giá hiện tại, volume: khối lượng (đơn vị lot = 100 cp)
df['value'] = (df['price'] * df['volume'] * 100) / 1_000_000_000  # tỷ VND
df['value'] = df['value'].round(1)

# % thay đổi (change_percent đã có sẵn trong ticker_overview)
df['change_percent'] = df['change_percent'].round(2)

# Top 10 tiền vào: tăng giá (%) > 0 và GTGD cao nhất
top_in = df[df['change_percent'] > 0].sort_values(by='value', ascending=False).head(10)

# Top 10 tiền ra: giảm giá (%) < 0 và GTGD cao nhất
top_out = df[df['change_percent'] < 0].sort_values(by='value', ascending=False).head(10)

# Chuyển sang list dict
def df_to_list(part):
    return part[['ticker', 'price', 'volume', 'change_percent', 'value']].rename(columns={'ticker': 'symbol'}).to_dict(orient='records')

data = {
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "top_in": df_to_list(top_in),
    "top_out": df_to_list(top_out)
}

# Ghi ra data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Update thành công! Top in: {len(top_in)}, Top out: {len(top_out)} mã")