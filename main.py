from datetime import date, datetime
from random import randint
from fastapi import FastAPI, HTTPException, Request, Response
from typing import Any

'''
Campaign(table)
-campaign_id
-campaign_name
-due_date(date)
-created_at (date)

every campaign has a bunch of pieces (marketing post, blog, advertisment)

pieces(table)
-piece_id
-campaing_id
-piece_name
-content
-content_type
-created_at(date)
'''

app =FastAPI(root_path="/app/v1")

# this is what root page shows
@app.get("/")
async def root():
    return {"message": "Hello World!!!"}

data:Any = [
    {
        "campaign_id":1,
        "campaign_name":"Summer Launch",
        "due_date":datetime.now(),
        "created_at":datetime.now()
    },
    {
        "campaign_id":2,
        "campaign_name":"Black Friday",
        "due_date":datetime.now(),
        "created_at":datetime.now()
    },
    {
        "campaign_id":3,
        "campaign_name":"Diwali Sale",
        "due_date":datetime.now(),
        "created_at":datetime.now()
    }
]

# getting all the data
@app.get("/campaign")
async def read_campaign():
    return {"campaign":data}


# geting the data for a single id
@app.get("/campaign/{id}")
async def read_campaign_through_id(id:int):
    for campaign in data:
        if campaign.get("campaign_id")==id:
            return {"campaign":campaign}
    raise HTTPException(status_code=404,detail="Campaign not Found ")

"""
@app.post("/campaign")
async def create_campaign(request:Request):
    body =await request.json()
    new={
        "campaign_id":4,
        "campaign_name":body.get("campaign_name"),
        "due_date":body.get("due_date"),
        "created_at":datetime.now()
    }
    data.append(new)
    return {"campaign": data}
    
thiss part shows an internal server which i dont know why ;-(    
    
"""

@app.post("/campaign",status_code=201)
async def create_campaign(body:dict[str,Any]):
    new={
        "campaign_id":randint(4,100),
        "campaign_name":body.get("campaign_name"),
        "due_date":body.get("due_date"),
        "created_at":datetime.now()
    }

    data.append(new)
    return {"campaigns": new}

@app.put("/campaign/{id}")
async def update_campaign(id:int,body:dict[str,Any]):
    for index, campaign in enumerate(data):
        if campaign.get("campaign_id")==id:
            update:Any={
                "campaign_id":id,
                "campaign_name":body.get("campaign_name"),
                "due_date":body.get("due_date"),
                "created_at":campaign.get("created_at")
            }
            data[index] = update

            return{"campaign": update}
    raise HTTPException(status_code=404)



@app.delete("/campaign/{id}")
async def delete_campaign(id:int):
    for index,campaign in enumerate(data):
        if campaign.get("campaign_id") == id:
            data.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404)