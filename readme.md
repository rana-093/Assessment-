Run `docker-compose up --build` or `docker compose up --build` depending on the `docker compose` version, for quick deployment. 
It does the Customer and restaurant migration from the JSON to Database! So give it some time after using this command! 

But if you wanna run this individually, here is the approach:

> python3 -m venv venv <br>
> source venv/bin/activate <br>
> pip install -r requirements.txt <br>
> ./manage.py migrate <br>
> ./manage.py load_restaurant_data <br>
> ./manage.py load_customer_data <br>
> ./manage.py runserver

#### Look at the models under the restaurants and customer app. <br>
#### load_restaurant_data script is: `restaurant/management/commands/load_restaurant_data.py`
#### load_customer_data script is: `customer/management/commands/load_customer_data.py`

Base URL: **http://localhost:8000**

## Get open restaurants

**GET** `/api/v1/restaurants/open`

| Parameter  | Type                     | Description                           |
|------------|--------------------------|---------------------------------------|
| `datetime` | datetime in 24hrs format | Required. Format is: `yyyy-MM-ddTHH:mm` |

#### Example Request: `http://localhost:8000/api/v1/restaurants/open?datetime=2024-09-10T00:00`
#### Example response:
```json
[
  {
    "id": 12,
    "name": "1913 Restaurant",
    "cash_balance": "940.0100"
  },
  {
    "id": 15,
    "name": "230 Forest Avenue",
    "cash_balance": "4662.4000"
  }
]
```


## Get restaurants By Dish Count

**GET** `/api/v1/restaurants/by-dish-count`

| Parameter            | Type    | Description                                                             |
|----------------------|---------|-------------------------------------------------------------------------|
| `limit`              | integer | Required. Limits the number of results returned by the API.             |
| `dish_count_more_than` | integer | Optional. Filters restaurants with a dish count greater than the specified value. |
| `dish_count_less_than` | integer | Optional. Filters restaurants with a dish count less than the specified value.   |

`Either dish_count_more_than or dish_count_less_than has to be in query params here`
#### Example Request: `http://localhost:8000/api/v1/restaurants/by-dish-count?limit=100&dish_count_more_than=2&dish_count_less_than=4`
#### Example response:
```json
[
    {
        "id": 6773,
        "name": "100% de Agave",
        "cash_balance": "4629.9100"
    },
    {
        "id": 6796,
        "name": "5 Spot",
        "cash_balance": "304.1100"
    }
]
```


## Search Restaurant / Customer by Name

**GET** `/api/v1/search`

| Parameter              | Type    | Description                                                                       |
|------------------------|---------|-----------------------------------------------------------------------------------|
| `query`                | string  | Required. Searched value                                                          |

#### Example Request: `http://localhost:8000/api/v1/search?query=Americana - Des Moines`
#### Example response:
```json
[
    {
        "type": "restaurant",
        "name": "Americana - Des Moines",
        "relevance_score": 6
    }
]
```
Output is sorted by `relevance score` here. If the query matches exactly, relevance score is higher. If the query starts with some prefix then its relevance score is less than the previous case and so on!


## Buy Dish

**POST** `/api/v1/buy-dish`

#### Request Body: 

```json
    {
    "restaurant_id": integer, 
    "customer_id": integer,
    "dish_id": integer,
    "quantity": integer
}
```

#### Example Request: `http://localhost:8000/api/v1/buy-dish`
#### Example Body:
```json
{
    "restaurant_id": 6771,
    "customer_id": 2885,
    "dish_id": 58025,
    "quantity": 2
}
```
During a buy, race condition has been handled using `Database Lock`. And it has been made sure that whole operation is atomic. Like Adding amount to Restaurant cash balance and deducting amount from customer wallet

#### Example Response:
```json
{
    "id": 49006,
    "transaction_amount": "20.5000",
    "transaction_date": "2024-11-07T10:05:06.019026Z",
    "customer": 2885,
    "menu": 58025,
    "restaurant": 6771
}
```

