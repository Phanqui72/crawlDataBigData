import pandas as pd
import re

# --- CÁC HÀM TRÍCH XUẤT THÔNG TIN TỪ TÊN SẢN PHẨM ---

def extract_cpu(name):
    """Trích xuất thông tin CPU từ tên sản phẩm."""
    # Các mẫu regex cho các loại CPU khác nhau
    patterns = [
        r'(i(?:3|5|7|9|)\s?-?\s?\d{4,5}[A-Z]{1,2}H?U?)',  # Intel Core i series (e.g., i5 1334U)
        r'(Core\s\d\s\d{3}U)',                           # Intel Core series (e.g., Core 5 120U)
        r'(Ryzen\s\d\s\d{4}[A-Z]{1,2}H?U?)',             # AMD Ryzen series (e.g., Ryzen 5 7520U)
        r'(R\d\s\d{4}[A-Z]{1,2}H?U?)',                   # AMD Ryzen viết tắt (e.g., R5 7520U)
        r'(Apple\sM\d)',                                 # Apple M series (e.g., Apple M4)
        r'(i3\sN\d+)'                                   # Intel i3 N series (e.g., i3 N305)
    ]
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1)
    return 'N/A'

def extract_ram(name):
    """Trích xuất dung lượng RAM (thường là số nhỏ hơn 100 và có chữ GB)."""
    match = re.search(r'\b(\d{1,2}GB)\b', name)
    return match.group(1) if match else 'N/A'

def extract_storage(name):
    """Trích xuất dung lượng ổ cứng (SSD/ROM)."""
    # Ưu tiên tìm TB trước, sau đó tìm GB (thường là số lớn hơn 100)
    patterns = [
        r'(\d{1,2}TB)',                                  # 1TB, 2TB
        r'(\d{3,4}GB)'                                  # 128GB, 256GB, 512GB
    ]
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            return match.group(1)
    return 'N/A'
    
def extract_screen_info(name):
    """Trích xuất thông tin màn hình (kích thước và độ phân giải)."""
    size_match = re.search(r'(\d{2}\.?\d?\s?inch)', name)
    size = size_match.group(1).strip() if size_match else 'N/A'

    reso_match = re.search(r'(Full HD|FHD|2K|2.8K|QHD|WUXGA)', name, re.IGNORECASE)
    resolution = reso_match.group(1) if reso_match else 'N/A'
    
    return size, resolution

def extract_os(name):
    """Trích xuất hệ điều hành."""
    if 'Win11' in name or 'Windows 11' in name:
        return 'Windows 11'
    if 'MacBook' in name:
        return 'macOS'
    return 'N/A'

def extract_software(name):
    """Trích xuất phần mềm đi kèm (Office)."""
    match = re.search(r'(Office[A-Za-z0-9+]+)', name)
    return match.group(1) if match else 'N/A'


# --- CHƯƠNG TRÌNH CHÍNH ---
def main():
    input_filename = 'laptops_basic_data_thegioididong.csv'
    output_filename = 'laptops_enriched_data.csv'

    try:
        # 1. Đọc file CSV gốc vào một DataFrame của pandas
        df = pd.read_csv(input_filename)
        print(f"Đã đọc thành công {len(df)} dòng từ file '{input_filename}'.")

        # 2. Áp dụng các hàm để tạo ra các cột mới
        print("Bắt đầu quá trình làm giàu dữ liệu...")
        df['cpu'] = df['product_name'].apply(extract_cpu)
        df['ram'] = df['product_name'].apply(extract_ram)
        df['storage'] = df['product_name'].apply(extract_storage)
        
        # Trích xuất màn hình thành 2 cột riêng biệt
        df[['screen_size', 'screen_resolution']] = df['product_name'].apply(
            lambda x: pd.Series(extract_screen_info(x))
        )
        
        df['os'] = df['product_name'].apply(extract_os)
        df['software'] = df['product_name'].apply(extract_software)
        print("Đã trích xuất và tạo các cột dữ liệu mới thành công.")

        # 3. Sắp xếp lại thứ tự các cột cho hợp lý
        final_columns = [
            'id', 'product_name', 'current_price', 'list_price', 'brand', 'category',
            'cpu', 'ram', 'storage', 'screen_size', 'screen_resolution', 'os', 'software',
            'average_rating', 'product_url'
        ]
        df = df[final_columns]

        # 4. Lưu DataFrame đã được làm giàu vào một file CSV mới
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\nHOÀN TẤT! Đã lưu dữ liệu đã được làm giàu vào file '{output_filename}'.")

    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file '{input_filename}'. Vui lòng đảm bảo file này nằm cùng thư mục.")
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()