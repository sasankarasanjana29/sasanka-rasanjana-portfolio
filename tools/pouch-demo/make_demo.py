"""Builds a fictional Pouch data file for portfolio screenshots, so no real money
shows on the site. Writes pouch-demo.json ({finance, settings}) next to this file.
Settings are copied from a given backup (theme, outfit, rates); the money is all made up.
Usage: python3 make_demo.py <backup-store.json> [YYYY-MM-DD, the day the shots are taken]"""
import json, random, sys, datetime as dt, os

random.seed(7)
TODAY = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else dt.date(2026, 10, 28)
ANCHOR_DAY = 20
d = lambda x: x.isoformat()

def cycle_start(day):
    s = day.replace(day=ANCHOR_DAY)
    if day.day < ANCHOR_DAY:
        m = s.month - 1 or 12
        s = s.replace(year=s.year - (1 if s.month == 1 else 0), month=m)
    return s

accounts = [
    {'id': 'cash', 'name': 'Cash', 'kind': 'cash', 'opening': 4_800, 'icon': 'Money', 'color': 1},
    {'id': 'bank', 'name': 'Everyday Bank', 'kind': 'bank', 'opening': 38_500, 'icon': 'CreditCard', 'color': 5},
    {'id': 'freelance', 'name': 'Freelance', 'kind': 'bank', 'opening': 12_000, 'icon': 'Coins', 'color': 4},
    {'id': 'card', 'name': 'Credit Card', 'kind': 'card', 'opening': 0, 'icon': 'CreditCard', 'color': 2, 'limit': 300_000, 'cardEnd': '4821'},
    {'id': 'savings', 'name': 'Savings', 'kind': 'savings', 'opening': 240_000, 'icon': 'PiggyBank', 'color': 6, 'rate': 7.5, 'rateFrom': '2026-06-01'},
    {'id': 'fd', 'name': 'Fixed Deposit', 'kind': 'savings', 'opening': 150_000, 'icon': 'PiggyBank', 'color': 1, 'rate': 9, 'rateFrom': '2026-06-01'},
]
P = lambda i, n, k, amt, g, icon: {'id': i, 'name': n, 'emoji': '', 'kind': k, 'planned': amt, 'group': g, 'icon': icon}
pots = [
    P('food', 'Eating out', 'flex', 12_000, 'food', 'fork.knife'),
    P('groceries', 'Groceries', 'flex', 22_000, 'food', 'cart.fill'),
    P('fuel', 'Fuel', 'flex', 9_000, 'transport', 'fuelpump.fill'),
    P('transport', 'Public transport', 'flex', 4_000, 'transport', 'bus.fill'),
    P('parking', 'Parking', 'flex', 1_500, 'transport', 'parkingsign.circle.fill'),
    P('rent', 'Rent', 'bill', 30_000, 'housing', 'house.fill'),
    P('internet', 'Internet', 'bill', 3_500, 'housing', 'wifi'),
    P('phone', 'Phone bill', 'bill', 1_500, 'housing', 'iphone'),
    P('clothes', 'Clothes', 'flex', 5_000, 'lifestyle', 'tshirt.fill'),
    P('gifts', 'Gifts', 'flex', 3_000, 'lifestyle', 'gift.fill'),
    P('books', 'Books and courses', 'flex', 4_000, 'lifestyle', 'graduationcap.fill'),
    P('cinema', 'Cinema', 'flex', 2_500, 'entertainment', 'film.fill'),
    P('gym', 'Gym', 'bill', 6_000, 'entertainment', 'dumbbell.fill'),
    P('misc', 'Miscellaneous', 'flex', 2_000, 'misc', 'shippingbox.fill'),
]
SPENDS = {  # pot: (merchants, low, high, times per cycle)
    'food': (['Lunch', 'Coffee shop', 'Rice and curry', 'Bakery'], 450, 1_900, 7),
    'groceries': (['Supermarket', 'Vegetable market', 'Corner shop'], 900, 6_500, 6),
    'fuel': (['Fuel station'], 2_500, 4_500, 3),
    'transport': (['Bus', 'Train', 'Taxi'], 120, 1_100, 6),
    'parking': (['Parking'], 100, 300, 4),
    'clothes': (['Clothing store'], 1_800, 4_200, 1),
    'gifts': (['Gift shop'], 1_200, 2_600, 1),
    'books': (['Bookshop', 'Online course'], 900, 3_200, 1),
    'cinema': (['Cinema'], 900, 2_200, 1),
    'misc': (['Pharmacy', 'Stationery'], 250, 900, 2),
}
txns, seq = [], 0
def add(**t):
    global seq
    seq += 1
    t.setdefault('reviewed', True)
    t['id'] = f'pf{seq:03d}'
    txns.append(t)

cur = cycle_start(TODAY)
starts = []
s = cur
for _ in range(6):
    starts.append(s)
    s = cycle_start(s - dt.timedelta(days=1))
