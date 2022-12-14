from fastapi import (APIRouter, Depends, HTTPException, Request, responses,
                     status)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.v1.route_login import login_for_access_token
from db.repository.tasks import list_tasks
from db.session import get_db
from webapps.auth.forms import LoginForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful")
            tasks = list_tasks(db=db)
            setattr(form, "tasks", tasks)

            response = templates.TemplateResponse(
                "general_pages/homepage.html", form.__dict__
            )
            login_for_access_token(response=response, form_data=form, db=db)

            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or password")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
    return templates.TemplateResponse("auth/login.html", form.__dict__)
