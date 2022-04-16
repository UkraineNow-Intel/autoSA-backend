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
--user admin:adminadmin \
--header 'Content-Type: application/json' \
--data-raw '{
    "tags": [],
    "interface": "website",
    "origin": "http://www.example.com",
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

List all, with default page size. By default, `deleted` will be excluded:

```shell
curl --location --request GET 'http://localhost:8000/api/sources' \
--user admin:adminadmin
```

List all, including deleted:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?deleted=all' \
--user admin:adminadmin
```

List all, while setting page size (limit) and offset:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?limit=10&offset=1' \
--user admin:adminadmin
```

Filter by timestamp:

```shell
# exact
curl --location --request GET 'http://localhost:8000/api/sources?timestamp=2022-04-01T20%3A25%3A00Z' \
--user admin:adminadmin

# less than
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__lt=2022-04-01' \
--user admin:adminadmin

# less than or equal
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__lte=2022-04-01' \
--user admin:adminadmin

# greater than
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__gt=2022-04-01' \
--user admin:adminadmin

# greater than or equal
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__gte=2022-04-01' \
--user admin:adminadmin

# range
curl --location --request GET 'http://localhost:8000/api/sources?timestamp__range=2022-04-01,2022-04-03' \
--user admin:adminadmin
```

Filter by interface:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?interface=twitter' \
--user admin:adminadmin
```

Filter by origin:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?origin=%40Blah' \
--user admin:adminadmin
```

Filter by `headline`, same filters for `text`:

```shell
# exact
curl --location --request GET 'http://localhost:8000/api/sources?headline=Terrible+events+in+Bucha' \
--user admin:adminadmin

# contains
curl --location --request GET 'http://localhost:8000/api/sources?headline__contains=Bucha' \
--user admin:adminadmin

# contains, case insensitive
curl --location --request GET 'http://localhost:8000/api/sources?headline_icontains=bucha' \
--user admin:adminadmin
```

Filter by tags:

```shell
# one tag
curl --location --request GET 'http://localhost:8000/api/sources?tags=Bucha' \
--user admin:adminadmin

# multiple tags
curl --location --request GET 'http://localhost:8000/api/sources?tags=Bucha,Kharkiv' \
--user admin:adminadmin
```

Multi-search. Search for a keyword in `text` OR `headline` OR `tags`, case-insensitive:

```shell
curl --location --request GET 'http://localhost:8000/api/sources?q=Bucha' \
--user admin:adminadmin
```

#### Delete source

Request:

```shell
curl --location --request DELETE 'http://localhost:8000/api/sources/1' \
--user admin:adminadmin
```

### Manually refresh data

```shell
# skip items if external_id exists
curl --location --request GET 'http://localhost:8000/api/refresh/' \
--user admin:adminadmin

# update items if external_id exists
curl --location --request GET 'http://localhost:8000/api/refresh/?overwrite=true' \
--user admin:adminadmin
```
