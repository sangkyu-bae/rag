# runserver_debug.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,        # 🔥 Debug 모드에서는 절대 reload 금지
        log_level="debug",
        loop="asyncio",      # 🔥 PyCharm debugger와 충돌 방지
    )
