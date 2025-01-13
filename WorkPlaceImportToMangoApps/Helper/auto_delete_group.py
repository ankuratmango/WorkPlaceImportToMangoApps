from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the driver (Chrome in this case)
driver = webdriver.Chrome()  # Ensure you have the correct version of chromedriver

try:
    # Open the login page
    driver.get("https://ankurqa.mangopulse.com/ce/pulse/admin/teams/group/all_projects")

    # Maximize the browser window
    driver.maximize_window()

    # Wait for the username field to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "user_id")))

    # Enter the username
    username_field = driver.find_element(By.ID, "user_id")
    username_field.send_keys("admin@ankurqa.com")
    
    # Enter the password
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("temp1234")

    # Click the login button
    login_button = driver.find_element(By.CSS_SELECTOR, "button.actionbutton")
    login_button.click()

    time.sleep(5)
    
    while True:
        try:
            # Wait for the dropdown to be visible
            dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sort_by"))
            )

            # Click to open the dropdown
            dropdown.click()

            # Wait for the dropdown options to be visible
            options = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sort_options"))
            )

            # Find the "Delete Group" option by its value attribute
            delete_group_option = driver.find_element(By.XPATH, "//a[@value='delete_team']")

            # Click the "Delete Group" option
            delete_group_option.click()

            print("Clicked on Delete Group option successfully.")

            # Wait for 2 seconds
            time.sleep(2)

            # Enter "DELETE" into the confirmation input field
            confirm_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "delete_confirm"))
            )
            confirm_input.send_keys("DELETE")

            # Click the "Delete" button
            delete_button = driver.find_element(By.ID, "team_delete_button")
            delete_button.click()

            print("Group deleted successfully.")

            # Wait for the page to reload
            time.sleep(3)

        except Exception as inner_exception:
            print("No more groups to delete or an error occurred.")
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the driver
    driver.quit()

