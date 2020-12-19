from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from time import sleep
import datetime
import json
import random



def _get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(
        '--user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57"')
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver


def _login_instagram(driver, insta_username, insta_password):
    driver.get('https://www.instagram.com/accounts/login/')
    sleep(2)
    username_input = driver.find_element_by_css_selector("input[name='username']")
    password_input = driver.find_element_by_css_selector("input[name='password']")
    username_input.send_keys(insta_username)
    password_input.send_keys(insta_password)
    login_button = driver.find_element_by_xpath("//button[@type='submit']")
    login_button.click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Not Now')]"))).click()
    sleep(2)


def _get_following_of_user(driver, account, following_accounts_count):
    try:
        driver.get('https://www.instagram.com/%s' % account)
        sleep(1)
        driver.find_element_by_xpath('//a[contains(@href, "%s")]' % 'following').click()
        sleep(1)

        total_following_count = following_accounts_count
        current_following_count = 0
        user_following = []

        while current_following_count < total_following_count:
            current_following_count += 1
            try:
                scr1 = driver.find_element_by_xpath(
                    '/html/body/div[4]/div/div/div[2]/ul/div/li[%s]' % current_following_count)
                driver.execute_script("arguments[0].scrollIntoView();", scr1)
                sleep(0.5)
                text = scr1.text
                list = text.encode('utf-8').split()
                following_user = f'{list[0]}'
                following_user = following_user[2: len(following_user) - 1]
                user_following.append(following_user)

            except Exception as err:
                break

        return user_following

    except Exception as err:
        return None

def _get_insta_graph_for_users_with_empty_following_list(driver, all_insta_accounts, graph_edges, following_accounts_count):
    current_level = []
    current_level.extend(all_insta_accounts)
    print(f'new level {current_level}')
    for account in current_level:
        if graph_edges.get(account, None) is None:
            print(f'===> Account : {account}')
            following_of_account = _get_following_of_user(driver=driver, account=account, following_accounts_count=following_accounts_count)
            if following_of_account is not None and len(following_of_account) > 0:
                sorted_following_of_account = [val for val in following_of_account if val in all_insta_accounts]
                if len(sorted_following_of_account) > 0:
                    list_account_following = graph_edges.get(account, [])
                    list_account_following.extend(sorted_following_of_account)
                    graph_edges[account] = list_account_following
                    print(list_account_following)

    return all_insta_accounts, graph_edges

def _get_insta_graph(driver, all_insta_accounts, graph_edges, accounts_count, following_accounts_count):
    current_level = []
    current_level.extend(all_insta_accounts)
    total_accounts_count = accounts_count
    current_accounts_count = len(all_insta_accounts)

    while len(current_level) > 0 and current_accounts_count < total_accounts_count:
        print(f'new level {current_level}')
        new_level = []
        for account in current_level:
            if graph_edges.get(account, None) is None:
                print(f'===> Account : {account}')
                following_of_account = _get_following_of_user(driver=driver, account=account, following_accounts_count=following_accounts_count)
                if following_of_account is not None and len(following_of_account) > 0:
                    sorted_following_of_account = {}
                    for following_account in following_of_account:
                        print(f'     following {following_account}')
                        following_of_following_account = _get_following_of_user(driver=driver, account=following_account, following_accounts_count=following_accounts_count)
                        if following_of_following_account is not None and len(following_of_following_account) > 0:
                            count_common = [val for val in following_of_following_account if val in all_insta_accounts]
                            count_common = len(count_common)
                            sorted_following_of_account[following_account] = count_common
                        else:
                            sorted_following_of_account[following_account] = 0

                    sorted_following_of_account = sorted(sorted_following_of_account.items(), key=lambda d: d[1], reverse=True)
                    total_top_accounts_count = random.randint(1, 10)
                    current_top_accounts_count = 0
                    list_account_following = graph_edges.get(account, [])
                    for k, v in sorted_following_of_account:
                        if v != 0:
                            total_top_accounts_count -= 1
                        else:
                            current_top_accounts_count += 1
                            if current_top_accounts_count > total_top_accounts_count:
                                break
                        new_level.append(k)
                        list_account_following.append(k)

                    graph_edges[account] = list_account_following
        new_level = [val for val in new_level if val not in all_insta_accounts]
        if len(new_level) == 0:
            break
        all_insta_accounts.extend(new_level)
        current_level = new_level
        current_accounts_count = len(all_insta_accounts)
        print(f'count of accounts after this level : {current_accounts_count}')
    return all_insta_accounts, graph_edges

if __name__ == '__main__':

    insta_username = 'your_instagram_username'
    insta_password = 'your_instagram_password'

    all_insta_accounts_filename = 'all_insta_accounts.json'
    graph_edges_filename = 'graph_edges.json'

    all_insta_accounts = None
    graph_edges = None

    try:
        with open(all_insta_accounts_filename) as input_file:
            all_insta_accounts = json.load(input_file)
        with open(graph_edges_filename) as input_file:
            graph_edges = json.load(input_file)
    except:
        all_insta_accounts = ['instagram']
        graph_edges = {}

    print(len(all_insta_accounts), all_insta_accounts)
    print(len(graph_edges), graph_edges)

    driver = _get_driver()
    _login_instagram(driver=driver, insta_username=insta_username, insta_password=insta_password)
    all_insta_accounts, graph_edges = _get_insta_graph(driver=driver, all_insta_accounts=all_insta_accounts, graph_edges=graph_edges, accounts_count=200, following_accounts_count=20)
    all_insta_accounts, graph_edges = _get_insta_graph_for_users_with_empty_following_list(driver=driver, all_insta_accounts=all_insta_accounts, graph_edges=graph_edges, following_accounts_count=50)
    driver.quit()

    with open(all_insta_accounts_filename, "w") as output_file:
        json.dump(all_insta_accounts, output_file)
    with open(graph_edges_filename, "w") as output_file:
        json.dump(graph_edges, output_file)

