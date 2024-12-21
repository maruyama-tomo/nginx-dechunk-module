# ngx_http_cache_dechunk_filter_module

allows range request for cached response that was recieved from upstream with Transfer-Encoding: chunked.

## Example Configuration

```nginx
load_module "/usr/lib64/nginx/modules/ngx_http_cache_dechunk_filter_module.so";

http {
    proxy_cache_path /var/lib/nginx/tmp/cache keys_zone=sample:10m max_size=10g;

    server {
        proxy_cache         sample;
        proxy_cache_valid   200 1h;
        proxy_http_version  1.1;

        cache_dechunk on;

        location / {
            proxy_pass http://upstream;
        }
    }
}
```

## Directives

|       |                                 |
|-------|---------------------------------|
|Syntax |**cache_dechunk** on \| off      |
|Default|cache_dechunk off                |
|Context|http, server, location           |
