"""feat: added default gtable settings

Revision ID: 7e980526de5c
Revises: aaa25c8916ef
Create Date: 2024-08-20 14:03:36.024681

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e980526de5c"
down_revision: Union[str, None] = "aaa25c8916ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            """INSERT INTO table_indexes(value, "verbose", label, col, col_int, row)
            VALUES
                ('penalties_down', 'Нет смен в Сохо и Барби', 'L14', 'L', 12, 14),
                ('shifts_on_week', 'Смены в неделю', 'X14', 'X', 24, 14),
                ('shifts_on_month', 'Смены в месяц', 'W14', 'W', 23, 14),
                ('total_shifts', 'Смены в 3 месяца', 'Y14', 'Y', 25, 14),
                ('percent', 'Повышенный процент', 'V14', 'V', 22, 14),
                ('users_start', 'Первый ряд пользователей', 'F14', 'F', 6, 14),
                ('users_end', 'Последний ряд пользователей', 'F24', 'F', 6, 24),
                ('final_percent', 'Итоговый процент', 'S1', 'S', 22, 24);
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.DDL("DELETE from table_indexes;"))
