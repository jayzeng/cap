## CapitalOne Coding Exercise


#### How to run: 
Both Python 2.7 and 3.6 are supported, no external dependencies/libraries are required.  


Update credential.ini to provide appropriate secrets. (Don't want to check in secrets to GitHub)
```ini

[level_money]
api_token = 
uid = value (integer)
interview_token = value
```

Usage:
```
usage: main.py [-h] [--ignore-donuts] [--crystal-ball] [--ignore-cc-payments]

CapitalOne coding exercise

optional arguments:
  -h, --help            show this help message and exit
  --ignore-donuts, -id  filter out donut-related transactions (are you
                        serious!?)
  --crystal-ball, -cb   Merge this month's projected transactions
  --ignore-cc-payments, -ic
                        ignore cc payments
```

You can pass in one or all arguments, e.g::
```bash
python main.py --ignore-donuts --crystal-ball --ignore-cc-payments
```

or with Python 3.6
```bash
python3.6 main.py --ignore-donuts --crystal-ball --ignore-cc-payments
```

Sample output:
```json
    "2017-06-29T07:00:00.000Z": {
        "average": -253.0,
        "credit_type": "debit",
        "income": [],
        "spent": [
            -505100
        ],
        "total": -506.0,
        "total_income": 0,
        "total_spent": -505100
    },
    "2017-06-30T07:00:00.000Z": {
        "average": -258.0,
        "credit_type": "debit",
        "income": [],
        "spent": [
            -515700
        ],
        "total": -516.0,
        "total_income": 0,
        "total_spent": -515700
    }
}
```

Future improvements: 
- Retry API requests if fail (can use @retryable or swap in ```requests```)
- Cache API responses if response remains the same
- More API response validations
- Unit test + mock responses
- Expose functionalities through REST API w/ Docker & Docker Compose