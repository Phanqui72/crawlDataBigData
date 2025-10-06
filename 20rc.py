import time
import csv
import re
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

# print("\n!!! CHẾ ĐỘ KIỂM TRA: Chỉ xử lý 5 sản phẩm đầu tiên. !!!")
# product_urls = product_urls[:5]

# --- GIAI ĐOẠN 2: TRUY CẬP TỪNG URL ĐỂ CÀO DỮ LIỆU CƠ BẢN ---
print("\n--- GIAI ĐOẠN 2: BẮT ĐẦU CÀO DỮ LIỆU CƠ BẢN TỪNG SẢN PHẨM ---")
all_products_data = []
total_urls = len(product_urls)
failed_urls = []
product_id_counter = 1 
LAPTOP_BRANDS = ['HP', 'Asus', 'Dell', 'Lenovo', 'MacBook', 'Acer', 'MSI', 'Gigabyte', 'LG', 'Samsung', 'Microsoft']

for i, url in enumerate(product_urls):
    try:
        driver.get(url)
        time.sleep(2) # Thời gian chờ có thể giảm bớt vì không cần đợi toàn bộ trang

        product_data = {}
        product_data['id'] = product_id_counter
        
        product_name = get_element_text(driver, 'h1')
        print(f"Đang cào sản phẩm ID {product_id_counter}/{total_urls}: {product_name}")

        # 1. Lấy các thông tin cơ bản
        product_data['product_name'] = product_name
        product_data['product_url'] = url

        # Lấy và làm sạch giá
        current_price = get_element_text(driver, '.box-price-present')
        list_price = get_element_text(driver, '.box-price-old')
        product_data['current_price'] = re.sub(r'[.₫*]', '', current_price).strip()
        product_data['list_price'] = re.sub(r'[.₫*]', '', list_price).strip()

        # Logic lấy brand
        brand_found = next((brand for brand in LAPTOP_BRANDS if brand.lower() in product_name.lower()), "N/A")
        product_data['brand'] = brand_found
        
        # Category cố định
        product_data['category'] = "Laptop"

        # Lấy và làm sạch thông tin đánh giá
        try:
            rating_container = driver.find_element(By.CSS_SELECTOR, 'div.wrap_rating.wrap_border')
            avg_rating_text = get_element_text(rating_container, '.point', '0')
            product_data['average_rating'] = avg_rating_text.split('/')[0].strip()
        except (NoSuchElementException, AttributeError):
            product_data['average_rating'] = 'N/A'
        
        all_products_data.append(product_data)
        product_id_counter += 1

    except Exception as e:
        print(f"  *** LỖI NGHIÊM TRỌNG KHI CÀO URL: {url} - BỎ QUA ***")
        print(f"  *** Chi tiết lỗi: {e} ***")
        failed_urls.append(url)
        continue

driver.quit()

# --- GIAI ĐOẠN 3: LƯU DỮ LIỆU RA FILE CSV ---
print("\n--- GIAI ĐOẠN 3: BẮT ĐẦU LƯU DỮ LIỆU RA FILE CSV ---")
if all_products_data:
    filename = 'laptops_basic_data_thegioididong.csv'
    # Cập nhật lại danh sách cột theo yêu cầu mới
    headers = [
        'id', 'product_name', 'current_price', 'list_price', 'brand', 'category', 
        'average_rating', 'product_url'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_products_data)
    
    print(f"\nHOÀN TẤT! Đã cào và lưu thông tin cơ bản của {len(all_products_data)} laptop vào file '{filename}'.")
    if failed_urls:
        print(f"Cảnh báo: Có {len(failed_urls)} sản phẩm không thể cào do lỗi. Vui lòng kiểm tra file 'failed_urls.txt'.")
        with open('failed_urls.txt', 'w') as f:
            for url in failed_urls:
                f.write(f"{url}\n")
else:
    print("\nKhông cào được dữ liệu của sản phẩm nào.")