from codecs import backslashreplace_errors
from functools import cache
from json import JSONDecodeError
from platform import java_ver
from progressbar import ProgressBar, Percentage, Bar, ETA
from pprint import pprint
import blocksmith, time, sys, os, uuid, datetime
from dotenv import load_dotenv
from etherscan import Etherscan
from pathlib import Path

##############################################
# Author: https://github.com/liamgoss        #
# This code is for educational purposes only #
#  The author is not responsible for misuse  #
##############################################


##############################################
#       Load in Environment Variables        #
##############################################
load_dotenv()
eth = Etherscan(os.environ.get("ETHERSCAN_API_KEY"))
searchAddresses = os.environ.get('SEARCH_ADDRESSES')
intoFile = bool(os.environ.get('OUTPUT_TO_FILE'))


if len(searchAddresses) == 0:
    # No search addresses provided
    searchAddresses = []
else:
    # Turn lengthy string into list
    searchAddresses = searchAddresses.split(',')

amountToGen=int(os.environ.get("AMOUNT_TO_GENERATE"))

# Define global (non .env) variables
pbar = ProgressBar()
savedAddresses = []
savedKeys = []


##############################################
#     Functions from Blocksmith Library      #
##############################################
def generatePrivateKey():
    # Generate Private Key
    kg = blocksmith.KeyGenerator()
    kg.seed_input('Truly random string. I rolled a dice and got 4.')
    key = kg.generate_key()
    return key

def privateKeyToBitcoinWallet(key):
    # Create Bitcoin wallet from private key
    address = blocksmith.BitcoinWallet.generate_address(key)
    return address
    

def privateKeyToEthereumWallet(key):
    # Create Ethereum wallet from private key
    address = blocksmith.EthereumWallet.generate_address(key)
    checksum_address = blocksmith.EthereumWallet.checksum_address(address)
    return checksum_address


##############################################
#   Custom Logic / Wrappers for Above Code   #
##############################################
def generateWallets(amount=amountToGen, bal=False, search=searchAddresses, printVals=False, saveAll=True):
    # bal is unused unless you use the code snippet commented out below
    # printVals will print every single address and private key generated (which is useful for piping into files) but can mess up the progress bar's display (nonfatal issue)
    # This function saves addresses to the global lists rather than local lists, this way we can return specific values such as a searchable wallet address's private key while also being able to access these generated values outside of the function

    # I noticed there was some weird behavior when bal and saveAll where both true, so for now I just avoid that use case
    if saveAll and bal:
        sys.exit("bal and saveAll conflict when both true (for now)")
    print("Generating Ethereum Wallet Lists...")
    for i in pbar(range(amount)):
        privateKey = generatePrivateKey()
        walletAddress = privateKeyToEthereumWallet(privateKey)
        if printVals == True:
            print(f"{walletAddress}\t:\t{privateKey}")
        if saveAll == True:
            savedAddresses.append(walletAddress)
            savedKeys.append(privateKey)
        # If you want to check individual balances as you generate them, use the following block of code
        '''if bal == True:
            try:
                balance = eth.get_eth_balance(walletAddress)
                if balance != '0':
                    print("Ether detected!")
                    print("Wallet: ", walletAddress)
                    print("Private Key: ", privateKey)
                    print("Balance: ", balance)
                    savedAddresses.append(walletAddress)
                    savedKeys.append(privateKey)
                else:
                    if printVals == True:
                        print("0 Ether balance...")
            except JSONDecodeError:
                # If you would like to track how many API calls fail (due to your limit being exceeded or some other issue) you can put your logic here
                #balanceCheckFailCount = balanceCheckFailCount + 1
                pass
        '''
        if walletAddress in search:
            print("WALLET FOUND")
            print("Wallet Address: ", walletAddress)
            print("Private Key: ", privateKey)
            return walletAddress, privateKey
 
