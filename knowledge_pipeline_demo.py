##
import asyncio
import aiohttp
from jinja2 import Template

##
from simple_pocket_flow import AsyncNode, AsyncFlow
async def async_call_llm(prompt):
    messages = [
        {
            "role": "user",
            "content": prompt
        },
    ]
    request_data = {
        "model": "phi4-mini",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.8,
        "stream": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/v1/chat/completions",
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            r = await response.json()
            response = [choice["message"]["content"] for choice in r["choices"]][0]
        return response

class DuplicateColumns(AsyncNode):
    async def exec(self, sample):
        sample['base_document'] = sample['document']
    
class BaseLLMBlock(AsyncNode):
    async def exec(self, sample):
        prompt_string = await self.get_input(sample)
        if prompt_string == "<|invalid input|>":
            return "end"
        output_string = await async_call_llm(prompt_string)
        await self.parse_output(sample, output_string)
    
class SimpleInputParse:
    def __init__(self, prompt_template, **kwargs):
        self.prompt_template = Template(prompt_template)

    async def get_input(self, sample):
        try:
            input_str = self.prompt_template.render(sample).strip()
            return input_str
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "<|invalid input|>"
    
class SimpleOutParse:
    def __init__(self, output_cols, start_tags=[""], end_tags=[""], **kwargs):
        self.output_cols = output_cols
        self.start_tags = start_tags
        self.end_tags = end_tags

    async def parse_output(self, sample, output_string):
        for start_tag, end_tag, out_col in zip(self.start_tags, self.end_tags, self.output_cols):
            if not start_tag and not end_tag:
                sample[out_col] = output_string
            else:
                raise NotImplementedError
            
class SimpleLLMBlock(BaseLLMBlock, SimpleInputParse, SimpleOutParse):
    def __init__(self, **kwargs):
        BaseLLMBlock.__init__(self)
        SimpleInputParse.__init__(self, **kwargs)
        SimpleOutParse.__init__(self, **kwargs)


if __name__ == "__main__":
    import prompt_templates as pts
    duplicate = DuplicateColumns()
    detailed_summary = SimpleLLMBlock(
        prompt_template=pts.detailed_summary,
        output_cols = ["summary_detailed"],
    )
    atomic_facts = SimpleLLMBlock(
        prompt_template=pts.atomic_facts,
        output_cols = ["summary_atomic_facts"]
    )
    
    extractive_summary = SimpleLLMBlock(
        prompt_template=pts.extractive_summary,
        output_cols = ["summary_extractive"]
    )
    
    duplicate >> detailed_summary
    detailed_summary >> atomic_facts
    atomic_facts >> extractive_summary

    flow = AsyncFlow(start=duplicate)

    sample = {
        "document":"""
# Bank of America Advantage Plus Banking®

## Clarity Statement® — Overview of key policies and fees

### Account Information

- **Opening Deposit**: $100 or more
- **Monthly Maintenance Fee**: $12.00 each month. You can avoid the Monthly Maintenance Fee when you meet ONE of the following requirements during each statement cycle:
  - Make at least one qualifying Direct Deposit of $250 or more to your account, OR
  - Maintain a minimum daily balance of $1,500 or more in your account, OR
  - Be a member of the Preferred Rewards program. Learn more at bankofamerica.com/preferred-rewards.

### ATM Fees

| ATM Type                  | Fee       | Description                                                                 |
|---------------------------|-----------|-----------------------------------------------------------------------------|
| Bank of America ATMs      | No ATM fee | For deposits, withdrawals, transfers or balance inquiries                    |
| Non-Bank of America ATMs  | $2.50     | In the U.S., plus any fee charged by the ATM's operator                      |
|                           | $5.00     | Outside the U.S., plus any fee charged by the ATM's operator                 |

### Overdraft Policy

- To help you avoid fees, we won't authorize ATM withdrawals or everyday debit card purchases when you don't have enough money in your account at the time of the transaction.
- When we determine you don't have enough money in your account to cover other items such as checks or scheduled payments, we'll either authorize and pay the item and overdraw your account (an overdraft item), or decline or return the item unpaid (a returned item). When this happens, you may be charged a fee. See details below.
- We offer two overdraft setting options for how you want us to process your other transactions.

### Overdraft Settings and Fees

#### Option 1: Standard

- This setting will be automatically applied to your account.
  - Your checks and scheduled payments may be paid, causing an overdraft.
  - You may be charged an Overdraft Item Fee if you overdraw your account.
  - If we return an item unpaid, we won’t charge a fee, but the payee may.

#### Overdraft Item Fee

- **Fee**: $10.00 per item
  - *(We won’t charge you more than 2 of these fees per day.)*
- We won’t charge this fee:
  - If your account is overdrawn by $1 or less OR
  - For items that are $1 or less OR
  - On items that were authorized when your account had enough funds available OR
  - On ACH resubmissions labeled by the merchant as "RETRY PYMT" or "REDEP CHECK"

#### Option 2: Decline All

- You can choose this setting if you would like to have your transactions declined or returned unpaid when you don’t have enough money. With this setting you can avoid Overdraft Item Fees.
  - Checks or scheduled payments will be returned unpaid if you don’t have enough money in your account.
  - If your account becomes overdrawn for any reason, we won’t charge you an Overdraft Item Fee.
  - When we decline or return a transaction, we won’t charge a fee, but the payee may.

Keep in mind, regardless of your overdraft setting, if you set up Balance Connect® for overdraft protection, we’ll automatically transfer available funds from one or more of your linked backup accounts if you’re about to overdraw your account.

----

Please see the *Personal Schedule of Fees and Deposit Agreement and Disclosures* for your account terms.

1. Our overdraft fee of $10 may apply for overdrafts created by check, recurring debit card transactions, or other electronic means. If your account is overdrawn, you must immediately bring your account to a positive balance. We pay overdrafts at our discretion and we reserve the right not to pay. For example, we typically do not pay overdrafts if your account is not in good standing.
2. Transfers from a linked (1) brokerage account enrolled in margin lending, (2) Loan Management Account®, (3) credit card, or (4) line of credit and/or Home Equity Line of Credit are subject to interest charges and governed by the terms and conditions of the account.

*Information is current as of 11/2024 and is subject to change.*
---
# Additional Fees

| Service                          | Fee Details                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| Statement copies                 | **No fee** Paper copies available upon request. Printable statements are available in Online Banking. |
| Check images                     | **No fee** Printable check images from the last 18 months are available online. |
| Ordering checks                  | Varies Depending on the style you choose.                                   |
| Card replacement                 | **No fee** For each ATM or debit card.                                      |
|                                  | $15.00 For rush delivery.                                                   |
| Stop payment                     | $30.00 For each request; WAIVED for requests on debit card or Bill Pay transactions. |
| Cashier's checks                 | $15.00 For each check.                                                      |
| Domestic wire transfers          | $15.00 For each incoming wire transfer.                                     |
|                                  | $30.00 For each outgoing wire transfer.                                     |
| International wire transfers     | $15.00 For each incoming wire transfer: If received in a foreign currency, it will be converted into U.S. Dollars using the applicable exchange rate determined solely by us. |
|                                  | **No wire fee** For each outgoing wire transfer sent in foreign currency. Please be advised, exchange rate markups will apply. See below. |
|                                  | $45.00 For each outgoing wire transfer sent in U.S. Dollars.                |

For international wire transfers, other fees may also apply, including those charged by recipient's financial institution, foreign taxes, and other fees that are part of the wire transfer process. We profit from markups associated with the currency conversion included in our exchange rate (determined solely by us). Before sending a foreign currency, you should consider factors that impact the total cost or the amount available after transfer.

| Service                          | Fee Details                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| Non-Bank of America Teller Withdrawal | Per transaction, greater of $5.00 or 3% of the amount (maximum $100.00) when you use your ATM or debit card, or card number, to make a withdrawal, transfer or payment at another bank and it is processed as a cash disbursement. |

# When Your Deposits Are Available

- **Cash, direct deposits, wire transfers:** On the day we receive them.
- **Checks:** Usually the next business day if deposited before the financial center or ATM cutoff time.
- **Mobile Check Deposit:** Usually the next business day if deposited by applicable cutoff times. Please refer to **Deposit Checks**, then Help in the Mobile Banking app for additional details and terms and conditions.
- **If we place a hold on your deposit,** we'll let you know the hold reason and when your funds will be available. This is typically provided at the time of deposit but may also be mailed later. Deposits greater than $5,525 and checks deposited within the first 30 days of account opening may be held longer.

# How We Post Transactions

The way we post transactions impacts your account balance. If there's not enough available money in your account to cover all of your transactions, the posting order can impact the number of overdraft fees you incur. At the end of each business day, we'll group transactions received that day into categories before posting them. Below are the most common categories, and common transaction types in each, in the order that they generally post to your account. Keep in mind that transactions that are still processing may lower your available balance.

- **Deposits:** Added from highest to lowest dollar amount.
- **Many debit transactions:** Subtracted based on the date and time you made them. If our system doesn't receive date and time of the transaction, they are posted and subtracted from highest to lowest dollar amount. These include one-time and recurring debit card transactions, one-time transfers, ATM withdrawals, and checks cashed with our tellers.
- **Other checks you wrote:** Subtracted in check number order, unless our system cannot detect the check number; then they are posted and subtracted from highest to lowest dollar amount.
- **Most other electronic payments and preauthorized transfers:** Subtracted from highest to lowest dollar amount. These include scheduled transfers, online bill payments and preauthorized payments that use your account number.
- **Most fees:** Subtracted from highest to lowest dollar amounts.

# Get the Most Out of Your Account

- Review all the features and benefits of your new account at bankofamerica.com/quickstart
- For questions, schedule an appointment to visit a financial center at bankofamerica.com/appointments
- Call us at 800.432.1000

Additional fee waivers may be available to Bank of America Private Bank and qualified Merrill Lynch Wealth Management® clients. Please contact your advisor to learn more.

Merrill Lynch, Pierce, Fenner & Smith Incorporated (also referred to as "MLPF&S" or "Merrill") makes available certain investment products sponsored, managed, distributed or provided by companies that are affiliates of Bank of America Corporation ("BofA Corp."). MLPF&S is a registered broker-dealer, registered investment advisor, Member SIPC and a wholly owned subsidiary of BofA Corp. Banking products are provided by Bank of America, N.A., and affiliated banks, Members FDIC and wholly owned subsidiaries of Bank of America Corporation.

© 2024 Bank of America Corporation. 6812380 | 00-14-9315 | ALL STATES
"""
    }
    r = asyncio.run(flow.run_async(sample))
    print(sample['summary_atomic_facts'])
    # r = asyncio.run(async_call_llm("hi"))


    from IPython import embed; embed()