starts.reverse()
for c0 in starts:
    last = min(c0 + dt.timedelta(days=30), TODAY)
    days = (last - c0).days
    add(kind='income', amount=150_000, date=d(c0), accountId='bank', merchant='Salary', recurringId='salary')
    add(kind='spend', amount=30_000, date=d(c0), accountId='bank', potId='rent', merchant='Landlord')
    if days >= 1: add(kind='spend', amount=3_500, date=d(c0 + dt.timedelta(days=1)), accountId='bank', potId='internet', merchant='Home internet')
    if days >= 2: add(kind='spend', amount=1_500, date=d(c0 + dt.timedelta(days=2)), accountId='card', potId='phone', merchant='Phone bill')
    if days >= 3: add(kind='spend', amount=6_000, date=d(c0 + dt.timedelta(days=3)), accountId='card', potId='gym', merchant='Gym', recurringId='gym')
    if days >= 1: add(kind='move', amount=25_000, date=d(c0 + dt.timedelta(days=1)), accountId='bank', toAccountId='savings', merchant='Monthly saving')
    frac = min(1, days / 30)
    before = len(txns)
    for pot, (names, lo, hi, n) in SPENDS.items():
        for _ in range(max(0, round(n * frac))):
            day = c0 + dt.timedelta(days=random.randint(0, max(0, days)))
            acct = random.choice(['card', 'cash', 'bank'])
            add(kind='spend', amount=random.randrange(lo, hi, 10), date=d(day), accountId=acct, potId=pot, merchant=random.choice(names))
    # Like a real person: cash comes from the ATM, and the card is paid off each month
    cyc = txns[before:]
    cash = sum(t['amount'] for t in cyc if t['accountId'] == 'cash')
    card = sum(t['amount'] for t in cyc if t['accountId'] == 'card')
    add(kind='move', amount=max(5_000, -(-cash // 1000) * 1000), date=d(c0), accountId='bank', toAccountId='cash', merchant='ATM')
    if days >= 25:
        add(kind='move', amount=card + 7_500, date=d(c0 + dt.timedelta(days=25)), accountId='bank', toAccountId='card', merchant='Card payment')

# Laptop bought on instalments last cycle: 90,000 down from savings, 150,000 over 12 months on the card.
plan_day = starts[-2] + dt.timedelta(days=1)
plans = [{'id': 'laptop', 'name': 'Laptop', 'date': d(plan_day), 'total': 240_000, 'treatment': 'own', 'potId': 'books',
          'down': {'amount': 90_000, 'fromAccountId': 'savings'},
          'financed': {'amount': 150_000, 'months': 12, 'accountId': 'card'}, 'firstDue': d(cur + dt.timedelta(days=1))}]
add(kind='move', amount=12_500, date=d(cur + dt.timedelta(days=2)), accountId='bank', toAccountId='card', merchant='Card payment', planId='laptop')
# Freelance work paid in US dollars, converted on entry (USD 250 at about 332).
add(kind='income', amount=83_050, date=d(starts[-2] + dt.timedelta(days=8)), accountId='freelance', merchant='Freelance design', note='USD 250.00 at 332.20')
# Normal bigger costs this month, so safe to spend looks like an ordinary month
add(kind='spend', amount=4_800, date='2026-10-12', accountId='card', potId='food', merchant='Birthday dinner')
add(kind='spend', amount=2_400, date='2026-10-26', accountId='card', potId='clothes', merchant='New shoes')
add(kind='spend', amount=2_200, date='2026-10-16', accountId='bank', potId='gifts', merchant='Wedding gift')
# A couple still to review today
for t in txns[-4:-2]:
    if t['kind'] == 'spend': t['reviewed'] = False

recurring = [
    {'id': 'salary', 'name': 'Salary', 'kind': 'income', 'amount': 150_000, 'accountId': 'bank', 'every': {'type': 'monthly', 'anchor': '2026-01-20'}, 'startDate': '2026-01-20'},
    {'id': 'gym', 'name': 'Gym membership', 'kind': 'spend', 'amount': 6_000, 'accountId': 'card', 'potId': 'gym', 'every': {'type': 'monthly', 'anchor': '2026-01-23'}, 'startDate': '2026-01-23'},
]
txns.sort(key=lambda t: t['date'])
finance = {'period': 'payday', 'currency': {'code': 'LKR', 'decimals': 0, 'symbol': 'Rs'}, 'cycle': {'type': 'monthly', 'anchor': '2026-01-20'},
           'accounts': accounts, 'pots': pots, 'txns': txns, 'recurring': recurring, 'plans': plans,
           'saveGoal': 20, 'saveTo': 'savings', 'rollover': False}
backup = json.load(open(sys.argv[1]))
settings = dict(backup['settings'])
settings.update({'appearance': 'light', 'seen': {'level': 0, 'week': ''}})
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pouch-demo.json')
json.dump({'finance': finance, 'settings': settings}, open(out, 'w'))
print(out, len(txns), 'entries')
