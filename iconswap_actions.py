import pprint
import json
from tools.myConvertion import *
from tools.myConvertion import from_hex
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from configu import BASE_DOMAIN_URL_V3_FOR_TEST
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.utils.convert_type import convert_bytes_to_hex_str
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.builder.transaction_builder import (CallTransactionBuilder)

icon_service = IconService(HTTPProvider(BASE_DOMAIN_URL_V3_FOR_TEST))
pp = pprint.PrettyPrinter(width=3)
address = "Put address here"
icx_score = "cx0000000000000000000000000000000000000000"
iconswap_score = "cx90d86f087c70187d1a054473887165815f6251a8"
tap_score = "cx22ca8e22e3d570b671d7a5b29bbc15a266b7dfae"
nid = 3
icx_balance = from_bigint(icon_service.get_balance(address))

my_wallet = KeyWallet.load("wallet keystore location", "password")
print("[wallet1] address: ", my_wallet.get_address(), " private key: ", my_wallet.get_private_key())


def token_balance():
    """ Returns your Tap Balance"""

    call = CallBuilder().from_(my_wallet.get_address()) \
        .to(tap_score) \
        .method("balanceOf") \
        .params({"_owner": address}) \
        .build()
    result = icon_service.call(call)
    # print(f"{from_bighexa(result)} Tap")
    return from_bighexa(result)


def get_my_pending_swaps():
    """Returns a list of dictionaries with all the info we need for your last 100 pending swaps, else an empty list"""

    call = CallBuilder().from_("hxb11448743cbb63fcf29609401cdc5782793be211") \
        .to(iconswap_score) \
        .method("get_account_pending_swaps") \
        .params({"address": address, "offset": str(hex(0))}) \
        .build()
    result = icon_service.call(call)
    return result


