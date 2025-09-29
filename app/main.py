from fastapi import FastAPI, HTTPException, status, Path, Query
from typing import List, Optional, Annotated
from decimal import Decimal
from fastapi.responses import JSONResponse
from schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseOut,
    ExpensesListOut,
    ExpenseEnvelope,
    SearchResultsOut,
    DeleteEnvelope,
)


# اطلاعات کاربردی و زیبا
app = FastAPI(
    title="💰 سیستم مدیریت هزینه‌ها",
    description="""
    🚀 **API مدیریت هزینه‌های شخصی**

    این سیستم امکانات زیر را فراهم می‌کند:

    * **ایجاد هزینه جدید** - ثبت هزینه‌های روزانه
    * **مشاهده لیست هزینه‌ها** - دسترسی به تمام هزینه‌ها
    * **جستجو در هزینه‌ها** - پیدا کردن هزینه‌های خاص
    * **ویرایش هزینه‌ها** - بروزرسانی اطلاعات
    * **حذف هزینه‌ها** - حذف هزینه‌های غیرضروری

    🎯 **ویژگی‌ها:**
    - نگهداری در حافظه (بدون دیتابیس)
    - پشتیبانی از عملیات CRUD کامل  
    - جستجوی پیشرفته
    - مرتب‌سازی انعطاف‌پذیر

    📝 **نوشته شده با FastAPI + Python**
    """,
    version="1.0.0",
    contact={
        "name": "تیم توسعه",
        "url": "https://github.com/aminkhaleghi1994",
        "email": "aminkhaleghi1373@gamil.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
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


@app.get("/expenses", response_model=ExpensesListOut, status_code=status.HTTP_200_OK)
def get_all_expenses():
    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="هیچ هزینه‌ای ثبت نشده است",
        )
    total_amount = sum(e["amount"] for e in expenses)

    return {
        "expenses": [ExpenseOut(**e).model_dump() for e in expenses],
        "total_count": len(expenses),
        "total_amount": total_amount,
    }


@app.post(
    "/expenses", response_model=ExpenseEnvelope, status_code=status.HTTP_201_CREATED
)
def create_expense(payload: ExpenseCreate):
    global next_id

    new_expense = {
        "id": next_id,
        "description": payload.description,
        "amount": payload.amount,
    }

    expenses.append(new_expense)
    next_id += 1

    return {
        "success": True,
        "message": "هزینه با موفقیت ایجاد شد",
        "expense": ExpenseOut(**new_expense),
    }


@app.get(
    "/expenses/search", response_model=SearchResultsOut, status_code=status.HTTP_200_OK
)
def search_expenses(
    q: Annotated[
        str,
        Query(..., description="متن جستجو", min_length=1, max_length=100),
    ],
):

    normalized_q = q.strip()
    matches = [
        expense for expense in expenses if normalized_q in expense["description"]
    ]

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="چیزی پیدا نشد"
        )

    return {
        "query": normalized_q,
        "results": [ExpenseOut(**expense) for expense in matches],
        "count": len(matches),
        "total_count": len(expenses),
    }


@app.get(
    "/expenses/{expense_id}", response_model=ExpenseOut, status_code=status.HTTP_200_OK
)
def get_expense(
    expense_id: Annotated[
        int,
        Path(
            ...,
            description="شناسه هزینه",
            ge=1,
            le=999999,
        ),
    ],
):

    expense = find_expense_by_id(expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    return ExpenseOut(**expense)


@app.put(
    "/expenses/{expense_id}",
    response_model=ExpenseEnvelope,
    status_code=status.HTTP_200_OK,
)
def update_expense(
    expense_id: Annotated[
        int,
        Path(
            ...,
            description="شناسه هزینه",
            ge=1,
            le=999999,
        ),
    ],
    payload: ExpenseUpdate = ...,
):

    expense_index = find_expense_index(expense_id)

    if expense_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    if payload.description is not None:
        expenses[expense_index]["description"] = payload.description

    if payload.amount is not None:
        expenses[expense_index]["amount"] = payload.amount

    return {
        "message": "هزینه با موفقیت بروزرسانی شد",
        "expense": ExpenseOut(**expenses[expense_index]),
    }


@app.delete(
    "/expenses/{expense_id}",
    response_model=DeleteEnvelope,
    status_code=status.HTTP_200_OK,
)
def delete_expense(
    expense_id: Annotated[
        int,
        Path(
            ...,
            description="شناسه هزینه",
            ge=1,
            le=999999,
        ),
    ],
):

    expense_index = find_expense_index(expense_id)

    if expense_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    deleted_expense = expenses.pop(expense_index)

    return {
        "message": "هزینه با موفقیت حذف شد",
        "deleted_expense": ExpenseOut(**deleted_expense),
    }
