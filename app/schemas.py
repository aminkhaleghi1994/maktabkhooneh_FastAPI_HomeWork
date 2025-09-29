# app/schemas/expenses_annotated.py
from __future__ import annotations
from typing import Annotated, List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator
import re

DESCRIPTION_PATTERN = r"^[\u0600-\u06FFA-Za-z0-9\s\-.,!()،]+$"

