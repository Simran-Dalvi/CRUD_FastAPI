from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from random import randint
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select

'''
Campaign(table)
-campaign_id
-campaign_name
-due_date(date)
-created_at (date)
'''
class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    campaign_name: str =Field(index=True)
    due_date: datetime |None =Field(default=None,index=True)
    created_at: datetime =Field(default_factory=lambda:datetime.now(timezone.utc), index=True)

class CampaignCreate(SQLModel):
    campaign_name: str
    due_date: datetime | None =None

sqllite_file_name = "database.db"
sqllite_url = f"sqlite:///{sqllite_file_name}"

connection_arguments = {"check_same_thread": False}
engine=create_engine(sqllite_url,connect_args=connection_arguments, echo=True)


def create_db_and_Table():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_Table()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(campaign_name="Summer Launch", due_date=datetime.now()),
                Campaign(campaign_name="Black Friday", due_date=datetime.now()),
                Campaign(campaign_name="Diwali Special", due_date=datetime.now()),
                Campaign(campaign_name="Christmas Offer", due_date=datetime.now())            
            ])
            session.commit()
        yield

app =FastAPI(root_path="/app/v1", lifespan=lifespan)

# this is what root page shows
@app.get("/")
async def root():
    return {"Root gives": "Hello World!!!"}

T=TypeVar("T")
class Response(BaseModel, Generic[T]):
    data : T


@app.get("/campaigns", response_model=Response[list[Campaign]])
async def read_campaigns(session:SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data": data}

@app.get("/campaign/{id}", response_model=Response[Campaign])
async def read_campaign_by_id(id:int,session:SessionDep):
    data=session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    return{"data":data}

@app.post("/campaign",status_code=201,response_model=Response[Campaign])
async def create_campaign(campaign:CampaignCreate, session:SessionDep):
    data=Campaign.model_validate(campaign)
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}
    
@app.put("/campaign/{id}",response_model=Response[Campaign])
async def update_campaign(id:int, campaign: CampaignCreate, session:SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    data.campaign_name= campaign.campaign_name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}


@app.delete("/campaign",status_code=204)
async def delete_campaign(id:int, session:SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()