from celery.worker.state import total_count
from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Expense Management API",
    description="API for managing expenses with array storage",
)


expenses: List[dict] = [
    {"id": 1, "description": "خرید مواد غذایی", "amount": 250000.0},
    {"id": 2, "description": "پرداخت قبض برق", "amount": 185000.0},
    {"id": 3, "description": "خرید بنزین", "amount": 120000.0},
    {"id": 4, "description": "هزینه اینترنت ماهانه", "amount": 95000.0},
    {"id": 5, "description": "خرید لباس", "amount": 420000.0},
]


next_id = len(expenses) + 1


def find_expense_by_id(expense_id: int) -> Optional[dict]:
    for expense in expenses:
        if expense["id"] == expense_id:
            return expense
    return None


def find_expense_index(expense_id: int) -> int:
    for i, expense in enumerate(expenses):
        if expense["id"] == expense_id:
            return i
    return -1


@app.get("/")
def read_root():
    return {"message": "Expense Management API - استفاده از /docs برای مشاهده مستندات"}


@app.get("/expenses")
def get_all_expenses(sort_by: Optional[str] = None, order: Optional[str] = "asc"):
    """
    دریافت لیست همه هزینه‌ها
    sort_by: id, description, amount
    order: asc, desc
    """

    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "هیچ هزینه‌ای ثبت نشده است",
                "expenses": [],
                "total_count": 0,
                "total_amount": 0,
            },
        )

    sorted_expenses = expenses.copy()

    if sort_by in ["id", "description", "amount"]:
        reverse_order = order == "desc"
        sorted_expenses.sort(key=lambda x: x[sort_by], reverse=reverse_order)

    total_amount = sum(expense["amount"] for expense in expenses)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "expenses": sorted_expenses,
            "total_count": len(expenses),
            "total_amount": total_amount,
        },
    )


@app.post("/expenses")
def create_expense(description: str, amount: float):
    global next_id

    # اعتبارسنجی ورودی‌ها
    if not description or not description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="توضیح هزینه نمی‌تواند خالی باشد",
        )

    if not amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="مقدار هزینه نمی‌تواند خالی باشد",
        )

    if amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="مبلغ هزینه باید بزرگ‌تر از صفر باشد",
        )

    new_expense = {"id": next_id, "description": description, "amount": amount}

    expenses.append(new_expense)
    next_id += 1

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "هزینه با موفقیت ایجاد شد", "expenses": expenses},
    )


@app.get("/expenses/search")
def search_expenses(query: str):
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="متن جستجو نمی‌تواند خالی باشد",
        )
    query = query.strip()

    matching_expenses = [
        expense for expense in expenses if query in expense["description"]
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "query": query,
            "results": matching_expenses,
            "count": len(matching_expenses),
        },
    )


@app.get("/expenses/{expense_id}")
def get_expense_by_id(expense_id: int):
    expense = find_expense_by_id(expense_id)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"expenses": expense})


@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int, description: Optional[str] = None, amount: Optional[float] = None
):
    expense_index = find_expense_index(expense_id)

    if expense_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    # اعتبارسنجی ورودی‌ها
    if description is not None:
        if not description or not description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="توضیح هزینه نمی‌تواند خالی باشد",
            )
        expenses[expense_index]["description"] = description.strip()

    if amount is not None:
        if amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="مبلغ هزینه باید بزرگ‌تر از صفر باشد",
            )

        expenses[expense_index]["amount"] = amount

    if description is None and amount is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="حداقل یک فیلد برای بروزرسانی ارسال کنید",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "هزینه با موفقیت بروزرسانی شد",
            "expense": expenses[expense_index],
        },
    )


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    expense_index = find_expense_index(expense_id)

    if expense_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    deleted_expense = expenses.pop(expense_index)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "هزینه با موفقیت حذف شد",
            "deleted_expense": deleted_expense,
        },
    )
