from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

def setup_cors(app:FastAPI)->None:
    """配置 CORS 中间件，允许前端开发服务器跨域访问"""
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    '''
    浏览器视 localhost 和 127.0.0.1 为不同的 origin。
    在地址栏输入 localhost:5173，Origin 头是 http://localhost:5173；
    输入 127.0.0.1:5173，Origin 头是 http://127.0.0.1:5173。
    只配一个的话，另一个打不开。两边都加上，避免这种无谓的排查时间。
    '''

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins, #origins 列表,精确匹配，不给 ["*"]。* 会导致 allow_credentials=True 不生效（浏览器安全限制）
        allow_credentials=True, #	后续 JWT 认证需要 Authorization header 跨域携带
        allow_methods=["*"], #开发阶段全放，生产收敛为 ["GET", "POST", "PUT", "DELETE"]
        allow_headers=["*"] #同上
    )






'''
浏览器有一个同源策略（Same-Origin Policy）：
localhost:5173 的页面发 AJAX 请求到 localhost:8000，浏览器会先拦截，问后端"允许吗？"
这个过程就是 CORS

localhost:5173 (前端页面)
       │
       │  fetch('/api/v1/health')
       ▼
浏览器先发一个 OPTIONS 预检请求 ──→ localhost:8000
       │                              │
       │                    后端说："允许 5173 访问"
       │                              │
       ▼                              ▼
  真正发 GET 请求 ──────────────→ 返回数据 ✅

'''


'''

Q: allow_origins=["*"] 加了但跨域还是报错，怎么回事？

检查是否同时设了 allow_credentials=True。浏览器规范禁止 credentials + origin=* 组合。如果你确实需要允许所有 origin + 携带 cookie，需要动态设置 allow_origin_regex 或写自定义中间件——但这种情况极少，通常意味架构设计有问题。

Q: 为什么不把 origins 放进 .env？

当前只有一个开发环境的 origin，不需要配置化。过度配置化的问题是：每加一个变量就增加一个理解负担。等到 Phase 3+ 需要支持 staging/production 多 origin 时再提取。这叫"推迟决策到最晚责任时刻"。
'''