from fastapi import FastAPI, HTTPException, status, Query, Path, Body
from typing import Optional, Dict, Any
import uvicorn


app = FastAPI(
    title="Maktabkhooneh Expense Management FastAPI HomeWork",
    description="An API to manage expenses using an in-memory dictionary.",
    version="1.0.0",
)


expenses_db: Dict[int, Dict[str, Any]] = {
    1 : {"id": 1, "description": "خرید هفتگی", "amount": 150.75},
    2: {"id": 2, "description": "پرداخت قبض برق", "amount": 65.20},
    3: {"id": 3, "description": "بلیط سینما", "amount": 25.0},
}

next_id = max(expenses_db.keys()) + 1 if expenses_db else 1

@app.get("/expenses", status_code=status.HTTP_200_OK)
async def get_all_expenses():
    return list(expenses_db.values())


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
async def create_expense(description: str = Body(title="Description", message="Description Field"),
                         amount: float = Body(gt=0, title="Amount", message="Amount Field"),
                         ):
    global next_id
    new_expense = {
        "id": next_id,
        "description": description,
        "amount": amount,
    }
    expenses_db[next_id] = new_expense
    next_id += 1
    return new_expense



@app.get("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def retrieve_expense(expense_id: int = Path(..., gt=0, title="Expense ID")
                           ):
    if expense_id not in expenses_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد."
        )
    return expenses_db[expense_id]


@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense(expense_id: int = Path(..., gt=0, title="Expense ID"),
                   description: str = Query(..., title="Description", message="Description Field"),
                   amount: float = Query(..., gt=0, title="Amount", message="Amount Field"),
                   ):
    if expense_id not in expenses_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} برای ویرایش یافت نشد."
        )
    expenses_db[expense_id]["description"] = description
    expenses_db[expense_id]["amount"] = amount
    return expenses_db[expense_id]


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: int = Path(gt=0, title="Expense ID")
                         ):
    if expense_id not in expenses_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} برای حذف یافت نشد."
        )
    del expenses_db[expense_id]
    return


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True, reload_delay=500)