def cancel_my_swap(swap_id):
    """Cancels my swap by id, Returning the txhash """
    swap_id = hex(swap_id)
    params = {"swap_id": swap_id}
    transaction = CallTransactionBuilder() \
        .from_(address) \
        .to(iconswap_score) \
        .value(0) \
        .method("cancel_swap") \
        .params(params) \
        .step_limit(40000000) \
        .nid(nid) \
        .nonce(50) \
        .build()

    signed_transaction = SignedTransaction(transaction, my_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash


def cancel_all_my_pending_swaps():
    """ Finding the pending swaps and cancelling them one by one"""
    pending_swaps = get_my_pending_swaps()

    for swap in pending_swaps:
        cancel_my_swap(from_hex(swap["id"]))
    print(f" All {len(pending_swaps)} swaps have been canceled with success")


def buy_tap_create_swap(icx_amount, tap_amount):
    """ Creating a buy swap order from the given amounts. Returning the tx hash"""

    if isinstance(icx_amount, int):
        icx_amount = int_to_bigint(icx_amount)
    else:
        icx_amount = float_value(icx_amount)

    tap_amount = int_to_bighexa(tap_amount)
    params = {"taker_contract": tap_score, "taker_amount": tap_amount}
    transaction = CallTransactionBuilder() \
        .from_(address) \
        .to(iconswap_score) \
        .value(icx_amount) \
        .method("create_icx_swap") \
        .params(params) \
        .step_limit(40000000) \
        .nid(nid) \
        .nonce(50) \
        .build()

    signed_transaction = SignedTransaction(transaction, my_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash


def buy_tap_fill_swap(icx_amount, swap_id):
    """ It will fill someone's sell order if you provide the icx_amount and the swap_id. Returns tx hash """

    if isinstance(icx_amount, int):
        icx_amount = int_to_bigint(icx_amount)
    else:
        icx_amount = float_value(icx_amount)

    swap_id = hex(swap_id)
    swap = {"swap_id": swap_id}

    transaction = CallTransactionBuilder() \
        .from_(address) \
        .to(iconswap_score) \
        .value(icx_amount) \
        .method("fill_icx_order") \
        .params(swap) \
        .step_limit(40000000) \
        .nid(nid) \
        .nonce(50) \
        .build()

    signed_transaction = SignedTransaction(transaction, my_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash


def sell_tap_create_swap(icx_amount, tap_amount):
    """ Creating a sell swap order from the given amounts. Returning the tx hash"""

    if isinstance(icx_amount, int):
        icx_amount = int_to_bigint(icx_amount)
    else:
        icx_amount = float_value(icx_amount)
    tap_amount = int_to_bighexa(tap_amount)
    pre_data = {"action": "create_irc2_swap", "taker_contract": icx_score, "taker_amount": hex(icx_amount)}
    aft_data = json.dumps(pre_data, separators=(',', ':')).encode('utf-8')
    data = convert_bytes_to_hex_str(aft_data)
    # c = convert_hex_str_to_bytes("put hash here")
    params = {"_to": iconswap_score, "_value": tap_amount, "_data": data}
    transaction = CallTransactionBuilder() \
        .from_(address) \
        .to(tap_score) \
        .step_limit(40000000) \
        .nid(nid) \
        .nonce(50) \
        .method("transfer") \
        .params(params) \
        .build()
    signed_transaction = SignedTransaction(transaction, my_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash


def sell_tap_fill_swap(tap_amount, swap_id):
    """ It will fill someone's sell order if you provide the tap_amount and the swap_id. Returns tx hash """
    swap_id = hex(swap_id)
    tap_amount = int_to_bighexa(tap_amount)
    pre_data = {'action': 'fill_irc2_order', 'swap_id': swap_id}
    aft_data = json.dumps(pre_data, separators=(',', ':')).encode('utf-8')
    data = convert_bytes_to_hex_str(aft_data)
    # c = convert_hex_str_to_bytes(" put has here")
    params = {"_to": iconswap_score, "_value": tap_amount, "_data": data}
    transaction = CallTransactionBuilder() \
        .from_(address) \
        .to(tap_score) \
        .step_limit(40000000) \
        .nid(nid) \
        .nonce(50) \
        .method("transfer") \
        .params(params) \
        .build()
    signed_transaction = SignedTransaction(transaction, my_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash


def get_filled_swaps_acc():
    """Returns a list of dictionaries for your last 100 filled swaps by wallet"""

    call = CallBuilder().from_("hxb11448743cbb63fcf29609401cdc5782793be211") \
        .to(iconswap_score) \
        .method("get_account_filled_swaps") \
        .params({"address": address, "offset": hex(0)}) \
        .build()
    result = icon_service.call(call)
    return result


def find_tap_buyers():
    """Returning the list of dictionaries with all the info for the 100 last buyers"""

    pair = icx_score + "/" + tap_score
    call = CallBuilder().from_("hxb11448743cbb63fcf29609401cdc5782793be211") \
        .to(iconswap_score) \
        .method("get_market_sellers_pending_swaps") \
        .params({"pair": pair, "offset": "0x0"}) \
        .build()
    result = icon_service.call(call)

    return result


def find_TAP_sellers():
    """Returning the list of dictionaries with all the info for the 100 last sellers"""

    pair = icx_score + "/" + tap_score
    call = CallBuilder().from_("hxb11448743cbb63fcf29609401cdc5782793be211") \
        .to(iconswap_score) \
        .method("get_market_buyers_pending_swaps") \
        .params({"pair": pair, "offset": "0x0"}) \
        .build()
    result = icon_service.call(call)

    return result


"""
Test what each function does.
1)For icx values use integer or decimal. For tap values use only integer.
2)Uncomment one function at the time to see the result. Go to UI and check there.
3) We will print the result in a more readable way later.
"""

# print("You will put a swap order to buy 1000 tap for 10 icx")
# buy_tap_create_swap(10, 1000)

# print("You will put a swap order to sell 1000 tap for 10 tap")
# sell_tap_create_swap(10,1000)


# print("You will buy-fill a swap sell order. Provide icx and swap id. Ex: Buy 1 icx to the swap id 364. Check UI")
# buy_tap_fill_swap(1,364)

# print("You will sell-fill a swap buy order. Provide tap and swap id. Ex: Sell 1 tap to the swap id 441. Check UI")
# sell_tap_fill_swap(1,441)

# print("Canceling your swap order by providing the id in the brackets")
# cancel_my_swap()

# print("Finding you pending swaps. Have at least 1 order to see the result")
# swaps = get_my_pending_swaps()
# for swap in swaps:
#     pp.pprint(swap)


# print("It will find and cancel all your pending swaps")
# cancel_all_my_pending_swaps()


# print("It will find your last 100 swaps")
# pp.pprint(get_filled_swaps_acc())


# print("It will find those who want to buy tap and sell icx ")
# pp.pprint(find_tap_buyers())


# print("It will find those who want to sell tap and buy icx ")
# pp.pprint(find_TAP_sellers())
