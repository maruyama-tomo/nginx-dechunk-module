# NGINX HTTP unchunk module

sets Content-Length header for cached response so that browsers can estimate download time.

## Example Configuration

```nginx
load_module "/usr/lib64/nginx/modules/ngx_http_unchunk_module.so";

http {
    proxy_cache_path /var/lib/nginx/tmp/cache keys_zone=sample:10m max_size=10g;

    server {
        proxy_cache         sample;
        proxy_cache_valid   200 1h;
        proxy_http_version  1.1;

        proxy_cache_unchunk on;

        location / {
            proxy_pass http://upstream;
        }
    }
}
```

## Directives

|       |                                 |
|-------|---------------------------------|
|Syntax |**proxy_cache_unchunk** on \| off|
|Default|proxy_cache_unchunk off          |
|Context|http, server, location           |

Sets Content-Length header for cached response that was recieved from upstream with Transfer-Encoding: chunked.
