#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

static ngx_int_t ngx_http_dechunk_init(ngx_conf_t *cf);
static void *ngx_http_dechunk_create_loc_conf(ngx_conf_t *cf);
static char *ngx_http_dechunk_merge_loc_conf(ngx_conf_t *cf, void *parent, void *child);

static ngx_int_t ngx_http_dechunk_filter(ngx_http_request_t *r);

static ngx_http_module_t ngx_http_dechunk_module_ctx = {
    NULL, /* preconfiguration */
    ngx_http_dechunk_init, /* postconfiguration */
    NULL, /* create main configuration */
    NULL, /* init main configuration */
    NULL, /* create server configuration */
    NULL, /* merge server configuration */
    ngx_http_dechunk_create_loc_conf, /* create location configuration */
    ngx_http_dechunk_merge_loc_conf /* merge location configuration */
};

typedef struct {
    ngx_flag_t proxy_cache_dechunk;
} ngx_http_dechunk_loc_conf_t;

static ngx_command_t ngx_http_dechunk_commands[] = {
    { ngx_string("proxy_cache_dechunk"),
      NGX_HTTP_MAIN_CONF|NGX_HTTP_SRV_CONF|NGX_HTTP_LOC_CONF|NGX_HTTP_LIF_CONF|NGX_CONF_TAKE1,
      ngx_conf_set_flag_slot,
      NGX_HTTP_LOC_CONF_OFFSET,
      offsetof(ngx_http_dechunk_loc_conf_t, proxy_cache_dechunk),
      NULL},
    ngx_null_command
};

ngx_module_t ngx_http_dechunk_module = {
    NGX_MODULE_V1,
    &ngx_http_dechunk_module_ctx, /* module context */
    ngx_http_dechunk_commands, /* module directives */
    NGX_HTTP_MODULE, /* module type */
    NULL, /* init master */
    NULL, /* init module */
    NULL, /* init process */
    NULL, /* init thread */
    NULL, /* exit thread */
    NULL, /* exit process */
    NULL, /* exit master */
    NGX_MODULE_V1_PADDING
};

static ngx_http_output_header_filter_pt  ngx_http_next_header_filter;


static ngx_int_t ngx_http_dechunk_filter(ngx_http_request_t *r)
{
    ngx_http_dechunk_loc_conf_t *conf = ngx_http_get_module_loc_conf(r, ngx_http_dechunk_module);

    if (!conf->proxy_cache_dechunk || r->upstream == NULL || r->cache == NULL) {
        return ngx_http_next_header_filter(r);
    }

    if (r->upstream->cache_status == NGX_HTTP_CACHE_MISS ||
        r->upstream->cache_status == NGX_HTTP_CACHE_EXPIRED ||
        r->upstream->cache_status == NGX_HTTP_CACHE_BYPASS) {
        return ngx_http_next_header_filter(r);
    }

    if (r->cache->length <= (off_t)r->cache->body_start) {
        return ngx_http_next_header_filter(r);
    }

    r->allow_ranges = 1;

    if (r->headers_out.content_encoding && r->headers_out.content_encoding->value.len > 0) {
        r->allow_ranges = 0;
    }

    if (r->headers_out.content_length_n == -1) {
        r->headers_out.content_length_n = r->cache->length - r->cache->body_start;
    }

    return ngx_http_next_header_filter(r);
}


static ngx_int_t ngx_http_dechunk_init(ngx_conf_t *cf)
{
    ngx_http_next_header_filter = ngx_http_top_header_filter;
    ngx_http_top_header_filter = ngx_http_dechunk_filter;
    return NGX_OK;
}


static void *ngx_http_dechunk_create_loc_conf(ngx_conf_t *cf)
{
    ngx_http_dechunk_loc_conf_t *conf = ngx_pcalloc(cf->pool, sizeof(ngx_http_dechunk_loc_conf_t));
    if (conf == NULL)
        return NULL;
    conf->proxy_cache_dechunk = NGX_CONF_UNSET;
    return conf;
}


static char *ngx_http_dechunk_merge_loc_conf(ngx_conf_t *cf, void *parent, void *child)
{
    ngx_http_dechunk_loc_conf_t *prev = parent;
    ngx_http_dechunk_loc_conf_t *conf = child;
    ngx_conf_merge_value(conf->proxy_cache_dechunk, prev->proxy_cache_dechunk, 0);
    return NGX_CONF_OK;
}
