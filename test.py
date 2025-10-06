import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- HÀM HỖ TRỢ ĐỂ LẤY TEXT AN TOÀN ---
def get_element_text(parent, selector, default="N/A"):
    """Hàm này giúp lấy text của một element, nếu không tìm thấy sẽ trả về giá trị mặc định."""
    try:
        return parent.find_element(By.CSS_SELECTOR, selector).text
    except NoSuchElementException:
        return default

# --- GIAI ĐOẠN 1: THU THẬP TẤT CẢ CÁC URL CỦA SẢN PHẨM ---
print("--- GIAI ĐOẠN 1: BẮT ĐẦU THU THẬP URL SẢN PHẨM ---")
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.thegioididong.com/laptop")
print("Đã mở trình duyệt và truy cập trang danh sách laptop.")
time.sleep(5)

# Tự động nhấn "Xem thêm" để tải hết sản phẩm
while True:
    try:
        view_more_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.view-more > a"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_more_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", view_more_button)
        print(f"Đã nhấn nút '{view_more_button.text}'...")
        time.sleep(4)
    except TimeoutException:
        print("Đã tải xong tất cả sản phẩm trên trang danh sách.")
        break
    except Exception as e:
        print(f"Gặp lỗi khi nhấn nút 'Xem thêm': {e}")
        break

product_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.listproduct > li.item a.main-contain')
product_urls = [elem.get_attribute('href') for elem in product_elements if elem.get_attribute('href')]
print(f"Đã thu thập được {len(product_urls)} URL sản phẩm.")
time.sleep(2)

# --- GIAI ĐOẠN 2: TRUY CẬP TỪNG URL ĐỂ CÀO DỮ LIỆU CHI TIẾT ---
print("\n--- GIAI ĐOẠN 2: BẮT ĐẦU CÀO DỮ LIỆU CHI TIẾT TỪNG SẢN PHẨM ---")
all_products_data = []
total_urls = len(product_urls)
failed_urls = []

