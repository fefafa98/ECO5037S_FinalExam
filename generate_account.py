from algosdk import account, encoding, mnemonic

# Generate and store 5 accounts in a list
accounts = []

for i in range(5):
    private_key, address = account.generate_account()
    pass_phrase = mnemonic.from_private_key(private_key)
    
    accounts.append({
        "private_key": private_key,
        "address": address,
        "mnemonic": pass_phrase
    })
    
    print(f"Account {i+1}:")
    print("Private Key: ", private_key)
    print("Address: ", address)
    print("Mnemonic Phrase: ", pass_phrase)
    
    # Check if the address is valid
    if encoding.is_valid_address(address):
        print("The address is valid!\n")
    else:
        print("The address is invalid.\n")

# Store accounts in a variable for future use without re-running
print("\nAll Accounts Generated:")
for idx, acc in enumerate(accounts, start=1):
    print(f"Account {idx}: {acc['address']}")

# Save accounts to a file for re-use 
with open("accounts.txt", "w") as file:
     for acc in accounts:
         file.write(f"Address: {acc['address']}\nMnemonic: {acc['mnemonic']}\n\n")