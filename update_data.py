import json
from datetime import datetime
from vnstock import Trading, Listing

# Lấy danh sách tất cả mã cổ phiếu (all symbols)
listing = Listing()
all_symbols = listing.all_symbols()  # Trả về list string các ticker

# Nếu list quá dài, có thể giới hạn top 500-1000 mã có GTGD cao (nhưng để all cũng ổn, vnstock xử lý tốt)
# Hoặc lọc chỉ HOSE: all_symbols = [s for s in all_symbols if s.startswith('') ] nhưng để all cho toàn thị trường

# Lấy bảng giá realtime cho tất cả mã
df = Trading().price_board(all_symbols)

# Kiểm tra nếu df rỗng (ngoài giờ hoặc lỗi)
if df.empty:
    print("Không lấy được dữ liệu - có thể ngoài giờ giao dịch hoặc lỗi tạm thời")
    exit()

# Các cột chính trong df (dựa trên phiên bản mới): thường có 'ticker', 'price' (giá khớp), 'volume' (lot), 'change_percent' hoặc 'change_pct'
# In columns để debug lần đầu (xóa sau khi ổn)
print("Columns:", df.columns.tolist())

# Chuẩn hóa cột (tùy phiên bản có thể hơi khác, nhưng thường là):
df.rename(columns={
    'ticker': 'symbol',
    'price': 'price',  # giá hiện tại
    'volume': 'volume',  # khối lượng lot
    'change_percent': 'change_percent',  # hoặc 'change_pct' / 'pct_change'
}, inplace=True)

# Nếu cột % thay đổi tên khác, chỉnh thủ công sau khi thấy print columns

# Tính GTGD tỷ VND (volume lot x 100 cp x price)
df['value'] = (df['price'] * df['volume'] * 100) / 1_000_000_000
df['value'] = df['value'].round(1)
df['change_percent'] = df['change_percent'].round(2)

# Lọc và sort top 10
top_in = df[df['change_percent'] > 0].sort_values(by='value', ascending=False).head(10)
top_out = df[df['change_percent'] < 0].sort_values(by='value', ascending=False).head(10)

# Chuyển sang list dict
def df_to_list(part):
    return part[['symbol', 'price', 'volume', 'change_percent', 'value']].to_dict(orient='records')

data = {
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "top_in": df_to_list(top_in),
    "top_out": df_to_list(top_out)
}

# Ghi file
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Update thành công! Top in: {len(top_in)} mã, Top out: {len(top_out)} mã")