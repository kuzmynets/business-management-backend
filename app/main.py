from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.employee.router import router as employee_router
from app.modules.manager.task.router_task import router as manager_router
from app.modules.invites.router import router as invites_router
from app.modules.manager.projects.router_projects import projects_router, employees_router as router_projects, tasks_router as task
from app.modules.manager.orders.router_orders import router as orders_router
from app.modules.manager.tasks.router_tasks import router as tasks_router
from app.modules.manager.dashboard.router_dashboard import router as dashboard_router
from app.modules.owner.MyBusiness.router_business import router as business_router
from app.modules.owner.Finance.router_finance import router as finance_router
from app.modules.owner.Analytic.router_analytics import router as analytic_router
from app.modules.owner.Subscription.router_subscription import router as subscription_router
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
app.include_router(router_projects)
app.include_router(projects_router)
app.include_router(task)
app.include_router(orders_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)
app.include_router(business_router)
app.include_router(finance_router)
app.include_router(analytic_router)
app.include_router(subscription_router)