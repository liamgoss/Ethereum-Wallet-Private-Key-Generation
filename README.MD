# Wallet Generation (Proof of Concept)
**This code is for educational purposes only, I am not responsible for any misuse of this code**

I created this code in order to learn more about secp256k1 and how wallets and private keys are generated. All of these wallets generated can be imported into Metamask (if desired) because they are valid wallets and can even be viewed on Etherscan. These addresses are unique (given how the algorithm works), however, the odds of guessing a bitcoin private key are 1/10,000,000,000,000,000,000,000,000,000,000,000,000 - improbable, but not impossible!

Although inconceivably small, it is not impossible. As such, I included a way to query the wallet's `Ether` value on [Etherscan.io](https://etherscan.io/) just for fun. The amount of public/private keys you can generate is dependent on your hardware's capabilities. And the amount of wallets you can query on Etherscan is dependent on your internet speeds and API plan.

## Privacy Matters! 
This code is also useful for creating your own Ethereum mainnet compatible address and private key without the need for a third party like Metamask!
Did you know that when you have multiple accounts in your Metamask wallet, it uses the same api key across all your accounts? So any accounts in your Metamask can easily be linked together and then linked to you! 

With this code, you can create your address and private key without anyone knowing that the address is your's! Tornado and other anonymization services are great, but since you can generate hundreds of thousands of addresses within seconds, you could chain together a network of unknown, never before seen wallets to keep yourself private online!

## Usage

V1 of this code consists of my first attempt at generating values using the `secrets` Python module along with some commented notes.
V2 of this code is the newest version of the code with all aforementioned features.


Inside of V2, rename `env.example` to `.env` and fill out all desired values
- `ETHERSCAN_API_KEY` corresponds to the API generated for your account from [Etherscan.io](https://etherscan.io/)
- `SEARCH_ADDRESSES` is a string of comma separated wallet addresses (on the Ethereum mainnet) that, if the private key is generated for (near impossible, see odds above), you would like to be notified of in the output. Leave blank or put in a random address if unused.
- `AMOUNT_TO_GENERATE` is an integer value for how many wallet addresses and private keys you want to generate *Note: All of these, if the check balance option in the code is set to True, will be sent to Etherscan in batches of 20. This could take a long time, and could likely exceed your API plan's limits!*


The Flask web server will present all output files (if `OUTPUT_TO_FILE=True` is present in your `.env` file). This way you can configure this script to run on a server (you can setup automation via CRON if desired or just simply send a GET request) and you'll be able to view all outputs

The script can be via Flask run by sending a GET request (or visiting) to `127.0.0.5000/runGeneration` or `127.0.0.5000/runGenCheck`
You can port forward 5000 so that you can run this remotely.  

### Sample Output
```
Generating Ethereum Wallet Lists...
100% |#####################################################################################|
-----Generated 1000 unique addresses-----
-----Divided list into 50 sets of 20 addresses-----
Checking Ether Values...
[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>] 100% Time: 0:00:29

-----Process completed!-----
_____STATS_____
Amount of wallets generated:  1000
Amount of valuable wallets found:  0
Amount of wallets not checked: 0        [Due to Etherscan.io rate limiting]
```
