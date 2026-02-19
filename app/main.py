from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.employee.router import router as employee_router
from app.modules.manager.router import router as manager_router
from app.modules.invites.router import router as invites_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(invites_router)
app.include_router(employee_router)
app.include_router(manager_router)