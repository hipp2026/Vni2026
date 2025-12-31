import json
from datetime import datetime
from vnstock import Trading

# Lấy bảng giá realtime cho một số mã lớn có GTGD cao (top thường xuyên)
# Để tránh quá tải khi lấy all (có thể chậm hoặc giới hạn), chọn ~100 mã phổ biến
symbols = [
    'VCB', 'BID', 'CTG', 'TCB', 'VPB', 'MBB', 'HDB', 'STB', 'ACB', 'SHB',
    'HPG', 'FPT', 'MWG', 'VHM', 'VIC', 'VNM', 'GAS', 'SAB', 'MSN', 'VRE',
    'SSI', 'VND', 'HCM', 'SHS', 'VCI', 'CTS', 'BVB', 'AGR', 'FTS', 'BSI',
    'TCH', 'DXG', 'KBC', 'NVL', 'PDR', 'DIG', 'KDH', 'NLG', 'HDG', 'KHG',
    'POW', 'REE', 'PLX', 'DPM', 'DCM', 'BMP', 'GVR', 'PVD', 'PVS', 'NT2'
]  # Bạn có thể thêm/bớt mã

# Lấy dữ liệu realtime
df = Trading(source='TCBS').price_board(symbols)  # hoặc source='VCI' nếu muốn

# Kiểm tra dữ liệu
if df.empty:
    print("Không lấy được dữ liệu - có thể ngoài giờ giao dịch")
    exit()

# In columns để debug lần đầu (xóa dòng này sau khi chạy ổn)
print("Columns:", df.columns.tolist())

# Chuẩn hóa cột (thường là: 'symbol', 'price' hoặc 'close', 'volume' hoặc 'lot', 'change_pc' hoặc 'change_percent')
df.rename(columns={
    'symbol': 'symbol',
    'close': 'price',  # hoặc 'price' tùy phiên bản
    'lot': 'volume',   # hoặc 'volume'
    'change_pc': 'change_percent',  # hoặc 'change_percent' / 'pct_change'
}, inplace=True, errors='ignore')

# Nếu cột % thay đổi là 'change_percent' hoặc khác, chỉnh sau khi thấy print columns

# Tính GTGD tỷ VND (volume lot x 100 cp)
df['value'] = (df['price'] * df['volume'] * 100) / 1_000_000_000
df['value'] = df['value'].round(1)
df['change_percent'] = df['change_percent'].round(2)

# Top 10 tiền vào/ra
top_in = df[df['change_percent'] > 0].sort_values(by='value', ascending=False).head(10)
top_out = df[df['change_percent'] < 0].sort_values(by='value', ascending=False).head(10)

# Chuyển list dict
def df_to_list(part):
    return part[['symbol', 'price', 'volume', 'change_percent', 'value']].to_dict(orient='records')

data = {
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "top_in": df_to_list(top_in),
    "top_out": df_to_list(top_out)
}

# Ghi file JSON
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Update thành công! Top in: {len(top_in)} mã, Top out: {len(top_out)} mã")