from __future__ import annotations
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re


"""
این الگو اجازه می‌دهد متن توضیح شامل حروف فارسی/لاتین، ارقام، فاصله و تعدادی علائم مجاز باشد
تا داده متنی کنترل‌شده‌تری دریافت شود.
"""

DESCRIPTION_PATTERN = r"^[\u0600-\u06FFA-Za-z0-9\s\-.,!()،]+$"

DescriptionStr = Annotated[
    str,
    Field(
        min_length=1,
        max_length=200,
        pattern=DESCRIPTION_PATTERN,
        description="Amount Description",
    ),
]

"""
فیلد amount از نوع Decimal
با قیود بزرگ‌تر از صفر، سقف ۱۰۰ میلیون، کنترل تعداد کل ارقام و تعداد اعشار (صفر برای تومان) تنظیم می‌شود
تا دقت مالی حفظ و محدوده مجاز اعمال گردد.
"""
AmountInt = Annotated[
    int,
    Field(
        gt=0,
        le=100_000_000,
        description="Amount in Tooman",
    ),
]

ExpenseID = Annotated[int, Field(ge=1, le=999999)]


class ExpenseBase(BaseModel):
    description: DescriptionStr
    amount: AmountInt

    @field_validator("description", mode="after")
    @classmethod
    def normalize_description(cls, v) -> str:
        v = re.sub(r"\s+", " ", v.strip())
        if not v:
            raise ValueError("توضیح بعد از trim نباید خالی باشد")
        return v


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    description: Optional[DescriptionStr] = None
    amount: Optional[AmountInt] = None

    @field_validator("description", mode="after")
    @classmethod
    def normalize_optional_description(cls, v) -> str:
        if v is None:
            return v
        v2 = re.sub(r"\s+", " ", v.strip())
        if not v2:
            raise ValueError("توضیح بعد از trim نباید خالی باشد")
        return v2

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.amount is None and self.description is None:
            raise ValueError(
                "حداقل یکی از فیلدهای description یا amount باید ارسال شود"
            )
        return self


class ExpenseOut(BaseModel):
    id: ExpenseID
    description: str
    amount: AmountInt


class ExpensesListOut(BaseModel):
    expenses: List[ExpenseOut]
    total_count: Annotated[int, Field(ge=0)]
    total_amount: AmountInt


class ExpenseEnvelope(BaseModel):
    success: bool = True
    message: str
    expense: ExpenseOut


class SearchResultsOut(BaseModel):
    query: str
    results: List[ExpenseOut]
    count: int
    total_count: int


class DeleteEnvelope(BaseModel):
    message: str
    deleted_expense: ExpenseOut


"""
این کار ارجاع‌های رو‌به‌جلو را تثبیت می‌کند
و خطای TypeAdapter/Annotated not fully defined را رفع می‌کند.
"""

# در انتهای فایل schemas.py بعد از همهٔ کلاس‌ها:
for m in (
    ExpenseOut,
    ExpensesListOut,
    ExpenseEnvelope,
    SearchResultsOut,
    DeleteEnvelope,
    ExpenseCreate,
    ExpenseUpdate,
):
    m.model_rebuild()
