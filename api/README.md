### The API

The API has the following features:

* add source
* update source
* delete sources

### Example requests

#### Create source

Request:

```shell
curl --location --request POST 'http://localhost:8000/api/sources' \
--user admin:adminadnin \
--header 'Content-Type: application/json' \
--data-raw '{
    "tags": [],
    "interface": "website",
    "source": "http://www.example.com",
    "headline": "Hi there",
    "text": "Щось трапилося",
    "language": "ua",
    "timestamp": "2022-04-01T20:25:00Z",
    "pinned": "false",
    "translations": [],
    "locations": []
}'
```

#### List sources

Sources are sorted by timestamp in descending order (newest first).

List all, with default page size:

```shell
curl --location --request GET 'http://localhost:8000/api/sources' \
--user admin:adminadnin
```

List all, while setting page size (limit) and offset:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?limit=10&offset=1' \
--user admin:adminadnin
```

Filter by timestamp:

```shell
# exact
curl --location --request GET 'http://localhost:8000/api/sources?timestamp=2022-04-01T20%3A25%3A00Z' \
--user admin:adminadnin

# less than
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__lt=2022-04-01' \
--user admin:adminadnin

# less than or equal
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__lte=2022-04-01' \
--user admin:adminadnin

# greater than
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__gt=2022-04-01' \
--user admin:adminadnin

# greater than or equal
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__gte=2022-04-01' \
--user admin:adminadnin

# range
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__range=2022-04-01,2022-04-03' \
--user admin:adminadnin
```

Filter by interface:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?interface=twitter' \
--user admin:adminadnin
```

Filter by source:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?source=%40Blah' \
--user admin:adminadnin
```

Filter by `headline`, same filters for `text`:

```shell
# exact
curl --location --request GET 'http://localhost:8000/api/sources?headline=Terrible+events+in+Bucha' \
--user admin:adminadnin

# contains
curl --location --request GET 'http://localhost:8000/api/sources?headline__contains=Bucha' \
--user admin:adminadnin

# contains, case insensitive
curl --location --request GET 'http://localhost:8000/api/sources?headline_icontains=bucha' \
--user admin:adminadnin
```

Filter by tags:

```shell
# one tag
curl --location --request GET 'http://localhost:8000/api/sources?tags=Bucha' \
--user admin:adminadnin

# multiple tags
curl --location --request GET 'http://localhost:8000/api/sources?tags=Bucha' \
--user admin:adminadnin
```

#### Delete source

Request:

```shell
curl --location --request DELETE 'http://localhost:8000/api/sources/1' \
--user admin:adminadnin
```