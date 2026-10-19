import requests


class Currency:
    @staticmethod
    def get_currency_rates(currency):
        currency_code = currency["code"]
        currency_name = currency["ru_name"]
        currency_symbol = currency["symbol"]
        try:
            response = requests.get(f'https://open.er-api.com/v6/latest/{currency_code}')
            response.raise_for_status()
            data = response.json()
            usd_rate = "?"
            eur_rate = "?"
            rub_rate = "?"
            if "USD" in data['rates']:
                usd_rate = data['rates']["USD"]
            if "EUR" in data['rates']:
                eur_rate = data['rates']["EUR"]
            if "RUB" in data['rates']:
                rub_rate = data['rates']["RUB"]
            if rub_rate == "?" or rub_rate == 1:
                message = (f" 1{currency_symbol} ({currency_code}, {currency_name}) равен"
                           f" {usd_rate:.2f} долларам США и {eur_rate:.2f} евро.")
            elif usd_rate == 1:
                message = (f" 1 {currency_symbol} ({currency_code}, {currency_name})"
                           f" равен {rub_rate:.2f} рублям и {eur_rate:.2f} евро.")
            elif eur_rate == 1:
                message = (f" 1 {currency_symbol} ({currency_code}, {currency_name}) "
                           f"равен {rub_rate:.2f} рублям и {usd_rate:.2f} долларам США.")
            else:
                message = (
                    f" 1 {currency_symbol} ({currency_code}, {currency_name}) равен {rub_rate:.2f}"
                    f" рублям, {usd_rate:.2f} долларам США и {eur_rate:.2f} евро.")
            return message
        except Exception as e:
            return f"Ошибка: {e}"

    @staticmethod
    def calculate_amount(amount, base_code, target_code):
        try:
            response = requests.get(f'https://open.er-api.com/v6/latest/{base_code}')
            response.raise_for_status()
            data = response.json()
            if target_code in data['rates']:
                exchange_rate = data['rates'][target_code]
                res = int(amount) * exchange_rate
                return str(round(res, 2))
        except Exception as e:
            return f"Ошибка: {e}"
