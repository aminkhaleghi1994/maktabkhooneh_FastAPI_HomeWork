from fastapi import FastAPI, HTTPException, status, Path, Query
from typing import List, Optional, Annotated
from fastapi.responses import JSONResponse


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


@app.get("/expenses")
def get_all_expenses():

    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "هیچ هزینه‌ای ثبت نشده است",
                "expenses": [],
                "total_count": 0,
                "total_amount": 0,
            },
        )

    total_amount = sum(expense["amount"] for expense in expenses)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "expenses": expenses,
            "total_count": len(expenses),
            "total_amount": total_amount,
        },
    )


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(
    description: Annotated[
        str,
        Query(
            title="توضیح هزینه",
            description="توضیح کاملی از هزینه انجام شده",
            min_length=1,
            max_length=200,
            example="خرید مواد غذایی از فروشگاه",
        ),
    ],
    amount: Annotated[
        float,
        Query(
            title="مبلغ هزینه",
            description="مبلغ هزینه به تومان",
            gt=0,  # greater than 0
            le=10000000,  # حداکثر 10 میلیون تومان
            example=150000.0,
        ),
    ],
):
    global next_id

    new_expense = {
        "id": next_id,
        "description": description.strip(),
        "amount": amount,
    }

    expenses.append(new_expense)
    next_id += 1

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "هزینه با موفقیت ایجاد شد",
            "expense": new_expense,
        },
    )


@app.get("/expenses/search")
def search_expenses(
    query: Annotated[
        str,
        Query(
            title="متن جستجو",
            description="متنی که می‌خواهید در توضیحات هزینه‌ها جستجو کنید",
            min_length=1,
            max_length=100,
            example="خرید",
        ),
    ],
):

    matching_expenses = [
        expense for expense in expenses if query in expense["description"]
    ]

    if not matching_expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="چیزی پیدا نشد"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "query": query,
            "results": matching_expenses,
            "count": len(matching_expenses),
            "total_searched": len(expenses),
        },
    )


@app.get("/expenses/{expense_id}")
def get_expense(
    expense_id: Annotated[
        int,
        Path(
            title="شناسه هزینه",
            description="شناسه یکتای عددی هزینه که باید بزرگتر از 0 باشد",
            ge=1,  # greater than or equal to 1
            le=999999,  # less than or equal to 999999
            example=1,
        ),
    ],
):

    expense = find_expense_by_id(expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"expenses": expense})


@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: Annotated[
        int,
        Path(
            title="شناسه هزینه",
            description="شناسه هزینه‌ای که می‌خواهید ویرایش کنید",
            ge=1,
            example=1,
        ),
    ],
    description: Optional[str] = None,
    amount: Optional[float] = None,
):

    expense_index = find_expense_index(expense_id)

    if expense_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"هزینه‌ای با شناسه {expense_id} یافت نشد",
        )

    if description is not None:
        if not description or not description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="توضیح هزینه نمی‌تواند خالی باشد",
            )
        expenses[expense_index]["description"] = description.strip()

    if amount is not None:
        if amount <= 0:
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
def delete_expense(
    expense_id: Annotated[
        int,
        Path(
            title="شناسه هزینه",
            description="شناسه هزینه‌ای که می‌خواهید حذف کنید",
            ge=1,
            le=999999,
            example=1,
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "هزینه با موفقیت حذف شد",
            "deleted_expense": deleted_expense,
        },
    )
