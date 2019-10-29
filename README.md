# NGINX HTTP dechunk module

allows range request for cached response that was recieved from upstream with Transfer-Encoding: chunked.

## Example Configuration

```nginx
load_module "/usr/lib64/nginx/modules/ngx_http_dechunk_module.so";

http {
    proxy_cache_path /var/lib/nginx/tmp/cache keys_zone=sample:10m max_size=10g;

    server {
        proxy_cache         sample;
        proxy_cache_valid   200 1h;
        proxy_http_version  1.1;

        proxy_cache_dechunk on;

        location / {
            proxy_pass http://upstream;
        }
    }
}
```

## Directives

|       |                                 |
|-------|---------------------------------|
|Syntax |**proxy_cache_dechunk** on \| off|
|Default|proxy_cache_dechunk off          |
|Context|http, server, location           |
