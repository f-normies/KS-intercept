# KS-intercept
KS-intercept is a tool designed to intercept data from ks.rsmu.ru

- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
  - [Install mitmproxy](#install-mitmproxy)
- [Usage](#usage)
- [License](#license)

## Installation
### Clone the Repository

First, you need to clone the repository from GitHub. Open a terminal or command prompt and navigate to the directory where you want to clone the repository. Then, run:

```sh
git clone https://github.com/f-normies/KS-intercept.git
cd KS-intercept
```

### Install Dependencies
Install the required dependencies listed in the requirements.txt file:

```sh
pip install -r requirements.txt
```

### Configure mitmproxy
1. *Set System Proxy to `localhost:8080`*
    * **Windows**:
        1. Open Settings and go to Network & Internet.
        2. Click on Proxy.
        3. In the Manual proxy setup section, set the Address to localhost and the Port to 8080.
        4. Save your changes.
    * **macOS**:
        1. Open System Preferences and go to Network.
        2. Select your active network connection and click Advanced.
        3. Go to the Proxies tab.
        4. Check Web Proxy (HTTP) and Secure Web Proxy (HTTPS).
        5. Set the Web Proxy Server and Secure Web Proxy Server to localhost and the Port to 8080.
        6. Click OK and then Apply.
    * **Linux**:
        1. Open Settings and go to Network.
        2. Click the Settings icon next to your network.
        3. Go to the Proxy tab.
        4. Select Manual and set the HTTP Proxy and HTTPS Proxy to localhost:8080.
        5. Save your changes.

2. *Install mitmproxy Certificates*
    * Open your browser and navigate to `http://mitm.it`
    * Follow the instructions on the website to download and install the mitmproxy certificate for your operating system and browser.
        
    * There can be no instructions, then:
        * **Windows**:
            1. Open Command Prompt as administrator and navigate to the mitmproxy directory: 
            ```
            cd %USERPROFILE%\.mitmproxy
            ```
            2. Install the certificate using the following command:
            ```
            certutil -addstore -f "ROOT" mitmproxy-ca-cert.pem
            ```
        * **macOS**:
            1. Open Terminal and navigate to the mitmproxy directory: 
            ```
            cd ~/.mitmproxy
            ```
            2. Install the certificate using the following command:
            ```
            sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain mitmproxy-ca-cert.pem
            ```
        * **Linux**:
            1. Open Terminal and navigate to the mitmproxy directory: 
            ```
            cd ~/.mitmproxy
            ```
            2. Copy the certificate to the system certificates directory:
            ```
            sudo cp mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy-ca-cert.crt
            ```
            3. Update the certificate store:
            ```
            sudo update-ca-certificates
            ```

## Usage
### WARNING
Any additional VPN, Proxy or another traffic-changing app can be a problem to work with. **Please, turn off any VPN, Proxy or another traffic-changing app SYSTEM-WIDE.**

### Start the Proxy
Navigate to the src\KS-intercept directory:
```sh
cd src\KS-intercept
```

To start the proxy and begin listening for browser requests, run:
```sh
python app.py start [-q, --quiet] 

OPTIONAL FLAGS:
-q  Suppress mitmproxy logs
```

After that you can open tests in `ks2.rsmu.ru`. **Using ks2 is important**.

### Save Collected Data
After intercepting the required data, run:

```sh
python app.py save
```

This command will save the collected data to the output folder.

### Stop the Proxy
To stop the proxy, run:

```sh
python app.py stop
```