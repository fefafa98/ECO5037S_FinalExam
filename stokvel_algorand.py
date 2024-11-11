from typing import Dict, Any
from base64 import b64decode
from algosdk import account, transaction, mnemonic
from algosdk.v2client import algod

import time, json
# Setup Algod client for testnet
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""  # No token needed for public Algonode API

algod_client = algod.AlgodClient(algod_token, algod_address)

# Replace with your mnemonic phrases for each account
account_1_mnemonic = "allow raw mixture sort torch crumble gallery bullet payment clip normal lion daring second street night fee tool glue actor grid bomb task above output"
account_2_mnemonic = "ivory private relax phrase rifle remain rally brush when drum chief feature dolphin bounce work globe police quiz toast essence mother desk video about level"
account_3_mnemonic = "aim person afraid volcano security inch tool curious cushion alley faculty minimum kit drastic design bulk child note above metal sword friend brief abstract notice"
account_4_mnemonic = "audit print flag crop destroy staff art chicken sheriff demise unlock kitchen wise during zoo meadow sand shed badge super also planet goose ability this"
account_5_mnemonic = "climb host weapon tool damage copy flower energy same dinosaur sketch cook drop fiber flower shiver loan alcohol hero vintage bag army hunt ability useful"

import json
import random
from typing import List
from algosdk import account, transaction, mnemonic
from algosdk.v2client import algod

# Setup Algod client for testnet
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""  # No token needed for public Algonode API
algod_client = algod.AlgodClient(algod_token, algod_address)

# Replace with your mnemonic phrases
account_mnemonics = [
    "allow raw mixture sort torch crumble gallery bullet payment clip normal lion daring second street night fee tool glue actor grid bomb task above output",
    "ivory private relax phrase rifle remain rally brush when drum chief feature dolphin bounce work globe police quiz toast essence mother desk video about level",
    "aim person afraid volcano security inch tool curious cushion alley faculty minimum kit drastic design bulk child note above metal sword friend brief abstract notice",
    "audit print flag crop destroy staff art chicken sheriff demise unlock kitchen wise during zoo meadow sand shed badge super also planet goose ability this",
    "climb host weapon tool damage copy flower energy same dinosaur sketch cook drop fiber flower shiver loan alcohol hero vintage bag army hunt ability useful"
]

# Recover private keys and derive addresses
private_keys = [mnemonic.to_private_key(mn) for mn in account_mnemonics]
addresses = [account.address_from_private_key(pk) for pk in private_keys]

# Display account details
for i, addr in enumerate(addresses, start=1):
    print(f"Account {i} Address: {addr}")

# Prompt to fund all accounts
input("Please fund all accounts via the testnet dispenser (https://bank.testnet.algorand.network) and press Enter to continue...")

# Create multisig account
version = 1
threshold = 4  # Minimum 4 of 5 signatures required
msig = transaction.Multisig(version, threshold, addresses)
print(f"Multisig Address: {msig.address()}")

# Fund multisig account: Each member sends 5 Algo to the multisig account
sp = algod_client.suggested_params()
for i, pk in enumerate(private_keys):
    funding_txn = transaction.PaymentTxn(addresses[i], sp, msig.address(), int(5e6))  # 5 Algo
    funding_signed_txn = funding_txn.sign(pk)
    funding_txid = algod_client.send_transaction(funding_signed_txn)
    transaction.wait_for_confirmation(algod_client, funding_txid, 4)
    print(f"Account {i+1} funded multisig with 5 Algo. TxID: {funding_txid}")

# Simulate 5 monthly payout rounds
for month in range(1, 6):
    print(f"\n=== Month {month} ===")
    recipient = random.choice(addresses)  # Randomly select a recipient
    print(f"Recipient for Month {month}: {recipient}")

    # Create a payment transaction of 15 Algo
    payment_txn = transaction.PaymentTxn(
        msig.address(), sp, recipient, int(15e6)  # 15 Algo
    )
    
    # Multisig transaction: Collect 4 signatures
    msig_txn = transaction.MultisigTransaction(payment_txn, msig)
    msig_txn.sign(private_keys[0])  # 1st signature
    msig_txn.sign(private_keys[1])  # 2nd signature
    msig_txn.sign(private_keys[2])  # 3rd signature
    msig_txn.sign(private_keys[3])  # 4th signature

    # Submit the multisig transaction
    msig_txid = algod_client.send_transaction(msig_txn)
    result = transaction.wait_for_confirmation(algod_client, msig_txid, 4)
    print(f"Multisig payment for Month {month} confirmed in round {result['confirmed-round']}")

print("\n=== End of 5-month Stokvel cycle ===")
