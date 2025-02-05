Run `docker-compose up --build` or `docker compose up --build` depending on the `docker compose` version, for quick deployment. 
It does the Customer and restaurant migration from the JSON to Database! So give it some time after using this command! 

#### `You can update the DB configurations in local.py file under the food_delivery app. For now, it is configured to run as docker-compose config. Ideally it should be on the .gitignore file and this file should not be shared in the Github. But I kept it for the ease of yours to run it in one go without any manual efforts from your side. Thanks!` 

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


## Get All restaurants

**GET** `/api/v1/restaurants`

#### Example Request: `http://localhost:8000/api/v1/restaurants`
#### Example response:
```json
[
    {
        "id": 6772,
        "name": "100% Mexicano Restaurant",
        "cash_balance": "1320.1900"
    },
    {
        "id": 6773,
        "name": "100% de Agave",
        "cash_balance": "4629.9100"
    }
]
```

## Get menus under a restaurant

**GET** `/api/v1/restaurants/<int:restaurant_id>/menus`

#### Example Request: `http://localhost:8000/api/v1/restaurants/6771/menus`
#### Example response:
```json
[
    {
        "id": 58023,
        "name": "Sweetbreads",
        "price": "13.5700",
        "restaurant": 6771
    },
    {
        "id": 58024,
        "name": "Old pepper bourbon",
        "price": "10.1500",
        "restaurant": 6771
    }
]
```


## Get All Customers

**GET** `/api/v1/customers`

#### Example Request: `http://localhost:8000/api/v1/customers`
#### Example response:
```json
[
    {
        "id": 2001,
        "name": "Edith Johnson",
        "customer_id": 0,
        "cash_balance": "700.7000"
    },
    {
        "id": 2002,
        "name": "Edward Gonzalez",
        "customer_id": 1,
        "cash_balance": "237.6100"
    }
]
```

## Get purchase history for a customer

**GET** `/api/v1/customers/<int:customer_id>/purchase-histories`

#### Example Request: `http://localhost:8000/api/v1/customers/2001/purchase-histories`
#### Example response:
```json
[
    {
        "id": 39696,
        "transaction_amount": "13.1800",
        "transaction_date": "2020-02-10T04:09:00",
        "customer": 2001,
        "menu": 58698,
        "restaurant": 8330
    },
    {
        "id": 39697,
        "transaction_amount": "12.8100",
        "transaction_date": "2020-04-03T13:56:00",
        "customer": 2001,
        "menu": 58315,
        "restaurant": 8025
    }
]
```


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
#### Example Request: `http://localhost:8000/api/v1/restaurants/by-dish-count?limit=100&dish_count_more_than=2`
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
    "restaurant_id": "integer", 
    "customer_id": "integer",
    "dish_id": "integer",
    "quantity": "integer"
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
During a buy, race condition has been handled using `Database Lock`. 
And it has been made sure that whole operation is `atomic`. Like Adding amount to Restaurant cash balance and deducting amount from customer wallet
Moreover the `chosen dish should be present in that restaurant`. 
Otherwise it will give some validation errors. 
You can check from the `First 2  (Restaurants & Menus by restaurant)` for checking this endpoint. As the Database port is exposed to 5432 port. You can easily connect to this DB using tools like `PgAdmin / DataGrip / Dbeaver` etc.
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

#### Added Unit tests for search API. Plz see under the `customer/tests` folder! 