for i, url in enumerate(product_urls):
    try:
        driver.get(url)
        time.sleep(3) 

        product_data = {}
        product_name = get_element_text(driver, 'h1')
        print(f"Đang cào sản phẩm {i+1}/{total_urls}: {product_name}")

        # Lấy thông tin chung, giá, khuyến mãi...
        product_data['product_name'] = product_name
        product_data['product_url'] = url
        product_data['brand'] = product_name.split(' ')[0]
        product_data['category'] = "Laptop"
        product_data['product_sku'] = url.split('/')[-1]
        product_data['current_price'] = get_element_text(driver, '.box-price-present')
        product_data['list_price'] = get_element_text(driver, '.box-price-old')
        promo_elements = driver.find_elements(By.CSS_SELECTOR, '.box-promotion-content p, .promotion-item .content')
        promotions_text = [promo.text for promo in promo_elements if promo.text]
        product_data['promotions_text'] = " | ".join(promotions_text)

        # Mở rộng tất cả các mục cấu hình
        try:
            spec_container = driver.find_element(By.CSS_SELECTOR, "div.specification-item")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", spec_container)
            time.sleep(1)

            spec_headers_to_click = spec_container.find_elements(By.CSS_SELECTOR, "div.box-specifi")
            print(f"  - Tìm thấy {len(spec_headers_to_click)} mục cấu hình để mở rộng.")
            for header in spec_headers_to_click:
                if header.is_displayed():
                    driver.execute_script("arguments[0].click();", header)
                    time.sleep(0.5)
        except NoSuchElementException:
            print("  - Không tìm thấy khu vực cấu hình chi tiết.")

        # **SỬA LỖI QUAN TRỌNG: DÙNG ĐÚNG SELECTOR `ul.text-specifi li`**
        # Sau khi đã mở rộng, cào dữ liệu từ các dòng thông tin
        spec_rows = driver.find_elements(By.CSS_SELECTOR, 'ul.text-specifi li')
        print(f"  - Tìm thấy {len(spec_rows)} dòng thông số chi tiết để cào.")
        for row in spec_rows:
            try:
                # Mỗi 'li' có 2 thẻ 'aside', thẻ đầu là tên, thẻ sau là giá trị
                parts = row.find_elements(By.TAG_NAME, 'aside')
                if len(parts) == 2:
                    spec_name = parts[0].text.strip()
                    spec_value = parts[1].text.strip()

                    if not spec_name or not spec_value: continue # Bỏ qua nếu dòng trống

                    if "Công nghệ CPU" in spec_name: product_data['cpu_spec'] = spec_value
                    elif "RAM" in spec_name: product_data['ram_spec'] = spec_value
                    elif "Ổ cứng" in spec_name: product_data['storage_spec'] = spec_value
                    elif "Màn hình" in spec_name or "Độ phân giải" in spec_name or "Tần số quét" in spec_name or "Công nghệ màn hình" in spec_name:
                        current_screen_spec = product_data.get('screen_spec', '')
                        product_data['screen_spec'] = f"{current_screen_spec}{spec_name}: {spec_value} | "
                    elif "Card màn hình" in spec_name: product_data['gpu_spec'] = spec_value
                    elif "Hệ điều hành" in spec_name: product_data['os_spec'] = spec_value
                    elif "Thiết kế" in spec_name: product_data['design_spec'] = spec_value
                    elif "Kích thước, khối lượng" in spec_name: product_data['size_weight_spec'] = spec_value
                    elif "Cổng kết nối" in spec_name or "Kết nối không dây" in spec_name:
                        current_conn_spec = product_data.get('connectivity_spec', '')
                        product_data['connectivity_spec'] = f"{current_conn_spec}{spec_name}: {spec_value} | "

            except Exception: continue
        
        # Lấy thông tin đánh giá
        try:
            rating_container = driver.find_element(By.CSS_SELECTOR, 'div.wrap_rating.wrap_border')
            product_data['average_rating'] = get_element_text(rating_container, '.point')
            total_reviews_text = get_element_text(rating_container, '.total-review')
            product_data['total_reviews'] = total_reviews_text.replace(' đánh giá', '')
        except NoSuchElementException:
            product_data['average_rating'] = 'N/A'
            product_data['total_reviews'] = 'N/A'
        
        # Lấy thông tin tồn kho
        product_data['stock_status'] = "Hết hàng"
        try:
            driver.find_element(By.CSS_SELECTOR, '.box-buy-detail, .btn-buy-now')
            product_data['stock_status'] = "Còn hàng"
        except NoSuchElementException: pass
        
        all_products_data.append(product_data)

    except Exception as e:
        print(f"  *** LỖI NGHIÊM TRỌNG KHI CÀO URL: {url} - BỎ QUA ***")
        print(f"  *** Chi tiết lỗi: {e} ***")
        failed_urls.append(url)
        continue

driver.quit()

# --- GIAI ĐOẠN 3: LƯU TẤT CẢ DỮ LIỆU RA FILE CSV ---
print("\n--- GIAI ĐOẠN 3: BẮT ĐẦU LƯU DỮ LIỆU RA FILE CSV ---")
if all_products_data:
    filename = 'laptops_full_data_thegioididong.csv'
    headers = [
        'product_name', 'current_price', 'list_price', 'brand', 'category', 
        'cpu_spec', 'ram_spec', 'storage_spec', 'screen_spec', 'gpu_spec',
        'os_spec', 'design_spec', 'size_weight_spec', 'connectivity_spec',
        'promotions_text', 'average_rating', 'total_reviews', 'stock_status',
        'product_sku', 'product_url'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_products_data)
    
    print(f"\nHOÀN TẤT! Đã cào và lưu thông tin chi tiết của {len(all_products_data)} laptop vào file '{filename}'.")
    if failed_urls:
        print(f"Cảnh báo: Có {len(failed_urls)} sản phẩm không thể cào do lỗi. Vui lòng kiểm tra file 'failed_urls.txt'.")
        with open('failed_urls.txt', 'w') as f:
            for url in failed_urls:
                f.write(f"{url}\n")
else:
    print("\nKhông cào được dữ liệu chi tiết của sản phẩm nào.")