from Constants.constants import Constants
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()  
try:
    driver.get(Constants.MANGOAPPS_URL + "/ce/pulse/admin/teams/group/all_projects")
    driver.maximize_window()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "user_id")))
    username_field = driver.find_element(By.ID, "user_id")
    username_field.send_keys(Constants.MANGOAPPS_USERNAME)
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(Constants.MANGOAPPS_PASSWORD_WITHOUTBASE64)
    login_button = driver.find_element(By.CSS_SELECTOR, "button.actionbutton")
    login_button.click()

    time.sleep(5)
    
    while True:
        try:
            dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sort_by"))
            )

            dropdown.click()

            options = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sort_options"))
            )

            delete_group_option = driver.find_element(By.XPATH, "//a[@value='delete_team']")
            delete_group_option.click()

            print("Clicked on Delete Group option successfully.")
            time.sleep(2)
            confirm_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "delete_confirm"))
            )
            confirm_input.send_keys("DELETE")
            delete_button = driver.find_element(By.ID, "team_delete_button")
            delete_button.click()

            print("Group deleted successfully.")
            time.sleep(3)

        except Exception as inner_exception:
            print("No more groups to delete or an error occurred.")
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

