import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- PHẦN KHỞI TẠO ---
driver = webdriver.Chrome()
driver.maximize_window() # Phóng to cửa sổ trình duyệt
driver.get("https://www.thegioididong.com/laptop")
print("Đã mở trình duyệt và truy cập trang web.")
# Đợi 5 giây để trang web ổn định và tải hết các script/popup ban đầu
time.sleep(5) 

# --- PHẦN 1: TỰ ĐỘNG TẢI TẤT CẢ SẢN PHẨM ---
print("Bắt đầu quá trình tự động tải thêm sản phẩm...")
while True:
    try:
        # **SỬA LỖI QUAN TRỌNG NHẤT TẠI ĐÂY**
        # Sử dụng CSS Selector cực kỳ cụ thể để chỉ tìm nút "Xem thêm" của danh sách sản phẩm.
        # Selector này có nghĩa là: "Tìm thẻ <a> bên trong một thẻ <div> có class là 'view-more'".
        # Điều này đảm bảo không bao giờ nhầm lẫn với nút "Xem thêm" ở cuối trang.
        view_more_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.view-more > a"))
        )
        
        # Dùng JavaScript để cuộn đến nút và nhấn, đây là cách ổn định nhất
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_more_button)
        time.sleep(1) # Chờ một chút để hành động cuộn hoàn tất
        driver.execute_script("arguments[0].click();", view_more_button)
        
        print(f"Chương trình đã tự động nhấn '{view_more_button.text}'...")
        # Đợi 4 giây để sản phẩm mới tải về
        time.sleep(4) 
    except TimeoutException:
        # Lỗi này xảy ra khi đã hết nút "Xem thêm" -> Tải thành công
        print("Đã tải xong tất cả sản phẩm (không tìm thấy nút 'Xem thêm' nữa).")
        break
    except Exception as e:
        # Bắt các lỗi khác có thể xảy ra
        print(f"Gặp lỗi khi nhấn nút, có thể đã hết sản phẩm hoặc nút bị che khuất: {e}")
        break

# --- PHẦN 2: TỰ ĐỘNG CÀO DỮ LIỆU ---
print("\nBắt đầu cào dữ liệu từ các sản phẩm đã tải...")
laptops = []
product_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.listproduct > li.item')

for element in product_elements:
    try:
        name = element.find_element(By.CSS_SELECTOR, 'h3').text
        price = element.find_element(By.CSS_SELECTOR, '.price').text
        ram_info = "N/A"
        ssd_info = "N/A"
        
        specs = element.find_elements(By.CSS_SELECTOR, '.utility p')
        if len(specs) >= 2:
            ram_info = specs[0].text
            ssd_info = specs[1].text

        laptops.append({
            'Tên': name,
            'Giá': price,
            'RAM': ram_info,
            'SSD': ssd_info
        })
    except NoSuchElementException:
        continue

# Tự động đóng trình duyệt
driver.quit()

# --- PHẦN 3: TỰ ĐỘNG LƯU RA FILE CSV ---
if laptops:
    filename = 'laptops_thegioididong.csv'
    headers = ['Tên', 'Giá', 'RAM', 'SSD']
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(laptops)
    print(f"\nHOÀN TẤT! Đã cào và lưu thông tin của {len(laptops)} laptop vào file '{filename}'.")
else:
    print("\nKhông cào được dữ liệu của sản phẩm nào.")