import json
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

# Create an Algod client
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

# Generate random accounts for liquidity providers and traders
lp1_private_key, lp1_address = account.generate_account()
lp2_private_key, lp2_address = account.generate_account()
trader1_private_key, trader1_address = account.generate_account()
trader2_private_key, trader2_address = account.generate_account()

print(f"Liquidity Provider 1 Address: {lp1_address}")
print(f"Liquidity Provider 2 Address: {lp2_address}")
print(f"Trader 1 Address: {trader1_address}")
print(f"Trader 2 Address: {trader2_address}")

input("Fund the liquidity provider and trader accounts using the testnet dispenser and press Enter to continue...")

# Create a UCTZAR asset
def create_asset(creator_private_key, total_units):
    params = algod_client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=account.address_from_private_key(creator_private_key),
        sp=params,
        total=total_units,
        decimals=2,
        unit_name="UCTZAR",
        asset_name="UCTZAR Stablecoin",
        manager=None,
        reserve=None,
        freeze=None,
        clawback=None,
        strict_empty_address_check=False
    )
    stxn = txn.sign(creator_private_key)
    txid = algod_client.send_transaction(stxn)
    result = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Created UCTZAR ASA with ID: {result['asset-index']}")
    return result['asset-index']

uctzar_asset_id = create_asset(lp1_private_key, 1_000_000)

# Opt-in function
def opt_in_asset(account_private_key, asset_id):
    account_address = account.address_from_private_key(account_private_key)
    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=account_address,
        sp=params,
        receiver=account_address,
        amt=0,
        index=asset_id,
    )
    stxn = txn.sign(account_private_key)
    txid = algod_client.send_transaction(stxn)
    transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"{account_address} opted in to asset ID {asset_id}")

# Opt-in for all participants
opt_in_asset(lp2_private_key, uctzar_asset_id)
opt_in_asset(trader1_private_key, uctzar_asset_id)
opt_in_asset(trader2_private_key, uctzar_asset_id)

# Initialize liquidity pool
liquidity_pool = {
    "ALGO": 0,
    "UCTZAR": 0,
    "lp_tokens": {},  # Tracks LP token ownership
    "fees": 0  # Tracks accumulated fees
}

# Provide liquidity function
def provide_liquidity(lp_private_key, algo_amount, uctzar_amount):
    global liquidity_pool
    lp_address = account.address_from_private_key(lp_private_key)
    liquidity_pool["ALGO"] += algo_amount
    liquidity_pool["UCTZAR"] += uctzar_amount

    # Mint LP tokens based on the liquidity provided
    lp_tokens = algo_amount + uctzar_amount
    liquidity_pool["lp_tokens"][lp_address] = liquidity_pool["lp_tokens"].get(lp_address, 0) + lp_tokens

    print(f"{lp_address} provided liquidity: {algo_amount} ALGO, {uctzar_amount} UCTZAR. Total LP tokens: {lp_tokens}")

# Simulate trading
def trade(trader_private_key, trade_algo_to_uctzar, amount):
    global liquidity_pool
    trader_address = account.address_from_private_key(trader_private_key)
    params = algod_client.suggested_params()

    fee_rate = 0.003  # 0.3% fee
    if trade_algo_to_uctzar:
        txn = transaction.PaymentTxn(trader_address, params, lp1_address, amount)
        trade_uctzar = (amount * 2) * (1 - fee_rate)
        liquidity_pool["ALGO"] += amount
        liquidity_pool["UCTZAR"] -= trade_uctzar
        liquidity_pool["fees"] += amount * 2 * fee_rate
        print(f"Trader {trader_address} traded {amount} ALGO for {trade_uctzar} UCTZAR")
    else:
        txn = transaction.AssetTransferTxn(
            sender=trader_address,
            sp=params,
            receiver=lp1_address,
            amt=amount,
            index=uctzar_asset_id
        )
        trade_algo = (amount / 2) * (1 - fee_rate)
        liquidity_pool["UCTZAR"] += amount
        liquidity_pool["ALGO"] -= trade_algo
        liquidity_pool["fees"] += amount / 2 * fee_rate
        print(f"Trader {trader_address} traded {amount} UCTZAR for {trade_algo} ALGO")

# Distribute fees
def distribute_fees():
    global liquidity_pool
    total_fees = liquidity_pool["fees"]
    print(f"Total fees accumulated: {total_fees}")

    for lp_address, lp_token_share in liquidity_pool["lp_tokens"].items():
        lp_share_percentage = lp_token_share / sum(liquidity_pool["lp_tokens"].values())
        lp_reward = total_fees * lp_share_percentage
        print(f"Liquidity Provider {lp_address} receives {lp_reward} as fee reward.")
    
    # Reset fees after distribution
    liquidity_pool["fees"] = 0

provide_liquidity(lp1_private_key, 1000000, 2000000)
trade(trader1_private_key, True, 500000)
trade(trader2_private_key, False, 300000)
distribute_fees()


# Example trades
trade(trader1_private_key, True, 50)  # Trade ALGO for UCTZAR
trade(trader2_private_key, False, 30)  # Trade UCTZAR for ALGO
