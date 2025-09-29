from fastapi import FastAPI, HTTPException, status, Path, Query
from typing import List, Optional, Annotated
from fastapi.responses import JSONResponse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
def get_all_expenses(
    sort_by: Annotated[
        Optional[str],
        Query(
            title="مرتب‌سازی بر اساس",
            description="فیلدی که می‌خواهید بر اساس آن مرتب‌سازی کنید",
            regex="^(id|description|amount)$",  # فقط این مقادیر مجاز
            example="amount",
        ),
    ] = None,
    order: Annotated[
        Optional[str],
        Query(
            title="ترتیب مرتب‌سازی",
            description="ترتیب صعودی یا نزولی",
            regex="^(asc|desc)$",
            example="desc",
        ),
    ] = "asc",
    limit: Annotated[
        Optional[int],
        Query(
            title="تعداد محدود",
            description="حداکثر تعداد هزینه‌هایی که برگردانده شود",
            ge=1,
            le=100,
            example=10,
        ),
    ] = None,
    min_amount: Annotated[
        Optional[float],
        Query(
            title="حداقل مبلغ",
            description="فیلتر هزینه‌ها بر اساس حداقل مبلغ",
            ge=0,
            example=50000,
        ),
    ] = None,
    max_amount: Annotated[
        Optional[float],
        Query(
            title="حداکثر مبلغ",
            description="فیلتر هزینه‌ها بر اساس حداکثر مبلغ",
            ge=0,
            example=500000,
        ),
    ] = None,
):

    if not expenses:
        return {
            "message": "هیچ هزینه‌ای ثبت نشده است",
            "expenses": [],
            "total_count": 0,
            "total_amount": 0,
        }

    filtered_expenses = expenses.copy()

    if min_amount is not None:
        filtered_expenses = [
            exp for exp in filtered_expenses if exp["amount"] >= min_amount
        ]

    if max_amount is not None:
        filtered_expenses = [
            exp for exp in filtered_expenses if exp["amount"] <= max_amount
        ]

    if min_amount is not None and max_amount is not None:
        if min_amount > max_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="حداقل مبلغ نمی‌تواند بزرگ‌تر از حداکثر مبلغ باشد",
            )

    if sort_by in ["id", "description", "amount"]:
        reverse_order = order == "desc"
        filtered_expenses.sort(key=lambda x: x[sort_by], reverse=reverse_order)

    if limit is not None:
        filtered_expenses = filtered_expenses[:limit]

    total_amount = sum(expense["amount"] for expense in filtered_expenses)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "expenses": filtered_expenses,
            "total_count": len(filtered_expenses),
            "total_amount": total_amount,
            "filters_applied": {
                "sort_by": sort_by,
                "order": order,
                "limit": limit,
                "min_amount": min_amount,
                "max_amount": max_amount,
            },
        },
    )


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(
    description: Annotated[
        str,
        Query(
            title="توضیح هزینه",
            description="توضیح کاملی از هزینه انجام شده",
            min_length=3,
            max_length=200,
            regex=r"^[آ-ی\u0600-\u06FFa-zA-Z0-9\s\-_.,!؟]+$",
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
    category: Annotated[
        Optional[str],
        Query(
            title="دسته‌بندی",
            description="دسته‌بندی هزینه",
            regex="^(غذا|حمل‌ونقل|خرید|قبوض|تفریح|سایر)$",
            example="غذا",
        ),
    ] = "سایر",
):
    global next_id

    new_expense = {
        "id": next_id,
        "description": description.strip(),
        "amount": amount,
        "category": category,
        "created_at": "2025-09-29T14:45:00",  # در حالت واقعی از datetime استفاده کنید
    }

    expenses.append(new_expense)
    next_id += 1

    return {
        "success": True,
        "message": "هزینه با موفقیت ایجاد شد",
        "expense": new_expense,
    }


@app.get("/expenses/search")
def search_expenses(
    query: Annotated[
        str,
        Query(
            title="متن جستجو",
            description="متنی که می‌خواهید در توضیحات هزینه‌ها جستجو کنید",
            min_length=1,
            max_length=100,
            regex=r"^[آ-ی\u0600-\u06FFa-zA-Z0-9\s]+$",  # فارسی، انگلیسی، عدد و فاصله
            example="خرید",
        ),
    ],
    case_sensitive: Annotated[
        Optional[bool],
        Query(
            title="حساسیت به حروف",
            description="آیا جستجو حساس به حروف بزرگ و کوچک باشد؟",
            example=False,
        ),
    ] = False,
    exact_match: Annotated[
        Optional[bool],
        Query(
            title="تطابق دقیق",
            description="جستجو برای تطابق دقیق یا جزئی",
            example=False,
        ),
    ] = False,
    limit_results: Annotated[
        Optional[int],
        Query(
            title="محدود کردن نتایج",
            description="حداکثر تعداد نتایج جستجو",
            ge=1,
            le=50,
            example=20,
        ),
    ] = None,
):

    search_query = query if case_sensitive else query.lower()

    matching_expenses = []

    for expense in expenses:
        expense_desc = (
            expense["description"] if case_sensitive else expense["description"].lower()
        )

        # نوع جستجو
        if exact_match:
            if search_query == expense_desc:
                matching_expenses.append(expense)
        else:
            if search_query in expense_desc:
                matching_expenses.append(expense)

    if limit_results is not None:
        matching_expenses = matching_expenses[:limit_results]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "query": query,
            "search_options": {
                "case_sensitive": case_sensitive,
                "exact_match": exact_match,
                "limit_results": limit_results,
            },
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