def checkBalances():
    # We can check the balances inside of the generateWallets() function but this allows for more speed and more flexibility by checking them after the fact
    # As of now, when you call generateWallets(), saveAll must be set to true in order to use this function on those addresses



    # In order to save on API calls, we will use Etherscan's built in ability to query addresses in batches of up to 20.
    # n will be how many addresses you want queried at a time (MAX: 20)
    n = 20
    dividedList = [savedAddresses[i * n:(i + 1) * n] for i in range((len(savedAddresses) + n - 1) // n )]
    print(f"-----Generated {amountToGen} unique addresses-----")
    print(f"-----Divided list into {len(dividedList)} sets of {n} addresses-----")
    print("Checking Ether Values...")
    # hits will hold the number of addresses that had Ether in them, if any
    hits = 0

    # Setting ProgressBar's maxval is important because the progress bar defaults to being filled at value 100, so if we generate more than 100 wallets, we need to make sure the progress bar won't throw an error
    pbar_Large = ProgressBar(widgets=[Bar('>', '[', ']'), ' ',
                                                Percentage(), ' ',
                                                ETA()],maxval=amountToGen/n).start()
    failedCount = 0
    for i in range(len(dividedList)):
        try:
            # TODO: Can we implement the same API functionality for Binance Smart Chain and the Polygon mainnet? 
            setOfNBalances = eth.get_eth_balance_multiple(dividedList[i])
        except: #except JSONDecodeError: # It's a better practice to specify that specific error, 
            #                               but there may be errors returned by Etherscan I haven't seen yet so let's catch them all
            # We simply wait and retry the request half a second later just in case we sent too many requests
            # You can increase, decrease, or remove this delay but I figured 0.5s is not a *ton* of added time (depends on how many wallets, of course)
            time.sleep(0.5)
            try:
                setOfNBalances = eth.get_eth_balance_multiple(dividedList[i])
            except: #except JSONDecodeError:
                failedCount = failedCount + 1
                pass
        
        
        for j in range(len(setOfNBalances)):
            if setOfNBalances[j]['balance'] != '0':
                # We have an account with $$$ in it
                hits = hits + 1
                index = savedAddresses.index(setOfNBalances[j]['account'])
                print(f"{savedAddresses[index]}\t{savedKeys[index]}\tBalance: {setOfNBalances[j]['balance']} Ether")
        pbar_Large.update(i)
    # There may be an error where it claims to have completed but it stops at like 4%? 
    # The issue was due to the maximum value being set to what we generate but I overlooked the fact that I am dividing the calls by n
    #       This has since be fixed
    
    # The amount of API calls on etherscan.io doesn't seem to align with how many calls we should be making
    # Either my understanding of this is wrong or somehow my code to detect failed calls is flawed
    pbar_Large.finish()
    print(f"\n-----Process completed!-----")
    print("_____STATS_____")
    print("Amount of wallets generated: ", amountToGen)
    print("Amount of valuable wallets found: ", hits)
    # Multiply failedCount by n because one failed call = n addresses failed to be checked
    print(f"Amount of wallets not checked: {failedCount * n}\t[Due to Etherscan.io rate limiting]")



def generateWallets_File(amount=amountToGen, bal=False, search=searchAddresses, printVals=False, saveAll=True, unique_filename="ERROR-NONAME.log", count=False):
    with open(unique_filename, 'a') as outFile:
        # bal is unused unless you use the code snippet commented out below
        # printVals will print every single address and private key generated (which is useful for piping into files) but can mess up the progress bar's display (nonfatal issue)
        # This function saves addresses to the global lists rather than local lists, this way we can return specific values such as a searchable wallet address's private key while also being able to access these generated values outside of the function
 
        # I noticed there was some weird behavior when bal and saveAll where both true, so for now I just avoid that use case
        if saveAll and bal:
            sys.exit("bal and saveAll conflict when both true (for now)")
        outFile.write("Generating Ethereum Wallet Lists...\n")
        for i in range(amount):
            privateKey = generatePrivateKey()
            walletAddress = privateKeyToEthereumWallet(privateKey)
            if printVals == True:

                # value_when_true if condition else value_when_false
                # fruit = 'Apple'
                # isApple = True if fruit == 'Apple' else False
                if count:
                    txCount = getTransactionCount(walletAddress, 0, 99999999, "asc")
                else:
                    txCount = -1 # Need to assign this before referencing it below
                outFile.write(f"{walletAddress}\t:\t{privateKey}\t:\t{txCount}\n") if count else outFile.write(f"{walletAddress}\t:\t{privateKey}\n")
            if saveAll == True:
                savedAddresses.append(walletAddress)
                savedKeys.append(privateKey)
            # If you want to check individual balances as you generate them, use the following block of code
            '''if bal == True:
                try:
                    balance = eth.get_eth_balance(walletAddress)
                    if balance != '0':
                        print("Ether detected!")
                        print("Wallet: ", walletAddress)
                        print("Private Key: ", privateKey)
                        print("Balance: ", balance)
                        savedAddresses.append(walletAddress)
                        savedKeys.append(privateKey)
                    else:
                        if printVals == True:
                            print("0 Ether balance...")
                except JSONDecodeError:
                    # If you would like to track how many API calls fail (due to your limit being exceeded or some other issue) you can put your logic here
                    #balanceCheckFailCount = balanceCheckFailCount + 1
                    pass
            '''
            if walletAddress in search:
                outFile.write("\nWALLET FOUND")
                outFile.write(f"\nWallet Address: {walletAddress}")
                outFile.write(f"\nPrivate Key: {privateKey}")
                #return walletAddress, privateKey
        outFile.write("\n-----GENERATION COMPLETE-----\n")
    

def checkBalances_File(unique_filename):
    
    with open(unique_filename, 'a') as outFile:
        print(f"opened: {outFile}")
        # We can check the balances inside of the generateWallets() function but this allows for more speed and more flexibility by checking them after the fact
        # As of now, when you call generateWallets(), saveAll must be set to true in order to use this function on those addresses



        # In order to save on API calls, we will use Etherscan's built in ability to query addresses in batches of up to 20.
        # n will be how many addresses you want queried at a time (MAX: 20)
        n = 20
        dividedList = [savedAddresses[i * n:(i + 1) * n] for i in range((len(savedAddresses) + n - 1) // n )]
        outFile.write(f"\n-----Generated {amountToGen} unique addresses-----")
        outFile.write(f"\n-----Divided list into {len(dividedList)} sets of {n} addresses-----")
        outFile.write("\nChecking Ether Values...")
        # hits will hold the number of addresses that had Ether in them, if any
        hits = 0

        failedCount = 0
        for i in range(len(dividedList)):
            try:
                # TODO: Can we implement the same API functionality for Binance Smart Chain and the Polygon mainnet? 
                setOfNBalances = eth.get_eth_balance_multiple(dividedList[i])
            except: #except JSONDecodeError: # It's a better practice to specify that specific error, 
                #                               but there may be errors returned by Etherscan I haven't seen yet so let's catch them all
                # We simply wait and retry the request half a second later just in case we sent too many requests
                # You can increase, decrease, or remove this delay but I figured 0.5s is not a *ton* of added time (depends on how many wallets, of course)
                time.sleep(0.5)
                try:
                    setOfNBalances = eth.get_eth_balance_multiple(dividedList[i])
                except: #except JSONDecodeError:
                    failedCount = failedCount + 1
                    pass
            
            
            for j in range(len(setOfNBalances)):
                if setOfNBalances[j]['balance'] != '0':
                    # We have an account with $$$ in it
                    hits = hits + 1
                    index = savedAddresses.index(setOfNBalances[j]['account'])
                    outFile.write(f"{savedAddresses[index]}\t{savedKeys[index]}\tBalance: {setOfNBalances[j]['balance']} Ether")
            
        
        outFile.write(f"\n-----Process completed!-----")
        outFile.write("\n_____STATS_____")
        outFile.write(f"\nAmount of wallets generated: {amountToGen}")
        outFile.write(f"\nAmount of valuable wallets found: {hits}")
        # Multiply failedCount by n because one failed call = n addresses failed to be checked
        outFile.write(f"\nAmount of wallets not checked: {failedCount * n}\t[Due to Etherscan.io rate limiting]")
    

def getTransactionCount(address, startBlock, endBlock, sortStr, consolePrint=False):
    try:
        txList = eth.get_normal_txs_by_address(address, startBlock, endBlock, sortStr)
        print(f"{len(txList)} transaction(s) for {address}") if consolePrint else len(txList) # Need an else statement so doing this to accomplish nothing 

        '''
        print(txList[i][k]) where i is transaction index in list, k is a (string) dictionary key from below
        ____Dictionary Keys____
            "blockNumber"
            "timeStamp"
            "hash"
            "nonce"
            "blockHash"
            "transactionIndex"
            "from"
            "to"
            "value"
            "gas"
            "gasPrice"
            "isError"
            "txreceipt_status"
            "input"
            "contractAddress"
            "cumulativeGasUsed"
            "gasUsed"
            "confirmations"
        '''
        return len(txList)
    except AssertionError:
        if consolePrint:
            print(f"No transactions for {address}")
        return 0
    


# These functions are used to be imported to streamline the flask implementation
def runAll():
    if intoFile == True:
        unique_filename = os.path.join(str(Path(__file__).parent.resolve())[:-2], str("webServer/static/" + datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S__') + str(uuid.uuid4()) + '.log'))
        start = time.time()
        generateWallets_File(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True, unique_filename=unique_filename)
        checkBalances_File(unique_filename)
        end = time.time()
        print("Time Elapsed (seconds):", end - start)
    else:
        start = time.time()
        generateWallets(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True)
        checkBalances()
        end = time.time()
        print("Time Elapsed (seconds):", end - start)
    

def runGen():
    if intoFile == True:
        unique_filename = os.path.join(str(Path(__file__).parent.resolve())[:-2], str("webServer/static/" + datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S__') + str(uuid.uuid4()) + '.log'))
        start = time.time()
        generateWallets_File(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True, unique_filename=unique_filename)
        end = time.time()
        print("Time Elapsed (seconds):", end - start)
    else:
        start = time.time()
        generateWallets(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True)
        end = time.time()
        print("Time Elapsed (seconds):", end - start)
    
def runTransCount():
    if intoFile == True:
        unique_filename = os.path.join(str(Path(__file__).parent.resolve())[:-2], str("webServer/static/" + datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S__') + str(uuid.uuid4()) + '.log'))
        start = time.time()
        generateWallets_File(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True, unique_filename=unique_filename,count=True)
        end = time.time()
        print("Time Elapsed (seconds):", end - start)
    else:
        start = time.time()
        generateWallets(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True, count=True)
        end = time.time()
        print("Time Elapsed (seconds):", end - start)


'''
if __name__ == '__main__':
    start = time.time()
    generateWallets(amount=amountToGen, bal=False, search=searchAddresses, printVals=True, saveAll=True)
    #checkBalances()
    end = time.time()
    print("Time Elapsed (seconds):", end - start)
    if intoFile == True:
        # This will help separate outputs if desired
        print("~~~~~~END_OF_RUN~~~~~~") 
'''

if __name__ == '__main__':
    
    tx = getTransactionCount('0x73BCEb1Cd57C711feaC4224D062b0F6ff338501e', 0, 99999999, "asc", consolePrint=True)
    if tx == 0:
        print(tx)
    else:
        print(tx)
    
    