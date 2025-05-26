import requests
from bs4 import BeautifulSoup # To parse HTML and find flash messages or specific content

BASE_URL = 'http://127.0.0.1:5001' # Assuming app.py runs on this port

def extract_flash_messages(html_content):
    """Extracts flash messages from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    alerts = soup.find_all('div', class_=lambda x: x and x.startswith('alert-'))
    messages = [alert.get_text(strip=True) for alert in alerts]
    return messages

def signup_user(session, username, email, password):
    """Attempts to sign up a new user."""
    url = f"{BASE_URL}/signup"
    data = {
        'username': username,
        'email': email,
        'password': password
    }
    try:
        response = session.post(url, data=data, allow_redirects=True) # Allow redirects to see where it lands
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        flash_messages = extract_flash_messages(response.text)
        return response, flash_messages
    except requests.exceptions.RequestException as e:
        print(f"TEST_RUNNER_ERROR: Signup request failed: {e}")
        return None, [str(e)]

def login_user(session, username_or_email, password):
    """Attempts to log in a user."""
    url = f"{BASE_URL}/login"
    data = {
        'username': username_or_email,
        'password': password
    }
    try:
        response = session.post(url, data=data, allow_redirects=True)
        response.raise_for_status()
        flash_messages = extract_flash_messages(response.text)
        # Check if login was successful by looking for dashboard content or username in session (indirectly)
        # For now, we rely on redirection path and flash messages.
        is_successful = "dashboard" in response.url.lower() or any("welcome back" in msg.lower() for msg in flash_messages)
        return response, flash_messages, is_successful
    except requests.exceptions.RequestException as e:
        print(f"TEST_RUNNER_ERROR: Login request failed: {e}")
        return None, [str(e)], False

def logout_user(session):
    """Attempts to log out a user."""
    url = f"{BASE_URL}/logout"
    try:
        response = session.get(url, allow_redirects=True)
        response.raise_for_status()
        flash_messages = extract_flash_messages(response.text)
        is_successful = "login" in response.url.lower() or any("logged out" in msg.lower() for msg in flash_messages)
        return response, flash_messages, is_successful
    except requests.exceptions.RequestException as e:
        print(f"TEST_RUNNER_ERROR: Logout request failed: {e}")
        return None, [str(e)], False

def access_page(session, path):
    """Accesses a generic page and returns the response."""
    url = f"{BASE_URL}{path}"
    try:
        response = session.get(url, allow_redirects=True)
        # For protected pages, a 3xx redirect to login is common if not logged in.
        # For this generic access, we primarily care if it errors out.
        # Specific status code checks can be done by the caller.
        # response.raise_for_status() # Don't raise for status here, let caller decide based on expected behavior
        flash_messages = extract_flash_messages(response.text)
        return response, flash_messages
    except requests.exceptions.RequestException as e:
        print(f"TEST_RUNNER_ERROR: Accessing page {path} failed: {e}")
        return None, [str(e)]

if __name__ == '__main__':
    # Example Usage (for direct testing of this script)
    # Assumes app.py is running. This won't be part of the automated test flow directly.
    print("--- Direct Test Runner Tests ---")
    
    # Test 1: Sign up a new user
    test_session = requests.Session()
    print("Attempting signup for 'testrunneruser'...")
    signup_resp, signup_flash = signup_user(test_session, 'testrunneruser', 'testrunner@example.com', 'password123')
    if signup_resp:
        print(f"Signup Response URL: {signup_resp.url}, Status: {signup_resp.status_code}")
        print(f"Signup Flash: {signup_flash}")
    else:
        print("Signup failed.")

    # Test 2: Log in the user
    if signup_resp and "login" in signup_resp.url: # If signup redirected to login
        print("\nAttempting login for 'testrunneruser'...")
        login_resp, login_flash, login_success = login_user(test_session, 'testrunneruser', 'password123')
        if login_resp:
            print(f"Login Response URL: {login_resp.url}, Status: {login_resp.status_code}")
            print(f"Login Flash: {login_flash}")
            print(f"Login Successful Flag: {login_success}")

            if login_success:
                # Test 3: Access dashboard
                print("\nAttempting to access dashboard...")
                dash_resp, dash_flash = access_page(test_session, '/dashboard')
                if dash_resp:
                    print(f"Dashboard Response URL: {dash_resp.url}, Status: {dash_resp.status_code}")
                    # print(f"Dashboard Flash: {dash_flash}") # Usually no flash on direct dash access
                    # print(f"Dashboard Content (first 200 chars): {dash_resp.text[:200]}")
                
                # Test 4: Logout
                print("\nAttempting logout...")
                logout_resp, logout_flash, logout_success = logout_user(test_session)
                if logout_resp:
                    print(f"Logout Response URL: {logout_resp.url}, Status: {logout_resp.status_code}")
                    print(f"Logout Flash: {logout_flash}")
                    print(f"Logout Successful Flag: {logout_success}")
        else:
            print("Login failed.")
    
    print("--- End Direct Test Runner Tests ---")
